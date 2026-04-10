package com.example.flowable.dynamic.config;

import com.example.flowable.dynamic.model.ProcessConfig;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 流程配置加载器
 * 在应用启动时加载所有流程配置文件
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Component
public class ProcessConfigLoader implements ApplicationRunner {
    
    private final Map<String, ProcessConfig> processConfigs = new ConcurrentHashMap<>();
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());
    private final PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
    
    @Override
    public void run(ApplicationArguments args) throws Exception {
        log.info("开始加载流程配置文件...");
        loadAllConfigs();
        log.info("流程配置加载完成，共加载 {} 个流程", processConfigs.size());
    }
    
    /**
     * 加载所有配置文件
     */
    public void loadAllConfigs() {
        processConfigs.clear();
        
        try {
            // 查找所有 *-config.yml 文件
            Resource[] resources = resolver.getResources("classpath:process-configs/*-config.yml");
            
            for (Resource resource : resources) {
                try {
                    ProcessConfig config = yamlMapper.readValue(
                        resource.getInputStream(), 
                        ProcessConfig.class
                    );
                    
                    String processKey = config.getProcess().getKey();
                    processConfigs.put(processKey, config);
                    
                    log.info("✅ 加载配置: {} - {}", 
                        config.getProcess().getName(), 
                        config.getProcess().getApiPrefix());
                    
                } catch (IOException e) {
                    log.error("❌ 加载配置文件失败: {}", resource.getFilename(), e);
                }
            }
            
        } catch (IOException e) {
            log.error("❌ 扫描配置目录失败", e);
        }
    }
    
    /**
     * 重新加载所有配置（用于热更新）
     */
    public synchronized void reloadConfigs() {
        log.info("🔄 重新加载流程配置...");
        loadAllConfigs();
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