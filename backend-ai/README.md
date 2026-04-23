# BPM-Nova Backend AI Service

基于FastAPI的AI驱动BPMN流程设计后端服务。

## 技术栈

- **FastAPI**: 现代、高性能的Web框架
- **SQLAlchemy**: ORM数据库操作
- **PostgreSQL**: 关系型数据库
- **OpenAI Client**: AI服务集成（支持DeepSeek/通义千问）
- **Pydantic**: 数据验证和设置管理

## 项目结构

```
backend-ai/
├── app/
│   ├── api/              # API路由
│   │   ├── __init__.py
│   │   └── bpmn.py       # BPMN相关端点
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   └── database.py   # 数据库连接
│   ├── models/           # SQLAlchemy模型
│   │   ├── project.py    # 项目模型
│   │   ├── process.py    # 流程模型
│   │   └── artifact.py   # 制品模型
│   ├── schemas/          # Pydantic schemas
│   │   ├── process.py    # 流程相关schema
│   │   ├── chat.py       # 聊天相关schema
│   │   └── artifact.py   # 制品相关schema
│   └── services/         # 业务服务
│       └── ai_service.py # AI服务
├── main.py               # FastAPI应用入口
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量示例
└── README.md             # 本文件
```

## 安装步骤

### 1. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://asset:asset@localhost:15432/Asset

# AI服务配置（DeepSeek示例）
AI_API_KEY=your_deepseek_api_key
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat

# 或使用通义千问
# AI_API_KEY=your_qwen_api_key
# AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# AI_MODEL=qwen-plus

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### 4. 初始化数据库

确保PostgreSQL数据库正在运行，然后执行：

```bash
python init_db.py
```

这将创建以下表：
- `bpm_project`: 项目表
- `bpm_process`: 流程表
- `bpm_artifact`: 制品表（对话历史、中间结果等）

### 5. 启动服务

```bash
# 开发模式（自动重载）
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

## API文档

启动服务后，访问以下地址查看自动生成的API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 主要API端点

### 1. 需求分析对话

**POST** `/api/bpmn/analyze`

通过对话分析用户需求，生成5维分析矩阵。

请求体：
```json
{
  "process_id": null,  // 首次对话为null，后续传入流程ID
  "message": "我想设计一个请假流程",
  "context": [],  // 对话上下文
  "user_id": "user123"
}
```

响应：
```json
{
  "process_id": 1,
  "message": "好的，我来帮您设计请假流程...",
  "analysis_matrix": {
    "actors": ["员工", "直属领导", "HR"],
    "goals": ["申请休假", "审批请假"],
    "constraints": ["需提前3天申请"],
    "data": ["请假类型", "开始日期", "结束日期"],
    "rules": ["3天以内直属领导审批", "超过3天需HR审批"]
  },
  "stage": "analysis",
  "suggestions": ["请假有哪些类型？", "审批流程是怎样的？"]
}
```

### 2. 获取流程详情

**GET** `/api/bpmn/process/{process_id}`

### 3. 更新分析矩阵

**PUT** `/api/bpmn/process/{process_id}/matrix`

### 4. 生成结构化需求

**POST** `/api/bpmn/process/{process_id}/requirements`

根据分析矩阵生成结构化需求文档。

### 5. 生成用户用例

**POST** `/api/bpmn/process/{process_id}/cases`

根据需求文档生成用户用例。

### 6. 获取对话历史

**GET** `/api/bpmn/process/{process_id}/history`

### 7. 更新流程阶段

**POST** `/api/bpmn/process/{process_id}/stage?stage=requirements`

## 数据库表结构

### bpm_project (项目表)
- `id`: 项目ID
- `name`: 项目名称
- `description`: 项目描述
- `status`: 项目状态
- `created_by`: 创建人
- `created_at`: 创建时间
- `updated_at`: 更新时间

### bpm_process (流程表)
- `id`: 流程ID
- `project_id`: 所属项目ID
- `name`: 流程名称
- `description`: 流程描述
- `analysis_matrix`: 分析矩阵JSON
- `structured_requirements`: 结构化需求JSON
- `user_cases`: 用户用例JSON数组
- `bpmn_xml`: BPMN XML内容
- `bpmn_json`: BPMN JSON配置
- `current_stage`: 当前阶段 (analysis/requirements/cases/design)
- `status`: 流程状态
- `created_by`: 创建人
- `created_at`: 创建时间
- `updated_at`: 更新时间

### bpm_artifact (制品表)
- `id`: 制品ID
- `process_id`: 所属流程ID
- `artifact_type`: 制品类型 (chat_message/analysis_result/requirement_draft/case_draft/bpmn_draft)
- `content`: 制品内容JSON
- `content_text`: 制品文本内容
- `metadata`: 元数据
- `version`: 版本号
- `parent_id`: 父制品ID
- `created_by`: 创建人
- `created_at`: 创建时间

## AI服务配置

### 使用DeepSeek

```env
AI_API_KEY=sk-xxxxx
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

### 使用通义千问

```env
AI_API_KEY=sk-xxxxx
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-plus
```

## 开发说明

### 添加新的API端点

1. 在 `app/api/bpmn.py` 中添加路由函数
2. 定义相应的Pydantic schema（如需要）
3. 实现业务逻辑

### 添加新的AI功能

在 `app/services/ai_service.py` 中添加新方法。

### 数据库迁移

如果修改了模型，需要：
1. 更新模型定义
2. 重新运行 `python init_db.py`（开发环境）
3. 生产环境建议使用Alembic进行迁移

## 故障排除

### 数据库连接失败

检查：
1. PostgreSQL是否正在运行
2. `.env` 中的数据库连接字符串是否正确
3. 数据库用户权限是否足够

### AI服务调用失败

检查：
1. API Key是否正确
2. Base URL是否正确
3. 网络连接是否正常
4. API配额是否充足

### 端口被占用

修改 `.env` 中的 `SERVER_PORT` 或使用：
```bash
uvicorn main:app --port 8001
```

## 性能优化建议

1. **数据库连接池**: 已配置连接池，可根据需要调整 `pool_size` 和 `max_overflow`
2. **异步处理**: AI调用已使用async/await
3. **缓存**: 可考虑添加Redis缓存常用数据
4. **日志**: 生产环境建议配置日志轮转

## 安全建议

1. 不要将 `.env` 文件提交到版本控制
2. 使用强密码和安全的API Key
3. 生产环境启用HTTPS
4. 配置CORS白名单
5. 添加API限流

## 许可证

MIT License