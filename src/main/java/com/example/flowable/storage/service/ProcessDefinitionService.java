package com.example.flowable.storage.service;

import com.example.flowable.dynamic.config.DatabaseProcessConfigLoader;
import com.example.flowable.dynamic.model.ProcessConfig;
import com.example.flowable.storage.entity.ProcessDefinitionEntity;
import com.example.flowable.storage.entity.ProcessDeploymentHistoryEntity;
import com.example.flowable.storage.repository.ProcessDefinitionRepository;
import com.example.flowable.storage.repository.ProcessDeploymentHistoryRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import lombok.extern.slf4j.Slf4j;
import org.flowable.bpmn.converter.BpmnXMLConverter;
import org.flowable.bpmn.model.BpmnModel;
import org.flowable.engine.RepositoryService;
import org.flowable.engine.repository.Deployment;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayInputStream;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 流程定义服务
 * 
 * 核心职责：
 * - 流程定义的上传和保存
 * - BPMN和YAML的验证
 * - 部署到Flowable引擎
 * - 版本管理
 * - 部署历史记录
 * 
 * @author Auto-Code Platform
 */
@Service
@Slf4j
public class ProcessDefinitionService {
    
    @Autowired
    private ProcessDefinitionRepository processRepository;
    
    @Autowired
    private ProcessDeploymentHistoryRepository historyRepository;
    
    @Autowired
    private RepositoryService repositoryService;
    
    @Autowired
    private DatabaseProcessConfigLoader configLoader;
    
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());
    
    /**
     * 上传新流程定义（热部署）
     * 
     * 核心流程：
     * 1. 验证BPMN和YAML格式
     * 2. 保存到数据库（如果已存在则版本号递增）
     * 3. 部署到Flowable引擎
     * 4. 记录部署历史
     * 5. 触发热加载
     * 
     * @param processKey 流程Key
     * @param processName 流程名称
     * @param bpmnContent BPMN文件内容
     * @param configContent YAML配置内容
     * @param apiPrefix API前缀
     * @param createdBy 创建人
     * @return 流程定义实体
     */
    @Transactional
    public ProcessDefinitionEntity uploadProcessDefinition(
            String processKey,
            String processName,
            String bpmnContent,
            String configContent,
            String apiPrefix,
            String createdBy) {
        
        log.info("📥 开始上传流程定义: {}", processKey);
        
        // 1. 验证BPMN和YAML格式
        validateBpmnAndConfig(bpmnContent, configContent, processKey);
        
        // 2. 检查是否已存在
        Optional<ProcessDefinitionEntity> existing = processRepository.findByProcessKey(processKey);
        
        ProcessDefinitionEntity definition;
        if (existing.isPresent()) {
            // 更新现有定义（版本号递增）
            definition = existing.get();
            log.info("🔄 更新现有流程定义，当前版本: {}, 新版本: {}", 
                definition.getVersion(), definition.getVersion() + 1);
            
            definition.setVersion(definition.getVersion() + 1);
            definition.setBpmnContent(bpmnContent);
            definition.setConfigContent(configContent);
            definition.setProcessName(processName);
            definition.setApiPrefix(apiPrefix);
            definition.setUpdatedBy(createdBy);
            definition.setUpdatedTime(LocalDateTime.now());
            definition.setDeployed(false); // 标记为未部署
        } else {
            // 创建新定义
            log.info("✨ 创建新流程定义");
            definition = new ProcessDefinitionEntity();
            definition.setProcessKey(processKey);
            definition.setProcessName(processName);
            definition.setBpmnContent(bpmnContent);
            definition.setConfigContent(configContent);
            definition.setApiPrefix(apiPrefix);
            definition.setCreatedBy(createdBy);
        }
        
        // 3. 保存到数据库
        definition = processRepository.save(definition);
        log.info("💾 流程定义已保存到数据库，ID: {}", definition.getId());
        
        // 4. 部署到Flowable引擎（关键步骤）
        try {
            deployToFlowable(definition, createdBy);
            log.info("🚀 流程已部署到Flowable引擎，DeploymentId: {}", definition.getDeploymentId());
        } catch (Exception e) {
            log.error("❌ 部署到Flowable失败", e);
            // 记录失败历史
            recordDeploymentHistory(definition, createdBy, "FAILED", e.getMessage());
            throw new RuntimeException("部署到Flowable引擎失败: " + e.getMessage(), e);
        }
        
        // 5. 触发热加载（重新加载所有配置）
        try {
            configLoader.loadAllConfigsFromDatabase();
            log.info("🔄 配置热加载完成");
        } catch (Exception e) {
            log.error("⚠️ 配置热加载失败", e);
            // 热加载失败不影响部署成功
        }
        
        log.info("✅ 流程定义上传成功: {} - v{}", processKey, definition.getVersion());
        
        return definition;
    }
    
    /**
     * 部署BPMN到Flowable引擎
     * 这是实现动态流程的核心方法
     * 必须通过API部署，不能直接插入引擎表
     * 
     * @param definition 流程定义实体
     * @param deployedBy 部署人
     */
    private void deployToFlowable(ProcessDefinitionEntity definition, String deployedBy) {
        log.info("🚀 开始部署到Flowable引擎: {}", definition.getProcessKey());
        
        try {
            // 使用RepositoryService完成部署
            Deployment deployment = repositoryService.createDeployment()
                .name(definition.getProcessName() + " - v" + definition.getVersion())
                .addString(definition.getProcessKey() + ".bpmn20.xml", definition.getBpmnContent())
                .deploy();
            
            // 更新部署信息
            definition.setDeploymentId(deployment.getId());
            definition.setDeployed(true);
            definition.setDeployedTime(LocalDateTime.now());
            processRepository.save(definition);
            
            // 记录部署历史
            recordDeploymentHistory(definition, deployedBy, "SUCCESS", null);
            
            log.info("✅ 部署成功 - DeploymentId: {}, Name: {}", 
                deployment.getId(), deployment.getName());
            
        } catch (Exception e) {
            log.error("❌ 部署失败: {}", definition.getProcessKey(), e);
            throw new RuntimeException("部署BPMN到Flowable引擎失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 记录部署历史
     * 
     * @param definition 流程定义
     * @param deployedBy 部署人
     * @param status 部署状态
     * @param errorMessage 错误信息
     */
    private void recordDeploymentHistory(
            ProcessDefinitionEntity definition, 
            String deployedBy, 
            String status, 
            String errorMessage) {
        
        ProcessDeploymentHistoryEntity history = new ProcessDeploymentHistoryEntity();
        history.setProcessDefinitionId(definition.getId());
        history.setDeploymentId(definition.getDeploymentId());
        history.setVersion(definition.getVersion());
        history.setDeploymentStatus(status);
        history.setErrorMessage(errorMessage);
        history.setDeployedBy(deployedBy);
        history.setBpmnSnapshot(definition.getBpmnContent());
        history.setConfigSnapshot(definition.getConfigContent());
        
        historyRepository.save(history);
    }
    
    /**
     * 验证BPMN和YAML配置
     * 
     * @param bpmnContent BPMN内容
     * @param configContent YAML配置内容
     * @param processKey 流程Key
     */
    private void validateBpmnAndConfig(String bpmnContent, String configContent, String processKey) {
        // 1. 验证BPMN格式
        try {
            // Flowable 7.x 需要使用 InputStreamProvider
            byte[] bytes = bpmnContent.getBytes();
            BpmnModel model = new BpmnXMLConverter().convertToBpmnModel(
                () -> new ByteArrayInputStream(bytes),
                false, false
            );
            
            if (model.getProcesses().isEmpty()) {
                throw new RuntimeException("BPMN文件不包含任何流程定义");
            }
            
            String bpmnProcessId = model.getMainProcess().getId();
            if (bpmnProcessId == null || bpmnProcessId.isEmpty()) {
                throw new RuntimeException("流程定义缺少process id");
            }
            
            // 验证BPMN中的process id与参数一致
            if (!bpmnProcessId.equals(processKey)) {
                throw new RuntimeException(
                    "BPMN中的process id (" + bpmnProcessId + ") 与参数processKey (" + processKey + ") 不一致"
                );
            }
            
        } catch (Exception e) {
            throw new RuntimeException("BPMN文件格式无效: " + e.getMessage(), e);
        }
        
        // 2. 验证YAML配置
        try {
            ProcessConfig config = yamlMapper.readValue(configContent, ProcessConfig.class);
            
            // 验证process.key一致性
            if (!config.getProcess().getKey().equals(processKey)) {
                throw new RuntimeException(
                    "配置文件中的process.key (" + config.getProcess().getKey() + 
                    ") 与参数processKey (" + processKey + ") 不一致"
                );
            }
            
            // 验证必填字段
            if (config.getStatuses() == null || config.getStatuses().isEmpty()) {
                throw new RuntimeException("配置文件缺少statuses定义");
            }
            
            if (config.getTasks() == null || config.getTasks().isEmpty()) {
                throw new RuntimeException("配置文件缺少tasks定义");
            }
            
            if (config.getInitialization() == null) {
                throw new RuntimeException("配置文件缺少initialization定义");
            }
            
        } catch (Exception e) {
            throw new RuntimeException("配置文件格式无效: " + e.getMessage(), e);
        }
        
        log.info("✅ BPMN和配置文件验证通过");
    }
    
    /**
     * 删除流程定义（软删除）
     * 
     * @param processKey 流程Key
     */
    @Transactional
    public void deleteProcessDefinition(String processKey) {
        ProcessDefinitionEntity definition = processRepository.findByProcessKey(processKey)
            .orElseThrow(() -> new RuntimeException("流程定义不存在: " + processKey));
        
        definition.setEnabled(false);
        processRepository.save(definition);
        
        log.info("🗑️ 流程定义已禁用: {}", processKey);
        
        // 触发热加载
        configLoader.loadAllConfigsFromDatabase();
    }
    
    /**
     * 启用流程定义
     * 
     * @param processKey 流程Key
     */
    @Transactional
    public void enableProcessDefinition(String processKey) {
        ProcessDefinitionEntity definition = processRepository.findByProcessKey(processKey)
            .orElseThrow(() -> new RuntimeException("流程定义不存在: " + processKey));
        
        definition.setEnabled(true);
        processRepository.save(definition);
        
        log.info("✅ 流程定义已启用: {}", processKey);
        
        // 触发热加载
        configLoader.loadAllConfigsFromDatabase();
    }
    
    /**
     * 查询所有流程定义
     */
    public List<ProcessDefinitionEntity> getAllProcessDefinitions() {
        return processRepository.findAll();
    }
    
    /**
     * 查询所有启用的流程定义
     */
    public List<ProcessDefinitionEntity> getEnabledProcessDefinitions() {
        return processRepository.findByEnabledTrue();
    }
    
    /**
     * 根据processKey查询流程定义
     */
    public ProcessDefinitionEntity getProcessDefinitionByKey(String processKey) {
        return processRepository.findByProcessKey(processKey)
            .orElseThrow(() -> new RuntimeException("流程定义不存在: " + processKey));
    }
    
    /**
     * 查询部署历史
     */
    public List<ProcessDeploymentHistoryEntity> getDeploymentHistory(String processKey) {
        ProcessDefinitionEntity definition = getProcessDefinitionByKey(processKey);
        return historyRepository.findByProcessDefinitionIdOrderByDeploymentTimeDesc(
            definition.getId()
        );
    }
}
