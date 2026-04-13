package com.example.flowable.dynamic.service;

import com.example.flowable.dynamic.model.*;
import com.example.flowable.engine.service.ProcessEngineService;
import com.example.flowable.engine.service.TaskEngineService;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 动态流程服务
 * 提供通用的流程操作逻辑，配置驱动
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Service
public class DynamicProcessService {
    
    @Autowired
    private ProcessConfigService configService;
    
    @Autowired
    private BusinessRuleEngine ruleEngine;
    
    @Autowired
    private ProcessEngineService processEngineService;
    
    @Autowired
    private TaskEngineService taskEngineService;
    
    /**
     * 申请流程（通用方法）
     * 
     * @param processKey 流程定义Key
     * @param requestData 申请数据
     * @return 响应Map，包含processInstanceId等信息
     */
    public Map<String, Object> applyProcess(String processKey, Map<String, Object> requestData) {
        ProcessConfig config = configService.getConfig(processKey);
        
        if (config == null) {
            throw new RuntimeException("流程配置不存在: " + processKey);
        }
        
        // 1. 验证必填字段
        validateRequiredFields(config, requestData);
        
        // 2. 准备流程变量
        Map<String, Object> variables = new HashMap<>(requestData);
        
        // 3. 执行初始化规则
        InitializationConfig initConfig = config.getInitialization();
        String initialStatus = initConfig.getDefaultStatus();
        boolean shouldStopProcess = false;
        
        // 只在DEBUG级别输出详细信息
        if (log.isDebugEnabled()) {
            log.debug("评估业务规则 - 流程: {}, 变量: {}", processKey, variables);
        }
        
        if (initConfig != null && initConfig.getBusinessRules() != null && !initConfig.getBusinessRules().isEmpty()) {
            BusinessRule matchedRule = ruleEngine.evaluateRules(
                initConfig.getBusinessRules(),
                variables
            );
            
            if (matchedRule != null) {
                initialStatus = matchedRule.getStatus();
                shouldStopProcess = Boolean.TRUE.equals(matchedRule.getStopProcess());
                log.info("业务规则匹配 - 流程: {}, 状态: {}", processKey, initialStatus);
            }
        }
        
        // 设置初始状态
        variables.put("status", initialStatus);
        
        // 4. 启动流程
        String processInstanceId = processEngineService.startProcess(
            processKey,
            null,
            variables
        );
        
        log.info("流程已启动 - {}: {}", config.getProcess().getName(), processInstanceId);
        
        // 6. 返回响应
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("processInstanceId", processInstanceId);
        response.put("message", config.getProcess().getName() + "申请已提交");
        response.put("status", initialStatus);
        
        return response;
    }
    
    /**
     * 审批任务（通用方法）
     * 
     * @param processKey 流程定义Key
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     * @return 响应Map
     */
    public Map<String, Object> approveTask(String processKey, String taskId, boolean approved, String comment) {
        ProcessConfig config = configService.getConfig(processKey);
        
        if (config == null) {
            throw new RuntimeException("流程配置不存在: " + processKey);
        }
        
        // 1. 获取任务信息
        TaskDTO task = taskEngineService.getTaskById(taskId);
        if (task == null) {
            throw new RuntimeException("任务不存在: " + taskId);
        }
        
        // 2. 根据任务名称查找任务配置
        TaskConfig taskConfig = configService.getTaskConfig(processKey, task.getName());
        if (taskConfig == null) {
            throw new RuntimeException("任务配置不存在: " + task.getName());
        }
        
        // 3. 准备审批变量
        Map<String, Object> variables = new HashMap<>();
        
        VariableConfig varConfig = taskConfig.getVariables();
        variables.put(varConfig.getApprovalResult(), approved);
        variables.put(varConfig.getCommentField(), comment);
        variables.put("comment", comment);  // 通用评论字段
        
        // 4. 根据审批结果设置状态
        Map<String, String> statusMapping = taskConfig.getStatusMapping();
        String newStatus = approved ? statusMapping.get("approved") : statusMapping.get("rejected");
        variables.put("status", newStatus);
        
        // 5. 完成任务
        taskEngineService.completeTask(taskId, variables);
        
        log.info("任务审批完成 - {}: {}", task.getName(), approved ? "批准" : "拒绝");
        
        // 6. 返回响应
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "审批完成");
        response.put("approved", approved);
        response.put("comment", comment);
        response.put("status", newStatus);
        
        return response;
    }
    
    /**
     * 查询流程实例（填充业务状态）
     * 
     * @param processKey 流程定义Key
     * @param processInstanceId 流程实例ID
     * @return 流程实例DTO
     */
    public ProcessInstanceDTO getProcessInstance(String processKey, String processInstanceId) {
        ProcessConfig config = configService.getConfig(processKey);
        
        if (config == null) {
            throw new RuntimeException("流程配置不存在: " + processKey);
        }
        
        // 1. 使用引擎服务获取流程实例
        ProcessInstanceDTO dto = processEngineService.getProcessInstanceById(processInstanceId);
        
        if (dto == null) {
            return null;
        }
        
        // 2. 填充业务状态信息
        Map<String, Object> variables = processEngineService.getProcessVariables(processInstanceId);
        
        if (variables.containsKey("status")) {
            String statusName = (String) variables.get("status");
            StatusConfig statusConfig = configService.getStatusConfig(processKey, statusName);
            
            if (statusConfig != null) {
                dto.setStatus(statusName);
                dto.setStatusDisplayName(statusConfig.getDisplayName());
            }
        }
        
        return dto;
    }
    
    /**
     * 查询流程的所有待办任务
     * 
     * @param processKey 流程定义Key
     * @return 任务列表
     */
    public List<TaskDTO> getTaskList(String processKey) {
        return taskEngineService.getTasksByProcessDefinitionKey(processKey);
    }
    
    /**
     * 验证必填字段
     */
    private void validateRequiredFields(ProcessConfig config, Map<String, Object> data) {
        List<String> requiredFields = config.getRequiredFields();
        
        if (requiredFields == null || requiredFields.isEmpty()) {
            return;
        }
        
        for (String field : requiredFields) {
            if (!data.containsKey(field) || data.get(field) == null) {
                throw new RuntimeException("缺少必填字段: " + field);
            }
        }
    }
}
