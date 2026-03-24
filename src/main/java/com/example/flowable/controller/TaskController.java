package com.example.flowable.controller;

import com.example.flowable.model.TaskCompleteRequest;
import com.example.flowable.model.TaskDTO;
import com.example.flowable.service.TaskServiceImpl;
import com.example.flowable.util.TaskMapper;
import org.flowable.task.api.Task;
import org.flowable.task.api.history.HistoricTaskInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 任务管理控制器
 * 
 * @author Generated
 */
@RestController
@RequestMapping("/api/task")
public class TaskController {

    @Autowired
    private TaskServiceImpl taskService;

    /**
     * 查询所有待办任务
     */
    @GetMapping("/list")
    public ResponseEntity<List<TaskDTO>> getAllTasks() {
        List<Task> tasks = taskService.getAllTasks();
        List<TaskDTO> taskDTOs = TaskMapper.toDTOList(tasks);
        return ResponseEntity.ok(taskDTOs);
    }

    /**
     * 根据执行人查询待办任务
     */
    @GetMapping("/assignee/{assignee}")
    public ResponseEntity<List<TaskDTO>> getTasksByAssignee(@PathVariable String assignee) {
        List<Task> tasks = taskService.getTasksByAssignee(assignee);
        List<TaskDTO> taskDTOs = TaskMapper.toDTOList(tasks);
        return ResponseEntity.ok(taskDTOs);
    }

    /**
     * 根据任务ID查询任务
     */
    @GetMapping("/{taskId}")
    public ResponseEntity<TaskDTO> getTaskById(@PathVariable String taskId) {
        Task task = taskService.getTaskById(taskId);
        if (task != null) {
            TaskDTO taskDTO = TaskMapper.toDTO(task);
            return ResponseEntity.ok(taskDTO);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * 完成任务
     */
    @PostMapping("/complete/{taskId}")
    public ResponseEntity<Map<String, Object>> completeTask(
            @PathVariable String taskId,
            @RequestBody(required = false) TaskCompleteRequest request) {
        try {
            Map<String, Object> variables = request != null ? request.getVariables() : null;
            taskService.completeTask(taskId, variables);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "任务完成成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "任务完成失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 认领任务
     */
    @PostMapping("/claim/{taskId}")
    public ResponseEntity<Map<String, Object>> claimTask(
            @PathVariable String taskId,
            @RequestParam String userId) {
        try {
            taskService.claimTask(taskId, userId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "任务认领成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "任务认领失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 委托任务
     */
    @PostMapping("/delegate/{taskId}")
    public ResponseEntity<Map<String, Object>> delegateTask(
            @PathVariable String taskId,
            @RequestParam String userId) {
        try {
            taskService.delegateTask(taskId, userId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "任务委托成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "任务委托失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 转办任务
     */
    @PostMapping("/transfer/{taskId}")
    public ResponseEntity<Map<String, Object>> transferTask(
            @PathVariable String taskId,
            @RequestParam String userId) {
        try {
            taskService.transferTask(taskId, userId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "任务转办成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "任务转办失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 查询候选任务
     */
    @GetMapping("/candidate/user/{candidateUser}")
    public ResponseEntity<List<TaskDTO>> getCandidateTasks(@PathVariable String candidateUser) {
        List<Task> tasks = taskService.getCandidateTasks(candidateUser);
        List<TaskDTO> taskDTOs = TaskMapper.toDTOList(tasks);
        return ResponseEntity.ok(taskDTOs);
    }

    /**
     * 查询候选组任务
     */
    @GetMapping("/candidate/group/{candidateGroup}")
    public ResponseEntity<List<TaskDTO>> getCandidateGroupTasks(@PathVariable String candidateGroup) {
        List<Task> tasks = taskService.getCandidateGroupTasks(candidateGroup);
        List<TaskDTO> taskDTOs = TaskMapper.toDTOList(tasks);
        return ResponseEntity.ok(taskDTOs);
    }

    /**
     * 查询历史任务
     */
    @GetMapping("/history/process/{processInstanceId}")
    public ResponseEntity<List<HistoricTaskInstance>> getHistoricTasks(@PathVariable String processInstanceId) {
        List<HistoricTaskInstance> tasks = taskService.getHistoricTasks(processInstanceId);
        return ResponseEntity.ok(tasks);
    }

    /**
     * 查询已完成的任务
     */
    @GetMapping("/finished/{assignee}")
    public ResponseEntity<List<HistoricTaskInstance>> getFinishedTasks(@PathVariable String assignee) {
        List<HistoricTaskInstance> tasks = taskService.getFinishedTasks(assignee);
        return ResponseEntity.ok(tasks);
    }

    /**
     * 添加任务评论
     */
    @PostMapping("/{taskId}/comment")
    public ResponseEntity<Map<String, Object>> addComment(
            @PathVariable String taskId,
            @RequestParam String processInstanceId,
            @RequestParam String message) {
        try {
            taskService.addComment(taskId, processInstanceId, message);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "评论添加成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "添加评论失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
}