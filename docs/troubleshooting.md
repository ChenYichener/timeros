# 故障排查指南

本文档提供常见问题的解决方案。

## 数据库问题

### 问题：数据库连接失败

**症状**：
- 错误信息：`Can't connect to MySQL server`
- 应用启动失败

**解决方案**：
1. 检查MySQL服务是否运行
   ```bash
   # Linux/Mac
   sudo systemctl status mysql
   
   # 或
   mysqladmin ping
   ```

2. 检查`.env`文件中的数据库配置
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`

3. 测试数据库连接
   ```bash
   mysql -h localhost -u root -p
   ```

4. 检查数据库用户权限
   ```sql
   SHOW GRANTS FOR 'your_user'@'localhost';
   ```

### 问题：表不存在错误

**症状**：
- 错误信息：`Table 'timeros.tasks' doesn't exist`

**解决方案**：
1. 初始化数据库
   ```bash
   python scripts/init_db.py
   ```

2. 或使用Alembic迁移
   ```bash
   alembic upgrade head
   ```

## AI服务问题

### 问题：AI API调用失败

**症状**：
- 错误信息：`AIServiceError`或API密钥错误

**解决方案**：
1. 检查API密钥是否正确配置
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   # 或
   echo $ANTHROPIC_API_KEY
   ```

2. 检查网络连接
   ```bash
   curl https://api.openai.com/v1/models
   ```

3. 检查API配额和余额
   - OpenAI: https://platform.openai.com/usage
   - Anthropic: https://console.anthropic.com/

4. 查看详细错误日志
   ```bash
   tail -f logs/app.error.log
   ```

### 问题：本地模型无法连接

**症状**：
- 错误信息：`Connection refused`或`Local model API call failed`

**解决方案**：
1. 检查Ollama服务是否运行
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. 确认模型已下载
   ```bash
   ollama list
   ```

3. 检查`.env`中的配置
   ```env
   # 如果使用自定义端口
   LOCAL_MODEL_BASE_URL=http://localhost:11434
   ```

## 任务执行问题

### 问题：任务执行失败

**症状**：
- 任务状态变为`failed`
- 执行记录中有错误信息

**解决方案**：
1. 查看执行记录详情
   ```bash
   curl http://localhost:8000/api/executions/{execution_id}
   ```

2. 查看应用日志
   ```bash
   tail -f logs/app.error.log
   ```

3. 检查任务参数是否正确
   - 验证任务描述是否完整
   - 检查任务参数格式

4. 手动执行任务进行调试
   ```bash
   curl -X POST http://localhost:8000/api/tasks/{task_id}/execute
   ```

### 问题：任务未按预期执行

**症状**：
- 任务状态为`pending`但未执行
- 执行时间已过但任务未触发

**解决方案**：
1. 检查调度器是否正常运行
   - 查看应用启动日志
   - 确认调度器已加载任务

2. 检查任务调度时间
   ```bash
   curl http://localhost:8000/api/tasks/{task_id}
   ```

3. 检查系统时间
   - 确保系统时间正确
   - 检查时区设置

4. 重启应用重新加载任务
   ```bash
   # 重启应用
   make run
   ```

## 性能问题

### 问题：应用响应慢

**症状**：
- API响应时间长
- 任务执行耗时过长

**解决方案**：
1. 检查数据库连接池配置
   - 增加`MYSQL_POOL_SIZE`
   - 检查数据库性能

2. 检查AI API响应时间
   - 使用更快的模型
   - 优化prompt减少token使用

3. 启用Redis作为任务队列（如需要）
   ```bash
   docker-compose --profile queue up -d
   ```

### 问题：内存占用高

**症状**：
- 应用内存使用持续增长

**解决方案**：
1. 检查是否有内存泄漏
   - 查看日志中的错误信息
   - 使用内存分析工具

2. 限制并发任务数
   - 在配置中添加最大并发数限制

3. 定期重启应用（生产环境）

## 部署问题

### 问题：Docker容器无法启动

**症状**：
- `docker-compose up`失败
- 容器立即退出

**解决方案**：
1. 查看容器日志
   ```bash
   docker-compose logs app
   ```

2. 检查环境变量配置
   - 确认`.env`文件存在且配置正确

3. 检查端口占用
   ```bash
   lsof -i :8000
   lsof -i :3306
   ```

4. 检查Docker资源限制
   - 确保有足够的内存和CPU

### 问题：数据库迁移失败

**症状**：
- `alembic upgrade head`失败
- 迁移冲突

**解决方案**：
1. 查看迁移历史
   ```bash
   alembic history
   ```

2. 检查当前数据库版本
   ```bash
   alembic current
   ```

3. 解决迁移冲突
   - 手动编辑迁移文件
   - 或回滚到上一个版本

4. 备份数据库（生产环境）
   ```bash
   mysqldump -u user -p timeros > backup.sql
   ```

## 日志问题

### 问题：日志文件过大

**症状**：
- `logs/`目录占用大量磁盘空间

**解决方案**：
1. 配置日志轮转（已在代码中实现）
   - 日志文件最大10MB
   - 保留10个备份文件

2. 手动清理旧日志
   ```bash
   find logs/ -name "*.log.*" -mtime +30 -delete
   ```

3. 调整日志级别
   ```env
   LOG_LEVEL=WARNING  # 减少日志输出
   ```

## 获取帮助

如果以上方案无法解决问题：

1. 查看详细日志：`logs/app.error.log`
2. 检查GitHub Issues
3. 提交新的Issue，包含：
   - 错误信息
   - 复现步骤
   - 环境信息（Python版本、操作系统等）
   - 相关日志

