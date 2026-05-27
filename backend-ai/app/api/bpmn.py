from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.process import Process
from app.models.project import Project
from app.models.artifact import Artifact
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.schemas.process import (
    ProcessCreate,
    ProcessUpdate,
    ProcessResponse,
    AnalysisMatrixUpdate,
    RequirementsUpdate,
    UserCasesUpdate,
    TestCasesUpdate,
    TestCaseFeedback
)
from app.services.ai_service import ai_service

router = APIRouter()


def get_or_create_default_project(db: Session) -> int:
    """获取或创建默认项目"""
    project = db.query(Project).filter(Project.name == "默认项目").first()
    if not project:
        project = Project(
            name="默认项目",
            description="系统默认项目，用于存放通过AI对话创建的流程",
            created_by="system"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
    return project.id


@router.post("/analyze", response_model=ChatResponse)
async def analyze_requirements(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    分析用户需求，生成或更新分析矩阵
    
    - 首次对话：创建新流程
    - 后续对话：更新现有流程
    """
    try:
        # 准备对话上下文
        context = []
        if request.context:
            context = [
                {"role": msg.role, "content": msg.content}
                for msg in request.context
            ]
        
        # 调用AI服务分析需求
        ai_result = await ai_service.analyze_requirements(
            user_message=request.message,
            context=context
        )
        
        # 如果是首次对话，创建新流程
        if request.process_id is None:
            # 获取或创建默认项目
            project_id = get_or_create_default_project(db)
            
            process = Process(
                project_id=project_id,
                name=f"流程_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description="通过AI对话创建的流程",
                analysis_matrix=ai_result.get("analysis_matrix"),
                current_stage="analysis",
                status="draft",
                created_by=request.user_id
            )
            db.add(process)
            db.commit()
            db.refresh(process)
            process_id = process.id
        else:
            # 更新现有流程
            process = db.query(Process).filter(Process.id == request.process_id).first()
            if not process:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"流程ID {request.process_id} 不存在"
                )
            
            # 更新分析矩阵
            process.analysis_matrix = ai_result.get("analysis_matrix")
            db.commit()
            process_id = process.id
        
        # 保存对话历史到artifact表
        user_artifact = Artifact(
            process_id=process_id,
            artifact_type="chat_message",
            content={"role": "user", "content": request.message},
            content_text=request.message,
            meta_data={"timestamp": datetime.now().isoformat()},
            created_by=request.user_id
        )
        db.add(user_artifact)
        
        assistant_artifact = Artifact(
            process_id=process_id,
            artifact_type="chat_message",
            content={"role": "assistant", "content": ai_result.get("message")},
            content_text=ai_result.get("message"),
            meta_data={
                "timestamp": datetime.now().isoformat(),
                "completeness": ai_result.get("completeness", 0.0)
            },
            created_by="system"
        )
        db.add(assistant_artifact)
        db.commit()
        
        # 构造响应
        return ChatResponse(
            process_id=process_id,
            message=ai_result.get("message", ""),
            analysis_matrix=ai_result.get("analysis_matrix"),
            stage=ai_result.get("stage", "analysis"),
            suggestions=ai_result.get("next_questions"),
            metadata={
                "completeness": ai_result.get("completeness", 0.0)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析需求时发生错误: {str(e)}"
        )


@router.get("/process/{process_id}", response_model=ProcessResponse)
async def get_process(
    process_id: int,
    db: Session = Depends(get_db)
):
    """获取流程详情"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    return process


@router.put("/process/{process_id}/matrix", response_model=ProcessResponse)
async def update_analysis_matrix(
    process_id: int,
    update: AnalysisMatrixUpdate,
    db: Session = Depends(get_db)
):
    """更新分析矩阵"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    # 更新分析矩阵
    process.analysis_matrix = update.analysis_matrix.model_dump()
    db.commit()
    db.refresh(process)
    
    return process


@router.post("/process/{process_id}/requirements", response_model=ProcessResponse)
async def generate_requirements(
    process_id: int,
    db: Session = Depends(get_db)
):
    """根据分析矩阵生成结构化需求"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    if not process.analysis_matrix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分析矩阵为空，无法生成需求"
        )
    
    try:
        # 演示模式：直接返回已有数据
        if process.status == "demo" and process.structured_requirements:
            process.current_stage = "requirements"
            db.commit()
            db.refresh(process)
            return process

        # 调用AI服务生成需求
        requirements = await ai_service.generate_requirements(process.analysis_matrix)
        
        # 更新流程
        process.structured_requirements = requirements
        process.current_stage = "requirements"
        db.commit()
        db.refresh(process)
        
        # 保存到artifact
        artifact = Artifact(
            process_id=process_id,
            artifact_type="requirement_draft",
            content=requirements,
            meta_data={"generated_at": datetime.now().isoformat()},
            created_by="system"
        )
        db.add(artifact)
        db.commit()
        
        return process
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成需求时发生错误: {str(e)}"
        )


@router.put("/process/{process_id}/requirements", response_model=ProcessResponse)
async def update_requirements(
    process_id: int,
    update: RequirementsUpdate,
    db: Session = Depends(get_db)
):
    """更新结构化需求"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    process.structured_requirements = update.structured_requirements
    db.commit()
    db.refresh(process)
    
    return process


@router.post("/process/{process_id}/cases", response_model=ProcessResponse)
async def generate_user_cases(
    process_id: int,
    db: Session = Depends(get_db)
):
    """根据需求文档生成用户用例"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    if not process.structured_requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结构化需求为空，无法生成用例"
        )
    
    try:
        # 演示模式：直接返回已有数据
        if process.status == "demo" and process.user_cases:
            process.current_stage = "cases"
            db.commit()
            db.refresh(process)
            return process

        # 调用AI服务生成用例
        cases = await ai_service.generate_user_cases(process.structured_requirements)
        
        # 更新流程
        process.user_cases = cases
        process.current_stage = "cases"
        db.commit()
        db.refresh(process)
        
        # 保存到artifact
        artifact = Artifact(
            process_id=process_id,
            artifact_type="case_draft",
            content={"cases": cases},
            meta_data={"generated_at": datetime.now().isoformat()},
            created_by="system"
        )
        db.add(artifact)
        db.commit()
        
        return process
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成用例时发生错误: {str(e)}"
        )


@router.put("/process/{process_id}/cases", response_model=ProcessResponse)
async def update_user_cases(
    process_id: int,
    update: UserCasesUpdate,
    db: Session = Depends(get_db)
):
    """更新用户用例"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    process.user_cases = update.user_cases
    db.commit()
    db.refresh(process)
    
    return process


@router.get("/process/{process_id}/history")
async def get_chat_history(
    process_id: int,
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    artifacts = db.query(Artifact).filter(
        Artifact.process_id == process_id,
        Artifact.artifact_type == "chat_message"
    ).order_by(Artifact.created_at).all()
    
    messages = []
    for artifact in artifacts:
        if artifact.content:
            messages.append({
                "role": artifact.content.get("role"),
                "content": artifact.content.get("content"),
                "timestamp": artifact.created_at.isoformat()
            })
    
    return {"process_id": process_id, "messages": messages}


@router.post("/process/{process_id}/stage")
async def update_stage(
    process_id: int,
    stage: str,
    db: Session = Depends(get_db)
):
    """更新流程阶段"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    valid_stages = ["analysis", "requirements", "cases", "design"]
    if stage not in valid_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的阶段: {stage}，有效值: {valid_stages}"
        )
    
    process.current_stage = stage
    db.commit()
    
    return {"process_id": process_id, "stage": stage, "message": "阶段更新成功"}

@router.post("/process/{process_id}/generate")
async def generate_bpmn(
    process_id: int,
    db: Session = Depends(get_db)
):
    """根据测试案例生成BPMN流程定义"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    if not process.test_cases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="测试案例为空，无法生成BPMN"
        )
    
    try:
        # 演示模式：直接返回已有数据
        if process.status == "demo" and process.bpmn_xml:
            process.current_stage = "design"
            db.commit()
            return {"bpmn_xml": process.bpmn_xml, "message": "BPMN生成成功（演示模式）"}

        # 从test_cases中提取test_cases数组
        test_cases_list = process.test_cases.get("test_cases", []) if isinstance(process.test_cases, dict) else []
        
        if not test_cases_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="测试案例列表为空，无法生成BPMN"
            )
        
        # 调用AI服务生成BPMN
        bpmn_xml = await ai_service.generate_bpmn(
            process.name,
            test_cases_list,
            process.structured_requirements
        )
        
        # 更新流程
        process.bpmn_xml = bpmn_xml
        process.current_stage = "design"
        db.commit()
        db.refresh(process)
        
        # 保存到artifact
        artifact = Artifact(
            process_id=process_id,
            artifact_type="bpmn_draft",
            content={"bpmn_xml": bpmn_xml},
            meta_data={"generated_at": datetime.now().isoformat()},
            created_by="system"
        )
        db.add(artifact)
        db.commit()
        
        return {"bpmn_xml": bpmn_xml, "message": "BPMN生成成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成BPMN时发生错误: {str(e)}"
        )


@router.post("/process/{process_id}/validate-bpmn")
async def validate_bpmn(
    process_id: int,
    db: Session = Depends(get_db)
):
    """
    生成集成测试脚本并自动执行，验证BPMN流程是否正确。
    
    流程：
    1. 从测试案例中提取表单字段、审批节点、审批步骤
    2. 使用 Jinja2 模板生成可执行的 Python 集成测试脚本
    3. 自动运行该脚本（模拟API调用，走完整审批流程）
    4. 解析执行结果，返回脚本内容和测试报告
    """
    from app.services.test_generator import test_generator
    from app.services.test_runner import test_runner
    
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    if not process.bpmn_xml:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BPMN XML为空，请先生成BPMN流程图"
        )
    
    if not process.test_cases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="测试案例为空，无法验证"
        )
    
    # 提取测试案例列表
    test_cases_list = process.test_cases.get("test_cases", []) if isinstance(process.test_cases, dict) else []
    
    if not test_cases_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="测试案例列表为空"
        )
    
    try:
        # 1. 使用 Jinja2 模板生成集成测试脚本
        test_script = test_generator.generate_test_script(
            process_name=process.name,
            test_cases=test_cases_list,
            bpmn_xml=process.bpmn_xml,
            requirements=process.structured_requirements
        )
        
        # 2. 运行测试脚本
        run_result = test_runner.run_test_script(test_script, verbose=False)
        
        # 3. 构建返回结果
        total_cases = run_result['total']
        passed_cases = run_result['passed']
        failed_cases = run_result['failed']
        all_passed = run_result['all_passed']
        
        report_dict = {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "all_passed": all_passed,
            "success_rate": run_result['success_rate'],
            "summary": f"✅ 所有 {total_cases} 个测试案例验证通过！" if all_passed 
                       else f"验证完成：{passed_cases}/{total_cases} 通过，{failed_cases} 个未通过。",
            "test_script": test_script,
            "execution_output": run_result['output'],
            "execution_errors": run_result['stderr'],
            "exit_code": run_result['exit_code'],
            "errors": run_result['errors'],
        }
        
        # 4. 保存到artifact（脚本保存在DB中而非文件系统）
        artifact = Artifact(
            process_id=process_id,
            artifact_type="bpmn_integration_test",
            content=report_dict,
            meta_data={
                "validated_at": datetime.now().isoformat(),
                "all_passed": all_passed,
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "failed_cases": failed_cases,
            },
            created_by="system"
        )
        db.add(artifact)
        db.commit()
        
        return report_dict
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证BPMN时发生错误: {str(e)}"
        )


@router.post("/process/{process_id}/test-cases", response_model=ProcessResponse)
async def generate_test_cases(
    process_id: int,
    db: Session = Depends(get_db)
):
    """根据需求文档生成测试案例"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    if not process.structured_requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结构化需求为空，无法生成测试案例"
        )
    
    try:
        # 演示模式：直接返回已有数据
        if process.status == "demo" and process.test_cases:
            process.current_stage = "test_cases"
            db.commit()
            db.refresh(process)
            return process

        # 调用AI服务生成测试案例
        test_cases = await ai_service.generate_test_cases(
            process.structured_requirements,
            process.analysis_matrix or {}
        )
        
        # 更新流程
        process.test_cases = test_cases
        process.current_stage = "test_cases"
        db.commit()
        db.refresh(process)
        
        # 保存到artifact
        artifact = Artifact(
            process_id=process_id,
            artifact_type="test_case_draft",
            content=test_cases,
            meta_data={"generated_at": datetime.now().isoformat()},
            created_by="system"
        )
        db.add(artifact)
        db.commit()
        
        return process
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试案例时发生错误: {str(e)}"
        )


@router.put("/process/{process_id}/test-cases", response_model=ProcessResponse)
async def update_test_cases(
    process_id: int,
    update: TestCasesUpdate,
    db: Session = Depends(get_db)
):
    """更新测试案例"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    # 更新测试案例
    process.test_cases = {"test_cases": update.test_cases}
    db.commit()
    db.refresh(process)
    
    return process


@router.post("/process/{process_id}/test-cases/feedback", response_model=ProcessResponse)
async def submit_test_case_feedback(
    process_id: int,
    feedback: TestCaseFeedback,
    db: Session = Depends(get_db)
):
    """提交测试案例反馈，AI分析后更新测试案例"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程ID {process_id} 不存在"
        )
    
    if not process.test_cases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="测试案例为空，无法处理反馈"
        )
    
    try:
        # 调用AI服务分析反馈并更新测试案例
        updated_test_cases = await ai_service.process_test_case_feedback(
            current_test_cases=process.test_cases,
            feedback=feedback.feedback,
            requirements=process.structured_requirements or {},
            analysis_matrix=process.analysis_matrix or {}
        )
        
        # 更新流程
        process.test_cases = updated_test_cases
        db.commit()
        db.refresh(process)
        
        # 保存反馈到artifact
        feedback_artifact = Artifact(
            process_id=process_id,
            artifact_type="test_case_feedback",
            content={"feedback": feedback.feedback, "issues": feedback.issues},
            meta_data={"timestamp": datetime.now().isoformat()},
            created_by="user"
        )
        db.add(feedback_artifact)
        
        # 保存更新后的测试案例
        updated_artifact = Artifact(
            process_id=process_id,
            artifact_type="test_case_draft",
            content=updated_test_cases,
            meta_data={
                "generated_at": datetime.now().isoformat(),
                "updated_from_feedback": True
            },
            created_by="system"
        )
        db.add(updated_artifact)
        db.commit()
        
        return process
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理反馈时发生错误: {str(e)}"
        )


@router.post("/demo-init")
async def demo_init(db: Session = Depends(get_db)):
    """
    演示模式初始化：从固定的演示源 process 复制，创建一个新的 demo process。
    返回新 process 的 ID 和分析矩阵（相当于第一步 analyze 的结果）。
    前端后续可逐步调用各阶段 API（会检测 demo 标记直接返回已有数据）。
    """
    import os
    try:
        # 从环境变量获取固定的演示源 process ID
        demo_source_id = os.environ.get("DEMO_PROCESS_ID")
        
        if demo_source_id:
            source = db.query(Process).filter(Process.id == int(demo_source_id)).first()
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"演示源流程 ID={demo_source_id} 不存在，请检查 .env 中的 DEMO_PROCESS_ID 配置"
                )
        else:
            # 未配置固定ID时，回退到查找最近一个完整的 process
            source = db.query(Process).filter(
                Process.bpmn_xml.isnot(None),
                Process.test_cases.isnot(None),
                Process.analysis_matrix.isnot(None),
            ).order_by(Process.updated_at.desc()).first()

            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="没有找到可用的演示数据，请先完成一次完整流程，或在 .env 中配置 DEMO_PROCESS_ID"
                )

        # 获取或创建默认项目
        project_id = get_or_create_default_project(db)

        # 复制为新的 demo process
        demo_process = Process(
            project_id=project_id,
            name=f"演示_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="演示模式 - 基于历史流程数据",
            analysis_matrix=source.analysis_matrix,
            structured_requirements=source.structured_requirements,
            user_cases=source.user_cases,
            test_cases=source.test_cases,
            bpmn_xml=source.bpmn_xml,
            current_stage="analysis",
            status="demo",
            created_by="demo"
        )
        db.add(demo_process)
        db.commit()
        db.refresh(demo_process)

        return {
            "process_id": demo_process.id,
            "message": "🎬 演示模式已启动！这是基于历史成功流程的快速演示，所有AI分析步骤将瞬间完成。",
            "analysis_matrix": demo_process.analysis_matrix,
            "stage": "analysis",
            "suggestions": ["请点击下一步继续演示"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"演示初始化失败: {str(e)}"
        )


# Made with Bob
