"""
Notion客户端模块。

提供Notion API集成功能，用于将任务执行结果发布到Notion数据库。
支持创建页面、更新页面等操作。
"""

from typing import Any, Dict, Optional

import httpx

from app.utils.exceptions import TaskExecutionError
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class NotionClient:
    """
    Notion客户端类。

    封装Notion API调用，支持创建和更新Notion页面。
    用于将任务执行结果发布到Notion数据库。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Notion客户端。

        Args:
            api_key: Notion API密钥，如果为None则从配置中读取
        """
        self.api_key = api_key or settings.NOTION_API_KEY
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    async def create_page(
        self,
        database_id: str,
        title: str,
        content: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        在Notion数据库中创建页面。

        Args:
            database_id: Notion数据库ID
            title: 页面标题
            content: 页面内容，包含属性字段
            **kwargs: 其他页面属性

        Returns:
            创建的页面信息

        Raises:
            TaskExecutionError: 当API调用失败时
        """
        if not self.api_key:
            error_msg = "Notion API密钥未配置"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)

        try:
            logger.debug(f"创建Notion页面: title={title}, database_id={database_id}")

            # 构建页面属性
            properties: Dict[str, Any] = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title,
                            }
                        }
                    ]
                }
            }
            properties.update(content)

            # 构建请求体
            request_data: Dict[str, Any] = {
                "parent": {"database_id": database_id},
                "properties": properties,
            }
            request_data.update(kwargs)

            # 调用Notion API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=request_data,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

            logger.info(f"Notion页面创建成功: title={title}")
            return result

        except httpx.HTTPError as e:
            error_msg = f"Notion API调用失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e
        except Exception as e:
            error_msg = f"创建Notion页面失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e

    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        更新Notion页面。

        Args:
            page_id: 页面ID
            properties: 要更新的属性
            **kwargs: 其他更新参数

        Returns:
            更新后的页面信息

        Raises:
            TaskExecutionError: 当API调用失败时
        """
        if not self.api_key:
            error_msg = "Notion API密钥未配置"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)

        try:
            logger.debug(f"更新Notion页面: page_id={page_id}")

            # 构建请求体
            request_data: Dict[str, Any] = {"properties": properties}
            request_data.update(kwargs)

            # 调用Notion API
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    json=request_data,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

            logger.info(f"Notion页面更新成功: page_id={page_id}")
            return result

        except httpx.HTTPError as e:
            error_msg = f"Notion API调用失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e
        except Exception as e:
            error_msg = f"更新Notion页面失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e

