package com.example.flowable.controller;

import com.example.flowable.model.LeaveRequestDTO;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import com.example.flowable.service.LeaveService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 请假管理控制器
 * 整合了请假申请、审批、流程查询和任务管理功能
 * 
 * @author Generated
 */
@RestController
@RequestMapping("/api/leave")
public class LeaveController {

    @Autowired
    private LeaveService leaveService;

    /**
     * 申请请假
     * 
     * @param request 请假申请信息
     * @return 流程实例ID
     */
    @PostMapping("/apply")
    public ResponseEntity<Map<String, Object>> applyLeave(@RequestBody LeaveRequestDTO request) {
        try {
            String processInstanceId = leaveService.applyLeave(request);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("processInstanceId", processInstanceId);
            response.put("message", "请假申请已提交");
            response.put("applicant", request.getApplicantName());
            response.put("leaveDays", request.getLeaveDays());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "申请失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 直接经理审批（用于短期和长期请假）
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     * @return 审批结果
     */
    @PostMapping("/manager/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> managerApprove(
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        try {
            // 获取任务信息，判断是短期还是长期请假
            Map<String, Object> taskInfo = leaveService.getTaskInfo(taskId);
            if (taskInfo == null) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "任务不存在");
                return ResponseEntity.badRequest().body(response);
            }
            
            String taskName = (String) taskInfo.get("taskName");
            
            // 根据任务名称判断调用哪个审批方法
            if ("直接经理审批".equals(taskName)) {
                // 短期请假（<= 3天）
                leaveService.managerApproveShortLeave(taskId, approved, comment);
            } else if ("直接经理初审".equals(taskName)) {
                // 长期请假（> 3天）
                leaveService.managerApproveLongLeave(taskId, approved, comment);
            } else {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "任务类型不匹配");
                return ResponseEntity.badRequest().body(response);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "审批完成");
            response.put("approved", approved);
            response.put("comment", comment);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "审批失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 部门经理审批（仅用于长期请假 > 3天）
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     * @return 审批结果
     */
    @PostMapping("/dept-manager/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> departmentManagerApprove(
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        try {
            leaveService.departmentManagerApprove(taskId, approved, comment);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "部门经理审批完成");
            response.put("approved", approved);
            response.put("comment", comment);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "审批失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 查询任务详情
     * 
     * @param taskId 任务ID
     * @return 任务详情
     */
    @GetMapping("/task/{taskId}")
    public ResponseEntity<Map<String, Object>> getTaskInfo(@PathVariable String taskId) {
        Map<String, Object> taskInfo = leaveService.getTaskInfo(taskId);
        if (taskInfo == null) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "任务不存在");
            return ResponseEntity.notFound().build();
        }
        
        return ResponseEntity.ok(taskInfo);
    }

    /**
     * 查询流程实例（支持运行中和已结束的流程）
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程实例详情
     */
    @GetMapping("/process/instance/{processInstanceId}")
    public ResponseEntity<ProcessInstanceDTO> getProcessInstanceById(@PathVariable String processInstanceId) {
        ProcessInstanceDTO instanceDTO = leaveService.getProcessInstanceById(processInstanceId);
        if (instanceDTO != null) {
            return ResponseEntity.ok(instanceDTO);
        }
        return ResponseEntity.notFound().build();
    }

    /**
     * 查询所有待办任务
     * 
     * @return 待办任务列表
     */
    @GetMapping("/task/list")
    public ResponseEntity<List<TaskDTO>> getAllTasks() {
        List<TaskDTO> tasks = leaveService.getAllTasks();
        return ResponseEntity.ok(tasks);
    }
}
