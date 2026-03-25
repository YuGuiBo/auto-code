package com.example.flowable.leave.service;

import com.example.flowable.leave.enums.LeaveRequestStatus;
import com.example.flowable.leave.model.LeaveRequestDTO;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import com.example.flowable.common.util.ProcessMapper;
import com.example.flowable.common.util.TaskMapper;
import org.flowable.engine.HistoryService;
import org.flowable.engine.RuntimeService;
import org.flowable.engine.TaskService;
import org.flowable.engine.history.HistoricProcessInstance;
import org.flowable.engine.runtime.ProcessInstance;
import org.flowable.task.api.Task;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 请假服务类
 * 整合了请假业务逻辑、流程查询和任务管理功能
 * 使用通用工具类进行数据转换，业务状态由本服务自己管理
 * 
 * @author Generated
 */
@Service
public class LeaveService {

    @Autowired
    private RuntimeService runtimeService;

    @Autowired
    private TaskService taskService;

    @Autowired
    private HistoryService historyService;

    /**
     * 申请请假
     * 
     * @param request 请假申请信息
     * @return 流程实例ID
     */
    public String applyLeave(LeaveRequestDTO request) {
        // 准备流程变量
        Map<String, Object> variables = new HashMap<>();
        variables.put("applicantName", request.getApplicantName());
        variables.put("leaveDays", request.getLeaveDays());
        variables.put("remainingDays", request.getRemainingDays());
        variables.put("reason", request.getReason());
        variables.put("startDate", request.getStartDate());
        variables.put("endDate", request.getEndDate());
        variables.put("leaveType", request.getLeaveType());
        
        // 根据请假天数和剩余天数，设置正确的初始状态
        // 如果剩余天数不足，流程会自动走向"假期不足"结束事件
        // 否则，流程会进入待审批状态
        if (request.getLeaveDays() > request.getRemainingDays()) {
            variables.put("status", LeaveRequestStatus.INSUFFICIENT_LEAVE.name());
        } else {
            // 无论是短期还是长期请假，都会先进入直接经理审批
            variables.put("status", LeaveRequestStatus.PENDING_MANAGER_APPROVAL.name());
        }
        
        // 启动流程实例
        ProcessInstance processInstance = runtimeService
                .startProcessInstanceByKey("leaveRequestProcess", variables);
        
        return processInstance.getId();
    }

    /**
     * 直接经理审批短期请假（<= 3天）
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     */
    public void managerApproveShortLeave(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("approved", approved);
        variables.put("managerComment", comment);
        
        // 根据审批结果更新状态
        if (approved) {
            variables.put("status", LeaveRequestStatus.APPROVED.name());
        } else {
            variables.put("status", LeaveRequestStatus.REJECTED.name());
        }
        
        // 添加审批意见
        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task != null) {
            taskService.addComment(taskId, task.getProcessInstanceId(), comment);
        }
        
        // 完成任务
        taskService.complete(taskId, variables);
    }

    /**
     * 直接经理初审长期请假（> 3天）
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     */
    public void managerApproveLongLeave(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("managerApproved", approved);
        variables.put("managerComment", comment);
        
        // 根据审批结果更新状态
        if (approved) {
            // 直接经理同意，流程将进入部门经理审批
            variables.put("status", LeaveRequestStatus.PENDING_DEPT_MANAGER_APPROVAL.name());
        } else {
            // 直接经理拒绝，流程结束
            variables.put("status", LeaveRequestStatus.REJECTED.name());
        }
        
        // 添加审批意见
        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task != null) {
            taskService.addComment(taskId, task.getProcessInstanceId(), comment);
        }
        
        // 完成任务
        taskService.complete(taskId, variables);
    }

    /**
     * 部门经理审批长期请假（> 3天）
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     */
    public void departmentManagerApprove(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("deptManagerApproved", approved);
        variables.put("deptManagerComment", comment);
        
        // 根据审批结果更新状态
        if (approved) {
            variables.put("status", LeaveRequestStatus.APPROVED.name());
        } else {
            variables.put("status", LeaveRequestStatus.REJECTED.name());
        }
        
        // 添加审批意见
        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task != null) {
            taskService.addComment(taskId, task.getProcessInstanceId(), comment);
        }
        
        // 完成任务
        taskService.complete(taskId, variables);
    }

    /**
     * 查询任务信息
     * 
     * @param taskId 任务ID
     * @return 任务信息（包括流程变量）
     */
    public Map<String, Object> getTaskInfo(String taskId) {
        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task == null) {
            return null;
        }
        
        Map<String, Object> variables = taskService.getVariables(taskId);
        
        Map<String, Object> result = new HashMap<>();
        result.put("taskId", task.getId());
        result.put("taskName", task.getName());
        result.put("processInstanceId", task.getProcessInstanceId());
        result.put("variables", variables);
        
        return result;
    }

    /**
     * 根据流程实例ID查询流程（支持运行中的流程和历史流程）
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程实例DTO，如果不存在返回null
     */
    public ProcessInstanceDTO getProcessInstanceById(String processInstanceId) {
        // 先查询运行中的流程实例
        ProcessInstance instance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (instance != null) {
            // 使用通用工具类转换
            ProcessInstanceDTO dto = ProcessMapper.toDTO(instance);
            // 填充请假业务特有的状态信息
            LeaveRequestStatus status = getLeaveStatus(processInstanceId);
            dto.setStatus(status);
            dto.setStatusDisplayName(status.getDisplayName());
            return dto;
        }
        
        // 如果运行中的流程不存在，查询历史流程
        HistoricProcessInstance historicInstance = historyService
                .createHistoricProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (historicInstance != null) {
            // 使用通用工具类转换
            ProcessInstanceDTO dto = ProcessMapper.toDTO(historicInstance);
            // 填充请假业务特有的状态信息
            LeaveRequestStatus status = getLeaveStatus(processInstanceId);
            dto.setStatus(status);
            dto.setStatusDisplayName(status.getDisplayName());
            return dto;
        }
        
        return null;
    }

    /**
     * 查询所有待办任务
     * 
     * @return 任务DTO列表
     */
    public List<TaskDTO> getAllTasks() {
        List<Task> tasks = taskService.createTaskQuery()
                .orderByTaskCreateTime()
                .desc()
                .list();
        // 使用通用工具类转换
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 获取请假流程的业务状态
     * 从流程变量的 status 字段读取
     * 
     * @param processInstanceId 流程实例ID
     * @return 请假状态枚举
     */
    private LeaveRequestStatus getLeaveStatus(String processInstanceId) {
        // 尝试从运行中的流程获取
        ProcessInstance processInstance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (processInstance != null) {
            Map<String, Object> variables = runtimeService.getVariables(processInstanceId);
            if (variables.containsKey("status")) {
                String statusStr = (String) variables.get("status");
                try {
                    return LeaveRequestStatus.valueOf(statusStr);
                } catch (IllegalArgumentException e) {
                    return LeaveRequestStatus.SUBMITTED;
                }
            }
            return LeaveRequestStatus.SUBMITTED;
        }
        
        // 从历史流程获取
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
                return LeaveRequestStatus.SUBMITTED;
            }
        }
        
        return LeaveRequestStatus.SUBMITTED;
    }
}