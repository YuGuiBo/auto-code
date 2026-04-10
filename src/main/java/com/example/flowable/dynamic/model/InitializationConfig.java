package com.example.flowable.dynamic.model;

import lombok.Data;
import java.util.List;

/**
 * 初始化配置
 * 定义流程启动时的初始化规则
 * 
 * @author Auto-Code Platform
 */
@Data
public class InitializationConfig {
    
    /**
     * 默认状态
     * 流程启动时的初始状态
     */
    private String defaultStatus;
    
    /**
     * 业务规则列表
     * 按顺序执行，第一个匹配的规则生效
     */
    private List<BusinessRule> businessRules;
}