"""
AI服务提供商模块（已废弃）。

警告：此模块已被LangChain替代。

请使用以下新模块：
- app.llm.factory: LangChain Chat模型工厂
- app.agents.task_agent: LangGraph Agent实现

此模块保留用于向后兼容，但将在未来版本中移除。
"""

import warnings

# 发出废弃警告
warnings.warn(
    "app.ai_providers 模块已废弃，请使用 app.llm 和 app.agents 模块替代。"
    "此模块将在未来版本中移除。",
    DeprecationWarning,
    stacklevel=2,
)

# 保留原有导出以保持向后兼容
from app.ai_providers.base import BaseAIProvider
from app.ai_providers.openai_provider import OpenAIProvider
from app.ai_providers.anthropic_provider import AnthropicProvider
from app.ai_providers.local_provider import LocalProvider

__all__ = [
    "BaseAIProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalProvider",
]