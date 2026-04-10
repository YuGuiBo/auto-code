package com.example.flowable.dynamic.model;

import lombok.Data;
import java.util.Map;

/**
 * 任务配置
 * 定义每个任务节点的行为
 * 
 * @author Auto-Code Platform
 */
@Data
public class TaskConfig {
    
    /**
     * 任务名称（对应BPMN中的name属性）
     */
    private String taskName;
    
    /**
     * 任务Key（对应BPMN中的id属性）
     */
    private String taskKey;
    
    /**
     * 审批类型（用于API路径识别）
     * 例如：manager, dept-manager, admin
     */
    private String approvalType;
    
    /**
     * 变量配置
     */
    private VariableConfig variables;
    
    /**
     * 状态映射
     * key: approved/rejected
     * value: 对应的状态名称
     */
    private Map<String, String> statusMapping;
}