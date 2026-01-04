"""
工具集成模块。

该模块提供各种工具的封装，包括网络搜索、邮件发送、Notion集成、数据分析等。
支持两种接口：
- 原有的工具类（向后兼容）
- LangChain Tool格式（供LangGraph Agent使用）
"""

# 原有工具类（向后兼容）
from app.tools.data_analyzer import DataAnalyzer
from app.tools.email_client import EmailClient
from app.tools.notion_client import NotionClient
from app.tools.web_search import WebSearchTool

# LangChain工具
from app.tools.langchain_tools import (
    analyze_data,
    create_notion_page,
    generate_data_summary,
    get_all_tools,
    get_analysis_tools,
    get_report_tools,
    get_research_tools,
    search_news,
    send_email,
    send_task_result_email,
    update_notion_page,
    web_search,
)

__all__ = [
    # 原有工具类
    "WebSearchTool",
    "EmailClient",
    "NotionClient",
    "DataAnalyzer",
    # LangChain工具函数
    "web_search",
    "search_news",
    "send_email",
    "send_task_result_email",
    "create_notion_page",
    "update_notion_page",
    "analyze_data",
    "generate_data_summary",
    # 工具获取函数
    "get_all_tools",
    "get_research_tools",
    "get_analysis_tools",
    "get_report_tools",
]