"""
FastAPI应用主入口模块。

该模块创建和配置FastAPI应用实例，注册路由、中间件等。
应用启动时初始化数据库连接和任务调度器。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import execute_task_wrapper
from app.api.routes import executions, tasks
from app.core.database import init_db
from app.core.scheduler import scheduler
from app.utils.logger import get_logger, setup_logging

# 初始化日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理。

    在应用启动时执行初始化操作，在应用关闭时执行清理操作。

    Args:
        app: FastAPI应用实例

    Yields:
        None
    """
    # 启动时的初始化操作
    logger.info("应用启动中...")
    try:
        # 启动调度器
        scheduler.start()
        # 初始化数据库（仅开发环境，生产环境使用迁移工具）
        # init_db()
        logger.info("数据库连接已建立")

        # 从数据库加载任务到调度器
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            scheduler.load_tasks_from_db(db=db, executor_func=execute_task_wrapper)
        finally:
            db.close()

    except Exception as e:
        logger.error(f"应用初始化失败: {e}", exc_info=True)
        raise

    logger.info("应用启动完成")

    yield

    # 关闭时的清理操作
    logger.info("应用关闭中...")
    try:
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"关闭调度器失败: {e}", exc_info=True)
    logger.info("应用已关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title="TimerOS API",
    description="AI驱动的智能定时任务系统",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS中间件
# 允许跨域请求，便于前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    根路径接口。

    返回API基本信息，用于健康检查。

    Returns:
        包含API名称和版本的字典
    """
    return {"name": "TimerOS API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """
    健康检查接口。

    用于监控系统检查应用是否正常运行。

    Returns:
        包含健康状态的字典
    """
    return {"status": "healthy"}


# 注册API路由
app.include_router(tasks.router, prefix="/api")
app.include_router(executions.router, prefix="/api")

