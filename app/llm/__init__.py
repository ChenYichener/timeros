"""
LangChain LLM管理模块。

该模块提供统一的LangChain Chat模型工厂，支持多种AI服务提供商。
"""

from app.llm.factory import get_chat_model

__all__ = ["get_chat_model"]
