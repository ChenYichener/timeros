# Changelog

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 用户认证和授权
- 任务模板和预设
- 任务依赖关系
- 任务优先级队列

## [1.0.0] - 2024-01-15

### 新增
- 初始版本发布
- 支持自然语言任务描述解析
- 支持一次性任务和周期性任务调度
- 支持多种AI服务提供商（OpenAI、Anthropic、本地模型）
- 集成网络搜索、邮件、Notion等工具
- 完整的任务执行历史追踪
- RESTful API接口
- 完善的文档和开发规范

### 技术栈
- FastAPI作为Web框架
- APScheduler进行任务调度
- MySQL作为数据库
- SQLAlchemy作为ORM

[Unreleased]: https://github.com/yourusername/timeros/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/timeros/releases/tag/v1.0.0

