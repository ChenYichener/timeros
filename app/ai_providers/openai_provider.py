"""
OpenAI服务提供商实现模块。

实现OpenAI API的调用接口，支持GPT-4、GPT-3.5等模型。
使用OpenAI官方Python SDK进行API调用。
"""

from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from openai import APIError as OpenAIAPIError

from app.ai_providers.base import BaseAIProvider
from app.utils.exceptions import AIServiceError
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI服务提供商实现类。

    封装OpenAI API调用，提供统一的接口。支持GPT-4、GPT-3.5等模型。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "deepseek-chat",
        **kwargs: Any,
    ):
        """
        初始化OpenAI提供商。

        Args:
            api_key: OpenAI API密钥，如果为None则从配置中读取
            default_model: 默认使用的模型名称，如"gpt-4"、"gpt-3.5-turbo"
            **kwargs: 其他配置参数
        """
        api_key = api_key or settings.OPENAI_API_KEY
        super().__init__(api_key=api_key, **kwargs)
        self.default_model = default_model
        # 如果配置了自定义base_url（如DeepSeek等），使用自定义URL
        base_url = settings.OPENAI_BASE_URL or kwargs.get("base_url")
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        执行OpenAI对话补全。

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数（0-1）
            max_tokens: 最大生成token数
            **kwargs: 其他OpenAI API参数

        Returns:
            AI生成的文本响应

        Raises:
            AIServiceError: 当API调用失败时
        """
        try:
            model = model or self.default_model
            logger.debug(
                f"调用OpenAI API，模型: {model}, 消息数: {len(messages)}",
                extra={"model": model, "message_count": len(messages)},
            )

            # 构建请求参数
            request_params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # 添加其他参数
            request_params.update(kwargs)

            # 调用OpenAI API
            response = await self.client.chat.completions.create(**request_params)

            # 提取响应内容
            content = response.choices[0].message.content
            if not content:
                raise AIServiceError("OpenAI返回空响应")

            logger.debug(
                f"OpenAI API调用成功，响应长度: {len(content)}",
                extra={"response_length": len(content)},
            )

            return content

        except OpenAIAPIError as e:
            error_msg = f"OpenAI API调用失败: {str(e)}"
            logger.error(error_msg, extra={"error": str(e)}, exc_info=True)
            raise AIServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"OpenAI服务调用异常: {str(e)}"
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
        使用OpenAI生成文本。

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

