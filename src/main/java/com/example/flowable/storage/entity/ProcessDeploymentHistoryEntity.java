package com.example.flowable.storage.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 流程部署历史实体
 * 
 * 记录每次部署的详细信息，支持审计和回滚
 * 职责：
 * - 记录每次部署的详细信息
 * - 记录部署成功/失败状态
 * - 保存错误信息（失败时）
 * - 保存内容快照（支持回滚）
 * - 提供部署审计追踪
 * 
 * @author Auto-Code Platform
 */
@Entity
@Table(name = "process_deployment_history")
@Data
public class ProcessDeploymentHistoryEntity {
    
    /**
     * 主键ID
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * 关联的流程定义ID
     * 外键关联 process_definition 表
     */
    @Column(name = "process_definition_id", nullable = false)
    private Long processDefinitionId;
    
    /**
     * Flowable部署ID
     * 对应Flowable引擎中的部署记录
     */
    @Column(name = "deployment_id", length = 255)
    private String deploymentId;
    
    /**
     * 部署时的版本号
     */
    @Column(name = "version", nullable = false)
    private Integer version;
    
    /**
     * 部署时间
     */
    @Column(name = "deployment_time")
    private LocalDateTime deploymentTime;
    
    /**
     * 部署状态
     * SUCCESS - 部署成功
     * FAILED - 部署失败
     */
    @Column(name = "deployment_status", length = 50)
    private String deploymentStatus;
    
    /**
     * 错误信息
     * 部署失败时记录详细的错误信息
     */
    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;
    
    /**
     * 部署人
     */
    @Column(name = "deployed_by", length = 100)
    private String deployedBy;
    
    /**
     * BPMN内容快照
     * 保存部署时的BPMN内容，用于回滚
     */
    @Column(name = "bpmn_snapshot", columnDefinition = "TEXT")
    private String bpmnSnapshot;
    
    /**
     * 配置内容快照
     * 保存部署时的YAML配置，用于回滚
     */
    @Column(name = "config_snapshot", columnDefinition = "TEXT")
    private String configSnapshot;
    
    /**
     * 创建前自动设置部署时间
     */
    @PrePersist
    protected void onCreate() {
        deploymentTime = LocalDateTime.now();
    }
}