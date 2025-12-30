"""
数据库配置和会话管理模块。

该模块负责数据库连接的创建、会话管理和连接池配置。
使用SQLAlchemy作为ORM框架，支持MySQL数据库。
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings

# 创建数据库引擎
# 使用连接池管理数据库连接，提高性能和资源利用率
engine = create_engine(
    settings.mysql_url,
    pool_size=settings.MYSQL_POOL_SIZE,
    max_overflow=settings.MYSQL_MAX_OVERFLOW,
    pool_recycle=settings.MYSQL_POOL_RECYCLE,
    echo=settings.DEBUG,  # 开发环境打印SQL语句
)

# 创建会话工厂
# 用于创建数据库会话实例
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
# 所有数据模型都继承自这个基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖注入函数。

    该函数用于FastAPI的依赖注入系统，确保每个请求都有独立的数据库会话，
    并在请求结束后自动关闭会话。

    Yields:
        Session: SQLAlchemy数据库会话对象

    Example:
        ```python
        @app.get("/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            return db.query(Task).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库。

    创建所有数据表。在生产环境中，应该使用数据库迁移工具（如Alembic）
    来管理数据库结构变更。

    Note:
        该方法主要用于开发和测试环境。生产环境应使用迁移工具。
    """
    Base.metadata.create_all(bind=engine)

