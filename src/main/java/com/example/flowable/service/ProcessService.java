package com.example.flowable.service;

import org.flowable.engine.RepositoryService;
import org.flowable.engine.RuntimeService;
import org.flowable.engine.repository.Deployment;
import org.flowable.engine.repository.ProcessDefinition;
import org.flowable.engine.runtime.ProcessInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 流程服务类
 * 
 * @author Generated
 * @date 2026-03-11
 */
@Service
public class ProcessService {

    @Autowired
    private RuntimeService runtimeService;

    @Autowired
    private RepositoryService repositoryService;

    /**
     * 启动流程实例
     * 
     * @param processDefinitionKey 流程定义Key
     * @param businessKey 业务Key
     * @param variables 流程变量
     * @return 流程实例ID
     */
    public String startProcess(String processDefinitionKey, String businessKey, Map<String, Object> variables) {
        ProcessInstance processInstance;
        
        if (businessKey != null && !businessKey.isEmpty()) {
            processInstance = runtimeService.startProcessInstanceByKey(
                processDefinitionKey, businessKey, variables);
        } else {
            processInstance = runtimeService.startProcessInstanceByKey(
                processDefinitionKey, variables);
        }
        
        return processInstance.getId();
    }

    /**
     * 查询所有流程实例
     * 
     * @return 流程实例列表
     */
    public List<ProcessInstance> getProcessInstances() {
        return runtimeService.createProcessInstanceQuery().list();
    }

    /**
     * 根据流程实例ID查询
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程实例
     */
    public ProcessInstance getProcessInstanceById(String processInstanceId) {
        return runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
    }

    /**
     * 删除流程实例
     * 
     * @param processInstanceId 流程实例ID
     * @param reason 删除原因
     */
    public void deleteProcessInstance(String processInstanceId, String reason) {
        runtimeService.deleteProcessInstance(processInstanceId, reason);
    }

    /**
     * 挂起流程实例
     * 
     * @param processInstanceId 流程实例ID
     */
    public void suspendProcessInstance(String processInstanceId) {
        runtimeService.suspendProcessInstanceById(processInstanceId);
    }

    /**
     * 激活流程实例
     * 
     * @param processInstanceId 流程实例ID
     */
    public void activateProcessInstance(String processInstanceId) {
        runtimeService.activateProcessInstanceById(processInstanceId);
    }

    /**
     * 查询所有流程定义
     * 
     * @return 流程定义列表
     */
    public List<ProcessDefinition> getProcessDefinitions() {
        return repositoryService.createProcessDefinitionQuery()
                .orderByProcessDefinitionVersion()
                .desc()
                .list();
    }

    /**
     * 部署流程定义
     * 
     * @param resourceName 资源名称
     * @param inputStream 输入流
     * @return 部署ID
     */
    public String deployProcess(String resourceName, InputStream inputStream) {
        Deployment deployment = repositoryService.createDeployment()
                .addInputStream(resourceName, inputStream)
                .deploy();
        return deployment.getId();
    }

    /**
     * 获取流程变量
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程变量Map
     */
    public Map<String, Object> getProcessVariables(String processInstanceId) {
        return runtimeService.getVariables(processInstanceId);
    }

    /**
     * 设置流程变量
     * 
     * @param processInstanceId 流程实例ID
     * @param variables 变量Map
     */
    public void setProcessVariables(String processInstanceId, Map<String, Object> variables) {
        runtimeService.setVariables(processInstanceId, variables);
    }
}