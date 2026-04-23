from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    """BPM项目表"""
    __tablename__ = "bpm_project"

    id = Column(Integer, primary_key=True, index=True, comment="项目ID")
    name = Column(String(200), nullable=False, comment="项目名称")
    description = Column(Text, comment="项目描述")
    status = Column(String(50), default="draft", comment="项目状态: draft, in_progress, completed")
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"

# Made with Bob
