# Auto Code API 测试指南

本文档提供了详细的API测试步骤和示例。

## 前置条件

1. 确保PostgreSQL数据库已经创建并运行
2. 项目已经启动，访问 http://localhost:8080

## 测试工具

推荐使用以下工具之一：
- **Postman** (推荐)
- **curl** 命令行
- **VS Code REST Client** 插件
- **IntelliJ IDEA HTTP Client**

## 完整测试流程

### 步骤1: 健康检查

```bash
# 使用curl
curl -X GET http://localhost:8080/api/process/health

# 预期响应
{
  "status": "UP",
  "service": "Flowable Demo"
}
```

### 步骤2: 查看已部署的流程定义

```bash
# 查看所有流程定义
curl -X GET http://localhost:8080/api/process/definitions

# 预期响应
[
  {
    "id": "simpleProcess:1:xxx",
    "key": "simpleProcess",
    "name": "简单流程示例",
    "version": 1,
    ...
  }
]
```

### 步骤3: 启动一个流程实例

```bash
# 使用curl启动流程
curl -X POST http://localhost:8080/api/process/start \
  -H "Content-Type: application/json" \
  -d '{
    "processDefinitionKey": "simpleProcess",
    "businessKey": "TEST-001",
    "variables": {
      "applicant": "张三",
      "reason": "测试请假流程",
      "days": 3
    }
  }'

# 预期响应
{
  "success": true,
  "processInstanceId": "xxx",
  "message": "流程启动成功"
}
```

**注意**: 记录返回的 `processInstanceId`，后续步骤会用到。

### 步骤4: 查询待办任务

流程启动后，会自动创建第一个用户任务（分配给 user1）。

```bash
# 查询user1的待办任务
curl -X GET http://localhost:8080/api/task/assignee/user1

# 预期响应
[
  {
    "id": "task-id-xxx",
    "name": "用户任务1",
    "assignee": "user1",
    "processInstanceId": "xxx",
    ...
  }
]
```

**注意**: 记录任务的 `id`，下一步完成任务时需要使用。

### 步骤5: 完成第一个任务

```bash
# 使用curl完成任务
curl -X POST http://localhost:8080/api/task/complete/{taskId} \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "approved": true,
      "comment": "同意通过"
    }
  }'

# 预期响应
{
  "success": true,
  "message": "任务完成成功"
}
```

### 步骤6: 查询user2的待办任务

完成第一个任务后，流程会流转到第二个用户任务（分配给 user2）。

```bash
# 查询user2的待办任务
curl -X GET http://localhost:8080/api/task/assignee/user2

# 预期响应
[
  {
    "id": "task-id-xxx",
    "name": "用户任务2",
    "assignee": "user2",
    "processInstanceId": "xxx",
    ...
  }
]
```

### 步骤7: 完成第二个任务

```bash
# 完成user2的任务
curl -X POST http://localhost:8080/api/task/complete/{taskId} \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "finalApproved": true,
      "comment": "最终审批通过"
    }
  }'

# 预期响应
{
  "success": true,
  "message": "任务完成成功"
}
```

### 步骤8: 验证流程完成

完成所有任务后，流程实例应该已经结束。

```bash
# 查询流程实例（应该为空或状态为已结束）
curl -X GET http://localhost:8080/api/process/instances

# 查询历史任务
curl -X GET http://localhost:8080/api/task/history/process/{processInstanceId}
```

## Postman 测试集合

### 1. 创建环境变量

在Postman中创建以下环境变量：
- `baseUrl`: http://localhost:8080
- `processInstanceId`: (动态设置)
- `taskId`: (动态设置)

### 2. 测试请求示例

#### 请求1: 启动流程
```
POST {{baseUrl}}/api/process/start

Body (JSON):
{
  "processDefinitionKey": "simpleProcess",
  "businessKey": "TEST-{{$timestamp}}",
  "variables": {
    "applicant": "测试用户",
    "reason": "测试流程",
    "amount": 1000
  }
}

Tests (保存processInstanceId):
pm.test("启动流程成功", function() {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.be.true;
    pm.environment.set("processInstanceId", jsonData.processInstanceId);
});
```

#### 请求2: 查询任务
```
GET {{baseUrl}}/api/task/assignee/user1

Tests (保存taskId):
pm.test("获取任务成功", function() {
    pm.response.to.have.status(200);
    var tasks = pm.response.json();
    pm.expect(tasks.length).to.be.above(0);
    pm.environment.set("taskId", tasks[0].id);
});
```

#### 请求3: 完成任务
```
POST {{baseUrl}}/api/task/complete/{{taskId}}

Body (JSON):
{
  "variables": {
    "approved": true,
    "comment": "同意"
  }
}
```

## 高级测试场景

### 测试流程变量

```bash
# 1. 启动流程时设置变量
curl -X POST http://localhost:8080/api/process/start \
  -H "Content-Type: application/json" \
  -d '{
    "processDefinitionKey": "simpleProcess",
    "variables": {
      "var1": "value1",
      "var2": 100,
      "var3": true
    }
  }'

# 2. 查询流程变量
curl -X GET http://localhost:8080/api/process/instance/{processInstanceId}/variables

# 3. 更新流程变量
curl -X POST http://localhost:8080/api/process/instance/{processInstanceId}/variables \
  -H "Content-Type: application/json" \
  -d '{
    "var1": "newValue",
    "var4": "additionalValue"
  }'
```

### 测试任务认领

```bash
# 1. 启动流程（不指定assignee，使用候选用户）

# 2. 查询候选任务
curl -X GET http://localhost:8080/api/task/candidate/user/user1

# 3. 认领任务
curl -X POST "http://localhost:8080/api/task/claim/{taskId}?userId=user1"

# 4. 完成任务
curl -X POST http://localhost:8080/api/task/complete/{taskId}
```

### 测试任务转办

```bash
# 1. 查询user1的任务
curl -X GET http://localhost:8080/api/task/assignee/user1

# 2. 将任务转办给user3
curl -X POST "http://localhost:8080/api/task/transfer/{taskId}?userId=user3"

# 3. 验证user3的任务
curl -X GET http://localhost:8080/api/task/assignee/user3
```

### 测试流程挂起和激活

```bash
# 1. 挂起流程实例
curl -X POST http://localhost:8080/api/process/instance/{processInstanceId}/suspend

# 2. 尝试完成任务（应该失败）
curl -X POST http://localhost:8080/api/task/complete/{taskId}

# 3. 激活流程实例
curl -X POST http://localhost:8080/api/process/instance/{processInstanceId}/activate

# 4. 再次完成任务（应该成功）
curl -X POST http://localhost:8080/api/task/complete/{taskId}
```

## 常见问题

### Q1: 启动流程失败
**可能原因**:
- 数据库连接失败
- 流程定义未正确部署
- processDefinitionKey 不正确

**解决方案**:
```bash
# 检查流程定义
curl -X GET http://localhost:8080/api/process/definitions
```

### Q2: 查询不到任务
**可能原因**:
- 任务已经被完成
- assignee 不正确
- 流程实例已结束

**解决方案**:
```bash
# 查询所有任务
curl -X GET http://localhost:8080/api/task/list

# 查询历史任务
curl -X GET http://localhost:8080/api/task/finished/{assignee}
```

### Q3: 完成任务失败
**可能原因**:
- taskId 不正确
- 任务已经完成
- 流程实例被挂起

**解决方案**:
```bash
# 查询任务详情
curl -X GET http://localhost:8080/api/task/{taskId}

# 检查流程实例状态
curl -X GET http://localhost:8080/api/process/instance/{processInstanceId}
```

## 性能测试

### 批量启动流程

```bash
# Linux/Mac
for i in {1..10}
do
  curl -X POST http://localhost:8080/api/process/start \
    -H "Content-Type: application/json" \
    -d "{\"processDefinitionKey\":\"simpleProcess\",\"businessKey\":\"TEST-$i\"}"
done

# Windows PowerShell
1..10 | ForEach-Object {
  Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/process/start" `
    -ContentType "application/json" `
    -Body "{`"processDefinitionKey`":`"simpleProcess`",`"businessKey`":`"TEST-$_`"}"
}
```

## 总结

完成以上测试后，您应该能够：
- ✅ 启动和管理流程实例
- ✅ 查询和完成任务
- ✅ 操作流程变量
- ✅ 使用任务认领、转办等高级功能
- ✅ 查询历史数据

如有问题，请检查：
1. 数据库连接是否正常
2. 应用日志中的错误信息
3. API请求参数是否正确