@echo off
chcp 65001 >nul
echo ====================================================
echo  MySQL 数据库初始化脚本
echo  项目名称：GongChiBigWork
echo ====================================================
echo.

set /p db_password="请输入 MySQL root 用户密码: "
echo.

echo [1/4] 正在创建数据库...
mysql -u root -p%db_password% < "%~dp0scripts\mysql_create_database.sql"
if %errorlevel% neq 0 (
    echo 创建数据库失败，请检查 MySQL 服务是否启动或密码是否正确
    pause
    exit /b 1
)
echo.
echo [2/4] 正在创建数据表...
mysql -u root -p%db_password% gongchibigwork < "%~dp0scripts\mysql_create_tables.sql"
if %errorlevel% neq 0 (
    echo 创建数据表失败
    pause
    exit /b 1
)
echo.
echo [3/4] 正在更新配置文件...
echo DATABASE_URL=mysql+pymysql://root:%db_password%@localhost:3306/gongchibigwork > "%~dp0.env"
echo 已生成 .env 配置文件
echo.
echo ====================================================
echo 数据库初始化完成！
echo ====================================================
echo.
echo 后续步骤：
echo 1. 安装 MySQL 驱动：pip install pymysql
echo 2. 启动服务：python run.py
echo 3. 访问 http://localhost:8000/api/health 验证
echo.
pause
