package com.example.flowable.overtime.service;

import com.example.flowable.common.util.ProcessMapper;
import com.example.flowable.common.util.TaskMapper;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import com.example.flowable.overtime.enums.OvertimeStatus;
import com.example.flowable.overtime.model.OvertimeDTO;
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
 * 加班申请服务
 * 负责加班申请流程的业务逻辑处理
 * 
 * @author Generated
 */
@Service
public class OvertimeService {

    @Autowired
    private RuntimeService runtimeService;

    @Autowired
    private TaskService taskService;

    @Autowired
    private HistoryService historyService;

    /**
     * 提交加班申请
     * 
     * @param request 加班申请信息
     * @return 流程实例ID
     */
    public String applyOvertime(OvertimeDTO request) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("applicantName", request.getApplicantName());
        variables.put("department", request.getDepartment());
        variables.put("overtimeDate", request.getOvertimeDate());
        variables.put("startTime", request.getStartTime());
        variables.put("endTime", request.getEndTime());
        variables.put("hours", request.getHours());
        variables.put("overtimeType", request.getOvertimeType());
        variables.put("reason", request.getReason());
        variables.put("workContent", request.getWorkContent());
        variables.put("compensationType", request.getCompensationType());
        variables.put("status", OvertimeStatus.SUBMITTED.name());

        // 启动加班申请流程
        ProcessInstance processInstance = runtimeService
                .startProcessInstanceByKey("overtimeProcess", variables);

        // 更新状态为待经理审批
        runtimeService.setVariable(processInstance.getId(), "status", 
                OvertimeStatus.PENDING_MANAGER_APPROVAL.name());

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

        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task != null) {
            String processInstanceId = task.getProcessInstanceId();
            
            if (approved) {
                // 获取加班类型和时长，判断是否需要部门经理审批
                Map<String, Object> processVariables = runtimeService.getVariables(processInstanceId);
                String overtimeType = (String) processVariables.get("overtimeType");
                Double hours = (Double) processVariables.get("hours");
                
                // 判断路由：周末/节假日或工作日长时间加班需要部门经理审批
                if ("WEEKEND".equals(overtimeType) || "HOLIDAY".equals(overtimeType) || 
                    ("WEEKDAY".equals(overtimeType) && hours > 2)) {
                    variables.put("status", OvertimeStatus.PENDING_DEPT_MANAGER_APPROVAL.name());
                } else {
                    // 工作日短时间加班直接到HR确认
                    variables.put("status", OvertimeStatus.PENDING_HR_CONFIRMATION.name());
                }
            } else {
                variables.put("status", OvertimeStatus.REJECTED.name());
            }

            taskService.complete(taskId, variables);
        }
    }

    /**
     * 部门经理审批（仅周末/节假日加班或长时间工作日加班）
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     */
    public void departmentManagerApprove(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("deptManagerApproved", approved);
        variables.put("deptManagerComment", comment);

        if (approved) {
            variables.put("status", OvertimeStatus.PENDING_HR_CONFIRMATION.name());
        } else {
            variables.put("status", OvertimeStatus.REJECTED.name());
        }

        taskService.complete(taskId, variables);
    }

    /**
     * HR确认加班记录
     * 
     * @param taskId 任务ID
     * @param approved 是否确认
     * @param comment 确认意见
     */
    public void hrConfirm(String taskId, boolean approved, String comment) {
        Map<String, Object> variables = new HashMap<>();
        variables.put("hrApproved", approved);
        variables.put("hrComment", comment);

        if (approved) {
            variables.put("status", OvertimeStatus.APPROVED.name());
        } else {
            variables.put("status", OvertimeStatus.REJECTED.name());
        }

        taskService.complete(taskId, variables);
    }

    /**
     * 查询流程实例（支持运行中和已结束的流程）
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程实例详情
     */
    public ProcessInstanceDTO getProcessInstanceById(String processInstanceId) {
        // 先查询运行中的流程实例
        ProcessInstance instance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (instance != null) {
            // 使用通用工具类转换
            ProcessInstanceDTO dto = ProcessMapper.toDTO(instance);
            // 填充加班业务特有的状态信息
            OvertimeStatus status = getOvertimeStatus(processInstanceId);
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
            // 填充加班业务特有的状态信息
            OvertimeStatus status = getOvertimeStatus(processInstanceId);
            dto.setStatus(status);
            dto.setStatusDisplayName(status.getDisplayName());
            return dto;
        }
        
        return null;
    }

    /**
     * 查询所有待办任务
     * 
     * @return 待办任务列表
     */
    public List<TaskDTO> getAllTasks() {
        List<Task> tasks = taskService.createTaskQuery()
                .orderByTaskCreateTime()
                .desc()
                .list();
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 查询任务详情
     * 
     * @param taskId 任务ID
     * @return 任务详情信息
     */
    public Map<String, Object> getTaskInfo(String taskId) {
        Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
        if (task == null) {
            return null;
        }

        Map<String, Object> taskInfo = new HashMap<>();
        taskInfo.put("id", task.getId());
        taskInfo.put("name", task.getName());
        taskInfo.put("assignee", task.getAssignee());
        taskInfo.put("createTime", task.getCreateTime());
        taskInfo.put("processInstanceId", task.getProcessInstanceId());

        // 获取流程变量
        Map<String, Object> variables = taskService.getVariables(taskId);
        taskInfo.put("variables", variables);

        return taskInfo;
    }

    /**
     * 获取加班流程的业务状态
     * 从流程变量的 status 字段读取
     * 
     * @param processInstanceId 流程实例ID
     * @return 加班状态枚举
     */
    private OvertimeStatus getOvertimeStatus(String processInstanceId) {
        // 尝试从运行中的流程获取
        ProcessInstance processInstance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (processInstance != null) {
            Map<String, Object> variables = runtimeService.getVariables(processInstanceId);
            if (variables.containsKey("status")) {
                String statusStr = (String) variables.get("status");
                try {
                    return OvertimeStatus.valueOf(statusStr);
                } catch (IllegalArgumentException e) {
                    return OvertimeStatus.SUBMITTED;
                }
            }
            return OvertimeStatus.SUBMITTED;
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
                return OvertimeStatus.valueOf(statusStr);
            } catch (IllegalArgumentException e) {
                return OvertimeStatus.SUBMITTED;
            }
        }
        
        return OvertimeStatus.SUBMITTED;
    }
}
