package com.example.flowable.dynamic.service;

import com.example.flowable.dynamic.config.DatabaseProcessConfigLoader;
import com.example.flowable.dynamic.config.ProcessConfigLoader;
import com.example.flowable.dynamic.model.ProcessConfig;
import com.example.flowable.dynamic.model.StatusConfig;
import com.example.flowable.dynamic.model.TaskConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * 流程配置服务
 * 提供配置查询和管理功能
 * 优先使用数据库配置加载器，文件系统配置作为补充
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Service
public class ProcessConfigService {
    
    @Autowired
    private ProcessConfigLoader fileConfigLoader;
    
    @Autowired
    private DatabaseProcessConfigLoader dbConfigLoader;
    
    /**
     * 获取所有流程配置（合并数据库和文件系统配置，数据库优先）
     */
    public Map<String, ProcessConfig> getAllConfigs() {
        Map<String, ProcessConfig> merged = new HashMap<>();
        // 先加载文件系统配置
        merged.putAll(fileConfigLoader.getAllConfigs());
        // 再加载数据库配置（覆盖同名的文件配置）
        merged.putAll(dbConfigLoader.getAllConfigs());
        return merged;
    }
    
    /**
     * 根据流程Key获取配置（数据库优先）
     */
    public ProcessConfig getConfig(String processKey) {
        // 先从数据库加载器查找
        ProcessConfig config = dbConfigLoader.getConfig(processKey);
        if (config != null) {
            return config;
        }
        // 回退到文件系统加载器
        return fileConfigLoader.getConfig(processKey);
    }
    
    /**
     * 根据API前缀获取配置
     */
    public ProcessConfig getConfigByApiPrefix(String apiPrefix) {
        // 先从数据库加载器查找
        ProcessConfig config = dbConfigLoader.getConfigByApiPrefix(apiPrefix);
        if (config != null) {
            return config;
        }
        // 回退到文件系统加载器
        return fileConfigLoader.getConfigByApiPrefix(apiPrefix);
    }
    
    /**
     * 根据流程Key和状态名称获取状态配置
     */
    public StatusConfig getStatusConfig(String processKey, String statusName) {
        ProcessConfig config = getConfig(processKey);
        if (config == null || config.getStatuses() == null) {
            return null;
        }
        return config.getStatuses().get(statusName);
    }
    
    /**
     * 根据流程Key和任务名称获取任务配置
     */
    public TaskConfig getTaskConfig(String processKey, String taskName) {
        ProcessConfig config = getConfig(processKey);
        if (config == null || config.getTasks() == null) {
            return null;
        }
        
        return config.getTasks().stream()
            .filter(task -> task.getTaskName().equals(taskName))
            .findFirst()
            .orElse(null);
    }
    
    /**
     * 重新加载配置
     */
    public void reloadConfigs() {
        fileConfigLoader.reloadConfigs();
        dbConfigLoader.reloadConfigs();
    }
}
