from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class AnalysisMatrix(BaseModel):
    """分析矩阵 - 5个维度"""
    actors: List[str] = Field(default_factory=list, description="参与者/角色")
    scenarios: List[str] = Field(default_factory=list, description="场景/活动")
    data: List[str] = Field(default_factory=list, description="数据/信息")
    rules: List[str] = Field(default_factory=list, description="规则/逻辑")
    exceptions: List[str] = Field(default_factory=list, description="异常场景")


class ProcessCreate(BaseModel):
    """创建流程请求"""
    project_id: int = Field(..., description="项目ID")
    name: str = Field(..., min_length=1, max_length=200, description="流程名称")
    description: Optional[str] = Field(None, description="流程描述")
    created_by: Optional[str] = Field(None, description="创建人")


class ProcessUpdate(BaseModel):
    """更新流程请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    current_stage: Optional[str] = None
    status: Optional[str] = None


class AnalysisMatrixUpdate(BaseModel):
    """更新分析矩阵"""
    analysis_matrix: AnalysisMatrix


class RequirementsUpdate(BaseModel):
    """更新结构化需求"""
    structured_requirements: Dict[str, Any]


class UserCasesUpdate(BaseModel):
    """更新用户用例"""
    user_cases: List[Dict[str, Any]]


class ProcessResponse(BaseModel):
    """流程响应"""
    id: int
    project_id: int
    name: str
    description: Optional[str]
    analysis_matrix: Optional[Dict[str, Any]]
    structured_requirements: Optional[Dict[str, Any]]
    user_cases: Optional[List[Dict[str, Any]]]
    bpmn_xml: Optional[str]
    bpmn_json: Optional[Dict[str, Any]]
    current_stage: str
    status: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Made with Bob
