from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class ChatRequest(BaseModel):
    """聊天请求"""
    process_id: Optional[int] = Field(None, description="流程ID，首次对话时为空")
    message: str = Field(..., min_length=1, description="用户消息")
    context: Optional[List[ChatMessage]] = Field(default_factory=list, description="对话上下文")
    user_id: Optional[str] = Field(None, description="用户ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    process_id: int = Field(..., description="流程ID")
    message: str = Field(..., description="AI回复消息")
    analysis_matrix: Optional[Dict[str, Any]] = Field(None, description="分析矩阵（如果生成）")
    stage: str = Field(..., description="当前阶段")
    suggestions: Optional[List[str]] = Field(None, description="建议的后续问题")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")

# Made with Bob
