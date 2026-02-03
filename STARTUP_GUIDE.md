# 项目启动说明

本项目是一个前后端分离的 Web 应用，包含 Vue 3 前端和 FastAPI 后端，连接到 MySQL 数据库。

## 技术栈

- **前端**: Vue 3 + TypeScript + Element Plus + Vue Router + Pinia
- **后端**: FastAPI + SQLAlchemy + MySQL (PyMySQL)
- **数据库**: MySQL

## 前置条件

1. **Node.js** (>= 20.19.0 或 >= 22.12.0)
2. **Python** (3.11)
3. **MySQL** (5.7 或 8.0)

## 数据库配置

数据库配置位于 `backend/.env` 文件中：

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/gongchibigwork
```

请确保：
- MySQL 服务已启动
- 数据库 `gongchibigwork` 已创建
- 用户名和密码正确

## 安装步骤

### 1. 安装前端依赖

```bash
# 在项目根目录下
npm install
```

### 2. 安装后端依赖

```bash
# 进入 backend 目录
cd backend

# 创建虚拟环境（如果尚未创建）
python -m venv venv

# 激活虚拟环境
# Windows:
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
# 连接到 MySQL 并创建数据库
mysql -u root -p -e "CREATE DATABASE gongchibigwork CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 创建数据表
mysql -u root -p gongchibigwork < scripts\mysql_create_tables.sql
```

或者使用提供的批处理脚本：

```bash
# 双击运行
初始化MySQL数据库.bat
```

## 启动应用

### 1. 启动后端服务

**方法一：使用启动脚本（推荐）**

```powershell
# 在 backend 目录下
python run.py
```

**方法二：直接使用 uvicorn**

```bash
# 进入 backend 目录并激活虚拟环境
cd backend
.\venv\Scripts\activate

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**方法三：使用 PowerShell 脚本**

```powershell
.\backend\启动服务.ps1
```

后端服务将在 http://localhost:8000 启动

API 文档地址：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

**注意：** 数据库密码默认为空，如果需要设置密码，请修改 `backend/app/core/config.py` 中的 `DB_PASSWORD` 或创建 `.env` 文件覆盖配置。

### 2. 启动前端开发服务器

```bash
# 在项目根目录下
npm run dev
```

前端应用将在 http://localhost:5173 启动

## 测试数据库连接

```bash
# 在 backend 目录下
python test_db_connection.py
```

## 项目结构

```
GongChiBigWork/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── auth.py     # 认证相关 API
│   │   │   ├── documents.py # 文档管理 API
│   │   │   └── profile.py   # 个人信息 API
│   │   ├── core/           # 配置和安全
│   │   ├── db/             # 数据库模型和连接
│   │   └── main.py         # FastAPI 应用入口
│   ├── scripts/            # SQL 脚本
│   ├── docs/               # 文档
│   ├── requirements.txt    # Python 依赖
│   ├── .env               # 环境变量配置
│   └── test_db_connection.py # 数据库连接测试
│
├── src/                    # 前端项目
│   ├── services/          # API 服务
│   │   └── api.ts         # API 调用封装
│   ├── views/             # 页面组件
│   │   ├── AboutView.vue  # 登录页面
│   │   ├── TableView.vue  # 文档列表页面
│   │   ├── RichTextEditorView.vue # 富文本编辑器页面
│   │   └── ProfileView.vue # 个人信息页面
│   ├── router/            # 路由配置
│   └── main.ts            # Vue 应用入口
│
└── package.json           # npm 依赖
```

## API 接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

### 文档管理接口
- `GET /api/documents` - 获取文档列表（分页）
- `GET /api/documents/{id}` - 获取单个文档
- `POST /api/documents` - 创建文档
- `PUT /api/documents/{id}` - 更新文档
- `DELETE /api/documents/{id}` - 删除文档

### 个人信息接口
- `GET /api/profile` - 获取个人信息
- `PUT /api/profile` - 更新个人信息

## 常见问题

### 1. 数据库连接失败
- 检查 MySQL 服务是否启动
- 检查数据库用户名和密码是否正确
- 检查数据库是否已创建

### 2. 后端启动失败
- 检查 Python 依赖是否安装完整
- 检查虚拟环境是否激活
- 检查端口 8000 是否被占用

### 3. 前端无法连接后端
- 检查后端服务是否正在运行
- 检查 CORS 配置是否正确
- 检查 API 地址配置是否正确

## 开发建议

1. 使用 `npm run dev` 启动前端开发服务器，支持热重载
2. 使用 `uvicorn app.main:app --reload` 启动后端，支持热重载
3. 使用 MySQL Workbench 或其他 GUI 工具管理数据库
4. 使用 API 文档（/api/docs）测试后端接口
