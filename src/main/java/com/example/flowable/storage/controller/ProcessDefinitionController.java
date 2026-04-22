package com.example.flowable.storage.controller;

import com.example.flowable.storage.dto.ProcessDefinitionUploadRequest;
import com.example.flowable.storage.entity.ProcessDefinitionEntity;
import com.example.flowable.storage.entity.ProcessDeploymentHistoryEntity;
import com.example.flowable.storage.service.ProcessDefinitionService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 流程定义管理控制器
 * 
 * 提供流程定义的上传、查询、删除等REST API接口
 * 
 * @author Auto-Code Platform
 */
@RestController
@RequestMapping("/api/admin/process-definition")
@Slf4j
public class ProcessDefinitionController {
    
    @Autowired
    private ProcessDefinitionService processDefinitionService;
    
    /**
     * 上传流程定义
     * POST /api/admin/process-definition/upload
     */
    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadProcessDefinition(
            @RequestBody ProcessDefinitionUploadRequest request) {
        
        try {
            log.info("接收流程定义上传请求: {}", request.getProcessKey());
            
            ProcessDefinitionEntity definition = processDefinitionService.uploadProcessDefinition(
                request.getProcessKey(),
                request.getProcessName(),
                request.getBpmnContent(),
                request.getConfigContent(),
                request.getApiPrefix(),
                request.getCreatedBy()
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程定义上传成功并已部署");
            response.put("processKey", definition.getProcessKey());
            response.put("processName", definition.getProcessName());
            response.put("version", definition.getVersion());
            response.put("deploymentId", definition.getDeploymentId());
            response.put("apiPrefix", definition.getApiPrefix());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("流程定义上传失败", e);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "上传失败: " + e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 查询所有流程定义
     * GET /api/admin/process-definition/list
     */
    @GetMapping("/list")
    public ResponseEntity<List<ProcessDefinitionEntity>> listAllDefinitions() {
        List<ProcessDefinitionEntity> definitions = processDefinitionService.getAllProcessDefinitions();
        return ResponseEntity.ok(definitions);
    }
    
    /**
     * 查询启用的流程定义
     * GET /api/admin/process-definition/list/enabled
     */
    @GetMapping("/list/enabled")
    public ResponseEntity<List<ProcessDefinitionEntity>> listEnabledDefinitions() {
        List<ProcessDefinitionEntity> definitions = processDefinitionService.getEnabledProcessDefinitions();
        return ResponseEntity.ok(definitions);
    }
    
    /**
     * 根据processKey查询流程定义
     * GET /api/admin/process-definition/{processKey}
     */
    @GetMapping("/{processKey}")
    public ResponseEntity<ProcessDefinitionEntity> getDefinition(@PathVariable String processKey) {
        try {
            ProcessDefinitionEntity definition = processDefinitionService.getProcessDefinitionByKey(processKey);
            return ResponseEntity.ok(definition);
        } catch (Exception e) {
            log.error("查询流程定义失败: {}", processKey, e);
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 查询部署历史
     * GET /api/admin/process-definition/{processKey}/history
     */
    @GetMapping("/{processKey}/history")
    public ResponseEntity<List<ProcessDeploymentHistoryEntity>> getDeploymentHistory(
            @PathVariable String processKey) {
        try {
            List<ProcessDeploymentHistoryEntity> history = 
                processDefinitionService.getDeploymentHistory(processKey);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            log.error("查询部署历史失败: {}", processKey, e);
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 删除流程定义（软删除）
     * DELETE /api/admin/process-definition/{processKey}
     */
    @DeleteMapping("/{processKey}")
    public ResponseEntity<Map<String, Object>> deleteDefinition(@PathVariable String processKey) {
        try {
            processDefinitionService.deleteProcessDefinition(processKey);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程定义已禁用");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("删除流程定义失败: {}", processKey, e);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "删除失败: " + e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 启用流程定义
     * PUT /api/admin/process-definition/{processKey}/enable
     */
    @PutMapping("/{processKey}/enable")
    public ResponseEntity<Map<String, Object>> enableDefinition(@PathVariable String processKey) {
        try {
            processDefinitionService.enableProcessDefinition(processKey);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "流程定义已启用");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("启用流程定义失败: {}", processKey, e);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "启用失败: " + e.getMessage());
            
            return ResponseEntity.badRequest().body(response);
        }
    }
}
