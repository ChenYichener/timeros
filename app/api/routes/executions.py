"""
执行记录相关API路由模块。

提供任务执行记录的查询接口。
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_execution_service
from app.core.schemas import TaskExecutionResponse
from app.services.execution_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("", response_model=list[TaskExecutionResponse])
def list_executions(
    task_id: Optional[int] = Query(None, description="任务ID过滤"),
    status: Optional[str] = Query(None, description="执行状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """
    查询执行记录列表。

    支持按任务ID、状态过滤，支持分页。

    Args:
        task_id: 任务ID
        status: 执行状态
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        execution_service: 执行服务实例

    Returns:
        执行记录列表
    """
    executions, total = execution_service.list_executions(
        db=db,
        task_id=task_id,
        status=status,
        page=page,
        page_size=page_size,
    )

    return executions


@router.get("/{execution_id}", response_model=TaskExecutionResponse)
def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """
    获取执行记录详情。

    Args:
        execution_id: 执行记录ID
        db: 数据库会话
        execution_service: 执行服务实例

    Returns:
        执行记录对象

    Raises:
        HTTPException: 当执行记录不存在时
    """
    execution = execution_service.get_execution(db=db, execution_id=execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return execution

