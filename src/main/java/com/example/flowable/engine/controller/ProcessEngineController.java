package com.example.flowable.engine.controller;

import com.example.flowable.engine.service.ProcessEngineService;
import com.example.flowable.model.ProcessInstanceDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 通用流程引擎控制器
 * 提供与业务无关的流程操作API
 * 
 * @author Auto-Code Platform
 */
@RestController
@RequestMapping("/api/engine/process")
public class ProcessEngineController {

    @Autowired
    private ProcessEngineService processEngineService;

    /**
     * 启动流程实例（通用接口）
     * 
     * @param request {
     *   "processDefinitionKey": "leaveRequestProcess",
     *   "businessKey": "LEAVE-2024-001", (可选)
     *   "variables": { ...任意流程变量... }
     * }
     */
    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startProcess(@RequestBody Map<String, Object> request) {
        try {
            String processDefinitionKey = (String) request.get("processDefinitionKey");
            String businessKey = (String) request.get("businessKey");
            @SuppressWarnings("unchecked")
            Map<String, Object> variables = (Map<String, Object>) request.get("variables");
            
            if (processDefinitionKey == null || processDefinitionKey.isEmpty()) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("message", "processDefinitionKey is required");
                return ResponseEntity.badRequest().body(errorResponse);
            }
            
            String processInstanceId = processEngineService.startProcess(
                processDefinitionKey, 
                businessKey, 
                variables != null ? variables : new HashMap<>()
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("processInstanceId", processInstanceId);
            response.put("message", "Process started successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to start process: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 查询流程实例
     * 
     * @param processInstanceId 流程实例ID
     */
    @GetMapping("/instance/{processInstanceId}")
    public ResponseEntity<ProcessInstanceDTO> getProcessInstance(
            @PathVariable String processInstanceId) {
        
        ProcessInstanceDTO dto = processEngineService.getProcessInstanceById(processInstanceId);
        
        if (dto != null) {
            return ResponseEntity.ok(dto);
        }
        
        return ResponseEntity.notFound().build();
    }

    /**
     * 查询所有流程实例
     */
    @GetMapping("/instances")
    public ResponseEntity<List<ProcessInstanceDTO>> getAllProcessInstances() {
        List<ProcessInstanceDTO> instances = processEngineService.getAllProcessInstances();
        return ResponseEntity.ok(instances);
    }

    /**
     * 根据流程定义Key查询流程实例
     * 
     * @param processDefinitionKey 流程定义Key
     */
    @GetMapping("/instances/by-key/{processDefinitionKey}")
    public ResponseEntity<List<ProcessInstanceDTO>> getProcessInstancesByKey(
            @PathVariable String processDefinitionKey) {
        
        List<ProcessInstanceDTO> instances = processEngineService
            .getProcessInstancesByKey(processDefinitionKey);
        
        return ResponseEntity.ok(instances);
    }

    /**
     * 获取流程变量
     * 
     * @param processInstanceId 流程实例ID
     */
    @GetMapping("/instance/{processInstanceId}/variables")
    public ResponseEntity<Map<String, Object>> getProcessVariables(
            @PathVariable String processInstanceId) {
        
        Map<String, Object> variables = processEngineService
            .getProcessVariables(processInstanceId);
        
        return ResponseEntity.ok(variables);
    }

    /**
     * 设置流程变量
     * 
     * @param processInstanceId 流程实例ID
     * @param variables 要设置的变量
     */
    @PostMapping("/instance/{processInstanceId}/variables")
    public ResponseEntity<Map<String, Object>> setProcessVariables(
            @PathVariable String processInstanceId,
            @RequestBody Map<String, Object> variables) {
        
        try {
            processEngineService.setProcessVariables(processInstanceId, variables);
            
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

    /**
     * 删除流程实例
     * 
     * @param processInstanceId 流程实例ID
     * @param reason 删除原因
     */
    @DeleteMapping("/instance/{processInstanceId}")
    public ResponseEntity<Map<String, Object>> deleteProcessInstance(
            @PathVariable String processInstanceId,
            @RequestParam(required = false, defaultValue = "Deleted by user") String reason) {
        
        try {
            processEngineService.deleteProcessInstance(processInstanceId, reason);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Process instance deleted");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to delete process: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 挂起流程实例
     * 
     * @param processInstanceId 流程实例ID
     */
    @PostMapping("/instance/{processInstanceId}/suspend")
    public ResponseEntity<Map<String, Object>> suspendProcessInstance(
            @PathVariable String processInstanceId) {
        
        try {
            processEngineService.suspendProcessInstance(processInstanceId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Process instance suspended");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to suspend process: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }

    /**
     * 激活流程实例
     * 
     * @param processInstanceId 流程实例ID
     */
    @PostMapping("/instance/{processInstanceId}/activate")
    public ResponseEntity<Map<String, Object>> activateProcessInstance(
            @PathVariable String processInstanceId) {
        
        try {
            processEngineService.activateProcessInstance(processInstanceId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Process instance activated");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "Failed to activate process: " + e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
}