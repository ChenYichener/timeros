# REST API 文档

## 基础信息

- Base URL: `http://localhost:8000/api`
- API版本: v1
- 数据格式: JSON

## 接口列表

### 任务管理

#### 创建任务
- **POST** `/tasks`
- 请求体: `{"description": "自然语言任务描述"}`
- 响应: 创建的任务对象

#### 查询任务列表
- **GET** `/tasks?status=pending&page=1&page_size=20`
- 响应: 任务列表

#### 获取任务详情
- **GET** `/tasks/{task_id}`
- 响应: 任务对象

#### 更新任务
- **PUT** `/tasks/{task_id}`
- 请求体: 要更新的字段
- 响应: 更新后的任务对象

#### 删除任务
- **DELETE** `/tasks/{task_id}`
- 响应: 204 No Content

#### 手动执行任务
- **POST** `/tasks/{task_id}/execute`
- 响应: 执行结果

### 执行记录

#### 查询执行记录列表
- **GET** `/executions?task_id=1&page=1&page_size=20`
- 响应: 执行记录列表

#### 获取执行记录详情
- **GET** `/executions/{execution_id}`
- 响应: 执行记录对象

## 错误处理

所有错误响应格式：
```json
{
  "detail": "错误描述"
}
```

常见错误码：
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

