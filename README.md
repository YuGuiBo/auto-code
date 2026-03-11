# Auto Code 项目

这是一个基于 Flowable 7.0.1 + Spring Boot 3.2.1 + PostgreSQL 的工作流引擎项目。

## 📋 项目信息

- **Flowable版本**: 7.0.1
- **Spring Boot版本**: 3.2.1
- **数据库**: PostgreSQL 42.7.3 JDBC
- **Java版本**: 17+
- **构建工具**: Maven

## 🚀 快速开始

### 1. 环境准备

确保您已经安装以下软件：

- JDK 17 或更高版本
- Maven 3.6+
- PostgreSQL 数据库

### 2. 数据库配置

创建PostgreSQL数据库：

```sql
CREATE DATABASE flowable_db;
```

修改 `src/main/resources/application.yml` 中的数据库连接信息：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://127.0.0.1:15432/Asset
    username: asset
    password: asset
```

### 3. 构建项目

```bash
mvn clean install
```

### 4. 运行项目

```bash
mvn spring-boot:run
```

或者直接运行主类：`com.example.flowable.FlowableApplication`

项目启动后访问：http://localhost:8080

## 📚 API 文档

### 流程管理 API

#### 1. 健康检查
```
GET /api/process/health
```

#### 2. 启动流程实例
```
POST /api/process/start
Content-Type: application/json

{
  "processDefinitionKey": "simpleProcess",
  "businessKey": "business-001",
  "variables": {
    "applicant": "张三",
    "reason": "测试流程"
  }
}
```

#### 3. 查询所有流程定义
```
GET /api/process/definitions
```

#### 4. 查询所有流程实例
```
GET /api/process/instances
```

#### 5. 根据ID查询流程实例
```
GET /api/process/instance/{processInstanceId}
```

#### 6. 删除流程实例
```
DELETE /api/process/instance/{processInstanceId}?reason=删除原因
```

#### 7. 挂起流程实例
```
POST /api/process/instance/{processInstanceId}/suspend
```

#### 8. 激活流程实例
```
POST /api/process/instance/{processInstanceId}/activate
```

#### 9. 获取流程变量
```
GET /api/process/instance/{processInstanceId}/variables
```

#### 10. 设置流程变量
```
POST /api/process/instance/{processInstanceId}/variables
Content-Type: application/json

{
  "key1": "value1",
  "key2": "value2"
}
```

### 任务管理 API

#### 1. 查询所有待办任务
```
GET /api/task/list
```

#### 2. 查询指定用户的待办任务
```
GET /api/task/assignee/{assignee}
```

示例：`GET /api/task/assignee/user1`

#### 3. 根据任务ID查询任务
```
GET /api/task/{taskId}
```

#### 4. 完成任务
```
POST /api/task/complete/{taskId}
Content-Type: application/json

{
  "variables": {
    "approved": true,
    "comment": "同意"
  }
}
```

#### 5. 认领任务
```
POST /api/task/claim/{taskId}?userId=user1
```

#### 6. 委托任务
```
POST /api/task/delegate/{taskId}?userId=user2
```

#### 7. 转办任务
```
POST /api/task/transfer/{taskId}?userId=user3
```

#### 8. 查询候选任务
```
GET /api/task/candidate/user/{candidateUser}
```

#### 9. 查询候选组任务
```
GET /api/task/candidate/group/{candidateGroup}
```

#### 10. 查询历史任务
```
GET /api/task/history/process/{processInstanceId}
```

#### 11. 查询已完成的任务
```
GET /api/task/finished/{assignee}
```

## 📁 项目结构

```
auto-code/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/flowable/
│   │   │       ├── FlowableApplication.java          # 应用启动类
│   │   │       ├── config/
│   │   │       │   └── FlowableConfig.java           # Flowable配置
│   │   │       ├── controller/
│   │   │       │   ├── ProcessController.java        # 流程控制器
│   │   │       │   └── TaskController.java           # 任务控制器
│   │   │       ├── service/
│   │   │       │   ├── ProcessService.java           # 流程服务
│   │   │       │   └── TaskServiceImpl.java          # 任务服务
│   │   │       └── model/
│   │   │           ├── ProcessStartRequest.java      # 流程启动请求DTO
│   │   │           └── TaskCompleteRequest.java      # 任务完成请求DTO
│   │   └── resources/
│   │       ├── application.yml                       # 应用配置
│   │       └── processes/
│   │           └── simple-process.bpmn20.xml        # 示例BPMN流程
│   └── test/
├── pom.xml                                           # Maven配置
└── README.md                                         # 项目说明
```

## 🔧 配置说明

### application.yml 主要配置

```yaml
# Flowable配置
flowable:
  # 自动部署processes目录下的流程文件
  process-definition-location-prefix: classpath*:/processes/
  process-definition-location-suffixes: "**.bpmn20.xml,**.bpmn"
  
  # 数据库自动更新策略
  database-schema-update: true
  
  # 异步执行器