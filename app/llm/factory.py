"""
LangChain Chat模型工厂模块。

该模块提供统一的Chat模型工厂函数，根据配置选择使用不同的AI服务提供商。
支持OpenAI（包括兼容API如DeepSeek）、Anthropic和本地模型（Ollama）。
"""

from functools import lru_cache
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel

from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


def _create_openai_model(
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    创建OpenAI Chat模型实例。

    支持标准OpenAI API以及兼容API（如DeepSeek）。

    Args:
        model: 模型名称，默认为deepseek-chat
        temperature: 温度参数

    Returns:
        ChatOpenAI实例
    """
    from langchain_openai import ChatOpenAI

    model_name = model or "deepseek-chat"

    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        model=model_name,
        temperature=temperature,
    )


def _create_anthropic_model(
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    创建Anthropic Chat模型实例。

    Args:
        model: 模型名称，默认为claude-3-sonnet-20240229
        temperature: 温度参数

    Returns:
        ChatAnthropic实例
    """
    from langchain_anthropic import ChatAnthropic

    model_name = model or "claude-3-sonnet-20240229"

    return ChatAnthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        model=model_name,
        temperature=temperature,
    )


def _create_local_model(
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    创建本地Chat模型实例（使用Ollama）。

    Args:
        model: 模型名称，默认为llama3.2
        temperature: 温度参数

    Returns:
        ChatOllama实例
    """
    from langchain_community.chat_models import ChatOllama

    model_name = model or "llama3.2"

    return ChatOllama(
        model=model_name,
        temperature=temperature,
    )


def get_chat_model(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    获取Chat模型实例。

    根据配置或参数选择使用不同的AI服务提供商。

    选择逻辑：
    1. 如果明确指定了provider参数，使用指定的提供商
    2. 如果配置了AI_PROVIDER，使用配置的提供商
    3. 否则根据可用的API密钥自动选择（优先级：OpenAI > Anthropic > Local）

    Args:
        provider: AI提供商名称（openai, anthropic, local）
        model: 模型名称，如果为None则使用默认模型
        temperature: 温度参数，控制输出的随机性（0-1）

    Returns:
        LangChain BaseChatModel实例

    Raises:
        ValueError: 当指定的提供商无效或缺少必要的API密钥时
    """
    # 确定使用的提供商
    provider_name = provider or settings.AI_PROVIDER

    if provider_name:
        provider_name = provider_name.lower().strip()
    else:
        # 自动选择：根据可用的API密钥
        if settings.OPENAI_API_KEY:
            provider_name = "openai"
        elif settings.ANTHROPIC_API_KEY:
            provider_name = "anthropic"
        else:
            provider_name = "local"

    logger.debug(f"创建Chat模型: provider={provider_name}, model={model}")

    # 创建对应的模型实例
    if provider_name == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("已指定使用OpenAI，但未配置OPENAI_API_KEY")
        return _create_openai_model(model=model, temperature=temperature)

    elif provider_name == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("已指定使用Anthropic，但未配置ANTHROPIC_API_KEY")
        return _create_anthropic_model(model=model, temperature=temperature)

    elif provider_name == "local":
        return _create_local_model(model=model, temperature=temperature)

    else:
        raise ValueError(
            f"无效的AI提供商: {provider_name}。"
            f"支持的提供商: openai, anthropic, local"
        )


@lru_cache()
def get_default_chat_model() -> BaseChatModel:
    """
    获取默认的Chat模型实例（单例）。

    使用缓存确保整个应用使用同一个实例。

    Returns:
        LangChain BaseChatModel实例
    """
    return get_chat_model()
