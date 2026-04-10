package com.example.flowable.engine.service;

import com.example.flowable.common.util.ProcessMapper;
import com.example.flowable.model.ProcessInstanceDTO;
import org.flowable.engine.HistoryService;
import org.flowable.engine.RuntimeService;
import org.flowable.engine.history.HistoricProcessInstance;
import org.flowable.engine.runtime.ProcessInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 通用流程引擎服务
 * 提供纯粹的流程操作能力，不包含任何业务逻辑
 * 
 * @author Auto-Code Platform
 */
@Service
public class ProcessEngineService {

    @Autowired
    private RuntimeService runtimeService;

    @Autowired
    private HistoryService historyService;

    /**
     * 启动流程实例（通用方法）
     * 
     * @param processDefinitionKey 流程定义Key（如：leaveRequestProcess）
     * @param businessKey 业务Key（可选）
     * @param variables 流程变量
     * @return 流程实例ID
     */
    public String startProcess(String processDefinitionKey, String businessKey, Map<String, Object> variables) {
        ProcessInstance processInstance;
        
        if (businessKey != null && !businessKey.isEmpty()) {
            processInstance = runtimeService.startProcessInstanceByKey(
                processDefinitionKey, 
                businessKey, 
                variables
            );
        } else {
            processInstance = runtimeService.startProcessInstanceByKey(
                processDefinitionKey, 
                variables
            );
        }
        
        return processInstance.getId();
    }

    /**
     * 根据流程实例ID查询流程（支持运行中和历史流程）
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程实例DTO
     */
    public ProcessInstanceDTO getProcessInstanceById(String processInstanceId) {
        // 先查询运行中的流程实例
        ProcessInstance instance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (instance != null) {
            return ProcessMapper.toDTO(instance);
        }
        
        // 如果运行中的流程不存在，查询历史流程
        HistoricProcessInstance historicInstance = historyService
                .createHistoricProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (historicInstance != null) {
            return ProcessMapper.toDTO(historicInstance);
        }
        
        return null;
    }

    /**
     * 查询所有运行中的流程实例
     * 
     * @return 流程实例列表
     */
    public List<ProcessInstanceDTO> getAllProcessInstances() {
        List<ProcessInstance> instances = runtimeService.createProcessInstanceQuery()
                .orderByStartTime()
                .desc()
                .list();
        
        return instances.stream()
                .map(ProcessMapper::toDTO)
                .collect(Collectors.toList());
    }

    /**
     * 根据流程定义Key查询流程实例
     * 
     * @param processDefinitionKey 流程定义Key
     * @return 流程实例列表
     */
    public List<ProcessInstanceDTO> getProcessInstancesByKey(String processDefinitionKey) {
        List<ProcessInstance> instances = runtimeService.createProcessInstanceQuery()
                .processDefinitionKey(processDefinitionKey)
                .orderByStartTime()
                .desc()
                .list();
        
        return instances.stream()
                .map(ProcessMapper::toDTO)
                .collect(Collectors.toList());
    }

    /**
     * 获取流程变量
     * 
     * @param processInstanceId 流程实例ID
     * @return 流程变量Map
     */
    public Map<String, Object> getProcessVariables(String processInstanceId) {
        // 先尝试从运行中的流程获取
        ProcessInstance instance = runtimeService.createProcessInstanceQuery()
                .processInstanceId(processInstanceId)
                .singleResult();
        
        if (instance != null) {
            return runtimeService.getVariables(processInstanceId);
        }
        
        // 从历史流程获取
        return historyService
                .createHistoricVariableInstanceQuery()
                .processInstanceId(processInstanceId)
                .list()
                .stream()
                .filter(v -> v.getValue() != null)
                .collect(Collectors.toMap(
                        v -> v.getVariableName(),
                        v -> v.getValue()
                ));
    }

    /**
     * 设置流程变量
     * 
     * @param processInstanceId 流程实例ID
     * @param variables 要设置的变量
     */
    public void setProcessVariables(String processInstanceId, Map<String, Object> variables) {
        runtimeService.setVariables(processInstanceId, variables);
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
}