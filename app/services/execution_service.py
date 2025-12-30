"""
执行服务模块。

提供任务执行记录相关的业务逻辑，包括查询执行历史等操作。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.models import TaskExecution
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionService:
    """
    执行服务类。

    提供任务执行记录管理的业务逻辑。
    """

    def get_execution(self, db: Session, execution_id: int) -> Optional[TaskExecution]:
        """
        获取执行记录。

        Args:
            db: 数据库会话
            execution_id: 执行记录ID

        Returns:
            执行记录对象，如果不存在则返回None
        """
        return db.query(TaskExecution).filter(
            TaskExecution.id == execution_id
        ).first()

    def list_executions(
        self,
        db: Session,
        task_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[TaskExecution], int]:
        """
        查询执行记录列表。

        Args:
            db: 数据库会话
            task_id: 任务ID过滤
            status: 执行状态过滤
            page: 页码
            page_size: 每页数量

        Returns:
            (执行记录列表, 总数量) 元组
        """
        query = db.query(TaskExecution)

        if task_id:
            query = query.filter(TaskExecution.task_id == task_id)
        if status:
            query = query.filter(TaskExecution.status == status)

        total = query.count()
        executions = query.order_by(
            TaskExecution.execution_time.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()

        return executions, total

