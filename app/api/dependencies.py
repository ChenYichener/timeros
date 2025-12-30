"""
API依赖注入模块。

定义FastAPI的依赖项，包括数据库会话、服务实例等。
"""

from functools import lru_cache

from sqlalchemy.orm import Session

from app.ai_providers.anthropic_provider import AnthropicProvider
from app.ai_providers.base import BaseAIProvider
from app.ai_providers.local_provider import LocalProvider
from app.ai_providers.openai_provider import OpenAIProvider
from app.core.database import get_db
from app.core.executor import TaskExecutor
from app.core.scheduler import scheduler
from app.core.task_parser import TaskParser
from app.services.execution_service import ExecutionService
from app.services.task_service import TaskService
from config.settings import settings

# 创建全局AI提供商实例
# 根据配置选择使用哪个提供商
_ai_provider: BaseAIProvider | None = None


def get_ai_provider() -> BaseAIProvider:
    """
    获取AI服务提供商实例。

    根据配置选择使用OpenAI、Anthropic或本地模型。
    使用单例模式，确保整个应用使用同一个实例。

    选择逻辑：
    1. 如果明确指定了 AI_PROVIDER 配置，使用指定的提供商
    2. 否则根据可用的API密钥自动选择（优先级：OpenAI > Anthropic > Local）

    Returns:
        AI服务提供商实例

    Raises:
        ValueError: 当指定的提供商无效或缺少必要的API密钥时
    """
    global _ai_provider
    if _ai_provider is None:
        provider_name = settings.AI_PROVIDER

        # 如果明确指定了提供商
        if provider_name:
            provider_name = provider_name.lower().strip()
            if provider_name == "openai":
                if not settings.OPENAI_API_KEY:
                    raise ValueError("已指定使用OpenAI，但未配置OPENAI_API_KEY")
                _ai_provider = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                )
            elif provider_name == "anthropic":
                if not settings.ANTHROPIC_API_KEY:
                    raise ValueError("已指定使用Anthropic，但未配置ANTHROPIC_API_KEY")
                _ai_provider = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
            elif provider_name == "local":
                _ai_provider = LocalProvider()
            else:
                raise ValueError(
                    f"无效的AI提供商: {provider_name}。"
                    f"支持的提供商: openai, anthropic, local"
                )
        else:
            # 自动选择：根据可用的API密钥
            if settings.OPENAI_API_KEY:
                _ai_provider = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                )
            elif settings.ANTHROPIC_API_KEY:
                _ai_provider = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
            else:
                # 默认使用本地模型
                _ai_provider = LocalProvider()

    return _ai_provider


@lru_cache()
def get_task_parser() -> TaskParser:
    """
    获取任务解析器实例。

    使用缓存确保单例。

    Returns:
        任务解析器实例
    """
    ai_provider = get_ai_provider()
    return TaskParser(llm_provider=ai_provider)


@lru_cache()
def get_task_executor() -> TaskExecutor:
    """
    获取任务执行器实例。

    使用缓存确保单例。

    Returns:
        任务执行器实例
    """
    ai_provider = get_ai_provider()
    return TaskExecutor(ai_provider=ai_provider)


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

