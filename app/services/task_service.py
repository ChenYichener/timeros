"""
任务服务模块。

提供任务相关的业务逻辑，包括任务创建、更新、删除、查询等操作。
封装数据库操作和业务规则。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.models import Task
from app.core.scheduler import scheduler
from app.core.task_parser import TaskParser
from app.utils.exceptions import TaskParseError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskService:
    """
    任务服务类。

    提供任务管理的业务逻辑，包括：
    - 创建任务（解析自然语言描述）
    - 更新任务
    - 删除任务（软删除）
    - 查询任务
    - 任务状态管理
    """

    def __init__(self, task_parser: TaskParser):
        """
        初始化任务服务。

        Args:
            task_parser: 任务解析器实例
        """
        self.task_parser = task_parser

    async def create_task(
        self, db: Session, description: str, executor_func
    ) -> Task:
        """
        创建任务。

        解析自然语言描述，创建任务对象，保存到数据库，并注册到调度器。

        Args:
            db: 数据库会话
            description: 自然语言任务描述
            executor_func: 任务执行函数

        Returns:
            创建的任务对象

        Raises:
            TaskParseError: 当解析失败时
        """
        try:
            # 解析任务描述
            parsed = await self.task_parser.parse(description)

            # 创建任务对象
            task = Task(
                name=parsed.get("name", f"任务 - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"),
                description=description,
                task_type=parsed["task_type"],
                schedule=datetime.fromisoformat(parsed["schedule"].replace("Z", "+00:00")),
                cron_expression=parsed.get("cron_expression"),
                is_recurring=parsed.get("recurring", False),
                status="pending",
                params=parsed.get("params", {}),
            )

            # 保存到数据库
            db.add(task)
            db.commit()
            db.refresh(task)

            logger.info(f"任务创建成功: task_id={task.id}", extra={"task_id": task.id})

            # 注册到调度器
            scheduler.add_task(
                task_id=task.id,
                schedule=task.schedule,
                cron_expression=task.cron_expression,
                is_recurring=task.is_recurring,
                job_func=executor_func,
            )

            return task

        except TaskParseError:
            raise
        except Exception as e:
            db.rollback()
            error_msg = f"创建任务失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        """
        获取任务。

        Args:
            db: 数据库会话
            task_id: 任务ID

        Returns:
            任务对象，如果不存在则返回None
        """
        return db.query(Task).filter(
            Task.id == task_id, Task.deleted_time.is_(None)
        ).first()

    def list_tasks(
        self,
        db: Session,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Task], int]:
        """
        查询任务列表。

        Args:
            db: 数据库会话
            status: 任务状态过滤
            task_type: 任务类型过滤
            page: 页码
            page_size: 每页数量

        Returns:
            (任务列表, 总数量) 元组
        """
        query = db.query(Task).filter(Task.deleted_time.is_(None))

        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)

        total = query.count()
        tasks = query.order_by(Task.created_time.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return tasks, total

    def update_task(
        self,
        db: Session,
        task_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> Optional[Task]:
        """
        更新任务。

        Args:
            db: 数据库会话
            task_id: 任务ID
            name: 任务名称
            description: 任务描述
            status: 任务状态
            params: 任务参数

        Returns:
            更新后的任务对象，如果任务不存在则返回None
        """
        task = self.get_task(db, task_id)
        if not task:
            return None

        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
            # 如果状态改变，更新调度器
            if status == "paused":
                scheduler.pause_task(task_id)
            elif status == "pending":
                scheduler.resume_task(task_id)
        if params is not None:
            task.params = params

        task.updated_time = datetime.utcnow()
        db.commit()
        db.refresh(task)

        logger.info(f"任务更新成功: task_id={task_id}", extra={"task_id": task_id})
        return task

    def delete_task(self, db: Session, task_id: int) -> bool:
        """
        删除任务（软删除）。

        Args:
            db: 数据库会话
            task_id: 任务ID

        Returns:
            True表示删除成功，False表示任务不存在
        """
        task = self.get_task(db, task_id)
        if not task:
            return False

        # 软删除
        task.deleted_time = datetime.utcnow()
        task.status = "paused"
        db.commit()

        # 从调度器移除
        scheduler.remove_task(task_id)

        logger.info(f"任务删除成功: task_id={task_id}", extra={"task_id": task_id})
        return True

