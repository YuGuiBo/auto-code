package com.example.flowable.reimbursement.controller;

import com.example.flowable.reimbursement.model.ReimbursementDTO;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import com.example.flowable.reimbursement.service.ReimbursementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 报销管理控制器
 * 负责报销申请、审批和查询功能的API接口
 * 
 * @author Generated
 */
@RestController
@RequestMapping("/api/reimbursement")
public class ReimbursementController {

    @Autowired
    private ReimbursementService reimbursementService;

    /**
     * 申请报销
     * 
     * @param request 报销申请信息
     * @return 流程实例ID
     */
    @PostMapping("/apply")
    public ResponseEntity<Map<String, Object>> applyReimbursement(@RequestBody ReimbursementDTO request) {
        try {
            String processInstanceId = reimbursementService.applyReimbursement(request);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("processInstanceId", processInstanceId);
            response.put("message", "报销申请已提交");
            response.put("applicant", request.getApplicantName());
            response.put("amount", request.getAmount());
            response.put("reimbursementType", request.getReimbursementType());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "申请失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 直接经理审批
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
            reimbursementService.managerApprove(taskId, approved, comment);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "经理审批完成");
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
     * 部门经理审批（仅大额报销 > 1000元）
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
            reimbursementService.departmentManagerApprove(taskId, approved, comment);
            
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
     * 财务审批
     * 
     * @param taskId 任务ID
     * @param approved 是否批准
     * @param comment 审批意见
     * @return 审批结果
     */
    @PostMapping("/finance/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> financeApprove(
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        try {
            reimbursementService.financeApprove(taskId, approved, comment);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "财务审批完成");
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
        Map<String, Object> taskInfo = reimbursementService.getTaskInfo(taskId);
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
        ProcessInstanceDTO instanceDTO = reimbursementService.getProcessInstanceById(processInstanceId);
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
        List<TaskDTO> tasks = reimbursementService.getAllTasks();
        return ResponseEntity.ok(tasks);
    }
}