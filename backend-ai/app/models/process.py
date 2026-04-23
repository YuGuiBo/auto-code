from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Process(Base):
    """BPM流程表"""
    __tablename__ = "bpm_process"

    id = Column(Integer, primary_key=True, index=True, comment="流程ID")
    project_id = Column(Integer, ForeignKey("bpm_project.id"), nullable=False, comment="所属项目ID")
    name = Column(String(200), nullable=False, comment="流程名称")
    description = Column(Text, comment="流程描述")
    
    # 分析矩阵 (5个维度)
    analysis_matrix = Column(JSON, comment="分析矩阵JSON: {actors, goals, constraints, data, rules}")
    
    # 结构化需求
    structured_requirements = Column(JSON, comment="结构化需求JSON")
    
    # 用户用例
    user_cases = Column(JSON, comment="用户用例JSON数组")
    
    # BPMN相关
    bpmn_xml = Column(Text, comment="BPMN XML内容")
    bpmn_json = Column(JSON, comment="BPMN JSON配置")
    
    # 状态管理
    current_stage = Column(String(50), default="analysis", comment="当前阶段: analysis, requirements, cases, design")
    status = Column(String(50), default="draft", comment="流程状态: draft, in_progress, completed")
    
    # 审计字段
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Process(id={self.id}, name='{self.name}', stage='{self.current_stage}')>"

# Made with Bob
