package com.example.flowable.util;

import com.example.flowable.enums.LeaveRequestStatus;
import org.flowable.engine.HistoryService;
import org.flowable.engine.RuntimeService;
import org.flowable.engine.TaskService;
import org.flowable.engine.history.HistoricProcessInstance;
import org.flowable.engine.runtime.ProcessInstance;
import org.flowable.task.api.Task;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * 流程状态工具类
 * 用于获取流程的当前业务状态
 * 
 * @author Generated
 */
@Component
public class ProcessStatusUtil {
    
    @Autowired
    private RuntimeService runtimeService;
    
    @Autowired
    private TaskService taskService;
    
    @Autowired
    private HistoryService historyService;
    
    /**
     * 获取流程的当前状态
     * 
     * @param processInstanceId 流程实例ID
     * @return 状态枚举
     */
    public LeaveRequestStatus getProcessStatus(String processInstanceId) {
        // 首先检查流程变量中是否已经保存了状态
        ProcessInstance processInstance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (processInstance != null) {
            // 流程还在运行中
            Map<String, Object> variables = runtimeService.getVariables(processInstanceId);
            
            // 如果流程变量中有状态，直接返回
            if (variables.containsKey("status")) {
                String statusStr = (String) variables.get("status");
                try {
                    return LeaveRequestStatus.valueOf(statusStr);
                } catch (IllegalArgumentException e) {
                    // 如果状态值无效，继续通过任务判断
                }
            }
            
            // 根据当前任务判断状态
            Task currentTask = taskService.createTaskQuery()
                    .processInstanceId(processInstanceId)
                    .singleResult();
            
            if (currentTask != null) {
                String taskName = currentTask.getName();
                if (taskName.contains("直接经理")) {
                    return LeaveRequestStatus.PENDING_MANAGER_APPROVAL;
                } else if (taskName.contains("部门经理")) {
                    return LeaveRequestStatus.PENDING_DEPT_MANAGER_APPROVAL;
                }
            }
            
            // 默认返回已提交状态
            return LeaveRequestStatus.SUBMITTED;
        } else {
            // 流程已结束，查询历史
            HistoricProcessInstance historicProcessInstance = historyService
                    .createHistoricProcessInstanceQuery()
                    .processInstanceId(processInstanceId)
                    .singleResult();
            
            if (historicProcessInstance != null) {
                // 检查历史变量中的状态
                // 注意：过滤掉null值，因为Collectors.toMap()不接受null值
                Map<String, Object> variables = historyService
                        .createHistoricVariableInstanceQuery()
                        .processInstanceId(processInstanceId)
                        .list()
                        .stream()
                        .filter(v -> v.getValue() != null)
                        .collect(java.util.stream.Collectors.toMap(
                                v -> v.getVariableName(),
                                v -> v.getValue()
                        ));
                
                if (variables.containsKey("status")) {
                    String statusStr = (String) variables.get("status");
                    try {
                        return LeaveRequestStatus.valueOf(statusStr);
                    } catch (IllegalArgumentException e) {
                        // 继续通过deleteReason判断
                    }
                }
                
                // 根据结束原因判断
                String deleteReason = historicProcessInstance.getDeleteReason();
                if (deleteReason != null) {
                    if (deleteReason.contains("假期不足")) {
                        return LeaveRequestStatus.INSUFFICIENT_LEAVE;
                    } else if (deleteReason.contains("拒绝")) {
                        return LeaveRequestStatus.REJECTED;
                    } else if (deleteReason.contains("批准")) {
                        return LeaveRequestStatus.APPROVED;
                    }
                }
                
                // 根据结束节点判断
                if (historicProcessInstance.getEndActivityId() != null) {
                    String endActivityId = historicProcessInstance.getEndActivityId();
                    if (endActivityId.contains("approve")) {
                        return LeaveRequestStatus.APPROVED;
                    } else if (endActivityId.contains("reject")) {
                        return LeaveRequestStatus.REJECTED;
                    } else if (endActivityId.contains("insufficient")) {
                        return LeaveRequestStatus.INSUFFICIENT_LEAVE;
                    }
                }
            }
        }
        
        // 默认返回已提交状态
        return LeaveRequestStatus.SUBMITTED;
    }
    
    /**
     * 判断流程是否已结束
     * 
     * @param processInstanceId 流程实例ID
     * @return true-已结束，false-进行中
     */
    public boolean isProcessEnded(String processInstanceId) {
        ProcessInstance processInstance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        return processInstance == null;
    }
    
    /**
     * 获取流程结束原因
     * 
     * @param processInstanceId 流程实例ID
     * @return 结束原因，如果流程未结束返回null
     */
    public String getEndReason(String processInstanceId) {
        if (!isProcessEnded(processInstanceId)) {
            return null;
        }
        
        HistoricProcessInstance historicProcessInstance = historyService
                .createHistoricProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (historicProcessInstance != null) {
            return historicProcessInstance.getDeleteReason();
        }
        
        return null;
    }
}