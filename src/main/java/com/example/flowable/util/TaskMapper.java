package com.example.flowable.util;

import com.example.flowable.model.TaskDTO;
import org.flowable.task.api.Task;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Task到TaskDTO的转换工具类
 * 
 * @author Generated
 */
public class TaskMapper {
    
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
        dto.setTaskDefinitionKey(task.getTaskDefinitionKey());
        dto.setAssignee(task.getAssignee());
        dto.setProcessInstanceId(task.getProcessInstanceId());
        dto.setExecutionId(task.getExecutionId());
        dto.setProcessDefinitionId(task.getProcessDefinitionId());
        dto.setCreateTime(task.getCreateTime());
        dto.setDescription(task.getDescription());
        dto.setOwner(task.getOwner());
        dto.setPriority(task.getPriority());
        dto.setDueDate(task.getDueDate());
        dto.setCategory(task.getCategory());
        
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
                .map(TaskMapper::toDTO)
                .collect(Collectors.toList());
    }
}