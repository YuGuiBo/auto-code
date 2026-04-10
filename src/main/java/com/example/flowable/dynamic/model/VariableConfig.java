package com.example.flowable.dynamic.model;

import lombok.Data;

/**
 * 任务变量配置
 * 定义任务审批时使用的变量名
 * 
 * @author Auto-Code Platform
 */
@Data
public class VariableConfig {
    
    /**
     * 审批结果变量名
     * 例如：approved, managerApproved, deptManagerApproved
     */
    private String approvalResult;
    
    /**
     * 评论字段名
     * 例如：comment, managerComment, deptManagerComment
     */
    private String commentField;
}