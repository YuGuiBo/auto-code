package com.example.flowable.config;

import org.flowable.engine.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Flowable 配置类
 * 
 * @author Generated
 * @date 2026-03-11
 */
@Configuration
public class FlowableConfig {

    /**
     * 流程引擎配置
     * Spring Boot Starter 会自动配置，这里可以进行自定义配置
     */
    // @Bean
    // public SpringProcessEngineConfiguration processEngineConfiguration(
    //         DataSource dataSource,
    //         PlatformTransactionManager transactionManager) {
        
    //     SpringProcessEngineConfiguration config = new SpringProcessEngineConfiguration();
    //     config.setDataSource(dataSource);
    //     config.setTransactionManager(transactionManager);
    //     config.setDatabaseSchemaUpdate("true");
    //     config.setAsyncExecutorActivate(true);
    //     config.setHistoryLevel(HistoryLevel.FULL);
        
    //     return config;
    // }

    /**
     * 注入 RuntimeService
     * 用于流程实例管理
     */
    @Bean
    public RuntimeService runtimeService(ProcessEngine processEngine) {
        return processEngine.getRuntimeService();
    }

    /**
     * 注入 TaskService
     * 用于任务管理
     */
    @Bean
    public TaskService taskService(ProcessEngine processEngine) {
        return processEngine.getTaskService();
    }

    /**
     * 注入 RepositoryService
     * 用于流程定义管理
     */
    @Bean
    public RepositoryService repositoryService(ProcessEngine processEngine) {
        return processEngine.getRepositoryService();
    }

    /**
     * 注入 HistoryService
     * 用于历史数据查询
     */
    @Bean
    public HistoryService historyService(ProcessEngine processEngine) {
        return processEngine.getHistoryService();
    }

    /**
     * 注入 ManagementService
     * 用于引擎管理
     */
    @Bean
    public ManagementService managementService(ProcessEngine processEngine) {
        return processEngine.getManagementService();
    }
}