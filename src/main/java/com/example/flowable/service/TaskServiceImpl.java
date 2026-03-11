package com.example.flowable.service;

import org.flowable.engine.HistoryService;
import org.flowable.engine.TaskService;
import org.flowable.task.api.Task;
import org.flowable.task.api.history.HistoricTaskInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 任务服务实现类
 * 
 * @author Generated
 * @date 2026-03-11
 */
@Service
public class TaskServiceImpl {

    @Autowired
    private TaskService taskService;

    @Autowired
    private HistoryService historyService;

    /**
     * 查询用户的待办任务
     * 
     * @param assignee 任务执行人
     * @return 任务列表
     */
    public List<Task> getTasksByAssignee(String assignee) {
        return taskService.createTaskQuery()
                .taskAssignee(assignee)
                .orderByTaskCreateTime()
                .desc()
                .list();
    }

    /**
     * 查询所有待办任务
     * 
     * @return 任务列表
     */
    public List<Task> getAllTasks() {
        return taskService.createTaskQuery()
                .orderByTaskCreateTime()
                .desc()
                .list();
    }

    /**
     * 根据任务ID查询任务
     * 
     * @param taskId 任务ID
     * @return 任务
     */
    public Task getTaskById(String taskId) {
        return taskService.createTaskQuery()
                .taskId(taskId)
                .singleResult();
    }

    /**
     * 完成任务
     * 
     * @param taskId 任务ID
     * @param variables 任务变量
     */
    public void completeTask(String taskId, Map<String, Object> variables) {
        if (variables != null && !variables.isEmpty()) {
            taskService.complete(taskId, variables);
        } else {
            taskService.complete(taskId);
        }
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
     * @param userId 被委托人ID
     */
    public void delegateTask(String taskId, String userId) {
        taskService.delegateTask(taskId, userId);
    }

    /**
     * 转办任务
     * 
     * @param taskId 任务ID
     * @param userId 新的任务执行人ID
     */
    public void transferTask(String taskId, String userId) {
        taskService.setAssignee(taskId, userId);
    }

    /**
     * 添加任务评论
     * 
     * @param taskId 任务ID
     * @param processInstanceId 流程实例ID
     * @param message 评论内容
     */
    public void addComment(String taskId, String processInstanceId, String message) {
        taskService.addComment(taskId, processInstanceId, message);
    }

    /**
     * 查询候选任务（候选人可以认领的任务）
     * 
     * @param candidateUser 候选用户
     * @return 任务列表
     */
    public List<Task> getCandidateTasks(String candidateUser) {
        return taskService.createTaskQuery()
                .taskCandidateUser(candidateUser)
                .orderByTaskCreateTime()
                .desc()
                .list();
    }

    /**
     * 查询候选组任务
     * 
     * @param candidateGroup 候选组
     * @return 任务列表
     */
    public List<Task> getCandidateGroupTasks(String candidateGroup) {
        return taskService.createTaskQuery()
                .taskCandidateGroup(candidateGroup)
                .orderByTaskCreateTime()
                .desc()
                .list();
    }

    /**
     * 查询历史任务
     * 
     * @param processInstanceId 流程实例ID
     * @return 历史任务列表
     */
    public List<HistoricTaskInstance> getHistoricTasks(String processInstanceId) {
        return historyService.createHistoricTaskInstanceQuery()
                .processInstanceId(processInstanceId)
                .orderByHistoricTaskInstanceEndTime()
                .desc()
                .list();
    }

    /**
     * 查询已完成的任务
     * 
     * @param assignee 任务执行人
     * @return 历史任务列表
     */
    public List<HistoricTaskInstance> getFinishedTasks(String assignee) {
        return historyService.createHistoricTaskInstanceQuery()
                .taskAssignee(assignee)
                .finished()
                .orderByHistoricTaskInstanceEndTime()
                .desc()
                .list();
    }
}