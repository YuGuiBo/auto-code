package com.example.flowable.dynamic.model;

import lombok.Data;

/**
 * 流程基本信息
 * 
 * @author Auto-Code Platform
 */
@Data
public class ProcessInfo {
    
    /**
     * 流程定义Key（对应BPMN中的id）
     */
    private String key;
    
    /**
     * 流程名称
     */
    private String name;
    
    /**
     * API路径前缀
     */
    private String apiPrefix;
    
    /**
     * 版本号
     */
    private String version;
    
    /**
     * 描述
     */
    private String description;
}