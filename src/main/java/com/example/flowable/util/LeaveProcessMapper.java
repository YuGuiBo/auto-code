package com.example.flowable.util;

import com.example.flowable.enums.LeaveRequestStatus;
import com.example.flowable.model.ProcessInstanceDTO;
import org.flowable.engine.history.HistoricProcessInstance;
import org.flowable.engine.runtime.ProcessInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

/**
 * ProcessInstance到ProcessInstanceDTO的转换工具类（请假流程专用）
 * 
 * @author Generated
 */
@Component
public class LeaveProcessMapper {
    
    @Autowired
    private LeaveStatusUtil leaveStatusUtil;
    
    /**
     * 将单个ProcessInstance转换为ProcessInstanceDTO（包含状态信息）
     * 
     * @param processInstance Flowable流程实例对象
     * @return ProcessInstanceDTO
     */
    public ProcessInstanceDTO toDTO(ProcessInstance processInstance) {
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
        
        // 填充状态信息
        LeaveRequestStatus status = leaveStatusUtil.getProcessStatus(processInstance.getId());
        dto.setStatus(status);
        dto.setStatusDisplayName(status.getDisplayName());
        
        // 流程还在运行中，未结束
        dto.setEnded(false);
        dto.setEndTime(null);
        dto.setEndReason(null);
        
        return dto;
    }
    
    /**
     * 将历史流程实例转换为ProcessInstanceDTO（包含状态信息）
     * 
     * @param historicProcessInstance 历史流程实例对象
     * @return ProcessInstanceDTO
     */
    public ProcessInstanceDTO toDTO(HistoricProcessInstance historicProcessInstance) {
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
        
        // 填充状态信息
        LeaveRequestStatus status = leaveStatusUtil.getProcessStatus(historicProcessInstance.getId());
        dto.setStatus(status);
        dto.setStatusDisplayName(status.getDisplayName());
        
        // 填充结束信息
        dto.setEnded(historicProcessInstance.getEndTime() != null);
        dto.setEndTime(historicProcessInstance.getEndTime());
        dto.setEndReason(historicProcessInstance.getDeleteReason());
        
        return dto;
    }
    
    /**
     * 将ProcessInstance列表转换为ProcessInstanceDTO列表
     * 
     * @param processInstances Flowable流程实例列表
     * @return ProcessInstanceDTO列表
     */
    public List<ProcessInstanceDTO> toDTOList(List<ProcessInstance> processInstances) {
        if (processInstances == null) {
            return null;
        }
        
        return processInstances.stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 将历史流程实例列表转换为ProcessInstanceDTO列表
     * 
     * @param historicProcessInstances 历史流程实例列表
     * @return ProcessInstanceDTO列表
     */
    public List<ProcessInstanceDTO> toDTOListFromHistoric(List<HistoricProcessInstance> historicProcessInstances) {
        if (historicProcessInstances == null) {
            return null;
        }
        
        return historicProcessInstances.stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }
}