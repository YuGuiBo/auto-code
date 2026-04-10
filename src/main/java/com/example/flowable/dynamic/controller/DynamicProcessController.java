package com.example.flowable.dynamic.controller;

import com.example.flowable.dynamic.model.ProcessConfig;
import com.example.flowable.dynamic.service.DynamicProcessService;
import com.example.flowable.dynamic.service.ProcessConfigService;
import com.example.flowable.model.ProcessInstanceDTO;
import com.example.flowable.model.TaskDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 动态流程控制器
 * 根据配置动态处理所有流程的API请求
 * 
 * API路径模式: /api/{flowType}/...
 * 例如: /api/leave/apply, /api/business-trip/apply
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@RestController
@RequestMapping("/api")
public class DynamicProcessController {
    
    @Autowired
    private DynamicProcessService dynamicProcessService;
    
    @Autowired
    private ProcessConfigService configService;
    
    /**
     * 通用申请接口
     * POST /api/{flowType}/apply
     */
    @PostMapping("/{flowType}/apply")
    public ResponseEntity<Map<String, Object>> apply(
            @PathVariable String flowType,
            @RequestBody Map<String, Object> request) {
        
        try {
            // 根据flowType查找配置
            String processKey = findProcessKeyByFlowType(flowType);
            
            if (processKey == null) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "未找到流程配置: " + flowType);
                return ResponseEntity.badRequest().body(response);
            }
            
            // 调用动态流程服务
            Map<String, Object> response = dynamicProcessService.applyProcess(processKey, request);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("申请失败: {}", flowType, e);
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "申请失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 通用审批接口（简化版，自动识别任务类型）
     * POST /api/{flowType}/approve/{taskId}?approved=true&comment=同意
     */
    @PostMapping("/{flowType}/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> approve(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        try {
            String processKey = findProcessKeyByFlowType(flowType);
            
            if (processKey == null) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "未找到流程配置: " + flowType);
                return ResponseEntity.badRequest().body(response);
            }
            
            Map<String, Object> response = dynamicProcessService.approveTask(
                processKey, taskId, approved, comment
            );
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("审批失败: {} - taskId: {}", flowType, taskId, e);
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "审批失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 兼容性接口：直接经理审批
     * POST /api/{flowType}/manager/approve/{taskId}
     */
    @PostMapping("/{flowType}/manager/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> managerApprove(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        return approve(flowType, taskId, approved, comment);
    }
    
    /**
     * 兼容性接口：部门经理审批
     * POST /api/{flowType}/dept-manager/approve/{taskId}
     */
    @PostMapping("/{flowType}/dept-manager/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> deptManagerApprove(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        return approve(flowType, taskId, approved, comment);
    }
    
    /**
     * 兼容性接口：行政审批（用于出差流程）
     * POST /api/{flowType}/admin/approve/{taskId}
     */
    @PostMapping("/{flowType}/admin/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> adminApprove(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        return approve(flowType, taskId, approved, comment);
    }
    
    /**
     * 兼容性接口：HR确认（用于加班流程）
     * POST /api/{flowType}/hr/confirm/{taskId}
     */
    @PostMapping("/{flowType}/hr/confirm/{taskId}")
    public ResponseEntity<Map<String, Object>> hrConfirm(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        return approve(flowType, taskId, approved, comment);
    }
    
    /**
     * 兼容性接口：HR审批（备用路径）
     * POST /api/{flowType}/hr/approve/{taskId}
     */
    @PostMapping("/{flowType}/hr/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> hrApprove(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        return approve(flowType, taskId, approved, comment);
    }
    
    /**
     * 兼容性接口：财务审批（用于报销流程）
     * POST /api/{flowType}/finance/approve/{taskId}
     */
    @PostMapping("/{flowType}/finance/approve/{taskId}")
    public ResponseEntity<Map<String, Object>> financeApprove(
            @PathVariable String flowType,
            @PathVariable String taskId,
            @RequestParam boolean approved,
            @RequestParam String comment) {
        
        return approve(flowType, taskId, approved, comment);
    }
    
    /**
     * 查询流程实例
     * GET /api/{flowType}/process/instance/{processInstanceId}
     */
    @GetMapping("/{flowType}/process/instance/{processInstanceId}")
    public ResponseEntity<ProcessInstanceDTO> getProcessInstance(
            @PathVariable String flowType,
            @PathVariable String processInstanceId) {
        
        try {
            String processKey = findProcessKeyByFlowType(flowType);
            
            if (processKey == null) {
                return ResponseEntity.notFound().build();
            }
            
            ProcessInstanceDTO dto = dynamicProcessService.getProcessInstance(processKey, processInstanceId);
            
            if (dto != null) {
                return ResponseEntity.ok(dto);
            }
            
            return ResponseEntity.notFound().build();
            
        } catch (Exception e) {
            log.error("查询流程实例失败: {} - {}", flowType, processInstanceId, e);
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 查询待办任务列表
     * GET /api/{flowType}/task/list
     */
    @GetMapping("/{flowType}/task/list")
    public ResponseEntity<List<TaskDTO>> getTaskList(@PathVariable String flowType) {
        
        try {
            String processKey = findProcessKeyByFlowType(flowType);
            
            if (processKey == null) {
                return ResponseEntity.notFound().build();
            }
            
            List<TaskDTO> tasks = dynamicProcessService.getTaskList(processKey);
            
            return ResponseEntity.ok(tasks);
            
        } catch (Exception e) {
            log.error("查询任务列表失败: {}", flowType, e);
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 根据flowType查找流程定义Key
     * 
     * flowType是API路径中的类型标识，如：leave, business-trip
     * 需要从配置中查找对应的processKey
     * 
     * @param flowType API路径中的流程类型
     * @return 流程定义Key，如果未找到返回null
     */
    private String findProcessKeyByFlowType(String flowType) {
        // 将flowType转换为apiPrefix格式
        String apiPrefix = "/api/" + flowType;
        
        // 从所有配置中查找匹配的流程
        Map<String, ProcessConfig> allConfigs = configService.getAllConfigs();
        
        for (Map.Entry<String, ProcessConfig> entry : allConfigs.entrySet()) {
            ProcessConfig config = entry.getValue();
            if (config.getProcess().getApiPrefix().equals(apiPrefix)) {
                return config.getProcess().getKey();
            }
        }
        
        return null;
    }
}
