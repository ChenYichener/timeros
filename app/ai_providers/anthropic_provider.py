"""
Anthropic服务提供商实现模块。

实现Anthropic Claude API的调用接口，支持Claude 3等模型。
使用Anthropic官方Python SDK进行API调用。
"""

from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from anthropic import APIError as AnthropicAPIError

from app.ai_providers.base import BaseAIProvider
from app.utils.exceptions import AIServiceError
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic服务提供商实现类。

    封装Anthropic Claude API调用，提供统一的接口。支持Claude 3等模型。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "claude-3-opus-20240229",
        **kwargs: Any,
    ):
        """
        初始化Anthropic提供商。

        Args:
            api_key: Anthropic API密钥，如果为None则从配置中读取
            default_model: 默认使用的模型名称，如"claude-3-opus-20240229"
            **kwargs: 其他配置参数
        """
        api_key = api_key or settings.ANTHROPIC_API_KEY
        super().__init__(api_key=api_key, **kwargs)
        self.default_model = default_model
        self.client = AsyncAnthropic(api_key=self.api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        执行Anthropic对话补全。

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数（0-1）
            max_tokens: 最大生成token数，Anthropic要求必须提供
            **kwargs: 其他Anthropic API参数

        Returns:
            AI生成的文本响应

        Raises:
            AIServiceError: 当API调用失败时
        """
        try:
            model = model or self.default_model
            # Anthropic要求必须提供max_tokens
            max_tokens = max_tokens or 4096

            logger.debug(
                f"调用Anthropic API，模型: {model}, 消息数: {len(messages)}",
                extra={"model": model, "message_count": len(messages)},
            )

            # 构建请求参数
            request_params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            # 添加其他参数
            request_params.update(kwargs)

            # 调用Anthropic API
            response = await self.client.messages.create(**request_params)

            # 提取响应内容
            # Anthropic的响应格式与OpenAI略有不同
            if not response.content or len(response.content) == 0:
                raise AIServiceError("Anthropic返回空响应")

            # Anthropic返回的是content列表，第一个元素是文本内容
            content = response.content[0].text
            if not content:
                raise AIServiceError("Anthropic返回空文本")

            logger.debug(
                f"Anthropic API调用成功，响应长度: {len(content)}",
                extra={"response_length": len(content)},
            )

            return content

        except AnthropicAPIError as e:
            error_msg = f"Anthropic API调用失败: {str(e)}"
            logger.error(error_msg, extra={"error": str(e)}, exc_info=True)
            raise AIServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"Anthropic服务调用异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise AIServiceError(error_msg) from e

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        使用Anthropic生成文本。

        将prompt包装为消息格式，然后调用chat_completion。

        Args:
            prompt: 输入提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Returns:
            生成的文本内容
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

