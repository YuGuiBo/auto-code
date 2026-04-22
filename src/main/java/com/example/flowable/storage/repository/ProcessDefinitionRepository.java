package com.example.flowable.storage.repository;

import com.example.flowable.storage.entity.ProcessDefinitionEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.stereotype.Repository;

import jakarta.persistence.LockModeType;
import java.util.List;
import java.util.Optional;

/**
 * 流程定义仓库接口
 * 
 * 提供流程定义的数据库CRUD操作
 * 
 * @author Auto-Code Platform
 */
@Repository
public interface ProcessDefinitionRepository extends JpaRepository<ProcessDefinitionEntity, Long> {
    
    /**
     * 根据流程Key查找流程定义
     * 使用悲观锁防止并发部署冲突
     * 
     * @param processKey 流程Key
     * @return 流程定义实体（可能为空）
     */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    Optional<ProcessDefinitionEntity> findByProcessKey(String processKey);
    
    /**
     * 查找所有启用的流程定义
     * 
     * @return 启用的流程定义列表
     */
    List<ProcessDefinitionEntity> findByEnabledTrue();
    
    /**
     * 根据API前缀查找流程定义
     * 
     * @param apiPrefix API前缀（如：/api/leave）
     * @return 流程定义实体（可能为空）
     */
    Optional<ProcessDefinitionEntity> findByApiPrefix(String apiPrefix);
    
    /**
     * 检查流程Key是否已存在
     * 
     * @param processKey 流程Key
     * @return 是否存在
     */
    boolean existsByProcessKey(String processKey);
}
