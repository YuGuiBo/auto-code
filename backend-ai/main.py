from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import bpmn

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting BPM-Nova AI Service...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    yield
    
    # 关闭时
    logger.info("Shutting down BPM-Nova AI Service...")


# 创建FastAPI应用
app = FastAPI(
    title="BPM-Nova AI Service",
    description="AI驱动的工作流设计工具 - 后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(bpmn.router, prefix="/api/bpmn", tags=["BPMN"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "BPM-Nova AI Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )

# Made with Bob
