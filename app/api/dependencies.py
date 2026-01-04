"""
API依赖注入模块。

定义FastAPI的依赖项，包括数据库会话、服务实例等。
使用LangChain组件替代原有的自定义AI Provider。
"""

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from app.agents.task_agent import TaskAgent
from app.core.database import get_db
from app.core.executor import TaskExecutor
from app.core.scheduler import scheduler
from app.core.task_parser import TaskParser
from app.llm.factory import get_chat_model, get_default_chat_model
from app.services.execution_service import ExecutionService
from app.services.task_service import TaskService
from app.tools.langchain_tools import get_all_tools
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 缓存的LLM实例
_chat_model: BaseChatModel | None = None


def get_llm() -> BaseChatModel:
    """
    获取LangChain Chat模型实例。

    根据配置选择使用OpenAI、Anthropic或本地模型。
    使用单例模式，确保整个应用使用同一个实例。

    Returns:
        LangChain BaseChatModel实例
    """
    global _chat_model
    if _chat_model is None:
        _chat_model = get_chat_model()
        logger.info(f"初始化Chat模型: {type(_chat_model).__name__}")
    return _chat_model


@lru_cache()
def get_task_parser() -> TaskParser:
    """
    获取任务解析器实例。

    使用缓存确保单例。

    Returns:
        任务解析器实例
    """
    llm = get_llm()
    return TaskParser(llm=llm)


@lru_cache()
def get_task_executor() -> TaskExecutor:
    """
    获取任务执行器实例。

    使用缓存确保单例。

    Returns:
        任务执行器实例
    """
    llm = get_llm()
    return TaskExecutor(llm=llm)


@lru_cache()
def get_task_agent() -> TaskAgent:
    """
    获取任务执行Agent实例。

    使用缓存确保单例。

    Returns:
        TaskAgent实例
    """
    llm = get_llm()
    tools = get_all_tools()
    return TaskAgent(llm=llm, tools=tools)


def get_task_service() -> TaskService:
    """
    获取任务服务实例。

    Returns:
        任务服务实例
    """
    task_parser = get_task_parser()
    return TaskService(task_parser=task_parser)


def get_execution_service() -> ExecutionService:
    """
    获取执行服务实例。

    Returns:
        执行服务实例
    """
    return ExecutionService()


async def execute_task_wrapper(task_id: int) -> None:
    """
    任务执行包装函数。

    用于调度器调用，创建数据库会话并执行任务。

    Args:
        task_id: 任务ID
    """
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        executor = get_task_executor()
        await executor.execute_task(task_id=task_id, db=db)
    finally:
        db.close()


# 向后兼容：保留旧的函数名（已废弃）
def get_ai_provider():
    """
    已废弃：请使用 get_llm() 替代。

    此函数保留用于向后兼容，但建议迁移到新的LangChain接口。
    """
    import warnings
    warnings.warn(
        "get_ai_provider() 已废弃，请使用 get_llm() 替代",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_llm()
