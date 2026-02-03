# MySQL 数据库配置说明

## 1. 安装 MySQL 驱动

在 `requirements.txt` 中添加 MySQL 依赖：

```txt
# 添加到 requirements.txt
pymysql==1.1.0
# 或者
mysqlclient==2.2.0
```

或者使用以下命令安装：

```bash
pip install pymysql
```

## 2. 修改数据库配置

编辑 `backend/app/core/config.py` 文件，将数据库 URL 修改为 MySQL 格式：

```python
# 方式一：使用 pymysql
DATABASE_URL = "mysql+pymysql://root:your_password@localhost:3306/gongchibigwork"

# 方式二：使用 mysqlclient
DATABASE_URL = "mysql://root:your_password@localhost:3306/gongchibigwork"
```

**配置说明**：
- `root` - MySQL 用户名
- `your_password` - MySQL 密码
- `localhost` - MySQL 服务器地址
- `3306` - MySQL 端口号
- `gongchibigwork` - 数据库名称

## 3. 创建数据库

### 方式一：使用 MySQL 客户端

1. 登录 MySQL：
```bash
mysql -u root -p
```

2. 创建数据库：
```sql
CREATE DATABASE gongchibigwork CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 退出 MySQL：
```sql
EXIT;
```

### 方式二：使用提供的 SQL 脚本

执行 `backend/scripts/mysql_create_database.sql` 脚本：
```bash
mysql -u root -p < backend/scripts/mysql_create_database.sql
```

## 4. 创建数据表

### 方式一：自动创建（推荐）

启动应用时，SQLAlchemy 会自动创建表：
```bash
python run.py
```

### 方式二：手动创建表

执行 `backend/scripts/mysql_create_tables.sql` 脚本：
```bash
mysql -u root -p gongchibigwork < backend/scripts/mysql_create_tables.sql
```

## 5. 完整配置示例

### 环境变量文件 (.env)

在 `backend/` 目录下创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/gongchibigwork

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-change-this-in-production

# 其他配置
PROJECT_NAME=GongChiBigWork API
API_V1_STR=/api
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

### config.py 配置

```python
"""
应用配置模块

定义应用的各种配置项，包括数据库连接、JWT 密钥、CORS 设置等
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    
    使用 pydantic-settings 管理配置，支持从环境变量读取
    """
    
    # 项目名称
    PROJECT_NAME: str = "GongChiBigWork API"
    
    # API 前缀
    API_V1_STR: str = "/api"
    
    # 数据库配置（MySQL）
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/gongchibigwork"
    
    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # CORS 配置（允许的前端地址）
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite 开发服务器默认端口
        "http://localhost:3000",  # 其他可能的开发端口
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"  # 支持从 .env 文件读取配置


# 创建全局配置实例
settings = Settings()
```

## 6. 验证配置

1. 确保 MySQL 服务正在运行
2. 创建数据库和表
3. 启动应用：
```bash
python run.py
```

4. 访问健康检查接口：
```
http://localhost:8000/api/health
```

如果返回 `{"status": "ok", "message": "服务运行正常"}`，说明配置成功。

## 常见问题

### Q1: 提示 "ModuleNotFoundError: No module named 'pymysql'"
A: 需要安装 pymysql 驱动：
```bash
pip install pymysql
```

### Q2: 提示 "Access denied for user"
A: 检查用户名和密码是否正确，确保用户有创建数据库的权限。

### Q3: 提示 "Unknown database"
A: 确保已创建 `gongchibigwork` 数据库。

### Q4: 字符集问题
A: 创建数据库时指定 utf8mb4 字符集：
```sql
CREATE DATABASE gongchibigwork CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 7. 从 SQLite 迁移到 MySQL

如果已有 SQLite 数据需要迁移：

1. 导出 SQLite 数据：
```bash
sqlite3 app.db .dump > sqlite_data.sql
```

2. 转换数据格式（可能需要手动调整）
3. 导入到 MySQL：
```bash
mysql -u root -p gongchibigwork < sqlite_data.sql
```

注意：由于 SQLite 和 MySQL 的部分语法差异，可能需要手动调整导出的 SQL 文件。
