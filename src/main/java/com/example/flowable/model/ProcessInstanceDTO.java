package com.example.flowable.model;

import com.example.flowable.enums.LeaveRequestStatus;
import lombok.Data;
import java.util.Date;

/**
 * 流程实例DTO
 * 包含流程实例的基本信息和状态信息
 * 
 * @author Generated
 */
@Data
public class ProcessInstanceDTO {
    
    /**
     * 流程实例ID
     */
    private String id;
    
    /**
     * 流程定义ID
     */
    private String processDefinitionId;
    
    /**
     * 流程定义Key
     */
    private String processDefinitionKey;
    
    /**
     * 流程定义名称
     */
    private String processDefinitionName;
    
    /**
     * 流程定义版本
     */
    private Integer processDefinitionVersion;
    
    /**
     * 业务Key
     */
    private String businessKey;
    
    /**
     * 开始时间
     */
    private Date startTime;
    
    /**
     * 启动用户ID
     */
    private String startUserId;
    
    /**
     * 是否已挂起
     */
    private boolean suspended;
    
    /**
     * 租户ID
     */
    private String tenantId;
    
    /**
     * 流程名称
     */
    private String name;
    
    /**
     * 流程描述
     */
    private String description;
    
    /**
     * 流程状态（业务状态）
     */
    private LeaveRequestStatus status;
    
    /**
     * 状态显示名称（中文）
     */
    private String statusDisplayName;
    
    /**
     * 是否已结束
     */
    private boolean ended;
    
    /**
     * 结束时间
     */
    private Date endTime;
    
    /**
     * 结束原因
     */
    private String endReason;
}
