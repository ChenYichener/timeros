"""
日志配置模块。

该模块提供统一的日志配置和管理功能，支持结构化日志输出（JSON格式），
便于日志收集和分析。日志配置包括控制台输出和文件输出两种方式。
"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config.settings import settings


class JSONFormatter(logging.Formatter):
    """
    JSON格式的日志格式化器。

    将日志记录格式化为JSON格式，便于日志收集系统（如ELK、Loki）解析。
    包含时间戳、日志级别、模块信息、消息内容和上下文信息。
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为JSON字符串。

        Args:
            record: 日志记录对象，包含所有日志信息

        Returns:
            JSON格式的日志字符串
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # 添加额外上下文信息（如果存在）
        # 这些信息通过extra参数传入，如extra={"task_id": 123}
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "execution_id"):
            log_data["execution_id"] = record.execution_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # 如果有异常信息，添加异常堆栈
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    """
    配置应用日志系统。

    根据配置设置日志级别、格式和输出目标。
    开发环境输出到控制台，生产环境同时输出到文件。
    """
    # 获取日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除已有的处理器
    root_logger.handlers.clear()

    # 控制台处理器（开发环境）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # 开发环境使用简单格式，生产环境使用JSON格式
    if settings.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = JSONFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（生产环境）
    if not settings.DEBUG:
        # 创建logs目录
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # 应用日志文件（按日期轮转）
        file_handler = RotatingFileHandler(
            logs_dir / "app.log", maxBytes=10 * 1024 * 1024, backupCount=10
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

        # 错误日志文件（只记录ERROR及以上级别）
        error_handler = RotatingFileHandler(
            logs_dir / "app.error.log", maxBytes=10 * 1024 * 1024, backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器实例。

    推荐使用模块名作为logger名称，这样可以更好地追踪日志来源。

    Args:
        name: 日志记录器名称，通常使用__name__。如果为None，使用调用模块的名称

    Returns:
        配置好的日志记录器实例

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("任务创建成功", extra={"task_id": 123})
    """
    return logging.getLogger(name or __name__)


# 初始化日志配置
setup_logging()

