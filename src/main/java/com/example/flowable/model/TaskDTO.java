package com.example.flowable.model;

import lombok.Data;
import java.util.Date;

/**
 * 任务数据传输对象
 * 用于解决Flowable Task对象的懒加载序列化问题
 * 
 * @author Generated
 */
@Data
public class TaskDTO {
    
    /**
     * 任务ID
     */
    private String id;
    
    /**
     * 任务名称
     */
    private String name;
    
    /**
     * 任务Key
     */
    private String taskDefinitionKey;
    
    /**
     * 任务执行人
     */
    private String assignee;
    
    /**
     * 流程实例ID
     */
    private String processInstanceId;
    
    /**
     * 执行实例ID
     */
    private String executionId;
    
    /**
     * 流程定义ID
     */
    private String processDefinitionId;
    
    /**
     * 创建时间
     */
    private Date createTime;
    
    /**
     * 任务描述
     */
    private String description;
    
    /**
     * 任务所有者
     */
    private String owner;
    
    /**
     * 任务优先级
     */
    private Integer priority;
    
    /**
     * 到期时间
     */
    private Date dueDate;
    
    /**
     * 任务类别
     */
    private String category;
}