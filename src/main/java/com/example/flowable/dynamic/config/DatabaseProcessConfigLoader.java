package com.example.flowable.dynamic.config;

import com.example.flowable.dynamic.model.ProcessConfig;
import com.example.flowable.storage.entity.ProcessDefinitionEntity;
import com.example.flowable.storage.repository.ProcessDefinitionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import lombok.extern.slf4j.Slf4j;
import org.flowable.engine.RepositoryService;
import org.flowable.engine.repository.Deployment;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 数据库流程配置加载器
 * 
 * 核心职责：
 * - 从数据库加载流程定义（替代文件系统）
 * - 解析YAML配置
 * - 部署到Flowable引擎
 * - 缓存配置到内存
 * - 支持热加载
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Component
public class DatabaseProcessConfigLoader implements ApplicationRunner {
    
    @Autowired
    private ProcessDefinitionRepository processRepository;
    
    @Autowired
    private RepositoryService repositoryService;
    
    private final Map<String, ProcessConfig> processConfigs = new ConcurrentHashMap<>();
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());
    
    /**
     * 应用启动时自动执行
     */
    @Override
    public void run(ApplicationArguments args) throws Exception {
        log.info("🚀 开始从数据库加载流程配置...");
        loadAllConfigsFromDatabase();
        log.info("✅ 流程配置加载完成，共 {} 个流程", processConfigs.size());
    }
    
    /**
     * 从数据库加载所有流程配置并部署到Flowable
     * 这是核心方法，实现了数据库存储+热部署
     */
    public synchronized void loadAllConfigsFromDatabase() {
        processConfigs.clear();
        
        // 1. 从数据库查询所有启用的流程定义
        List<ProcessDefinitionEntity> definitions = processRepository.findByEnabledTrue();
        
        log.info("📊 从数据库查询到 {} 个启用的流程定义", definitions.size());
        
        for (ProcessDefinitionEntity definition : definitions) {
            try {
                // 2. 解析YAML配置
                ProcessConfig config = yamlMapper.readValue(
                    definition.getConfigContent(), 
                    ProcessConfig.class
                );
                
                // 3. 缓存配置到内存
                processConfigs.put(definition.getProcessKey(), config);
                
                log.info("✅ 加载配置: {} - {}", 
                    config.getProcess().getName(),
                    config.getProcess().getApiPrefix());
                
                // 4. 如果未部署到Flowable，则部署
                if (!definition.getDeployed() || definition.getDeploymentId() == null) {
                    log.info("🚀 流程未部署，开始部署: {}", definition.getProcessKey());
                    deployToFlowable(definition);
                } else {
                    log.debug("流程已部署，DeploymentId: {}", definition.getDeploymentId());
                }
                
            } catch (Exception e) {
                log.error("❌ 加载流程定义失败: {}", definition.getProcessKey(), e);
            }
        }
        
        log.info("✅ 所有流程配置加载完成");
    }
    
    /**
     * 部署BPMN到Flowable引擎
     * 注意：必须调用此方法，仅仅存入数据库是无效的
     */
    private void deployToFlowable(ProcessDefinitionEntity definition) {
        try {
            log.info("🚀 开始部署到Flowable引擎: {}", definition.getProcessKey());
            
            // 使用RepositoryService完成部署
            Deployment deployment = repositoryService.createDeployment()
                .name(definition.getProcessName() + " - v" + definition.getVersion())
                .addString(definition.getProcessKey() + ".bpmn20.xml", definition.getBpmnContent())
                .deploy();
            
            // 更新部署状态
            definition.setDeploymentId(deployment.getId());
            definition.setDeployed(true);
            definition.setDeployedTime(LocalDateTime.now());
            processRepository.save(definition);
            
            log.info("✅ 部署成功 - DeploymentId: {}, Name: {}", 
                deployment.getId(), deployment.getName());
            
        } catch (Exception e) {
            log.error("❌ 部署失败: {}", definition.getProcessKey(), e);
            throw new RuntimeException("部署BPMN到Flowable引擎失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 重新加载所有配置（用于热更新）
     */
    public synchronized void reloadConfigs() {
        log.info("🔄 重新加载流程配置...");
        loadAllConfigsFromDatabase();
        log.info("✅ 流程配置重新加载完成");
    }
    
    /**
     * 获取所有配置
     */
    public Map<String, ProcessConfig> getAllConfigs() {
        return processConfigs;
    }
    
    /**
     * 根据流程Key获取配置
     */
    public ProcessConfig getConfig(String processKey) {
        return processConfigs.get(processKey);
    }
    
    /**
     * 根据API前缀获取配置
     */
    public ProcessConfig getConfigByApiPrefix(String apiPrefix) {
        return processConfigs.values().stream()
            .filter(config -> config.getProcess().getApiPrefix().equals(apiPrefix))
            .findFirst()
            .orElse(null);
    }
}