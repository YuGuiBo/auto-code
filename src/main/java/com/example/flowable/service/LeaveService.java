package com.example.flowable.service;

import com.example.flowable.enums.LeaveRequestStatus;
import com.example.flowable.model.LeaveRequestDTO;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import com.example.flowable.util.LeaveProcessMapper;
import com.example.flowable.util.LeaveTaskMapper;
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

    @Autowired
    private LeaveProcessMapper leaveProcessMapper;

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
            return leaveProcessMapper.toDTO(instance);
        }
        
        // 如果运行中的流程不存在，查询历史流程
        HistoricProcessInstance historicInstance = historyService
                .createHistoricProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (historicInstance != null) {
            return leaveProcessMapper.toDTO(historicInstance);
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
        return LeaveTaskMapper.toDTOList(tasks);
    }
}
