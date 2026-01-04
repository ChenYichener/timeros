"""
任务解析器单元测试。

测试任务解析器的各种功能，包括LangChain结构化输出解析等。
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.core.task_parser import TaskParser, ParsedTask


class MockChatModel:
    """模拟LangChain Chat模型，用于测试"""

    def __init__(self):
        self._structured_output = None

    def with_structured_output(self, schema):
        """返回带结构化输出的模拟模型"""
        mock = MagicMock()
        mock.ainvoke = AsyncMock(return_value=ParsedTask(
            schedule="2024-01-15T09:00:00",
            task_type="research_task",
            params={"topic": "AI新闻"},
            recurring=False,
            cron_expression=None,
        ))
        return mock

    async def ainvoke(self, messages):
        """模拟调用"""
        return MagicMock(content="test response")


@pytest.mark.asyncio
async def test_parse_simple_task():
    """测试解析简单任务"""
    parser = TaskParser(llm=MockChatModel())
    result = await parser.parse("明天上午9点研究AI新闻")
    assert result["task_type"] == "research_task"
    assert "schedule" in result
    assert result["schedule"] == "2024-01-15T09:00:00"


@pytest.mark.asyncio
async def test_parse_empty_description():
    """测试解析空描述"""
    parser = TaskParser(llm=MockChatModel())
    with pytest.raises(ValueError):
        await parser.parse("")


@pytest.mark.asyncio
async def test_parse_whitespace_only_description():
    """测试解析仅空格描述"""
    parser = TaskParser(llm=MockChatModel())
    with pytest.raises(ValueError):
        await parser.parse("   ")


def test_preprocess_description():
    """测试描述预处理"""
    parser = TaskParser(llm=MockChatModel())
    cleaned = parser._preprocess_description("  测试  描述  ")
    assert cleaned == "测试 描述"


def test_preprocess_description_with_control_chars():
    """测试预处理移除控制字符"""
    parser = TaskParser(llm=MockChatModel())
    cleaned = parser._preprocess_description("测试\x00\x08描述")
    assert cleaned == "测试描述"


@pytest.mark.asyncio
async def test_parse_caching():
    """测试解析结果缓存"""
    parser = TaskParser(llm=MockChatModel())

    # 第一次解析
    result1 = await parser.parse("明天上午9点研究AI新闻")

    # 第二次解析（应该从缓存获取）
    result2 = await parser.parse("明天上午9点研究AI新闻")

    assert result1 == result2


def test_clear_cache():
    """测试清空缓存"""
    parser = TaskParser(llm=MockChatModel())
    parser._cache[12345] = {"test": "data"}
    parser.clear_cache()
    assert len(parser._cache) == 0


def test_validate_parse_result():
    """测试验证解析结果"""
    parser = TaskParser(llm=MockChatModel())

    # 有效结果
    valid_result = {
        "schedule": "2024-01-15T09:00:00",
        "task_type": "research_task",
        "params": {},
        "recurring": False,
    }
    validated = parser._validate_parse_result(valid_result)
    assert validated["task_type"] == "research_task"


def test_validate_parse_result_invalid_task_type():
    """测试验证无效任务类型"""
    parser = TaskParser(llm=MockChatModel())

    result = {
        "schedule": "2024-01-15T09:00:00",
        "task_type": "invalid_task",
        "params": {},
        "recurring": False,
    }
    validated = parser._validate_parse_result(result)
    # 应该回退到默认类型
    assert validated["task_type"] == "research_task"


def test_parsed_task_model():
    """测试ParsedTask Pydantic模型"""
    task = ParsedTask(
        schedule="2024-01-15T09:00:00",
        task_type="research_task",
        params={"topic": "AI"},
        recurring=True,
        cron_expression="0 9 * * *",
    )
    assert task.schedule == "2024-01-15T09:00:00"
    assert task.task_type == "research_task"
    assert task.recurring is True
    assert task.cron_expression == "0 9 * * *"
