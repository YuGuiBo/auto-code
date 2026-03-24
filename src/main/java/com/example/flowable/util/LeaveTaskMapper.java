package com.example.flowable.util;

import com.example.flowable.model.TaskDTO;
import org.flowable.task.api.Task;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Task到TaskDTO的转换工具类（请假流程专用）
 * 
 * @author Generated
 */
public class LeaveTaskMapper {
    
    /**
     * 将单个Task转换为TaskDTO
     * 
     * @param task Flowable任务对象
     * @return TaskDTO
     */
    public static TaskDTO toDTO(Task task) {
        if (task == null) {
            return null;
        }
        
        TaskDTO dto = new TaskDTO();
        dto.setId(task.getId());
        dto.setName(task.getName());
        dto.setDescription(task.getDescription());
        dto.setPriority(task.getPriority());
        dto.setAssignee(task.getAssignee());
        dto.setOwner(task.getOwner());
        dto.setProcessInstanceId(task.getProcessInstanceId());
        dto.setProcessDefinitionId(task.getProcessDefinitionId());
        dto.setTaskDefinitionKey(task.getTaskDefinitionKey());
        dto.setCreateTime(task.getCreateTime());
        dto.setDueDate(task.getDueDate());
        dto.setCategory(task.getCategory());
        dto.setExecutionId(task.getExecutionId());
        
        return dto;
    }
    
    /**
     * 将Task列表转换为TaskDTO列表
     * 
     * @param tasks Flowable任务列表
     * @return TaskDTO列表
     */
    public static List<TaskDTO> toDTOList(List<Task> tasks) {
        if (tasks == null) {
            return null;
        }
        
        return tasks.stream()
                .map(LeaveTaskMapper::toDTO)
                .collect(Collectors.toList());
    }
}