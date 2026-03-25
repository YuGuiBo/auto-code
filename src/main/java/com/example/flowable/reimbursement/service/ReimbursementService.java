package com.example.flowable.reimbursement.service;

import com.example.flowable.reimbursement.enums.ReimbursementStatus;
import com.example.flowable.reimbursement.model.ReimbursementDTO;
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
 * 报销服务类
 * 负责报销申请、审批流程和查询功能
 * 使用通用工具类进行数据转换，业务状态由本服务自己管理
 * 
 * @author Generated
 */
@Service
public class ReimbursementService {

    @Autowired
    private RuntimeService runtimeService;

    @Autowired
    private TaskService taskService;

    @Autowired
    private HistoryService historyService;

    /**
     * 申请报销
     * 
     * @param request 报销申请信息
     * @return 流程实例ID
     */
    public String applyReimbursement(ReimbursementDTO request) {
        // 准备流程变量
        Map<String, Object> variables = new HashMap<>();
        variables.put("applicantName", request.getApplicantName());
        variables.put("department", request.getDepartment());
        variables.put("reimbursementType", request.getReimbursementType());
        variables.put("amount", request.getAmount());
        variables.put("currency", request.getCurrency());
        variables.put("expenseDate", request.getExpenseDate());
        variables.put("description", request.getDescription());
        variables.put("invoiceNumber", request.getInvoiceNumber());
        variables.put("bankAccount", request.getBankAccount());
        
        // 设置初始状态
        variables.put("status", ReimbursementStatus.PENDING_MANAGER_APPROVAL.name());
        
        // 启动流程实例
        ProcessInstance processInstance = runtimeService
                .startProcessInstanceByKey("reimbursementProcess", variables);
        
        return processInstance.getId();
    }

    /**
     * 直接经理审批
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     */
    public void managerApprove(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("managerApproved", approved);
        variables.put("managerComment", comment);
        
        // 获取任务信息以判断后续流程
        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task == null) {
            throw new RuntimeException("任务不存在");
        }
        
        // 获取报销金额
        Map<String, Object> processVariables = runtimeService.getVariables(task.getProcessInstanceId());
        Double amount = (Double) processVariables.get("amount");
        
        // 根据审批结果和金额更新状态
        if (!approved) {
            // 经理拒绝，流程结束
            variables.put("status", ReimbursementStatus.REJECTED.name());
        } else {
            // 经理批准，判断金额决定下一步
            if (amount != null && amount > 1000) {
                // 大额报销，需要部门经理审批
                variables.put("status", ReimbursementStatus.PENDING_DEPT_MANAGER_APPROVAL.name());
            } else {
                // 小额报销，直接进入财务审批
                variables.put("status", ReimbursementStatus.PENDING_FINANCE_APPROVAL.name());
            }
        }
        
        // 添加审批意见
        taskService.addComment(taskId, task.getProcessInstanceId(), comment);
        
        // 完成任务
        taskService.complete(taskId, variables);
    }

    /**
     * 部门经理审批（仅大额报销 > 1000元）
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
            // 部门经理批准，进入财务审批
            variables.put("status", ReimbursementStatus.PENDING_FINANCE_APPROVAL.name());
        } else {
            // 部门经理拒绝，流程结束
            variables.put("status", ReimbursementStatus.REJECTED.name());
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
     * 财务审批
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     */
    public void financeApprove(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("financeApproved", approved);
        variables.put("financeComment", comment);
        
        // 根据审批结果更新状态
        if (approved) {
            variables.put("status", ReimbursementStatus.APPROVED.name());
        } else {
            variables.put("status", ReimbursementStatus.REJECTED.name());
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
            // 填充报销业务特有的状态信息
            ReimbursementStatus status = getReimbursementStatus(processInstanceId);
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
            // 填充报销业务特有的状态信息
            ReimbursementStatus status = getReimbursementStatus(processInstanceId);
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
     * 获取报销流程的业务状态
     * 从流程变量的 status 字段读取
     * 
     * @param processInstanceId 流程实例ID
     * @return 报销状态枚举
     */
    private ReimbursementStatus getReimbursementStatus(String processInstanceId) {
        // 尝试从运行中的流程获取
        ProcessInstance processInstance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (processInstance != null) {
            Map<String, Object> variables = runtimeService.getVariables(processInstanceId);
            if (variables.containsKey("status")) {
                String statusStr = (String) variables.get("status");
                try {
                    return ReimbursementStatus.valueOf(statusStr);
                } catch (IllegalArgumentException e) {
                    return ReimbursementStatus.SUBMITTED;
                }
            }
            return ReimbursementStatus.SUBMITTED;
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
                return ReimbursementStatus.valueOf(statusStr);
            } catch (IllegalArgumentException e) {
                return ReimbursementStatus.SUBMITTED;
            }
        }
        
        return ReimbursementStatus.SUBMITTED;
    }
}
