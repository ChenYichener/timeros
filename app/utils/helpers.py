"""
辅助函数模块。

提供通用的辅助函数，包括时间处理、数据转换、验证等功能。
这些函数可以在多个模块中复用，避免代码重复。
"""

from datetime import datetime
from typing import Any, Dict, Optional


def utc_now() -> datetime:
    """
    获取当前UTC时间。

    Returns:
        当前UTC时间的datetime对象
    """
    return datetime.utcnow()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化datetime对象为字符串。

    Args:
        dt: 要格式化的datetime对象
        format_str: 格式化字符串，默认为 "%Y-%m-%d %H:%M:%S"

    Returns:
        格式化后的时间字符串
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析时间字符串为datetime对象。

    Args:
        dt_str: 时间字符串
        format_str: 格式化字符串，默认为 "%Y-%m-%d %H:%M:%S"

    Returns:
        解析后的datetime对象

    Raises:
        ValueError: 当时间字符串格式不正确时
    """
    return datetime.strptime(dt_str, format_str)


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全地从字典中获取值。

    如果键不存在，返回默认值而不是抛出KeyError。

    Args:
        data: 要查询的字典
        key: 键名
        default: 默认值，当键不存在时返回

    Returns:
        键对应的值，如果键不存在则返回默认值
    """
    return data.get(key, default)


def validate_required_fields(data: Dict[str, Any], required_fields: list[str]) -> None:
    """
    验证字典中是否包含所有必需字段。

    Args:
        data: 要验证的字典
        required_fields: 必需字段列表

    Raises:
        ValueError: 当缺少必需字段时
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")

