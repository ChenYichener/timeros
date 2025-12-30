"""
任务解析器单元测试。

测试任务解析器的各种功能，包括规则匹配、LLM解析等。
"""

import pytest
from datetime import datetime

from app.ai_providers.base import BaseAIProvider
from app.core.task_parser import TaskParser


class MockAIProvider(BaseAIProvider):
    """模拟AI提供商，用于测试"""

    async def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs):
        return '{"schedule": "2024-01-15T09:00:00", "task_type": "research_task", "params": {}, "recurring": false}'

    async def generate_text(self, prompt, model=None, temperature=0.7, max_tokens=None, **kwargs):
        return '{"schedule": "2024-01-15T09:00:00", "task_type": "research_task", "params": {}, "recurring": false}'


@pytest.mark.asyncio
async def test_parse_simple_task():
    """测试解析简单任务"""
    parser = TaskParser(llm_provider=MockAIProvider())
    result = await parser.parse("明天上午9点研究AI新闻")
    assert result["task_type"] == "research_task"
    assert "schedule" in result


@pytest.mark.asyncio
async def test_parse_empty_description():
    """测试解析空描述"""
    parser = TaskParser(llm_provider=MockAIProvider())
    with pytest.raises(ValueError):
        await parser.parse("")


@pytest.mark.asyncio
async def test_preprocess_description():
    """测试描述预处理"""
    parser = TaskParser(llm_provider=MockAIProvider())
    cleaned = parser._preprocess_description("  测试  描述  ")
    assert cleaned == "测试 描述"

