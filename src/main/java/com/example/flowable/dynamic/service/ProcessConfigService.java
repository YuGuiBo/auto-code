package com.example.flowable.dynamic.service;

import com.example.flowable.dynamic.config.ProcessConfigLoader;
import com.example.flowable.dynamic.model.ProcessConfig;
import com.example.flowable.dynamic.model.StatusConfig;
import com.example.flowable.dynamic.model.TaskConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * 流程配置服务
 * 提供配置查询和管理功能
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Service
public class ProcessConfigService {
    
    @Autowired
    private ProcessConfigLoader configLoader;
    
    /**
     * 获取所有流程配置
     */
    public Map<String, ProcessConfig> getAllConfigs() {
        return configLoader.getAllConfigs();
    }
    
    /**
     * 根据流程Key获取配置
     */
    public ProcessConfig getConfig(String processKey) {
        return configLoader.getConfig(processKey);
    }
    
    /**
     * 根据API前缀获取配置
     */
    public ProcessConfig getConfigByApiPrefix(String apiPrefix) {
        return configLoader.getConfigByApiPrefix(apiPrefix);
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
        configLoader.reloadConfigs();
    }
}