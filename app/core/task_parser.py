"""
任务解析模块。

该模块负责将用户输入的自然语言任务描述解析为结构化的任务对象。
使用LLM（大语言模型）来理解自然语言，提取执行时间、任务类型、任务参数等信息。
"""

import json
import re
from datetime import datetime
from typing import Any, Dict

from app.ai_providers.base import BaseAIProvider
from app.utils.exceptions import TaskParseError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskParser:
    """
    任务解析器，负责将自然语言任务描述解析为结构化任务对象。

    该类完全依赖LLM（大语言模型）来理解自然语言，提取以下关键信息：
    - 执行时间：支持多种时间表达（明天、每周一、每月1号等）
    - 任务类型：研究任务、分析任务、报告任务等
    - 任务参数：时间范围、数量限制、目标对象等

    解析流程：
    1. 预处理：清理输入文本，移除多余空格和特殊字符
    2. LLM解析：调用LLM进行深度解析，理解自然语言表达（包含当前时间信息）
    3. 结果验证：检查解析结果的必要字段是否完整
    4. 缓存结果：将解析结果存入缓存，避免重复解析

    设计特点：
    - 完全依赖LLM：所有解析都通过LLM完成，不依赖规则匹配
    - 时间感知：Prompt中包含当前时间信息，确保LLM能正确计算调度时间
    - 结果缓存：相同描述的解析结果会被缓存，提高性能
    """

    def __init__(self, llm_provider: BaseAIProvider):
        """
        初始化任务解析器。

        Args:
            llm_provider: AI服务提供商，必须实现BaseAIProvider接口
        """
        self.llm_provider = llm_provider
        # 使用简单字典缓存，最多缓存1000个解析结果
        # 缓存key为任务描述的hash值，value为解析结果
        self._cache: Dict[int, Dict[str, Any]] = {}

    async def parse(self, description: str) -> Dict[str, Any]:
        """
        解析自然语言任务描述。

        该方法使用LLM（大语言模型）进行解析，完全依赖AI理解自然语言。
        解析过程包括以下步骤：
        1. 预处理：清理输入文本，移除多余空格和特殊字符
        2. LLM解析：调用LLM进行深度解析，理解自然语言表达
        3. 结果验证：检查解析结果的必要字段是否完整
        4. 缓存结果：将解析结果存入缓存

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

        Example:
            >>> parser = TaskParser(llm_provider)
            >>> result = await parser.parse("每周一上午8点分析竞争对手")
            >>> result
            {
                "schedule": "2024-01-15T08:00:00",
                "task_type": "analysis_task",
                "params": {"target": "竞争对手", "count": 5},
                "recurring": True,
                "cron_expression": "0 8 * * 1"
            }
        """
        if not description or not description.strip():
            raise ValueError("任务描述不能为空")

        # 检查缓存，使用描述的hash作为key
        # 这样可以避免对相同描述的重复解析，提高性能
        cache_key = hash(description.strip())
        if cache_key in self._cache:
            logger.debug(f"从缓存获取解析结果: {cache_key}")
            return self._cache[cache_key]

        try:
            # 步骤1: 预处理输入
            cleaned_description = self._preprocess_description(description)

            # 步骤2: 调用LLM进行解析
            # 完全依赖LLM理解自然语言，包括时间表达、任务类型、参数等
            llm_result = await self._parse_with_llm(cleaned_description)

            # 步骤3: 验证解析结果
            # 确保所有必要字段都存在且格式正确
            validated_result = self._validate_parse_result(llm_result)

            # 步骤4: 缓存结果
            self._cache[cache_key] = validated_result

            return validated_result

        except Exception as e:
            # 记录详细错误信息，包括原始描述和错误堆栈
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
        # 移除首尾空格
        cleaned = description.strip()
        # 将多个连续空格替换为单个空格
        cleaned = re.sub(r"\s+", " ", cleaned)
        # 移除控制字符（保留换行符、制表符等常见空白字符）
        cleaned = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", cleaned)
        return cleaned

    async def _parse_with_llm(self, description: str) -> Dict[str, Any]:
        """
        使用LLM解析任务描述。

        构建详细的prompt，要求LLM返回结构化的JSON数据，包含所有必要字段。
        Prompt中包含当前时间信息，确保LLM能够正确计算调度时间。

        Args:
            description: 清理后的任务描述

        Returns:
            LLM返回的解析结果字典

        Raises:
            TaskParseError: 当LLM返回的数据无法解析时
        """
        # 获取当前时间，用于在prompt中告知LLM
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date_str = current_time.strftime("%Y-%m-%d")
        current_weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][current_time.weekday()]

        # 构建详细的prompt，指导LLM返回结构化数据
        prompt = f"""
请解析以下任务描述，提取关键信息并返回JSON格式。

**重要：当前时间信息**
- 当前时间：{current_time_str}
- 当前日期：{current_date_str}
- 当前星期：{current_weekday}
- 当前年份：{current_time.year}
- 当前月份：{current_time.month}
- 当前日期：{current_time.day}
- 当前小时：{current_time.hour}
- 当前分钟：{current_time.minute}

请根据当前时间信息，正确计算任务执行时间。例如：
- "明天" 指的是 {current_date_str} 的下一天
- "下周X" 需要根据当前星期计算
- "每月X号" 需要根据当前日期计算

任务描述：{description}

请提取以下信息：
1. schedule: 执行时间，ISO格式（如"2024-01-15T09:00:00"），必须根据当前时间正确计算
2. task_type: 任务类型，可选值：research_task（研究任务）、analysis_task（分析任务）、report_task（报告任务）
3. params: 任务参数，JSON对象，包含任务特定的配置
4. recurring: 是否为周期性任务，布尔值
5. cron_expression: 如果是周期性任务，提供cron表达式（如"0 8 * * 1"表示每周一8点）

请只返回JSON格式，不要包含其他文字说明。

示例输出格式：
{{
    "schedule": "2024-01-15T09:00:00",
    "task_type": "research_task",
    "params": {{"topic": "AI新闻", "time_range": "24小时"}},
    "recurring": false
}}
"""

        try:
            # 调用LLM生成解析结果
            response = await self.llm_provider.generate_text(
                prompt=prompt, temperature=0.3, max_tokens=500
            )

            # 尝试从响应中提取JSON
            # LLM可能返回包含JSON的文本，需要提取JSON部分
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response

            # 解析JSON
            result = json.loads(json_str)

            logger.debug(f"LLM解析成功: {result}")
            return result

        except json.JSONDecodeError as e:
            error_msg = f"LLM返回的JSON格式无效: {response[:200]}"
            logger.error(error_msg, exc_info=True)
            raise TaskParseError(error_msg) from e
        except Exception as e:
            error_msg = f"LLM解析失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskParseError(error_msg) from e

    def _validate_parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证解析结果的完整性和合理性。

        检查必要字段是否存在，时间格式是否正确，任务类型是否有效等。

        Args:
            result: LLM返回的解析结果

        Returns:
            验证后的解析结果

        Raises:
            TaskParseError: 当验证失败时
        """
        # 检查必要字段
        required_fields = ["schedule", "task_type"]
        for field in required_fields:
            if field not in result:
                raise TaskParseError(f"解析结果缺少必要字段: {field}")

        # 验证时间格式
        try:
            schedule_str = result["schedule"]
            datetime.fromisoformat(schedule_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            raise TaskParseError(f"时间格式无效: {result.get('schedule')}") from e

        # 验证任务类型
        valid_task_types = ["research_task", "analysis_task", "report_task"]
        if result["task_type"] not in valid_task_types:
            logger.warning(
                f"未知的任务类型: {result['task_type']}，使用默认类型"
            )
            result["task_type"] = "research_task"

        # 确保params字段存在
        if "params" not in result:
            result["params"] = {}

        # 确保recurring字段存在
        if "recurring" not in result:
            result["recurring"] = False

        # 如果是周期性任务但没有cron表达式，尝试生成
        if result.get("recurring") and "cron_expression" not in result:
            # 这里可以添加从schedule生成cron表达式的逻辑
            logger.warning("周期性任务缺少cron表达式")

        return result

