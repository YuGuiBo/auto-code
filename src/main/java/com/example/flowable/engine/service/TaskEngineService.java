package com.example.flowable.engine.service;

import com.example.flowable.common.util.TaskMapper;
import com.example.flowable.model.TaskDTO;
import org.flowable.engine.TaskService;
import org.flowable.task.api.Task;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 通用任务引擎服务
 * 提供纯粹的任务操作能力，不包含任何业务逻辑
 * 
 * @author Auto-Code Platform
 */
@Service
public class TaskEngineService {

    @Autowired
    private TaskService taskService;

    /**
     * 完成任务（通用方法）
     * 
     * @param taskId 任务ID
     * @param variables 任务变量
     */
    public void completeTask(String taskId, Map<String, Object> variables) {
        // 添加评论（如果有comment变量）
        if (variables != null && variables.containsKey("comment")) {
            Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
            if (task != null) {
                String comment = String.valueOf(variables.get("comment"));
                taskService.addComment(taskId, task.getProcessInstanceId(), comment);
            }
        }
        
        // 完成任务
        if (variables != null && !variables.isEmpty()) {
            taskService.complete(taskId, variables);
        } else {
            taskService.complete(taskId);
        }
    }

    /**
     * 根据任务ID查询任务
     * 
     * @param taskId 任务ID
     * @return 任务DTO
     */
    public TaskDTO getTaskById(String taskId) {
        Task task = taskService.createTaskQuery()
                .taskId(taskId)
                .singleResult();
        
        return TaskMapper.toDTO(task);
    }

    /**
     * 查询所有待办任务
     * 
     * @return 任务列表
     */
    public List<TaskDTO> getAllTasks() {
        List<Task> tasks = taskService.createTaskQuery()
                .orderByTaskCreateTime()
                .desc()
                .list();
        
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 根据流程定义Key查询任务
     * 
     * @param processDefinitionKey 流程定义Key
     * @return 任务列表
     */
    public List<TaskDTO> getTasksByProcessDefinitionKey(String processDefinitionKey) {
        List<Task> tasks = taskService.createTaskQuery()
                .processDefinitionKey(processDefinitionKey)
                .orderByTaskCreateTime()
                .desc()
                .list();
        
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 根据流程实例ID查询任务
     * 
     * @param processInstanceId 流程实例ID
     * @return 任务列表
     */
    public List<TaskDTO> getTasksByProcessInstanceId(String processInstanceId) {
        List<Task> tasks = taskService.createTaskQuery()
                .processInstanceId(processInstanceId)
                .orderByTaskCreateTime()
                .desc()
                .list();
        
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 根据受理人查询任务
     * 
     * @param assignee 受理人
     * @return 任务列表
     */
    public List<TaskDTO> getTasksByAssignee(String assignee) {
        List<Task> tasks = taskService.createTaskQuery()
                .taskAssignee(assignee)
                .orderByTaskCreateTime()
                .desc()
                .list();
        
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 根据候选用户查询任务
     * 
     * @param candidateUser 候选用户
     * @return 任务列表
     */
    public List<TaskDTO> getTasksByCandidateUser(String candidateUser) {
        List<Task> tasks = taskService.createTaskQuery()
                .taskCandidateUser(candidateUser)
                .orderByTaskCreateTime()
                .desc()
                .list();
        
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 根据候选组查询任务
     * 
     * @param candidateGroup 候选组
     * @return 任务列表
     */
    public List<TaskDTO> getTasksByCandidateGroup(String candidateGroup) {
        List<Task> tasks = taskService.createTaskQuery()
                .taskCandidateGroup(candidateGroup)
                .orderByTaskCreateTime()
                .desc()
                .list();
        
        return TaskMapper.toDTOList(tasks);
    }

    /**
     * 认领任务
     * 
     * @param taskId 任务ID
     * @param userId 用户ID
     */
    public void claimTask(String taskId, String userId) {
        taskService.claim(taskId, userId);
    }

    /**
     * 委托任务
     * 
     * @param taskId 任务ID
     * @param userId 用户ID
     */
    public void delegateTask(String taskId, String userId) {
        taskService.delegateTask(taskId, userId);
    }

    /**
     * 转办任务
     * 
     * @param taskId 任务ID
     * @param userId 用户ID
     */
    public void setTaskAssignee(String taskId, String userId) {
        taskService.setAssignee(taskId, userId);
    }

    /**
     * 获取任务变量
     * 
     * @param taskId 任务ID
     * @return 任务变量Map
     */
    public Map<String, Object> getTaskVariables(String taskId) {
        return taskService.getVariables(taskId);
    }

    /**
     * 设置任务变量
     * 
     * @param taskId 任务ID
     * @param variables 变量Map
     */
    public void setTaskVariables(String taskId, Map<String, Object> variables) {
        taskService.setVariables(taskId, variables);
    }
}