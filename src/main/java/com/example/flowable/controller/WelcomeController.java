package com.example.flowable.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 欢迎页面控制器
 * 提供项目信息和API文档
 * 
 * @author Generated
 */
@RestController
public class WelcomeController {

    @Value("${spring.application.name}")
    private String applicationName;

    /**
     * 根路径 - 欢迎页面
     * 访问 http://localhost:8080/
     */
    @GetMapping("/")
    public ResponseEntity<Map<String, Object>> welcome() {
        Map<String, Object> response = new LinkedHashMap<>();
        
        // 基本信息
        response.put("projectName", applicationName);
        response.put("description", "基于Flowable的工作流引擎项目");
        response.put("version", "1.0.0");
        response.put("framework", "Flowable 7.0.1 + Spring Boot 3.2.1 + PostgreSQL");
        response.put("status", "Running");
        response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        
        // API端点
        Map<String, Object> apis = new LinkedHashMap<>();
        
        // 健康检查
        apis.put("健康检查", "GET /api/process/health");
        
        // 流程管理API
        Map<String, String> processApis = new LinkedHashMap<>();
        processApis.put("查询所有流程定义", "GET /api/process/definitions");
        processApis.put("启动流程实例", "POST /api/process/start");
        processApis.put("查询所有流程实例", "GET /api/process/instances");
        processApis.put("根据ID查询流程实例", "GET /api/process/instance/{processInstanceId}");
        processApis.put("删除流程实例", "DELETE /api/process/instance/{processInstanceId}");
        processApis.put("挂起流程实例", "POST /api/process/instance/{processInstanceId}/suspend");
        processApis.put("激活流程实例", "POST /api/process/instance/{processInstanceId}/activate");
        processApis.put("获取流程变量", "GET /api/process/instance/{processInstanceId}/variables");
        processApis.put("设置流程变量", "POST /api/process/instance/{processInstanceId}/variables");
        apis.put("流程管理", processApis);
        
        // 任务管理API
        Map<String, String> taskApis = new LinkedHashMap<>();
        taskApis.put("查询所有待办任务", "GET /api/task/list");
        taskApis.put("根据执行人查询任务", "GET /api/task/assignee/{assignee}");
        taskApis.put("根据ID查询任务", "GET /api/task/{taskId}");
        taskApis.put("完成任务", "POST /api/task/complete/{taskId}");
        taskApis.put("认领任务", "POST /api/task/claim/{taskId}?userId={userId}");
        taskApis.put("委托任务", "POST /api/task/delegate/{taskId}?userId={userId}");
        taskApis.put("转办任务", "POST /api/task/transfer/{taskId}?userId={userId}");
        taskApis.put("查询候选任务", "GET /api/task/candidate/user/{candidateUser}");
        taskApis.put("查询候选组任务", "GET /api/task/candidate/group/{candidateGroup}");
        taskApis.put("查询历史任务", "GET /api/task/history/process/{processInstanceId}");
        taskApis.put("查询已完成任务", "GET /api/task/finished/{assignee}");
        taskApis.put("添加任务评论", "POST /api/task/{taskId}/comment");
        apis.put("任务管理", taskApis);
        
        response.put("apis", apis);
        
        // 快速开始
        Map<String, String> quickStart = new LinkedHashMap<>();
        quickStart.put("1. 健康检查", "curl http://localhost:8080/api/process/health");
        quickStart.put("2. 查看流程定义", "curl http://localhost:8080/api/process/definitions");
        quickStart.put("3. 启动流程", "curl -X POST http://localhost:8080/api/process/start -H 'Content-Type: application/json' -d '{\"processDefinitionKey\":\"simpleProcess\"}'");
        quickStart.put("4. 查询任务", "curl http://localhost:8080/api/task/list");
        response.put("quickStart", quickStart);
        
        // 文档链接
        Map<String, String> documentation = new LinkedHashMap<>();
        documentation.put("API列表", "GET /api");
        documentation.put("项目说明", "查看项目根目录 README.md");
        documentation.put("API测试指南", "查看项目根目录 API测试指南.md");
        response.put("documentation", documentation);
        
        // 提示信息
        response.put("tips", "💡 访问 /api 端点查看简洁的API列表");
        
        return ResponseEntity.ok(response);
    }

    /**
     * API列表端点
     * 访问 http://localhost:8080/api
     */
    @GetMapping("/api")
    public ResponseEntity<Map<String, Object>> apiList() {
        Map<String, Object> response = new LinkedHashMap<>();
        
        response.put("projectName", applicationName);
        response.put("message", "欢迎使用 " + applicationName + " API");
        
        // 简洁的API端点列表
        Map<String, Object> endpoints = new LinkedHashMap<>();
        
        // 系统端点
        Map<String, String> systemEndpoints = new LinkedHashMap<>();
        systemEndpoints.put("欢迎页面", "GET /");
        systemEndpoints.put("API列表", "GET /api");
        systemEndpoints.put("健康检查", "GET /api/process/health");
        endpoints.put("系统", systemEndpoints);
        
        // 流程端点
        Map<String, String> processEndpoints = new LinkedHashMap<>();
        processEndpoints.put("流程定义", "GET /api/process/definitions");
        processEndpoints.put("流程实例", "GET /api/process/instances");
        processEndpoints.put("启动流程", "POST /api/process/start");
        endpoints.put("流程", processEndpoints);
        
        // 任务端点
        Map<String, String> taskEndpoints = new LinkedHashMap<>();
        taskEndpoints.put("任务列表", "GET /api/task/list");
        taskEndpoints.put("用户任务", "GET /api/task/assignee/{assignee}");
        taskEndpoints.put("完成任务", "POST /api/task/complete/{taskId}");
        endpoints.put("任务", taskEndpoints);
        
        response.put("endpoints", endpoints);
        response.put("baseUrl", "http://localhost:8080");
        response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        
        return ResponseEntity.ok(response);
    }
}