"""
应用配置管理模块。

该模块负责加载和管理应用的所有配置项，包括数据库配置、AI服务配置、
应用设置等。配置优先从环境变量读取，支持通过.env文件进行本地配置。
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类。

    使用Pydantic的BaseSettings来管理配置，支持从环境变量和.env文件加载。
    所有配置项都有类型提示和默认值（如适用）。
    """

    # MySQL数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # 数据库连接池配置
    MYSQL_POOL_SIZE: int = 10
    MYSQL_MAX_OVERFLOW: int = 20
    MYSQL_POOL_RECYCLE: int = 3600

    # AI服务配置
    # AI提供商选择：openai, anthropic, local
    # 如果未指定，将根据可用的API密钥自动选择
    AI_PROVIDER: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None  # OpenAI API基础URL，用于自定义API端点（如DeepSeek等）
    ANTHROPIC_API_KEY: Optional[str] = None

    # 应用配置
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # 邮件配置（可选）
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Notion配置（可选）
    NOTION_API_KEY: Optional[str] = None

    # Web搜索配置（可选）
    SERPAPI_KEY: Optional[str] = None

    @property
    def mysql_url(self) -> str:
        """
        构建MySQL数据库连接URL。

        返回格式化的SQLAlchemy数据库连接字符串，包含用户名、密码、
        主机、端口和数据库名，并指定使用utf8mb4字符集。

        Returns:
            MySQL连接URL字符串，格式：
            mysql+pymysql://user:password@host:port/database?charset=utf8mb4
        """
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    class Config:
        """
        Pydantic配置类。

        指定环境变量文件路径和大小写敏感设置。
        """

        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
# 在应用启动时加载，整个应用生命周期内使用同一个实例
settings = Settings()

