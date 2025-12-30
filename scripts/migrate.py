"""
数据库迁移脚本。

使用Alembic进行数据库迁移管理。

使用方法:
    # 创建迁移
    alembic revision --autogenerate -m "描述"
    
    # 升级数据库
    alembic upgrade head
    
    # 降级数据库
    alembic downgrade -1
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("使用Alembic进行数据库迁移:")
    print("  alembic revision --autogenerate -m '描述'  # 创建迁移")
    print("  alembic upgrade head                        # 升级数据库")
    print("  alembic downgrade -1                       # 降级数据库")
    sys.exit(0)

