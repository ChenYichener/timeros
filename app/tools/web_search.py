"""
网络搜索工具模块。

提供网络搜索功能，支持通过SerpAPI或Google Search API搜索信息。
用于研究任务中搜索新闻、文章等内容。
"""

from typing import Any, Dict, List, Optional

import httpx
import requests
from bs4 import BeautifulSoup

from app.utils.exceptions import TaskExecutionError
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class WebSearchTool:
    """
    网络搜索工具类。

    封装网络搜索功能，支持多种搜索API。
    搜索结果用于AI任务执行，如研究任务、分析任务等。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化网络搜索工具。

        Args:
            api_key: SerpAPI密钥，如果为None则从配置中读取
        """
        self.api_key = api_key or settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"

    async def search(
        self,
        query: str,
        num_results: int = 10,
        language: str = "zh",
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        执行网络搜索。

        Args:
            query: 搜索关键词
            num_results: 返回结果数量
            language: 搜索语言，默认为中文
            **kwargs: 其他搜索参数

        Returns:
            搜索结果列表，每个结果包含title、link、snippet等字段

        Raises:
            TaskExecutionError: 当搜索失败时
        """
        if not self.api_key:
            logger.warning("SerpAPI密钥未配置，使用备用搜索方法")
            return await self._fallback_search(query, num_results)

        try:
            logger.debug(f"执行网络搜索: query={query}, num_results={num_results}")

            # 构建请求参数
            params: Dict[str, Any] = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "hl": language,
            }
            params.update(kwargs)

            # 调用SerpAPI
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            # 提取搜索结果
            results = []
            if "organic_results" in data:
                for item in data["organic_results"][:num_results]:
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                        }
                    )

            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results

        except httpx.HTTPError as e:
            error_msg = f"网络搜索API调用失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # 如果API调用失败，尝试使用备用方法
            return await self._fallback_search(query, num_results)
        except Exception as e:
            error_msg = f"网络搜索失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e

    async def _fallback_search(
        self, query: str, num_results: int
    ) -> List[Dict[str, Any]]:
        """
        备用搜索方法。

        当API不可用时，使用简单的网页抓取方法（仅用于演示）。

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        logger.warning("使用备用搜索方法，结果可能不完整")
        # 这里可以实现简单的网页抓取逻辑
        # 为了演示，返回空列表
        return []

    async def search_news(
        self,
        query: str,
        time_range: str = "24h",
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        搜索新闻。

        专门用于搜索新闻内容，支持时间范围过滤。

        Args:
            query: 搜索关键词
            time_range: 时间范围，如"24h"、"7d"、"1m"
            num_results: 返回结果数量

        Returns:
            新闻搜索结果列表
        """
        return await self.search(
            query=query,
            num_results=num_results,
            tbm="nws",  # 新闻搜索
            tbs=f"qdr:{time_range}",  # 时间范围
        )

