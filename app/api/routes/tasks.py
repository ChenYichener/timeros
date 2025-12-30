"""
任务相关API路由模块。

提供任务的CRUD操作和手动执行接口。
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import (
    execute_task_wrapper,
    get_db,
    get_execution_service,
    get_task_executor,
    get_task_service,
)
from app.core.executor import TaskExecutor
from app.services.task_service import TaskService
from app.core.schemas import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    """
    创建任务。

    接收自然语言任务描述，解析后创建任务并注册到调度器。

    Args:
        task_data: 任务创建请求数据
        db: 数据库会话
        task_service: 任务服务实例

    Returns:
        创建的任务对象

    Raises:
        HTTPException: 当创建失败时
    """
    try:
        task = await task_service.create_task(
            db=db,
            description=task_data.description,
            executor_func=execute_task_wrapper,
        )
        return task
    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"创建任务失败: {str(e)}")


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: Optional[str] = Query(None, description="任务状态过滤"),
    task_type: Optional[str] = Query(None, description="任务类型过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    """
    查询任务列表。

    支持按状态、类型过滤，支持分页。

    Args:
        status: 任务状态
        task_type: 任务类型
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        task_service: 任务服务实例

    Returns:
        任务列表响应
    """
    tasks, total = task_service.list_tasks(
        db=db,
        status=status,
        task_type=task_type,
        page=page,
        page_size=page_size,
    )

    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    """
    获取任务详情。

    Args:
        task_id: 任务ID
        db: 数据库会话
        task_service: 任务服务实例

    Returns:
        任务对象

    Raises:
        HTTPException: 当任务不存在时
    """
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    """
    更新任务。

    Args:
        task_id: 任务ID
        task_data: 任务更新数据
        db: 数据库会话
        task_service: 任务服务实例

    Returns:
        更新后的任务对象

    Raises:
        HTTPException: 当任务不存在时
    """
    task = task_service.update_task(
        db=db,
        task_id=task_id,
        name=task_data.name,
        description=task_data.description,
        status=task_data.status,
        params=task_data.params,
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    """
    删除任务（软删除）。

    Args:
        task_id: 任务ID
        db: 数据库会话
        task_service: 任务服务实例

    Raises:
        HTTPException: 当任务不存在时
    """
    success = task_service.delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")


@router.post("/{task_id}/execute", status_code=202)
async def execute_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_executor: TaskExecutor = Depends(get_task_executor),
):
    """
    手动执行任务。

    立即执行指定的任务，不等待调度时间。

    Args:
        task_id: 任务ID
        db: 数据库会话
        task_executor: 任务执行器实例

    Returns:
        执行结果

    Raises:
        HTTPException: 当任务不存在或执行失败时
    """
    # 检查任务是否存在
    task_service = get_task_service()
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        result = await task_executor.execute_task(task_id=task_id, db=db)
        return result
    except Exception as e:
        logger.error(f"手动执行任务失败: task_id={task_id}, error={str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"执行任务失败: {str(e)}")

