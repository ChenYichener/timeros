"""
LangChain工具定义模块。

该模块将现有的工具类封装为LangChain Tool格式，供LangGraph Agent使用。
保留了原有的业务逻辑，只是添加了LangChain兼容的接口。
"""

import json
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from app.tools.data_analyzer import DataAnalyzer
from app.tools.email_client import EmailClient
from app.tools.notion_client import NotionClient
from app.tools.web_search import WebSearchTool
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建工具实例（单例）
_web_search_tool = WebSearchTool()
_email_client = EmailClient()
_notion_client = NotionClient()
_data_analyzer = DataAnalyzer()


@tool
async def web_search(query: str, num_results: int = 10) -> str:
    """
    搜索网络获取最新信息。

    用于研究任务、获取新闻、查找资料等场景。
    返回包含标题、链接和摘要的搜索结果。

    Args:
        query: 搜索关键词，描述你想要查找的内容
        num_results: 返回结果数量，默认10条

    Returns:
        JSON格式的搜索结果列表
    """
    logger.debug(f"执行web_search工具: query={query}, num_results={num_results}")

    results = await _web_search_tool.search(
        query=query,
        num_results=num_results,
    )

    if not results:
        return json.dumps({"message": "未找到相关结果", "results": []}, ensure_ascii=False)

    return json.dumps(
        {
            "message": f"找到 {len(results)} 条结果",
            "results": results,
        },
        ensure_ascii=False,
    )


@tool
async def search_news(query: str, time_range: str = "24h", num_results: int = 10) -> str:
    """
    搜索最新新闻。

    专门用于搜索新闻内容，支持时间范围过滤。
    适用于获取特定主题的最新动态、行业新闻等。

    Args:
        query: 搜索关键词，描述你想要查找的新闻主题
        time_range: 时间范围，可选值："24h"(24小时)、"7d"(7天)、"1m"(1个月)
        num_results: 返回结果数量，默认10条

    Returns:
        JSON格式的新闻搜索结果列表
    """
    logger.debug(f"执行search_news工具: query={query}, time_range={time_range}")

    results = await _web_search_tool.search_news(
        query=query,
        time_range=time_range,
        num_results=num_results,
    )

    if not results:
        return json.dumps({"message": "未找到相关新闻", "results": []}, ensure_ascii=False)

    return json.dumps(
        {
            "message": f"找到 {len(results)} 条新闻",
            "results": results,
        },
        ensure_ascii=False,
    )


@tool
def send_email(
    to_addresses: List[str],
    subject: str,
    body: str,
    is_html: bool = False,
) -> str:
    """
    发送电子邮件。

    用于发送任务结果通知、报告等。支持纯文本和HTML格式。

    Args:
        to_addresses: 收件人邮箱地址列表，如["user@example.com"]
        subject: 邮件主题
        body: 邮件正文内容
        is_html: 是否为HTML格式，默认为False（纯文本）

    Returns:
        发送结果的JSON字符串
    """
    logger.debug(f"执行send_email工具: to={to_addresses}, subject={subject}")

    try:
        success = _email_client.send_email(
            to_addresses=to_addresses,
            subject=subject,
            body=body,
            is_html=is_html,
        )
        return json.dumps(
            {"success": success, "message": "邮件发送成功"},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "message": f"邮件发送失败: {str(e)}"},
            ensure_ascii=False,
        )


@tool
def send_task_result_email(
    to_addresses: List[str],
    task_name: str,
    result: str,
    is_success: bool = True,
) -> str:
    """
    发送任务执行结果邮件。

    格式化任务执行结果并发送邮件通知，自动生成HTML格式的邮件。

    Args:
        to_addresses: 收件人邮箱地址列表
        task_name: 任务名称
        result: 任务执行结果内容
        is_success: 任务是否执行成功，默认True

    Returns:
        发送结果的JSON字符串
    """
    logger.debug(f"执行send_task_result_email工具: task_name={task_name}")

    try:
        success = _email_client.send_task_result(
            to_addresses=to_addresses,
            task_name=task_name,
            result=result,
            is_success=is_success,
        )
        return json.dumps(
            {"success": success, "message": "任务结果邮件发送成功"},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "message": f"发送失败: {str(e)}"},
            ensure_ascii=False,
        )


@tool
async def create_notion_page(
    database_id: str,
    title: str,
    content: str,
) -> str:
    """
    在Notion数据库中创建页面。

    用于将任务执行结果、报告等发布到Notion。

    Args:
        database_id: Notion数据库ID
        title: 页面标题
        content: 页面内容（纯文本，会自动转换为Notion格式）

    Returns:
        创建结果的JSON字符串，包含页面ID
    """
    logger.debug(f"执行create_notion_page工具: title={title}")

    try:
        # 将纯文本内容转换为Notion属性格式
        notion_content = {
            "内容": {
                "rich_text": [
                    {
                        "text": {
                            "content": content[:2000],  # Notion限制
                        }
                    }
                ]
            }
        }

        result = await _notion_client.create_page(
            database_id=database_id,
            title=title,
            content=notion_content,
        )

        return json.dumps(
            {
                "success": True,
                "message": "Notion页面创建成功",
                "page_id": result.get("id"),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "message": f"创建失败: {str(e)}"},
            ensure_ascii=False,
        )


@tool
async def update_notion_page(
    page_id: str,
    content: str,
) -> str:
    """
    更新Notion页面内容。

    用于更新已存在的Notion页面。

    Args:
        page_id: Notion页面ID
        content: 新的页面内容

    Returns:
        更新结果的JSON字符串
    """
    logger.debug(f"执行update_notion_page工具: page_id={page_id}")

    try:
        properties = {
            "内容": {
                "rich_text": [
                    {
                        "text": {
                            "content": content[:2000],
                        }
                    }
                ]
            }
        }

        result = await _notion_client.update_page(
            page_id=page_id,
            properties=properties,
        )

        return json.dumps(
            {
                "success": True,
                "message": "Notion页面更新成功",
                "page_id": result.get("id"),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "message": f"更新失败: {str(e)}"},
            ensure_ascii=False,
        )


@tool
def analyze_data(data_json: str) -> str:
    """
    分析数据并返回统计结果。

    对提供的JSON格式数据进行统计分析，返回关键指标。
    支持数值统计、分类统计等功能。

    Args:
        data_json: JSON格式的数据数组，如'[{"name": "A", "value": 100}, ...]'

    Returns:
        JSON格式的分析结果
    """
    logger.debug("执行analyze_data工具")

    try:
        data = json.loads(data_json)
        if not isinstance(data, list):
            return json.dumps(
                {"success": False, "message": "数据格式错误，需要JSON数组"},
                ensure_ascii=False,
            )

        result = _data_analyzer.analyze_data(data)
        return json.dumps(
            {"success": True, "analysis": result},
            ensure_ascii=False,
        )
    except json.JSONDecodeError:
        return json.dumps(
            {"success": False, "message": "JSON解析失败，请检查数据格式"},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "message": f"分析失败: {str(e)}"},
            ensure_ascii=False,
        )


@tool
def generate_data_summary(data_json: str, summary_type: str = "basic") -> str:
    """
    生成数据摘要报告。

    根据提供的数据生成文本摘要，适用于报告生成场景。

    Args:
        data_json: JSON格式的数据数组
        summary_type: 摘要类型，"basic"为基本摘要，"detailed"为详细摘要

    Returns:
        数据摘要文本
    """
    logger.debug(f"执行generate_data_summary工具: summary_type={summary_type}")

    try:
        data = json.loads(data_json)
        if not isinstance(data, list):
            return json.dumps(
                {"success": False, "message": "数据格式错误，需要JSON数组"},
                ensure_ascii=False,
            )

        summary = _data_analyzer.generate_summary(data, summary_type)
        return json.dumps(
            {"success": True, "summary": summary},
            ensure_ascii=False,
        )
    except json.JSONDecodeError:
        return json.dumps(
            {"success": False, "message": "JSON解析失败，请检查数据格式"},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "message": f"生成摘要失败: {str(e)}"},
            ensure_ascii=False,
        )


def get_all_tools() -> list:
    """
    获取所有可用的LangChain工具列表。

    Returns:
        LangChain Tool列表
    """
    return [
        web_search,
        search_news,
        send_email,
        send_task_result_email,
        create_notion_page,
        update_notion_page,
        analyze_data,
        generate_data_summary,
    ]


def get_research_tools() -> list:
    """
    获取研究任务相关的工具列表。

    Returns:
        LangChain Tool列表
    """
    return [
        web_search,
        search_news,
        send_email,
        send_task_result_email,
    ]


def get_analysis_tools() -> list:
    """
    获取分析任务相关的工具列表。

    Returns:
        LangChain Tool列表
    """
    return [
        analyze_data,
        generate_data_summary,
        send_email,
    ]


def get_report_tools() -> list:
    """
    获取报告任务相关的工具列表。

    Returns:
        LangChain Tool列表
    """
    return [
        web_search,
        search_news,
        analyze_data,
        generate_data_summary,
        create_notion_page,
        update_notion_page,
        send_email,
    ]
