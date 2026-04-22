package com.example.flowable.storage.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 流程定义实体
 * 
 * 存储BPMN文件和YAML配置的原始内容
 * 职责：
 * - 存储原始BPMN XML和YAML配置文本
 * - 版本管理（version字段自动递增）
 * - 审计信息（创建人、更新人、时间等）
 * - 部署状态（deployed, deployment_id）
 * - 支持回滚（保留历史版本）
 * 
 * @author Auto-Code Platform
 */
@Entity
@Table(name = "process_definition")
@Data
public class ProcessDefinitionEntity {
    
    /**
     * 主键ID
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * 流程Key（唯一标识）
     * 对应BPMN文件中的process id
     */
    @Column(name = "process_key", unique = true, nullable = false, length = 255)
    private String processKey;
    
    /**
     * 流程名称（中文）
     */
    @Column(name = "process_name", nullable = false, length = 255)
    private String processName;
    
    /**
     * 版本号（自动递增）
     * 每次更新流程定义时递增
     */
    @Column(name = "version", nullable = false)
    private Integer version = 1;
    
    /**
     * BPMN文件内容（XML格式）
     * 存储完整的BPMN XML文本
     */
    @Column(name = "bpmn_content", columnDefinition = "TEXT", nullable = false)
    private String bpmnContent;
    
    /**
     * YAML配置内容
     * 存储完整的YAML配置文本
     */
    @Column(name = "config_content", columnDefinition = "TEXT", nullable = false)
    private String configContent;
    
    /**
     * API路径前缀
     * 例如：/api/leave, /api/reimbursement
     */
    @Column(name = "api_prefix", length = 100)
    private String apiPrefix;
    
    /**
     * 流程描述
     */
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;
    
    /**
     * Flowable部署ID
     * 记录在Flowable引擎中的部署ID，用于查询关联
     * 注意：这不是外键，只是记录引用
     */
    @Column(name = "deployment_id", length = 255)
    private String deploymentId;
    
    /**
     * 是否已部署到Flowable引擎
     */
    @Column(name = "deployed")
    private Boolean deployed = false;
    
    /**
     * 是否启用
     */
    @Column(name = "enabled")
    private Boolean enabled = true;
    
    /**
     * 创建人
     */
    @Column(name = "created_by", length = 100)
    private String createdBy;
    
    /**
     * 创建时间
     */
    @Column(name = "created_time")
    private LocalDateTime createdTime;
    
    /**
     * 更新人
     */
    @Column(name = "updated_by", length = 100)
    private String updatedBy;
    
    /**
     * 更新时间
     */
    @Column(name = "updated_time")
    private LocalDateTime updatedTime;
    
    /**
     * 部署时间
     */
    @Column(name = "deployed_time")
    private LocalDateTime deployedTime;
    
    /**
     * 创建前自动设置时间
     */
    @PrePersist
    protected void onCreate() {
        createdTime = LocalDateTime.now();
        updatedTime = LocalDateTime.now();
    }
    
    /**
     * 更新前自动设置更新时间
     */
    @PreUpdate
    protected void onUpdate() {
        updatedTime = LocalDateTime.now();
    }
}