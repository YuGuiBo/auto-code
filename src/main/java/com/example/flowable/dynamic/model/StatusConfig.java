package com.example.flowable.dynamic.model;

import lombok.Data;

/**
 * 状态配置
 * 替代硬编码的枚举类
 * 
 * @author Auto-Code Platform
 */
@Data
public class StatusConfig {
    
    /**
     * 状态显示名称（中文）
     */
    private String displayName;
    
    /**
     * 状态描述
     */
    private String description;
}