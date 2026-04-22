package com.example.flowable.storage.dto;

import lombok.Data;

/**
 * 流程定义上传请求DTO
 * 
 * 用于接收前端上传的流程定义数据
 * 
 * @author Auto-Code Platform
 */
@Data
public class ProcessDefinitionUploadRequest {
    
    /**
     * 流程Key（必填）
     * 对应BPMN文件中的process id
     */
    private String processKey;
    
    /**
     * 流程名称（必填）
     * 流程的中文名称
     */
    private String processName;
    
    /**
     * BPMN文件内容（必填）
     * 完整的BPMN XML文本
     */
    private String bpmnContent;
    
    /**
     * YAML配置内容（必填）
     * 完整的YAML配置文本
     */
    private String configContent;
    
    /**
     * API路径前缀（可选）
     * 例如：/api/leave, /api/reimbursement
     */
    private String apiPrefix;
    
    /**
     * 流程描述（可选）
     */
    private String description;
    
    /**
     * 创建人（必填）
     * 记录是谁上传的流程定义
     */
    private String createdBy;
}