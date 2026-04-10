package com.example.flowable.dynamic.model;

import lombok.Data;

/**
 * 业务规则
 * 支持SpEL表达式进行动态判断
 * 
 * @author Auto-Code Platform
 */
@Data
public class BusinessRule {
    
    /**
     * 条件表达式（SpEL格式）
     * 例如：leaveDays > remainingDays
     */
    private String condition;
    
    /**
     * 满足条件时设置的状态
     */
    private String status;
    
    /**
     * 是否停止流程
     * true: 不启动Flowable流程，直接结束
     * false: 继续启动流程
     */
    private Boolean stopProcess;
}