"""
自定义异常类模块。

定义项目特定的异常类型，用于更精确的错误处理和错误信息传递。
所有自定义异常都继承自TimerOSException基类，便于统一处理。
"""


class TimerOSException(Exception):
    """
    基础异常类。

    所有项目自定义异常的基类，便于统一异常处理和错误分类。
    """

    pass


class TaskParseError(TimerOSException):
    """
    任务解析错误。

    当无法解析用户输入的自然语言任务描述时抛出。
    可能的原因包括：描述格式不正确、缺少必要信息、时间表达式无法识别等。
    """

    pass


class TaskExecutionError(TimerOSException):
    """
    任务执行错误。

    当任务执行过程中发生错误时抛出。
    可能的原因包括：AI服务调用失败、工具调用失败、数据格式错误等。
    """

    pass


class AIServiceError(TimerOSException):
    """
    AI服务错误。

    当调用AI服务（OpenAI、Anthropic等）时发生错误时抛出。
    可能的原因包括：API密钥无效、服务不可用、请求超时、配额超限等。
    """

    pass


class SchedulerError(TimerOSException):
    """
    任务调度错误。

    当任务调度过程中发生错误时抛出。
    可能的原因包括：调度器初始化失败、任务注册失败、时间表达式无效等。
    """

    pass


class DatabaseError(TimerOSException):
    """
    数据库操作错误。

    当数据库操作失败时抛出。
    可能的原因包括：连接失败、查询错误、事务回滚等。
    """

    pass

