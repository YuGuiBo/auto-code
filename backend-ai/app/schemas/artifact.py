from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ArtifactCreate(BaseModel):
    """创建制品请求"""
    process_id: int = Field(..., description="流程ID")
    artifact_type: str = Field(..., description="制品类型")
    content: Optional[Dict[str, Any]] = Field(None, description="制品内容JSON")
    content_text: Optional[str] = Field(None, description="制品文本内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    created_by: Optional[str] = Field(None, description="创建人")


class ArtifactResponse(BaseModel):
    """制品响应"""
    id: int
    process_id: int
    artifact_type: str
    content: Optional[Dict[str, Any]]
    content_text: Optional[str]
    metadata: Optional[Dict[str, Any]]
    version: int
    parent_id: Optional[int]
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Made with Bob
