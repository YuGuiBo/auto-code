package com.example.flowable.common.util;

import com.example.flowable.model.ProcessInstanceDTO;
import org.flowable.engine.history.HistoricProcessInstance;
import org.flowable.engine.runtime.ProcessInstance;

/**
 * 流程实例转换工具类（通用，所有流程共用）
 * 只做基础字段映射，不填充业务状态
 * 业务状态由各个业务Service自己填充
 * 
 * @author Generated
 */
public class ProcessMapper {
    
    /**
     * 将运行中的ProcessInstance转换为ProcessInstanceDTO
     * 
     * @param processInstance Flowable流程实例对象
     * @return ProcessInstanceDTO
     */
    public static ProcessInstanceDTO toDTO(ProcessInstance processInstance) {
        if (processInstance == null) {
            return null;
        }
        
        ProcessInstanceDTO dto = new ProcessInstanceDTO();
        dto.setId(processInstance.getId());
        dto.setProcessDefinitionId(processInstance.getProcessDefinitionId());
        dto.setProcessDefinitionKey(processInstance.getProcessDefinitionKey());
        dto.setProcessDefinitionName(processInstance.getProcessDefinitionName());
        dto.setProcessDefinitionVersion(processInstance.getProcessDefinitionVersion());
        dto.setBusinessKey(processInstance.getBusinessKey());
        dto.setStartTime(processInstance.getStartTime());
        dto.setStartUserId(processInstance.getStartUserId());
        dto.setSuspended(processInstance.isSuspended());
        dto.setTenantId(processInstance.getTenantId());
        dto.setName(processInstance.getName());
        dto.setDescription(processInstance.getDescription());
        
        // 流程还在运行中，未结束
        dto.setEnded(false);
        dto.setEndTime(null);
        dto.setEndReason(null);
        
        // 注意：不填充 status 和 statusDisplayName
        // 这些业务字段由调用方（业务Service）自己填充
        
        return dto;
    }
    
    /**
     * 将历史流程实例转换为ProcessInstanceDTO
     * 
     * @param historicProcessInstance 历史流程实例对象
     * @return ProcessInstanceDTO
     */
    public static ProcessInstanceDTO toDTO(HistoricProcessInstance historicProcessInstance) {
        if (historicProcessInstance == null) {
            return null;
        }
        
        ProcessInstanceDTO dto = new ProcessInstanceDTO();
        dto.setId(historicProcessInstance.getId());
        dto.setProcessDefinitionId(historicProcessInstance.getProcessDefinitionId());
        dto.setProcessDefinitionKey(historicProcessInstance.getProcessDefinitionKey());
        dto.setProcessDefinitionName(historicProcessInstance.getProcessDefinitionName());
        dto.setProcessDefinitionVersion(historicProcessInstance.getProcessDefinitionVersion());
        dto.setBusinessKey(historicProcessInstance.getBusinessKey());
        dto.setStartTime(historicProcessInstance.getStartTime());
        dto.setStartUserId(historicProcessInstance.getStartUserId());
        dto.setSuspended(false); // 历史流程不会是挂起状态
        dto.setTenantId(historicProcessInstance.getTenantId());
        dto.setName(historicProcessInstance.getName());
        dto.setDescription(historicProcessInstance.getDescription());
        
        // 填充结束信息
        dto.setEnded(historicProcessInstance.getEndTime() != null);
        dto.setEndTime(historicProcessInstance.getEndTime());
        dto.setEndReason(historicProcessInstance.getDeleteReason());
        
        // 注意：不填充 status 和 statusDisplayName
        // 这些业务字段由调用方（业务Service）自己填充
        
        return dto;
    }
}