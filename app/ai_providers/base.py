"""
AI服务提供商基类模块。

定义AI服务提供商的抽象接口，所有具体的AI提供商（OpenAI、Anthropic等）
都必须实现这个接口。这样可以方便地切换不同的AI服务，而不需要修改调用代码。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAIProvider(ABC):
    """
    AI服务提供商基类。

    定义了所有AI提供商必须实现的接口方法。子类需要实现这些方法来提供
    具体的AI服务功能，如文本生成、对话等。

    这个设计模式允许系统支持多个AI服务提供商，用户可以根据需要选择
    使用OpenAI、Anthropic或本地模型。
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any):
        """
        初始化AI服务提供商。

        Args:
            api_key: API密钥，不同提供商可能有不同的密钥格式
            **kwargs: 其他提供商特定的配置参数
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        执行对话补全（Chat Completion）。

        这是AI提供商的核心方法，用于与AI模型进行对话交互。

        Args:
            messages: 消息列表，每个消息包含role（角色）和content（内容）
                格式: [{"role": "user", "content": "..."}, ...]
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数，控制输出的随机性（0-1）
            max_tokens: 最大生成token数，如果为None则不限制
            **kwargs: 其他模型特定的参数

        Returns:
            AI生成的文本响应

        Raises:
            AIServiceError: 当API调用失败时
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        生成文本。

        基于给定的提示词生成文本内容。

        Args:
            prompt: 输入提示词
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数，控制输出的随机性（0-1）
            max_tokens: 最大生成token数，如果为None则不限制
            **kwargs: 其他模型特定的参数

        Returns:
            生成的文本内容

        Raises:
            AIServiceError: 当API调用失败时
        """
        pass

    def validate_config(self) -> bool:
        """
        验证配置是否有效。

        检查API密钥等必要配置是否存在。

        Returns:
            True表示配置有效，False表示配置无效

        Raises:
            AIServiceError: 当配置无效时
        """
        if not self.api_key:
            raise ValueError("API密钥未设置")
        return True

