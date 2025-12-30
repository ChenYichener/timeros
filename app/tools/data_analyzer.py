"""
数据分析工具模块。

提供数据分析功能，用于分析任务执行产生的数据。
支持基本的数据统计、可视化等功能。
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from app.utils.exceptions import TaskExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DataAnalyzer:
    """
    数据分析工具类。

    提供数据分析功能，包括：
    - 数据统计
    - 趋势分析
    - 数据可视化（生成报告）
    """

    def __init__(self):
        """初始化数据分析工具"""
        pass

    def analyze_data(
        self,
        data: List[Dict[str, Any]],
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        分析数据。

        对提供的数据进行统计分析，返回关键指标。

        Args:
            data: 要分析的数据列表，每个元素是一个字典
            metrics: 要计算的指标列表，如果为None则计算所有可能的指标

        Returns:
            包含分析结果的字典

        Raises:
            TaskExecutionError: 当数据分析失败时
        """
        try:
            if not data:
                return {"error": "数据为空"}

            logger.debug(f"开始分析数据，数据量: {len(data)}")

            # 将数据转换为DataFrame
            df = pd.DataFrame(data)

            # 计算基本统计信息
            result: Dict[str, Any] = {
                "total_count": len(df),
                "columns": list(df.columns),
            }

            # 对数值列计算统计信息
            numeric_columns = df.select_dtypes(include=["number"]).columns
            if len(numeric_columns) > 0:
                result["numeric_stats"] = df[numeric_columns].describe().to_dict()

            # 对分类列计算统计信息
            categorical_columns = df.select_dtypes(include=["object"]).columns
            for col in categorical_columns:
                result[f"{col}_value_counts"] = df[col].value_counts().to_dict()

            logger.info(f"数据分析完成，计算了 {len(result)} 个指标")
            return result

        except Exception as e:
            error_msg = f"数据分析失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e

    def generate_summary(
        self,
        data: List[Dict[str, Any]],
        summary_type: str = "basic",
    ) -> str:
        """
        生成数据摘要。

        根据数据生成文本摘要，用于报告生成。

        Args:
            data: 要分析的数据列表
            summary_type: 摘要类型，如"basic"、"detailed"

        Returns:
            数据摘要文本
        """
        try:
            if not data:
                return "数据为空，无法生成摘要"

            df = pd.DataFrame(data)

            summary_parts = []
            summary_parts.append(f"数据总量: {len(df)}")

            # 添加数值列的摘要
            numeric_columns = df.select_dtypes(include=["number"]).columns
            if len(numeric_columns) > 0:
                summary_parts.append("\n数值统计:")
                for col in numeric_columns:
                    summary_parts.append(
                        f"  {col}: 平均值={df[col].mean():.2f}, "
                        f"最大值={df[col].max():.2f}, "
                        f"最小值={df[col].min():.2f}"
                    )

            return "\n".join(summary_parts)

        except Exception as e:
            error_msg = f"生成数据摘要失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e

