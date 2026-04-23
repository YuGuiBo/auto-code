from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Artifact(Base):
    """BPM制品表 - 存储对话历史、中间结果等"""
    __tablename__ = "bpm_artifact"

    id = Column(Integer, primary_key=True, index=True, comment="制品ID")
    process_id = Column(Integer, ForeignKey("bpm_process.id"), nullable=False, comment="所属流程ID")
    
    # 制品类型: chat_message, analysis_result, requirement_draft, case_draft, bpmn_draft
    artifact_type = Column(String(50), nullable=False, comment="制品类型")
    
    # 制品内容
    content = Column(JSON, comment="制品内容JSON")
    content_text = Column(Text, comment="制品文本内容")
    
    # 元数据（避免与SQLAlchemy的metadata冲突）
    meta_data = Column(JSON, comment="元数据: {role, timestamp, version, etc.}")
    
    # 版本控制
    version = Column(Integer, default=1, comment="版本号")
    parent_id = Column(Integer, ForeignKey("bpm_artifact.id"), comment="父制品ID(用于版本追踪)")
    
    # 审计字段
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Artifact(id={self.id}, type='{self.artifact_type}', version={self.version})>"

# Made with Bob
