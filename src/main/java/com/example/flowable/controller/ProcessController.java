package com.example.flowable.controller;

import com.example.flowable.model.ProcessStartRequest;
import com.example.flowable.service.ProcessService;
import org.flowable.engine.repository.ProcessDefinition;
import org.flowable.engine.runtime.ProcessInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 流程管理控制器
 * 
 * @author Generated
 * @date 2026-03-11
 */
@RestController
@RequestMapping("/api/process")
public class ProcessController {

    @Autowired
    private ProcessService processService;

    /**
     * 健康检查
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "Flowable Demo");
        return ResponseEntity.ok(response);
    }

    /**
     * 启动流程实例
     */
    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startProcess(@RequestBody ProcessStartRequest request) {
        try {
            String processInstanceId = processService.startProcess(
                request.getProcessDefinitionKey(),
                request.getBusinessKey(),
                request.getVariables()
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("processInstanceId", processInstanceId);
            response.put("message", "流程启动成功");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "流程启动失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 查询所有流程定义
     */
    @GetMapping("/definitions")
    public ResponseEntity<List<ProcessDefinition>> getProcessDefinitions() {
        List<ProcessDefinition> definitions = processService.getProcessDefinitions();
        return ResponseEntity.ok(definitions);
    }

    /**
     * 查询所有流程实例
     */
    @GetMapping("/instances")
    public ResponseEntity<List<ProcessInstance>> getProcessInstances() {
        List<ProcessInstance> instances = processService.getProcessInstances();
        return ResponseEntity.ok(instances);
    }

    /**
     * 根据ID查询流程实例
     */
    @GetMapping("/instance/{processInstanceId}")
    public ResponseEntity<ProcessInstance> getProcessInstanceById(@PathVariable String processInstanceId) {
        ProcessInstance instance = processService.getProcessInstanceById(processInstanceId);
        if (instance != null) {
            return ResponseEntity.ok(instance);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * 删除流程实例
     */
    @DeleteMapping("/instance/{processInstanceId}")
    public ResponseEntity<Map<String, Object>> deleteProcessInstance(
            @PathVariable String processInstanceId,
            @RequestParam(required = false, defaultValue = "用户手动删除") String reason) {
        try {
            processService.deleteProcessInstance(processInstanceId, reason);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程实例删除成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "删除失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 挂起流程实例
     */
    @PostMapping("/instance/{processInstanceId}/suspend")
    public ResponseEntity<Map<String, Object>> suspendProcessInstance(@PathVariable String processInstanceId) {
        try {
            processService.suspendProcessInstance(processInstanceId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程实例已挂起");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "挂起失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 激活流程实例
     */
    @PostMapping("/instance/{processInstanceId}/activate")
    public ResponseEntity<Map<String, Object>> activateProcessInstance(@PathVariable String processInstanceId) {
        try {
            processService.activateProcessInstance(processInstanceId);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程实例已激活");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "激活失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 获取流程变量
     */
    @GetMapping("/instance/{processInstanceId}/variables")
    public ResponseEntity<Map<String, Object>> getProcessVariables(@PathVariable String processInstanceId) {
        Map<String, Object> variables = processService.getProcessVariables(processInstanceId);
        return ResponseEntity.ok(variables);
    }

    /**
     * 设置流程变量
     */
    @PostMapping("/instance/{processInstanceId}/variables")
    public ResponseEntity<Map<String, Object>> setProcessVariables(
            @PathVariable String processInstanceId,
            @RequestBody Map<String, Object> variables) {
        try {
            processService.setProcessVariables(processInstanceId, variables);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程变量设置成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "设置失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
}