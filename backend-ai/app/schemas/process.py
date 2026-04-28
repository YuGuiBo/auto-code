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


class TestCaseStep(BaseModel):
    """测试案例步骤"""
    step_no: int = Field(..., description="步骤编号")
    actor: str = Field(..., description="执行者")
    action: str = Field(..., description="操作内容")
    fields: Dict[str, Any] = Field(default_factory=dict, description="输入字段")
    expected_result: str = Field(..., description="预期结果")


class TestCase(BaseModel):
    """测试案例"""
    id: str = Field(..., description="测试案例ID")
    name: str = Field(..., description="测试案例名称")
    category: str = Field(..., description="类别: normal/branch/exception")
    description: str = Field(..., description="描述")
    preconditions: List[str] = Field(default_factory=list, description="前置条件")
    steps: List[TestCaseStep] = Field(default_factory=list, description="测试步骤")
    postconditions: List[str] = Field(default_factory=list, description="后置条件")
    expected_final_result: str = Field(..., description="预期最终结果")


class TestCasesMetadata(BaseModel):
    """测试案例元数据"""
    total_cases: int = Field(0, description="总测试案例数")
    normal_cases: int = Field(0, description="正常流程案例数")
    branch_cases: int = Field(0, description="分支流程案例数")
    exception_cases: int = Field(0, description="异常场景案例数")
    generated_at: Optional[str] = Field(None, description="生成时间")


class TestCasesData(BaseModel):
    """测试案例数据"""
    test_cases: List[TestCase] = Field(default_factory=list, description="测试案例列表")
    metadata: TestCasesMetadata = Field(default_factory=TestCasesMetadata, description="元数据")


class TestCasesUpdate(BaseModel):
    """更新测试案例"""
    test_cases: List[Dict[str, Any]]


class TestCaseFeedback(BaseModel):
    """测试案例反馈"""
    feedback: str = Field(..., min_length=1, description="反馈内容")
    issues: List[str] = Field(default_factory=list, description="问题列表")


class ProcessResponse(BaseModel):
    """流程响应"""
    id: int
    project_id: int
    name: str
    description: Optional[str]
    analysis_matrix: Optional[Dict[str, Any]]
    structured_requirements: Optional[Dict[str, Any]]
    user_cases: Optional[List[Dict[str, Any]]]
    test_cases: Optional[Dict[str, Any]]
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
