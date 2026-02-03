# 后端服务说明

这是 GongChiBigWork 项目的后端服务，使用 Python + FastAPI 构建。

## 技术栈

- **框架**：FastAPI 0.104.1
- **数据库**：SQLite（开发环境）/ PostgreSQL（生产环境）
- **ORM**：SQLAlchemy 2.0
- **认证**：JWT Token
- **密码加密**：bcrypt

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由模块
│   │   ├── auth.py       # 认证相关接口（登录、注册）
│   │   ├── documents.py  # 文档管理接口（CRUD）
│   │   └── profile.py    # 个人信息接口
│   ├── core/             # 核心配置模块
│   │   ├── config.py     # 应用配置
│   │   └── security.py   # 安全工具（密码加密、JWT）
│   ├── db/               # 数据库模块
│   │   ├── database.py   # 数据库连接配置
│   │   └── models.py     # 数据模型定义
│   └── main.py           # FastAPI 应用入口
├── requirements.txt       # Python 依赖包
├── run.py                # 启动脚本
└── README.md             # 本文件
```

## 安装和运行

### 1. 安装 Python 依赖

```bash
# 进入后端目录
cd backend

# 安装依赖（推荐使用虚拟环境）
python -m venv venv

# Windows 激活虚拟环境（根据使用的终端选择）
# 方式一：CMD 命令提示符
venv\Scripts\activate.bat

# 方式二：PowerShell（如果报错，先执行：Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser）
venv\Scripts\Activate.ps1

# 方式三：Git Bash（注意：使用正斜杠 /，不是反斜杠 \）
source venv/Scripts/activate

# Linux/Mac 激活虚拟环境
source venv/bin/activate

# 安装依赖包
# 方式一：直接安装（推荐先升级 pip）
python -m pip install --upgrade pip
pip install -r requirements.txt

# 方式二：使用安装脚本（如果方式一失败）
.\安装依赖.ps1
```

### 2. 启动服务

#### PowerShell 完整命令（推荐）

```powershell
# 1. 进入后端目录
cd backend

# 2. 如果首次使用 PowerShell，先设置执行策略（仅需执行一次）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 4. 安装依赖（如果还未安装）
pip install -r requirements.txt

# 5. 启动服务
python run.py
```

或者使用启动脚本：

```powershell
cd backend
.\启动服务.ps1
```

#### 其他方式

```bash
# 方式一：使用启动脚本
python run.py

# 方式二：直接使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，访问：
- **API 文档**：http://localhost:8000/api/docs
- **ReDoc 文档**：http://localhost:8000/api/redoc
- **健康检查**：http://localhost:8000/api/health

### 验证服务是否启动成功

#### 方法一：查看终端输出
启动成功后，终端会显示：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

#### 方法二：访问健康检查接口（推荐）
在浏览器中访问：http://localhost:8000/api/health

成功响应示例：
```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```

#### 方法三：访问 API 文档
在浏览器中访问：http://localhost:8000/api/docs

如果能看到 Swagger UI 界面，说明服务启动成功。

#### 方法四：使用 PowerShell 测试
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

更多验证方法请查看 `验证服务.md` 文件。

## API 接口说明

### 认证接口 (`/api/auth`)

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

### 文档管理接口 (`/api/documents`)

- `GET /api/documents` - 获取文档列表（支持分页）
- `GET /api/documents/{id}` - 获取文档详情
- `POST /api/documents` - 创建新文档
- `PUT /api/documents/{id}` - 更新文档
- `DELETE /api/documents/{id}` - 删除文档

### 个人信息接口 (`/api/profile`)

- `GET /api/profile` - 获取个人信息
- `PUT /api/profile` - 更新个人信息

## 认证方式

所有需要认证的接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer <your_token>
```

登录成功后，服务器会返回 `access_token`，前端需要保存并在后续请求中使用。

## 数据库

### 默认使用 SQLite

默认使用 SQLite 数据库，数据库文件 `app.db` 会在首次运行时自动创建。

### 初始化数据库

数据库表会在应用启动时自动创建（见 `app/main.py`）。

### 切换到 MySQL

如需使用 MySQL 数据库，请按照以下步骤操作：

#### 步骤 1：安装 MySQL 驱动

```bash
pip install pymysql
```

或者更新依赖：
```bash
pip install -r requirements.txt
```

#### 步骤 2：创建 MySQL 数据库

执行 SQL 脚本创建数据库：

```bash
# 方式一：登录 MySQL 后执行
mysql -u root -p
CREATE DATABASE gongchibigwork CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 方式二：直接执行 SQL 文件
mysql -u root -p < scripts/mysql_create_database.sql
```

#### 步骤 3：创建数据表

执行建表脚本：

```bash
mysql -u root -p gongchibigwork < scripts/mysql_create_tables.sql
```

或者启动应用后自动创建表（推荐）。

#### 步骤 4：修改数据库配置

编辑 `app/core/config.py` 中的 `DATABASE_URL`：

```python
# MySQL 连接示例
DATABASE_URL = "mysql+pymysql://root:your_password@localhost:3306/gongchibigwork"
```

或者创建 `.env` 文件配置：

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/gongchibigwork
```

详细配置说明请查看 `docs/MYSQL_CONFIG.md` 文件。

## 配置说明

配置文件位于 `app/core/config.py`，主要配置项：

- `SECRET_KEY`：JWT 密钥（**生产环境请务必修改**）
- `CORS_ORIGINS`：允许的前端地址列表
- `ACCESS_TOKEN_EXPIRE_MINUTES`：Token 过期时间（分钟）

## 开发建议

1. **生产环境配置**：
   - 修改 `SECRET_KEY` 为随机字符串
   - 使用 PostgreSQL 替代 SQLite
   - 关闭 SQL 日志（`echo=False`）
   - 配置 HTTPS

2. **数据库迁移**：
   - 当前使用自动创建表的方式
   - 生产环境建议使用 Alembic 进行数据库迁移

3. **错误处理**：
   - 当前已实现基础错误处理
   - 可根据需要添加更详细的错误日志

## 常见问题

### 1. 端口被占用

如果 8000 端口被占用，可以修改 `run.py` 中的端口号。

### 2. 跨域问题

确保前端地址已添加到 `CORS_ORIGINS` 配置中。

### 3. 数据库文件位置

SQLite 数据库文件 `app.db` 会创建在 `backend` 目录下。
