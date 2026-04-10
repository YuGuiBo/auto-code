package com.example.flowable.dynamic.model;

import lombok.Data;
import java.util.List;
import java.util.Map;

/**
 * 流程配置主类
 * 对应YAML配置文件的根结构
 * 
 * @author Auto-Code Platform
 */
@Data
public class ProcessConfig {
    
    /**
     * 流程基本信息
     */
    private ProcessInfo process;
    
    /**
     * 状态定义
     * key: 状态名称（如：SUBMITTED, APPROVED等）
     * value: 状态配置
     */
    private Map<String, StatusConfig> statuses;
    
    /**
     * 任务配置列表
     */
    private List<TaskConfig> tasks;
    
    /**
     * 初始化配置
     */
    private InitializationConfig initialization;
    
    /**
     * 必填字段列表
     */
    private List<String> requiredFields;
}