# 数据库配置说明

## 数据库信息

根据提供的数据库结构，配置如下：

- **数据库名称**: `gongchibigwork`
- **数据库类型**: MySQL
- **服务器地址**: `localhost`
- **端口**: `3306`
- **用户名**: `root`
- **密码**: `123456`

## 数据表结构

### users 表
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 用户ID（主键） |
| username | VARCHAR(50) | 用户名（唯一） |
| email | VARCHAR(100) | 邮箱地址（唯一） |
| phone | VARCHAR(20) | 手机号 |
| bio | TEXT | 个人简介 |
| hashed_password | VARCHAR(255) | 加密后的密码 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### documents 表
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 文档ID（主键） |
| title | VARCHAR(200) | 文档标题 |
| content | TEXT | 文档内容（HTML格式） |
| creator_id | INT | 创建者用户ID |
| creator_name | VARCHAR(50) | 创建者用户名 |
| created_at | DATETIME | 创建时间 |
| modified_time | DATETIME | 修改时间 |

## 环境配置

后端配置位于 `backend/.env` 文件中：

```env
# 数据库配置
DATABASE_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=gongchibigwork
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/gongchibigwork
```

## 启动步骤

### 1. 确保 MySQL 服务已启动

```bash
# Windows
net start mysql

# 或使用 MySQL Workbench 启动
```

### 2. 创建数据库（如果尚未创建）

```sql
CREATE DATABASE gongchibigwork CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 创建数据表

```bash
# 进入 backend 目录
cd backend

# 激活虚拟环境
.\venv\Scripts\activate

# 运行 SQL 脚本创建表
mysql -u root -p gongchibigwork < scripts\mysql_create_tables.sql
```

### 4. 启动后端服务

```bash
# 在 backend 目录下
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

或使用提供的脚本：

```powershell
.\启动服务.ps1
```

### 5. 启动前端开发服务器

```bash
# 在项目根目录下
npm run dev
```

## API 端点

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

### 文档管理
- `GET /api/documents` - 获取文档列表（分页）
- `GET /api/documents/{id}` - 获取单个文档
- `POST /api/documents` - 创建新文档
- `PUT /api/documents/{id}` - 更新文档
- `DELETE /api/documents/{id}` - 删除文档

### 个人信息
- `GET /api/profile` - 获取当前用户信息
- `PUT /api/profile` - 更新个人信息

## 测试数据库连接

```bash
# 在 backend 目录下
python test_db_connection.py
```

## 前端 API 配置

前端 API 服务文件位于 `src/services/api.ts`，配置如下：

```typescript
const API_BASE_URL = 'http://localhost:8000'
```

确保后端服务启动后，前端才能正常调用 API。
