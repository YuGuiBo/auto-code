# 员工请假流程自动化测试脚本

## 📋 概述

这是一个基于Python的自动化测试脚本，用于测试Flowable员工请假审批流程的所有场景。

## ✨ 特性

- ✅ 自动提取和传递processInstanceId和taskId
- ✅ 自动验证每个步骤的响应状态
- ✅ 彩色输出，清晰显示测试结果
- ✅ 支持运行单个或多个测试场景
- ✅ 完整的测试报告和错误信息
- ✅ 跨平台支持（Windows/Linux/Mac）

## 🎯 测试场景

脚本包含以下6个测试场景：

1. **场景1：短期请假 - 审批通过** ✅
   - 申请2天假期
   - 经理审批通过
   - 验证状态：PENDING_MANAGER_APPROVAL → APPROVED

2. **场景2：短期请假 - 审批拒绝** ❌
   - 申请2天假期
   - 经理审批拒绝
   - 验证状态：PENDING_MANAGER_APPROVAL → REJECTED

3. **场景3：长期请假 - 多级审批通过** ✅✅
   - 申请5天假期
   - 直接经理批准 → 部门经理批准
   - 验证状态：PENDING_MANAGER_APPROVAL → PENDING_DEPT_MANAGER_APPROVAL → APPROVED

4. **场景4：长期请假 - 经理初审拒绝** ❌
   - 申请5天假期
   - 直接经理拒绝
   - 验证状态：PENDING_MANAGER_APPROVAL → REJECTED

5. **场景5：长期请假 - 部门经理拒绝** ❌
   - 申请5天假期
   - 直接经理批准 → 部门经理拒绝
   - 验证状态：PENDING_MANAGER_APPROVAL → PENDING_DEPT_MANAGER_APPROVAL → REJECTED

6. **场景6：假期不足 - 自动拒绝** 🚫
   - 申请15天假期（只剩10天）
   - 系统自动拒绝
   - 验证状态：INSUFFICIENT_LEAVE

## 🚀 快速开始

### 前置条件

1. **Python 3.7+**
2. **Flowable应用已启动**（默认端口8080）
3. **数据库已连接**

### 安装依赖

```bash
cd tests/python
pip install -r requirements.txt
```

或者使用国内镜像加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 运行测试

#### 1. 运行所有测试场景

```bash
python test_scenarios.py --all
```

#### 2. 运行单个场景

```bash
# 运行场景1
python test_scenarios.py --scenario 1

# 运行场景6
python test_scenarios.py --scenario 6
```

#### 3. 运行多个场景

```bash
# 运行场景1、2和6
python test_scenarios.py --scenario 1 2 6
```

#### 4. 指定服务器地址

```bash
# 默认是http://localhost:8080
python test_scenarios.py --all --url http://192.168.1.100:8080
```

### 查看帮助

```bash
python test_scenarios.py --help
```

## 📊 输出示例

### 成功场景输出

```
============================================================
场景1：短期请假 - 审批通过 ✅
============================================================

[步骤] 步骤1
  申请2天假期
✓ 请假申请已提交
ℹ 流程实例ID: 12345-67890
ℹ 申请人: 张三, 请假天数: 2

[步骤] 步骤2
  验证流程状态为待审批
ℹ 当前状态: 待直接经理审批 (PENDING_MANAGER_APPROVAL)
ℹ 是否结束: 否
✓ 状态验证通过: PENDING_MANAGER_APPROVAL

...

场景1测试通过 ✓
```

### 测试汇总

```
============================================================
测试结果汇总
============================================================
总测试数: 6
通过: 6
失败: 0
============================================================
```

## 🎨 颜色说明

- 🔵 **蓝色**: 场景标题
- 🟢 **绿色**: 成功信息 (✓)
- 🔴 **红色**: 错误信息 (✗)
- 🟡 **黄色**: 提示信息 (ℹ)
- 🔷 **青色**: 步骤标题

## 📝 脚本特点

### 自动化ID管理

脚本会自动：
1. 从申请请假API的响应中提取`processInstanceId`
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
python test_scenarios.py --all
echo $?  # 0表示成功，非0表示失败
```

### 集成到测试套件

```python
from test_scenarios import FlowableTestClient

# 创建客户端
client = FlowableTestClient("http://localhost:8080")

# 运行单个场景
client.test_scenario_1()

# 检查结果
if client.result.failed == 0:
    print("所有测试通过！")
```

## ⚠️ 注意事项

1. **确保应用已启动**：测试前请确认Flowable应用正在运行
2. **端口号**: 默认使用8080端口，如需修改请使用`--url`参数
3. **数据清理**: 每次测试都会创建新的流程实例，测试完成后可能需要清理数据
4. **并发测试**: 建议单线程运行，避免任务冲突

## 🐛 故障排查

### 连接失败

```
✗ API调用失败: Connection refused
```

**解决方案**：检查应用是否启动，端口是否正确

### 找不到任务

```
✗ 没有找到待办任务
```

**解决方案**：
1. 检查流程是否正确创建
2. 检查前一个步骤是否成功
3. 查看应用日志

### 状态验证失败

```
✗ 状态验证失败: 期望=APPROVED, 实际=PENDING_MANAGER_APPROVAL
```

**解决方案**：
1. 检查审批操作是否成功
2. 等待时间可能不够，增加wait时间
3. 查看应用日志确认流程状态

## 📚 相关文档

- [完整测试指南.md](../../完整测试指南.md) - 手动测试步骤
- [状态管理功能说明.md](../../状态