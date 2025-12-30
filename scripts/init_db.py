"""
数据库初始化脚本。

该脚本用于创建数据库表结构，主要用于开发和测试环境。
生产环境应该使用数据库迁移工具（如Alembic）来管理数据库结构变更。

使用方法:
    python scripts/init_db.py
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import Base, engine
from app.utils.logger import get_logger, setup_logging

# 初始化日志
setup_logging()
logger = get_logger(__name__)


def init_database():
    """
    初始化数据库，创建所有数据表。

    该函数会创建所有在models.py中定义的数据表。
    如果表已存在，不会重复创建（SQLAlchemy的create_all特性）。
    """
    try:
        logger.info("开始初始化数据库...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    init_database()

