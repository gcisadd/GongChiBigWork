"""
后端服务启动脚本

使用 uvicorn 启动 FastAPI 应用
"""

import uvicorn

if __name__ == "__main__":
    # 启动开发服务器
    # host: 监听地址，0.0.0.0 表示监听所有网络接口
    # port: 监听端口，8000 是 FastAPI 的默认端口
    # reload: 开发模式，代码修改后自动重启
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发环境启用热重载
    )
