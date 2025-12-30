"""
任务调度模块。

该模块负责管理任务的调度和执行，使用APScheduler进行任务调度。
支持一次性任务和周期性任务（通过cron表达式），任务信息持久化到数据库。
"""

from datetime import datetime
from typing import Any, Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from app.core.models import Task
from app.utils.exceptions import SchedulerError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """
    任务调度器类。

    负责管理所有定时任务的调度，包括：
    - 注册新任务到调度器
    - 暂停/恢复任务
    - 删除任务
    - 更新任务调度时间
    - 从数据库加载任务到调度器

    使用APScheduler作为底层调度引擎，支持异步任务执行。
    """

    def __init__(self):
        """
        初始化任务调度器。

        创建APScheduler实例，配置为异步调度器。
        注意：调度器不会在初始化时自动启动，需要调用start()方法。
        """
        self.scheduler = AsyncIOScheduler()
        self._started = False

    def start(self):
        """
        启动任务调度器。

        如果调度器已经启动，则不会重复启动。
        """
        if not self._started:
            self.scheduler.start()
            self._started = True
            logger.info("任务调度器已启动")

    def add_task(
        self,
        task_id: int,
        schedule: datetime,
        cron_expression: Optional[str],
        is_recurring: bool,
        job_func: Callable,
        **kwargs: Any,
    ) -> str:
        """
        添加任务到调度器。

        根据任务类型（一次性或周期性）创建相应的调度任务。

        Args:
            task_id: 任务ID
            schedule: 执行时间
            cron_expression: Cron表达式（仅周期性任务）
            is_recurring: 是否为周期性任务
            job_func: 任务执行函数
            **kwargs: 传递给执行函数的其他参数

        Returns:
            调度器中的任务ID（job_id）

        Raises:
            SchedulerError: 当添加任务失败时
        """
        try:
            if is_recurring and cron_expression:
                # 周期性任务：使用CronTrigger
                trigger = CronTrigger.from_crontab(cron_expression)
                job_id = f"task_{task_id}"
                self.scheduler.add_job(
                    job_func,
                    trigger=trigger,
                    id=job_id,
                    args=[task_id],
                    kwargs=kwargs,
                    replace_existing=True,
                )
                logger.info(
                    f"添加周期性任务: task_id={task_id}, cron={cron_expression}",
                    extra={"task_id": task_id},
                )
            else:
                # 一次性任务：使用DateTrigger
                trigger = DateTrigger(run_date=schedule)
                job_id = f"task_{task_id}"
                self.scheduler.add_job(
                    job_func,
                    trigger=trigger,
                    id=job_id,
                    args=[task_id],
                    kwargs=kwargs,
                    replace_existing=True,
                )
                logger.info(
                    f"添加一次性任务: task_id={task_id}, schedule={schedule}",
                    extra={"task_id": task_id},
                )

            return job_id

        except Exception as e:
            error_msg = f"添加任务到调度器失败: task_id={task_id}, error={str(e)}"
            logger.error(error_msg, extra={"task_id": task_id}, exc_info=True)
            raise SchedulerError(error_msg) from e

    def remove_task(self, task_id: int) -> bool:
        """
        从调度器中移除任务。

        Args:
            task_id: 任务ID

        Returns:
            True表示移除成功，False表示任务不存在

        Raises:
            SchedulerError: 当移除任务失败时
        """
        try:
            job_id = f"task_{task_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"从调度器移除任务: task_id={task_id}", extra={"task_id": task_id})
                return True
            else:
                logger.warning(f"任务不存在于调度器: task_id={task_id}", extra={"task_id": task_id})
                return False

        except Exception as e:
            error_msg = f"从调度器移除任务失败: task_id={task_id}, error={str(e)}"
            logger.error(error_msg, extra={"task_id": task_id}, exc_info=True)
            raise SchedulerError(error_msg) from e

    def pause_task(self, task_id: int) -> bool:
        """
        暂停任务。

        Args:
            task_id: 任务ID

        Returns:
            True表示暂停成功，False表示任务不存在
        """
        try:
            job_id = f"task_{task_id}"
            job = self.scheduler.get_job(job_id)
            if job:
                job.pause()
                logger.info(f"暂停任务: task_id={task_id}", extra={"task_id": task_id})
                return True
            else:
                logger.warning(f"任务不存在: task_id={task_id}", extra={"task_id": task_id})
                return False

        except Exception as e:
            error_msg = f"暂停任务失败: task_id={task_id}, error={str(e)}"
            logger.error(error_msg, extra={"task_id": task_id}, exc_info=True)
            raise SchedulerError(error_msg) from e

    def resume_task(self, task_id: int) -> bool:
        """
        恢复任务。

        Args:
            task_id: 任务ID

        Returns:
            True表示恢复成功，False表示任务不存在
        """
        try:
            job_id = f"task_{task_id}"
            job = self.scheduler.get_job(job_id)
            if job:
                job.resume()
                logger.info(f"恢复任务: task_id={task_id}", extra={"task_id": task_id})
                return True
            else:
                logger.warning(f"任务不存在: task_id={task_id}", extra={"task_id": task_id})
                return False

        except Exception as e:
            error_msg = f"恢复任务失败: task_id={task_id}, error={str(e)}"
            logger.error(error_msg, extra={"task_id": task_id}, exc_info=True)
            raise SchedulerError(error_msg) from e

    def load_tasks_from_db(self, db: Session, executor_func: Callable) -> int:
        """
        从数据库加载所有待执行的任务到调度器。

        在应用启动时调用，确保所有pending状态的任务都被注册到调度器。

        Args:
            db: 数据库会话
            executor_func: 任务执行函数

        Returns:
            加载的任务数量
        """
        try:
            # 查询所有pending状态的任务
            tasks = db.query(Task).filter(
                Task.status == "pending",
                Task.deleted_time.is_(None),
            ).all()

            loaded_count = 0
            for task in tasks:
                try:
                    # 检查任务是否已经过期（一次性任务）
                    if not task.is_recurring and task.schedule < datetime.utcnow():
                        logger.warning(
                            f"任务已过期，跳过: task_id={task.id}",
                            extra={"task_id": task.id},
                        )
                        continue

                    # 添加任务到调度器
                    self.add_task(
                        task_id=task.id,
                        schedule=task.schedule,
                        cron_expression=task.cron_expression,
                        is_recurring=task.is_recurring,
                        job_func=executor_func,
                    )
                    loaded_count += 1

                except Exception as e:
                    logger.error(
                        f"加载任务失败: task_id={task.id}, error={str(e)}",
                        extra={"task_id": task.id},
                        exc_info=True,
                    )
                    continue

            logger.info(f"从数据库加载了 {loaded_count} 个任务到调度器")
            return loaded_count

        except Exception as e:
            error_msg = f"从数据库加载任务失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise SchedulerError(error_msg) from e

    def shutdown(self) -> None:
        """
        关闭调度器。

        在应用关闭时调用，优雅地关闭所有调度任务。
        """
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("任务调度器已关闭")
        except Exception as e:
            logger.error(f"关闭调度器失败: {str(e)}", exc_info=True)


# 创建全局调度器实例
# 整个应用使用同一个调度器实例
scheduler = TaskScheduler()

