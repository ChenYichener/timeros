# 生产环境部署指南

本文档说明如何在生产环境部署TimerOS项目。

## 部署架构

推荐的生产环境架构：

```
┌─────────────┐
│   Nginx     │  (反向代理)
└──────┬──────┘
       │
┌──────▼──────┐
│   Uvicorn   │  (应用服务器)
└──────┬──────┘
       │
┌──────▼──────┐
│   MySQL     │  (数据库)
└─────────────┘
```

## 部署步骤

### 1. 服务器准备

- 操作系统：Ubuntu 20.04+ 或 CentOS 7+
- Python 3.11+
- MySQL 5.7+ 或 8.0+

### 2. 安装依赖

```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv mysql-server nginx

# 或 CentOS
sudo yum install -y python3-pip python3-venv mysql-server nginx
```

### 3. 配置MySQL

```sql
CREATE DATABASE timeros CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'timeros'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON timeros.* TO 'timeros'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 部署应用

```bash
# 克隆项目
git clone <repository-url>
cd timeros

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填写生产环境配置
```

### 5. 配置systemd服务

创建服务文件 `/etc/systemd/system/timeros.service`：

```ini
[Unit]
Description=TimerOS Application
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/timeros
Environment="PATH=/path/to/timeros/venv/bin"
ExecStart=/path/to/timeros/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable timeros
sudo systemctl start timeros
```

### 6. 配置Nginx

创建Nginx配置 `/etc/nginx/sites-available/timeros`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/timeros /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. 配置SSL（可选但推荐）

使用Let's Encrypt配置HTTPS：

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 环境变量配置

生产环境的关键配置：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=timeros
MYSQL_PASSWORD=strong_password
MYSQL_DATABASE=timeros

# AI服务配置
OPENAI_API_KEY=your_production_api_key
# 或
ANTHROPIC_API_KEY=your_production_api_key

# 应用配置
DEBUG=False
LOG_LEVEL=INFO
```

## 监控和日志

### 查看应用日志

```bash
# systemd日志
sudo journalctl -u timeros -f

# 应用日志
tail -f /path/to/timeros/logs/app.log
tail -f /path/to/timeros/logs/app.error.log
```

### 监控建议

- 使用Prometheus + Grafana监控应用指标
- 配置日志收集系统（如ELK）
- 设置告警规则

## 备份策略

### 数据库备份

```bash
# 每日备份脚本
mysqldump -u timeros -p timeros > backup_$(date +%Y%m%d).sql
```

### 配置文件备份

定期备份`.env`和重要配置文件。

## 安全建议

1. **防火墙配置**
   - 只开放必要端口（80, 443）
   - 限制数据库访问（仅本地）

2. **密钥管理**
   - 使用密钥管理服务（如AWS Secrets Manager）
   - 不要在代码中硬编码密钥

3. **定期更新**
   - 定期更新依赖包
   - 关注安全公告

4. **访问控制**
   - 使用强密码
   - 限制管理员访问

## 性能优化

1. **数据库优化**
   - 配置连接池大小
   - 添加适当的索引
   - 定期优化表

2. **应用优化**
   - 使用多进程部署（gunicorn + uvicorn workers）
   - 配置缓存（Redis）

3. **Nginx优化**
   - 启用gzip压缩
   - 配置静态文件缓存

## 故障排查

### 应用无法启动

```bash
# 检查服务状态
sudo systemctl status timeros

# 查看日志
sudo journalctl -u timeros -n 50
```

### 数据库连接问题

```bash
# 测试数据库连接
mysql -u timeros -p -h localhost timeros
```

### 性能问题

- 检查数据库慢查询日志
- 监控系统资源使用情况
- 查看应用日志中的错误信息

## 回滚步骤

如果需要回滚到之前的版本：

```bash
# 停止服务
sudo systemctl stop timeros

# 切换到之前的版本
git checkout <previous-version>

# 重启服务
sudo systemctl start timeros
```

## 维护计划

- **每日**: 检查日志，监控系统状态
- **每周**: 检查备份，更新依赖
- **每月**: 性能优化，安全审计

