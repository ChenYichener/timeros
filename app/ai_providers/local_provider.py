"""
本地模型服务提供商实现模块。

实现本地模型（如Ollama）的调用接口，支持在本地运行AI模型，
无需调用外部API，适合对数据隐私要求高的场景。
"""

from typing import Any, Dict, List, Optional

import httpx

from app.ai_providers.base import BaseAIProvider
from app.utils.exceptions import AIServiceError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LocalProvider(BaseAIProvider):
    """
    本地模型服务提供商实现类。

    支持通过HTTP API调用本地运行的AI模型（如Ollama）。
    这种方式不需要外部API密钥，所有数据都在本地处理。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama2",
        **kwargs: Any,
    ):
        """
        初始化本地模型提供商。

        Args:
            api_key: 本地模型通常不需要API密钥，此参数保留以兼容基类
            base_url: 本地模型服务的URL，默认Ollama地址
            default_model: 默认使用的模型名称
            **kwargs: 其他配置参数
        """
        super().__init__(api_key=api_key, **kwargs)
        self.base_url = base_url
        self.default_model = default_model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=300.0)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        执行本地模型对话补全。

        通过HTTP API调用本地运行的AI模型（如Ollama）。

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数（0-1）
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Returns:
            AI生成的文本响应

        Raises:
            AIServiceError: 当API调用失败时
        """
        try:
            model = model or self.default_model

            logger.debug(
                f"调用本地模型API，模型: {model}, 消息数: {len(messages)}",
                extra={"model": model, "message_count": len(messages)},
            )

            # 构建请求体（Ollama格式）
            # 将消息列表转换为Ollama API格式
            prompt = self._messages_to_prompt(messages)

            request_data: Dict[str, Any] = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            }

            if max_tokens:
                request_data["options"]["num_predict"] = max_tokens

            # 调用本地模型API
            response = await self.client.post("/api/generate", json=request_data)
            response.raise_for_status()

            result = response.json()
            content = result.get("response", "")

            if not content:
                raise AIServiceError("本地模型返回空响应")

            logger.debug(
                f"本地模型API调用成功，响应长度: {len(content)}",
                extra={"response_length": len(content)},
            )

            return content

        except httpx.HTTPError as e:
            error_msg = f"本地模型API调用失败: {str(e)}"
            logger.error(error_msg, extra={"error": str(e)}, exc_info=True)
            raise AIServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"本地模型服务调用异常: {str(e)}"
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
        使用本地模型生成文本。

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

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        将消息列表转换为单个提示词字符串。

        本地模型（如Ollama）通常需要单个prompt字符串，而不是消息列表。

        Args:
            messages: 消息列表

        Returns:
            转换后的提示词字符串
        """
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n".join(prompt_parts)

