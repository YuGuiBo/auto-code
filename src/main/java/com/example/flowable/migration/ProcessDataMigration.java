package com.example.flowable.migration;

import com.example.flowable.dynamic.model.ProcessConfig;
import com.example.flowable.storage.entity.ProcessDefinitionEntity;
import com.example.flowable.storage.repository.ProcessDefinitionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;

/**
 * 流程数据迁移工具
 * 
 * 职责：
 * - 首次启动时自动将静态文件迁移到数据库
 * - 扫描 resources/processes/ 目录下的所有流程
 * - 读取BPMN和YAML文件内容
 * - 保存到数据库
 * 
 * 注意：
 * - 只在数据库为空时执行迁移
 * - 可以通过配置开关控制是否启用
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Component
@Order(1) // 确保在DatabaseProcessConfigLoader之前执行
public class ProcessDataMigration implements ApplicationRunner {
    
    @Autowired
    private ProcessDefinitionRepository processRepository;
    
    @Value("${app.process.migration.enabled:true}")
    private boolean migrationEnabled;
    
    private final PathMatchingResourcePatternResolver resolver = 
        new PathMatchingResourcePatternResolver();
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());
    
    @Override
    public void run(ApplicationArguments args) throws Exception {
        if (!migrationEnabled) {
            log.info("⏭️ 数据迁移已禁用（app.process.migration.enabled=false）");
            return;
        }
        
        // 检查数据库是否为空
        long count = processRepository.count();
        if (count > 0) {
            log.info("⏭️ 数据库已有 {} 个流程定义，跳过迁移", count);
            return;
        }
        
        log.info("🔄 开始从文件迁移流程定义到数据库...");
        migrateFromFiles();
        log.info("✅ 流程定义迁移完成");
    }
    
    /**
     * 从文件系统迁移到数据库
     */
    private void migrateFromFiles() {
        try {
            // 扫描所有 .bpmn20.xml 文件
            Resource[] bpmnResources = resolver.getResources(
                "classpath:processes/**/*.bpmn20.xml"
            );
            
            log.info("📂 发现 {} 个BPMN文件", bpmnResources.length);
            
            for (Resource bpmnResource : bpmnResources) {
                try {
                    migrateOneProcess(bpmnResource);
                } catch (Exception e) {
                    log.error("❌ 迁移失败: {}", bpmnResource.getFilename(), e);
                }
            }
            
        } catch (Exception e) {
            log.error("❌ 扫描配置目录失败", e);
        }
    }
    
    /**
     * 迁移单个流程
     */
    private void migrateOneProcess(Resource bpmnResource) throws Exception {
        // 1. 读取BPMN文件
        String bpmnContent = new String(
            bpmnResource.getInputStream().readAllBytes(), 
            StandardCharsets.UTF_8
        );
        
        // 2. 查找对应的YAML配置文件
        String bpmnPath = bpmnResource.getURL().getPath();
        String configPath = bpmnPath.replace(".bpmn20.xml", "-config.yml");
        
        Resource configResource = resolver.getResource("file:" + configPath);
        if (!configResource.exists()) {
            log.warn("⚠️ 未找到配置文件: {}", configPath);
            return;
        }
        
        String configContent = new String(
            configResource.getInputStream().readAllBytes(),
            StandardCharsets.UTF_8
        );
        
        // 3. 解析配置获取基本信息
        ProcessConfig config = yamlMapper.readValue(
            configContent, 
            ProcessConfig.class
        );
        
        // 4. 创建实体并保存
        ProcessDefinitionEntity entity = new ProcessDefinitionEntity();
        entity.setProcessKey(config.getProcess().getKey());
        entity.setProcessName(config.getProcess().getName());
        entity.setBpmnContent(bpmnContent);
        entity.setConfigContent(configContent);
        entity.setApiPrefix(config.getProcess().getApiPrefix());
        entity.setDescription(config.getProcess().getDescription());
        entity.setEnabled(true);
        entity.setCreatedBy("system");
        entity.setDeployed(false); // 标记为未部署，由DatabaseProcessConfigLoader负责部署
        
        processRepository.save(entity);
        
        log.info("✅ 迁移成功: {} - {}", 
            config.getProcess().getKey(), 
            config.getProcess().getName());
    }
}