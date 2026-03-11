package com.example.flowable.model;

import lombok.Data;
import java.util.Map;

/**
 * 流程启动请求DTO
 * 
 * @author Generated
 * @date 2026-03-11
 */
@Data
public class ProcessStartRequest {
    
    /**
     * 流程定义Key
     */
    private String processDefinitionKey;
    
    /**
     * 业务Key（可选）
     */
    private String businessKey;
    
    /**
     * 流程变量
     */
    private Map<String, Object> variables;
    
    /**
     * 流程启动人
     */
    private String startUserId;
}