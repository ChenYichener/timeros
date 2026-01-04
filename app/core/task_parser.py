"""
任务解析模块。

该模块负责将用户输入的自然语言任务描述解析为结构化的任务对象。
使用LangChain的结构化输出功能来理解自然语言，提取执行时间、任务类型、任务参数等信息。
"""

import re
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.utils.exceptions import TaskParseError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ParsedTask(BaseModel):
    """
    解析后的任务结构。

    使用Pydantic模型定义任务解析结果的结构，
    LangChain会使用这个结构来约束LLM的输出格式。
    """

    schedule: str = Field(
        description="执行时间，ISO格式，如'2024-01-15T09:00:00'。必须根据当前时间正确计算。"
    )
    task_type: Literal["research_task", "analysis_task", "report_task"] = Field(
        description="任务类型：research_task（研究任务）、analysis_task（分析任务）、report_task（报告任务）"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="任务参数，包含任务特定的配置，如主题、时间范围、目标对象等"
    )
    recurring: bool = Field(
        default=False,
        description="是否为周期性任务"
    )
    cron_expression: Optional[str] = Field(
        default=None,
        description="如果是周期性任务，提供cron表达式，如'0 8 * * 1'表示每周一8点"
    )


# 任务解析系统提示词
TASK_PARSE_SYSTEM_PROMPT = """你是一个任务解析助手，负责将自然语言任务描述解析为结构化的任务对象。

**重要：当前时间信息**
- 当前时间：{current_time}
- 当前日期：{current_date}
- 当前星期：{current_weekday}
- 当前年份：{current_year}
- 当前月份：{current_month}
- 当前日期：{current_day}
- 当前小时：{current_hour}
- 当前分钟：{current_minute}

请根据当前时间信息，正确计算任务执行时间。例如：
- "明天" 指的是 {current_date} 的下一天
- "下周X" 需要根据当前星期计算
- "每月X号" 需要根据当前日期计算

任务类型说明：
1. research_task（研究任务）：需要搜索网络信息、收集资料、生成摘要的任务
2. analysis_task（分析任务）：需要分析数据、生成分析报告的任务
3. report_task（报告任务）：需要生成报告并发布到Notion等平台的任务

请仔细分析用户的任务描述，提取所有关键信息。"""


class TaskParser:
    """
    任务解析器，负责将自然语言任务描述解析为结构化任务对象。

    该类使用LangChain的结构化输出功能来理解自然语言，提取以下关键信息：
    - 执行时间：支持多种时间表达（明天、每周一、每月1号等）
    - 任务类型：研究任务、分析任务、报告任务等
    - 任务参数：时间范围、数量限制、目标对象等

    设计特点：
    - 使用LangChain结构化输出：确保输出格式正确
    - 时间感知：Prompt中包含当前时间信息，确保LLM能正确计算调度时间
    - 结果缓存：相同描述的解析结果会被缓存，提高性能
    """

    def __init__(self, llm: BaseChatModel):
        """
        初始化任务解析器。

        Args:
            llm: LangChain Chat模型实例
        """
        self.llm = llm
        # 创建带结构化输出的LLM
        self.structured_llm = llm.with_structured_output(ParsedTask)
        # 使用简单字典缓存，最多缓存1000个解析结果
        self._cache: Dict[int, Dict[str, Any]] = {}

        logger.info("TaskParser初始化完成（使用LangChain结构化输出）")

    def _get_system_prompt(self) -> str:
        """
        获取包含当前时间信息的系统提示词。

        Returns:
            格式化后的系统提示词
        """
        current_time = datetime.now()
        current_weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][
            current_time.weekday()
        ]

        return TASK_PARSE_SYSTEM_PROMPT.format(
            current_time=current_time.strftime("%Y-%m-%d %H:%M:%S"),
            current_date=current_time.strftime("%Y-%m-%d"),
            current_weekday=current_weekday,
            current_year=current_time.year,
            current_month=current_time.month,
            current_day=current_time.day,
            current_hour=current_time.hour,
            current_minute=current_time.minute,
        )

    async def parse(self, description: str) -> Dict[str, Any]:
        """
        解析自然语言任务描述。

        使用LangChain的结构化输出功能，确保返回格式正确的解析结果。

        Args:
            description: 用户输入的自然语言任务描述
                例如："明天上午9点运行此任务：研究过去24小时内的热门AI新闻"

        Returns:
            包含以下字段的字典：
            - schedule (str): 执行时间，ISO格式 "2024-01-15T09:00:00"
            - task_type (str): 任务类型，如 "research_task", "analysis_task"
            - params (dict): 任务参数，包含任务特定的配置
            - recurring (bool): 是否为周期性任务
            - cron_expression (str, optional): 如果是周期性任务，包含cron表达式

        Raises:
            TaskParseError: 当无法解析任务描述时抛出
            ValueError: 当输入描述为空或格式不正确时抛出
        """
        if not description or not description.strip():
            raise ValueError("任务描述不能为空")

        # 检查缓存
        cache_key = hash(description.strip())
        if cache_key in self._cache:
            logger.debug(f"从缓存获取解析结果: {cache_key}")
            return self._cache[cache_key]

        try:
            # 预处理输入
            cleaned_description = self._preprocess_description(description)

            # 构建消息
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"请解析以下任务描述：\n\n{cleaned_description}"),
            ]

            # 调用结构化LLM
            logger.debug(f"开始解析任务描述: {cleaned_description[:100]}...")
            parsed_task: ParsedTask = await self.structured_llm.ainvoke(messages)

            # 转换为字典并验证
            result = parsed_task.model_dump()
            validated_result = self._validate_parse_result(result)

            # 缓存结果
            self._cache[cache_key] = validated_result

            logger.info(f"任务解析成功: task_type={validated_result['task_type']}")
            return validated_result

        except Exception as e:
            logger.error(
                f"解析任务描述失败: {description}",
                extra={"error": str(e), "description": description},
                exc_info=True,
            )
            raise TaskParseError(f"无法解析任务描述: {str(e)}") from e

    def _preprocess_description(self, description: str) -> str:
        """
        预处理任务描述文本。

        清理输入文本，包括：
        - 移除首尾空格
        - 统一多个连续空格为单个空格
        - 移除控制字符（但保留换行符）

        Args:
            description: 原始任务描述

        Returns:
            清理后的任务描述
        """
        cleaned = description.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", cleaned)
        return cleaned

    def _validate_parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证解析结果的完整性和合理性。

        Args:
            result: 解析结果

        Returns:
            验证后的解析结果

        Raises:
            TaskParseError: 当验证失败时
        """
        # 验证时间格式
        try:
            schedule_str = result["schedule"]
            datetime.fromisoformat(schedule_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError, KeyError) as e:
            raise TaskParseError(f"时间格式无效: {result.get('schedule')}") from e

        # 验证任务类型
        valid_task_types = ["research_task", "analysis_task", "report_task"]
        if result.get("task_type") not in valid_task_types:
            logger.warning(
                f"未知的任务类型: {result.get('task_type')}，使用默认类型"
            )
            result["task_type"] = "research_task"

        # 确保params字段存在
        if "params" not in result or result["params"] is None:
            result["params"] = {}

        # 确保recurring字段存在
        if "recurring" not in result:
            result["recurring"] = False

        # 如果是周期性任务但没有cron表达式，记录警告
        if result.get("recurring") and not result.get("cron_expression"):
            logger.warning("周期性任务缺少cron表达式")

        return result

    def clear_cache(self) -> None:
        """清空解析结果缓存。"""
        self._cache.clear()
        logger.debug("解析缓存已清空")
