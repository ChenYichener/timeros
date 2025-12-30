# 任务调度模块

## 1. 模块概述

### 1.1 模块职责

任务调度模块负责管理所有定时任务的调度和执行。主要功能包括：

- 注册任务到调度器
- 管理任务的暂停、恢复、删除
- 支持一次性任务和周期性任务
- 从数据库加载任务到调度器

### 1.2 模块位置

- 文件路径：`app/core/scheduler.py`
- 类名：`TaskScheduler`

### 1.3 依赖关系

- `apscheduler`: 任务调度框架
- `app.core.models.Task`: 任务数据模型
- `app.utils.exceptions.SchedulerError`: 自定义异常

## 2. API文档

### 2.1 类/函数列表

- `TaskScheduler`: 任务调度器类
  - `add_task()`: 添加任务到调度器
  - `remove_task()`: 移除任务
  - `pause_task()`: 暂停任务
  - `resume_task()`: 恢复任务
  - `load_tasks_from_db()`: 从数据库加载任务
  - `shutdown()`: 关闭调度器

### 2.2 详细API说明

#### TaskScheduler

任务调度器类，管理所有定时任务的调度。

**方法列表**:

- `add_task(task_id, schedule, cron_expression, is_recurring, job_func, **kwargs) -> str`: 添加任务
- `remove_task(task_id) -> bool`: 移除任务
- `pause_task(task_id) -> bool`: 暂停任务
- `resume_task(task_id) -> bool`: 恢复任务
- `load_tasks_from_db(db, executor_func) -> int`: 从数据库加载任务
- `shutdown()`: 关闭调度器

**示例**:

```python
from app.core.scheduler import scheduler
from app.core.executor import TaskExecutor

# 添加一次性任务
scheduler.add_task(
    task_id=1,
    schedule=datetime(2024, 1, 15, 9, 0, 0),
    cron_expression=None,
    is_recurring=False,
    job_func=execute_task_wrapper
)

# 添加周期性任务
scheduler.add_task(
    task_id=2,
    schedule=datetime(2024, 1, 15, 8, 0, 0),
    cron_expression="0 8 * * 1",  # 每周一8点
    is_recurring=True,
    job_func=execute_task_wrapper
)
```

## 3. 设计说明

### 3.1 设计思路

使用APScheduler作为底层调度引擎：

- **一次性任务**：使用`DateTrigger`，在指定时间执行一次
- **周期性任务**：使用`CronTrigger`，根据cron表达式重复执行
- **任务持久化**：任务信息存储在数据库中，应用重启后自动加载

### 3.2 关键流程

```
任务创建 → 保存到数据库 → 注册到调度器 → 到达执行时间 → 执行任务
```

### 3.3 数据流

1. 任务创建时注册到调度器
2. 调度器根据时间触发执行
3. 执行结果保存到数据库

## 4. 配置说明

### 4.1 环境变量

无需额外环境变量。

### 4.2 配置文件

无需额外配置文件。

## 5. 使用示例

### 5.1 基本使用

```python
from app.core.scheduler import scheduler

# 添加任务
job_id = scheduler.add_task(
    task_id=1,
    schedule=datetime(2024, 1, 15, 9, 0, 0),
    cron_expression=None,
    is_recurring=False,
    job_func=execute_task_wrapper
)

# 暂停任务
scheduler.pause_task(task_id=1)

# 恢复任务
scheduler.resume_task(task_id=1)

# 移除任务
scheduler.remove_task(task_id=1)
```

### 5.2 从数据库加载任务

```python
from app.core.database import SessionLocal
from app.core.scheduler import scheduler

db = SessionLocal()
try:
    count = scheduler.load_tasks_from_db(db=db, executor_func=execute_task_wrapper)
    print(f"加载了 {count} 个任务")
finally:
    db.close()
```

## 6. 常见问题

### Q: 应用重启后任务会丢失吗？

A: 不会。应用启动时会自动从数据库加载所有pending状态的任务。

### Q: 如何修改任务的执行时间？

A: 需要先移除旧任务，然后添加新任务，或更新数据库中的任务信息后重新加载。

### Q: 支持哪些cron表达式格式？

A: 支持标准的cron表达式格式，如"0 8 * * 1"表示每周一8点。

## 7. 更新日志

- 2024-01-15: 初始版本，支持一次性任务和周期性任务调度

