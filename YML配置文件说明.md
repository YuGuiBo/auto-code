# YML配置文件说明文档

## 📋 删除的4个YML配置文件

更新为数据库存储后，以下4个YML配置文件已从 `src/main/resources/processes/` 目录中删除：

1. `leave-request-process-config.yml` - 请假流程配置
2. `business-trip-process-config.yml` - 出差流程配置
3. `overtime-process-config.yml` - 加班流程配置
4. `reimbursement-process-config.yml` - 报销流程配置

---

## 🎯 这些YML文件的作用

### 主要作用：**BPMN流程的业务配置文件**

这些YML文件**不是给测试脚本用的**，而是**BPMN流程的配套业务配置文件**。它们定义了流程的业务逻辑和行为。

### 具体包含的配置内容

#### 1. 流程基本信息
```yaml
process:
  key: leaveRequestProcess      # 流程Key
  name: 员工请假流程             # 流程名称
  apiPrefix: /api/leave          # API路径前缀
  version: 1.0.0
```

#### 2. 状态定义与映射
```yaml
statuses:
  SUBMITTED:
    displayName: 已提交
    description: 请假申请已提交
  APPROVED:
    displayName: 已批准
    description: 请假申请已批准
  REJECTED:
    displayName: 已拒绝
    description: 请假申请已拒绝
```

#### 3. 任务配置
```yaml
tasks:
  - taskName: 部门经理审批
    taskKey: deptManagerApproval
    approvalType: manager
    variables:
      approvalResult: approved     # 审批结果变量名
      commentField: comment         # 评论字段名
    statusMapping:
      approved: APPROVED            # 通过时的状态
      rejected: REJECTED            # 拒绝时的状态
```

#### 4. 必填字段
```yaml
requiredFields:
  - applicantName    # 申请人姓名
  - leaveDays        # 请假天数
  - reason           # 请假原因
```

#### 5. 初始化配置
```yaml
initialization:
  defaultStatus: SUBMITTED
```

---

## 🔗 YML文件与BPMN文件的关系

```
leave-request-process.bpmn20.xml  ←→  leave-request-process-config.yml
         ↓                                      ↓
    定义流程结构                           定义业务逻辑
    - 节点和连线                           - 状态映射
    - 任务定义                             - API配置
    - 流转规则                             - 字段验证
```

**形象比喻：**
- **BPMN文件** = 流程的"骨架"（结构）
- **YML文件** = 流程的"血肉"（业务配置）

两者配合使用，才能构成一个完整可运行的业务流程。

---

## 💡 在系统中的使用方式

### 改造前（文件系统）

```java
// DatabaseProcessConfigLoader 从文件系统加载
1. 扫描 resources/processes/ 目录
2. 读取每个子目录下的 .yml 配置文件
3. 解析YAML内容为 ProcessConfig 对象
4. 根据配置动态生成REST API
5. 使用配置中的状态映射、字段验证等
```

**特点：**
- ✅ 配置文件直观可见
- ❌ 需要重启应用才能生效
- ❌ 无法动态更新
- ❌ 不支持版本管理

### 改造后（数据库存储）

```java
// DatabaseProcessConfigLoader 从数据库加载
1. 查询 process_definition 表
2. 从 config_content 字段读取YAML内容（原来YML文件的内容）
3. 解析YAML内容为 ProcessConfig 对象
4. 其他逻辑完全相同
```

**特点：**
- ✅ 支持动态上传和更新
- ✅ 无需重启应用（热加载）
- ✅ 支持版本管理和历史记录
- ✅ 可以通过API管理

---

## ❓ 为什么不是给测试脚本用的？

### 测试脚本使用的是什么？

测试脚本（如 `tests/python/` 中的脚本）使用的是：
- **REST API接口**：调用 `/api/leave/apply` 等接口
- **JSON格式的请求数据**：不需要读取YML配置

示例：
```python
# 测试脚本发送的是JSON请求
response = requests.post('http://localhost:8080/api/leave/apply', 
    json={
        "applicantName": "张三",
        "leaveDays": 3,
        "reason": "测试"
    })
```

### YML配置文件的使用者

YML配置文件是**后端系统内部使用**的，用于：

1. **动态生成REST API端点**
   - 根据 `apiPrefix` 配置生成 `/api/leave/apply` 等接口
   
2. **验证请求参数**
   - 根据 `requiredFields` 验证请求中的必填字段
   
3. **映射业务状态**
   - 根据 `statusMapping` 将审批结果映射为业务状态
   
4. **配置审批逻辑**
   - 根据 `tasks` 配置处理不同的审批任务

**测试脚本只需要知道API接口和请求格式，不需要读取YML配置。**

---

## 📊 对比总结

| 对比项 | BPMN文件 (.bpmn20.xml) | YML配置文件 (-config.yml) |
|-------|----------------------|-------------------------|
| **作用** | 定义流程结构和流转规则 | 定义业务配置和API行为 |
| **内容** | 任务节点、网关、连线 | 状态映射、字段验证、API配置 |
| **使用者** | Flowable引擎 | 自定义的动态API生成器 |
| **是否必需** | ✅ 必需 | ✅ 必需（在此架构中） |
| **给测试脚本用？** | ❌ 否 | ❌ 否 |
| **存储位置（改造前）** | resources/processes/*.bpmn20.xml | resources/processes/*-config.yml |
| **存储位置（改造后）** | process_definition.bpmn_content | process_definition.config_content |

---

## 🔄 数据迁移说明

### 迁移过程

当系统首次启动时，`ProcessDataMigration` 组件会自动执行迁移：

1. **扫描文件系统**
   - 扫描 `resources/processes/` 目录
   - 查找所有 `.bpmn20.xml` 和 `-config.yml` 文件

2. **读取文件内容**
   - 读取BPMN文件的XML内容
   - 读取YML文件的YAML内容

3. **存入数据库**
   - 将BPMN内容存入 `process_definition.bpmn_content` 字段
   - 将YML内容存入 `process_definition.config_content` 字段
   - 保存流程名称、Key、版本等元数据

4. **部署到Flowable**
   - 调用 Flowable 的 `RepositoryService.createDeployment()` API
   - 将流程部署到 Flowable 引擎
   - 记录部署ID和部署历史

### 迁移后的变化

| 项目 | 改造前 | 改造后 |
|-----|-------|-------|
| **配置来源** | 文件系统 | 数据库 |
| **配置更新** | 修改文件+重启 | API上传+热加载 |
| **版本管理** | 无 | 有（数据库记录） |
| **文件是否需要** | ✅ 必需 | ❌ 可删除 |

---

## ✅ 总结

### YML配置文件的性质

- ✅ **BPMN流程的配套业务配置文件**
- ✅ **后端系统用来动态生成API和业务逻辑的配置**
- ✅ **定义了流程的状态、任务、字段验证等业务规则**
- ❌ **不是给测试脚本用的**
- ❌ **不是数据文件或测试数据**

### 删除文件后的影响

删除这些YML文件后：
- ✅ **不影响系统运行**：内容已存储在数据库中
- ✅ **不影响测试脚本**：测试脚本使用REST API，不读取YML文件
- ✅ **保持了相同的功能**：系统从数据库读取配置，行为完全一致
- ✅ **增强了灵活性**：支持动态更新和热加载

### 最佳实践

1. **备份原始文件**
   - 在Git仓库中保留历史记录
   - 或者单独备份到其他位置

2. **禁用自动迁移**
   - 迁移完成后，在 `application.yml` 中设置：
     ```yaml
     app:
       process:
         migration:
           enabled: false
     ```

3. **使用数据库管理**
   - 后续新流程通过 API 上传
   - 在数据库中查看和管理流程配置
   - 利用版本管理功能进行回滚

---

**文档版本**：v1.0
**相关文档**：
- 数据库存储与热加载实施方案.md
- 实施指南-数据库存储与热加载.md