package com.example.flowable.model;

import lombok.Data;
import java.util.Map;

/**
 * 任务完成请求DTO
 * 
 * @author Generated
 * @date 2026-03-11
 */
@Data
public class TaskCompleteRequest {
    
    /**
     * 任务ID
     */
    private String taskId;
    
    /**
     * 任务变量
     */
    private Map<String, Object> variables;
    
    /**
     * 完成意见/备注
     */
    private String comment;
}