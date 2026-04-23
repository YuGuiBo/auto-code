from fastapi import APIRouter
from .bpmn import router as bpmn_router

api_router = APIRouter()

# 注册BPMN相关路由
api_router.include_router(bpmn_router, prefix="/bpmn", tags=["BPMN"])

# Made with Bob
