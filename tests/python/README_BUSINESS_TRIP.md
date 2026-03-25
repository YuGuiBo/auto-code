# 出差申请模块测试指南

## 📋 模块概述

出差申请模块用于处理员工的出差申请，支持基于出差天数的智能路由和多级审批流程。

## 🎯 功能特性

- ✅ 支持多种出差信息（目的地、时间、交通、住宿等）
- ✅ 基于天数的智能路由（≤3天 vs >3天）
- ✅ 三级审批流程（经理→部门经理→行政）
- ✅ 完整的状态管理（6种状态）
- ✅ 审批意见记录
- ✅ 流程历史查询

## 🔄 审批流程

### 短期出差流程（天数 ≤ 3天）
```
提交申请 → 直接经理审批 → 行政审批 → 完成
```

### 长期出差流程（天数 > 3天）
```
提交申请 → 直接经理审批 → 部门经理审批 → 行政审批 → 完成
```

## 📊 状态说明

| 状态代码 | 显示名称 | 说明 |
|---------|---------|------|
| `SUBMITTED` | 已提交 | 出差申请已提交，等待处理 |
| `PENDING_MANAGER_APPROVAL` | 待直接经理审批 | 等待直接经理审批 |
| `PENDING_DEPT_MANAGER_APPROVAL` | 待部门经理审批 | 等待部门经理审批（仅长期出差） |
| `PENDING_ADMIN_APPROVAL` | 待行政审批 | 等待行政部门审批 |
| `APPROVED` | 已批准 | 出差申请已批准，可以出差 |
| `REJECTED` | 已拒绝 | 出差申请已被拒绝 |

## 🚀 快速开始

### 前置条件

1. **启动后端服务**
   ```bash
   cd c:/Users/ZZ0DIB672/Desktop/Learning/Asset/auto-code
   mvn spring-boot:run
   ```

2. **安装Python依赖**
   ```bash
   cd tests/python
   pip install -r requirements.txt
   ```

### 运行测试

```bash
# 运行所有测试场景
python test_business_trip.py
```

## 🧪 测试场景

### 场景1：短期出差通过（≤3天）
- **申请人**：张三
- **目的地**：上海
- **天数**：2天
- **预算**：1500元
- **流程**：经理批准 → 行政批准 → 完成
- **预期结果**：✅ APPROVED

### 场景2：长期出差通过（>3天）
- **申请人**：李四
- **目的地**：深圳
- **天数**：7天
- **预算**：8000元
- **流程**：经理批准 → 部门经理批准 → 行政批准 → 完成
- **预期结果**：✅ APPROVED

### 场景3：经理拒绝场景
- **申请人**：王五
- **目的地**：北京
- **天数**：5天
- **预算**：5000元
- **流程**：经理拒绝 → 结束
- **预期结果**：❌ REJECTED

### 场景4：部门经理拒绝场景
- **申请人**：赵六
- **目的地**：广州
- **天数**：10天
- **预算**：12000元
- **流程**：经理批准 → 部门经理拒绝 → 结束
- **预期结果**：❌ REJECTED

### 场景5：行政拒绝场景
- **申请人**：孙七
- **目的地**：杭州
- **天数**：1天
- **预算**：800元
- **流程**：经理批准 → 行政拒绝 → 结束
- **预期结果**：❌ REJECTED

## 📡 API接口

### 1. 提交出差申请
```http
POST /api/business-trip/apply
Content-Type: application/json

{
  "applicantName": "张三",
  "department": "销售部",
  "destination": "上海",
  "startDate": "2026-04-01",
  "endDate": "2026-04-03",
  "days": 2,
  "purpose": "客户拜访",
  "transportation": "高铁",
  "accommodation": "经济型",
  "estimatedCost": 1500.0,
  "companions": "无",
  "contactPhone": "13800138000"
}
```

**响应示例：**
```json
{
  "success": true,
  "processInstanceId": "12345",
  "message": "出差申请已提交",
  "applicant": "张三",
  "destination": "上海",
  "days": 2
}
```

### 2. 经理审批
```http
POST /api/business-trip/manager/approve/{taskId}?approved=true&comment=同意出差，注意安全
```

**参数说明：**
- `taskId`: 任务ID（从待办任务列表获取）
- `approved`: 是否批准（true/false）
- `comment`: 审批意见

### 3. 部门经理审批
```http
POST /api/business-trip/dept-manager/approve/{taskId}?approved=true&comment=同意出差
```

### 4. 行政审批
```http
POST /api/business-trip/admin/approve/{taskId}?approved=true&comment=已预定高铁票和酒店
```

### 5. 查询流程实例
```http
GET /api/business-trip/process/instance/{processInstanceId}
```

**响应示例：**
```json
{
  "processInstanceId": "12345",
  "processDefinitionName": "出差申请流程",
  "status": "APPROVED",
  "statusDisplayName": "已批准",
  "ended": true,
  "businessKey": "TRIP-2026-001",
  "startTime": "2026-03-25T10:00:00",
  "endTime": "2026-03-25T10:30:00"
}
```

### 6. 查询待办任务
```http
GET /api/business-trip/task/list
```

**响应示例：**
```json
[
  {
    "id": "task-001",
    "name": "直接经理审批",
    "assignee": "manager01",
    "createTime": "2026-03-25T10:00:00",
    "processInstanceId": "12345"
  }
]
```

## ✅ 验收标准

测试通过需满足以下条件：

- ✅ 所有5个测试场景全部通过
- ✅ 天数路由判断正确（≤3天 vs >3天）
- ✅ 短期出差跳过部门经理审批
- ✅ 长期出差包含部门经理审批
- ✅ 状态转换正确
- ✅ 审批流程完整
- ✅ 拒绝场景正常处理
- ✅ 可以查询流程实例和待办任务

## 🎯 预期测试结果

```
出差申请模块测试

场景1：短期出差通过（≤3天）
✓ 出差申请已提交，流程ID: xxx
✓ 经理审批完成
✓ 行政审批完成
✓ ✅ 场景1测试通过！短期出差流程正常完成

场景2：长期出差通过（>3天）
✓ 出差申请已提交，流程ID: xxx
✓ 经理审批完成
✓ 部门经理审批完成
✓ 行政审批完成
✓ ✅ 场景2测试通过！长期出差流程正常完成

场景3：经理拒绝场景
✓ 出差申请已提交，流程ID: xxx
✓ 经理审批完成（拒绝）
✓ ✅ 场景3测试通过！经理拒绝流程正常结束

场景4：部门经理拒绝场景
✓ 出差申请已提交，流程ID: xxx
✓ 经理审批完成
✓ 部门经理审批完成（拒绝）
✓ ✅ 场景4测试通过！部门经理拒绝流程正常结束

场景5：行政拒绝场景
✓ 出差申请已提交，流程ID: xxx
✓ 经理审批完成
✓ 行政审批完成（拒绝）
✓ ✅ 场景5测试通过！行政拒绝流程正常结束

测试结果摘要
✓ 场景1：短期出差通过（≤3天）
✓ 场景2：长期出差通过（>3天）
✓ 场景3：经理拒绝场景
✓ 场景4：部门经理拒绝场景
✓ 场景5：行政拒绝场景

✓ ✅ 所有测试通过！(5/5)
✓ 出差申请模块测试完成，所有功能正常！
```

## 🎨 输出说明

测试脚本使用彩色输出：

- 🔵 **蓝色**: 场景标题和分隔线
- 🟢 **绿色**: 成功信息 (✓)
- 🔴 **红色**: 错误信息 (✗)
- 🟡 **黄色**: 警告信息 (⚠)

## 🐛 常见问题

### 1. 连接错误
```
requests.exceptions.ConnectionError: Failed to establish a new connection
```
**解决方案**：确认后端服务已启动（http://localhost:8080）

### 2. 找不到待办任务
```
AssertionError: 未找到待办任务
```
**解决方案**：
- 检查流程是否正确启动
- 查看服务器日志
- 确认processInstanceId正确

### 3. 状态不匹配
```
AssertionError: 状态不匹配
```
**解决方案**：
- 检查BPMN流程定义
- 验证Service状态更新逻辑
- 查看流程变量是否正确传递

### 4. 天数路由问题
```
长期出差没有经过部门经理审批
```
**解决方案**：
- 检查BPMN网关条件：`${days > 3}`
- 确认申请数据中days字段正确
- 查看流程执行日志

## 📝 脚本特点

### 自动化ID管理
脚本会自动：
1. 从申请出差API的响应中提取`processInstanceId`
2. 从任务列表API的响应中提取`taskId`
3. 自动传递给后续的API调用

**无需手动复制粘贴ID！**

### 状态验证
每个步骤都会验证：
- HTTP响应状态码
- 流程实例的`status`字段
- 流程实例的`ended`字段
- 任务列表的数量

### 错误处理
- API调用失败时会显示详细错误信息
- 每个场景独立执行，一个失败不影响其他场景
- 最后提供完整的测试汇总报告

## 🔧 高级用法

### 在CI/CD中使用

```bash
# 运行所有测试，返回退出码
python test_business_trip.py
echo $?  # 0表示成功，非0表示失败
```

### 修改API地址

如果后端服务不在localhost:8080，可以修改脚本中的BASE_URL：

```python
# 在test_business_trip.py中修改
BASE_URL = "http://your-server:port"
```

## ⚠️ 注意事项

1. **确保应用已启动**：测试前请确认Flowable应用正在运行
2. **端口号**: 默认使用8080端口
3. **数据清理**: 每次测试都会创建新的流程实例，测试完成后可能需要清理数据
4. **并发测试**: 建议单线程运行，避免任务冲突
5. **日期格式**: 所有日期使用ISO格式（YYYY-MM-DD）

## 📞 下一步

完成出差申请模块测试后，请继续：
1. ✅ 请假管理模块（已完成）
2. ✅ 报销管理模块（已完成）
3. ✅ 出差申请模块（当前）
4. ⏭️ 加班申请模块

## 📚 相关文档

- [测试指南.md](../../测试指南.md) - 总体测试指南
- [README_LEAVE.md](./README_LEAVE.md) - 请假模块测试指南
- [README_REIMBURSEMENT.md](./README_REIMBURSEMENT