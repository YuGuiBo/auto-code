package com.example.flowable.config;

import org.springframework.context.annotation.Configuration;

/**
 * Flowable 配置类
 * 
 * Spring Boot的Flowable Starter会自动配置所有必要的服务，
 * 包括：RuntimeService、TaskService、RepositoryService、HistoryService等。
 * 
 * 如果需要自定义配置，可以在application.yml中配置flowable属性，
 * 或者在这里添加自定义的Bean。
 * 
 * @author Generated
 */
@Configuration
public class FlowableConfig {
    
    /**
     * Flowable Spring Boot Starter 自动配置说明：
     * 
     * 1. ProcessEngine - 流程引擎自动配置
     * 2. RuntimeService - 流程实例管理服务
     * 3. TaskService - 任务管理服务
     * 4. RepositoryService - 流程定义管理服务
     * 5. HistoryService - 历史数据查询服务
     * 6. ManagementService - 引擎管理服务
     * 
     * 这些服务可以直接在其他类中使用@Autowired注入，无需手动配置。
     * 
     * 配置参数在application.yml中的flowable节点下设置。
     */
    
    // 这里可以添加自定义的Bean或配置
    // 例如：自定义监听器、拦截器等
}
