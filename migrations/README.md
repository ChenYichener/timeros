# 数据库迁移

本目录包含Alembic数据库迁移文件。

## 使用方法

### 创建迁移

```bash
# 自动生成迁移（推荐）
alembic revision --autogenerate -m "描述信息"

# 手动创建空迁移
alembic revision -m "描述信息"
```

### 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision>

# 降级一个版本
alembic downgrade -1

# 降级到指定版本
alembic downgrade <revision>
```

### 查看迁移历史

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

## 注意事项

- 生产环境必须使用Alembic进行数据库迁移
- 不要手动修改已应用的迁移文件
- 迁移文件应该包含可逆的upgrade和downgrade操作

