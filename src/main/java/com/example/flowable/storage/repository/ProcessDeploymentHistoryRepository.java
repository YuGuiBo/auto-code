package com.example.flowable.storage.repository;

import com.example.flowable.storage.entity.ProcessDeploymentHistoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 流程部署历史仓库接口
 * 
 * 提供流程部署历史的数据库CRUD操作
 * 
 * @author Auto-Code Platform
 */
@Repository
public interface ProcessDeploymentHistoryRepository extends JpaRepository<ProcessDeploymentHistoryEntity, Long> {
    
    /**
     * 根据流程定义ID查找所有部署历史
     * 按部署时间倒序排列（最新的在前）
     * 
     * @param processDefinitionId 流程定义ID
     * @return 部署历史列表
     */
    List<ProcessDeploymentHistoryEntity> findByProcessDefinitionIdOrderByDeploymentTimeDesc(Long processDefinitionId);
    
    /**
     * 根据流程定义ID和部署状态查找部署历史
     * 按部署时间倒序排列
     * 
     * @param processDefinitionId 流程定义ID
     * @param deploymentStatus 部署状态（SUCCESS, FAILED）
     * @return 部署历史列表
     */
    List<ProcessDeploymentHistoryEntity> findByProcessDefinitionIdAndDeploymentStatusOrderByDeploymentTimeDesc(
        Long processDefinitionId, String deploymentStatus);
    
    /**
     * 根据部署ID查找部署历史
     * 
     * @param deploymentId Flowable部署ID
     * @return 部署历史实体（可能为空）
     */
    List<ProcessDeploymentHistoryEntity> findByDeploymentId(String deploymentId);
}