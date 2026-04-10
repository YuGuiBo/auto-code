package com.example.flowable.engine.controller;

import com.example.flowable.engine.service.TaskEngineService;
import com.example.flowable.model.TaskDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 通用任务引擎控制器
 * 提供与业务无关的任务操作API
 * 
 * @author Auto-Code Platform
 */
@RestController
@RequestMapping("/api/engine/task")
public class TaskEngineController {

    @Autowired
    private TaskEngineService taskEngineService;

    /**
     * 完成任务（通用接口）
     * 
     * @param request {
     *   "taskId": "task-123",
     *   "variables": { ...任意任务变量... }
     * }
     */
    @PostMapping("/complete")
    public ResponseEntity<Map<String, Object>> completeTask(@RequestBody Map<String, Object> request) {
        try {
            String taskId = (String) request.get("taskId");
            @SuppressWarnings("unchecked")
            Map<String, Object> variables = (Map<String, Object>) request.get("variables");
            
            if (taskId == null || taskId.isEmpty()) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("message", "taskId is required");
                return ResponseEntity.badRequest().body(errorResponse);
            }
            
            taskEngineService.completeTask(taskId, variables);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Task completed successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to complete task: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 查询任务详情
     * 
     * @param taskId 任务ID
     */
    @GetMapping("/{taskId}")
    public ResponseEntity<TaskDTO> getTaskById(@PathVariable String taskId) {
        TaskDTO task = taskEngineService.getTaskById(taskId);
        
        if (task != null) {
            return ResponseEntity.ok(task);
        }
        
        return ResponseEntity.notFound().build();
    }

    /**
     * 查询所有待办任务
     */
    @GetMapping("/list")
    public ResponseEntity<List<TaskDTO>> getAllTasks() {
        List<TaskDTO> tasks = taskEngineService.getAllTasks();
        return ResponseEntity.ok(tasks);
    }

    /**
     * 根据流程定义Key查询任务
     * 
     * @param processDefinitionKey 流程定义Key
     */
    @GetMapping("/list/by-key/{processDefinitionKey}")
    public ResponseEntity<List<TaskDTO>> getTasksByProcessDefinitionKey(
            @PathVariable String processDefinitionKey) {
        
        List<TaskDTO> tasks = taskEngineService
            .getTasksByProcessDefinitionKey(processDefinitionKey);
        
        return ResponseEntity.ok(tasks);
    }

    /**
     * 根据流程实例ID查询任务
     * 
     * @param processInstanceId 流程实例ID
     */
    @GetMapping("/list/by-process/{processInstanceId}")
    public ResponseEntity<List<TaskDTO>> getTasksByProcessInstanceId(
            @PathVariable String processInstanceId) {
        
        List<TaskDTO> tasks = taskEngineService
            .getTasksByProcessInstanceId(processInstanceId);
        
        return ResponseEntity.ok(tasks);
    }

    /**
     * 根据受理人查询任务
     * 
     * @param assignee 受理人
     */
    @GetMapping("/list/by-assignee/{assignee}")
    public ResponseEntity<List<TaskDTO>> getTasksByAssignee(@PathVariable String assignee) {
        List<TaskDTO> tasks = taskEngineService.getTasksByAssignee(assignee);
        return ResponseEntity.ok(tasks);
    }

    /**
     * 根据候选用户查询任务
     * 
     * @param candidateUser 候选用户
     */
    @GetMapping("/list/by-candidate-user/{candidateUser}")
    public ResponseEntity<List<TaskDTO>> getTasksByCandidateUser(
            @PathVariable String candidateUser) {
        
        List<TaskDTO> tasks = taskEngineService.getTasksByCandidateUser(candidateUser);
        return ResponseEntity.ok(tasks);
    }

    /**
     * 根据候选组查询任务
     * 
     * @param candidateGroup 候选组
     */
    @GetMapping("/list/by-candidate-group/{candidateGroup}")
    public ResponseEntity<List<TaskDTO>> getTasksByCandidateGroup(
            @PathVariable String candidateGroup) {
        
        List<TaskDTO> tasks = taskEngineService.getTasksByCandidateGroup(candidateGroup);
        return ResponseEntity.ok(tasks);
    }

    /**
     * 认领任务
     * 
     * @param taskId 任务ID
     * @param userId 用户ID
     */
    @PostMapping("/{taskId}/claim")
    public ResponseEntity<Map<String, Object>> claimTask(
            @PathVariable String taskId,
            @RequestParam String userId) {
        
        try {
            taskEngineService.claimTask(taskId, userId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Task claimed successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to claim task: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 委托任务
     * 
     * @param taskId 任务ID
     * @param userId 用户ID
     */
    @PostMapping("/{taskId}/delegate")
    public ResponseEntity<Map<String, Object>> delegateTask(
            @PathVariable String taskId,
            @RequestParam String userId) {
        
        try {
            taskEngineService.delegateTask(taskId, userId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Task delegated successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to delegate task: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 转办任务
     * 
     * @param taskId 任务ID
     * @param userId 用户ID
     */
    @PostMapping("/{taskId}/assign")
    public ResponseEntity<Map<String, Object>> setTaskAssignee(
            @PathVariable String taskId,
            @RequestParam String userId) {
        
        try {
            taskEngineService.setTaskAssignee(taskId, userId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Task assigned successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to assign task: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 获取任务变量
     * 
     * @param taskId 任务ID
     */
    @GetMapping("/{taskId}/variables")
    public ResponseEntity<Map<String, Object>> getTaskVariables(@PathVariable String taskId) {
        Map<String, Object> variables = taskEngineService.getTaskVariables(taskId);
        return ResponseEntity.ok(variables);
    }

    /**
     * 设置任务变量
     * 
     * @param taskId 任务ID
     * @param variables 变量Map
     */
    @PostMapping("/{taskId}/variables")
    public ResponseEntity<Map<String, Object>> setTaskVariables(
            @PathVariable String taskId,
            @RequestBody Map<String, Object> variables) {
        
        try {
            taskEngineService.setTaskVariables(taskId, variables);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Variables set successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to set variables: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
}
