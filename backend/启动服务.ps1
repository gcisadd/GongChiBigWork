# PowerShell 启动脚本
# 使用方法：在 PowerShell 中执行 .\启动服务.ps1

# 设置执行策略（如果需要，仅需执行一次）
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 进入后端目录（如果不在 backend 目录）
# cd backend

# 激活虚拟环境
& .\venv\Scripts\Activate.ps1

# 检查虚拟环境是否激活成功
if ($env:VIRTUAL_ENV) {
    Write-Host "虚拟环境已激活: $env:VIRTUAL_ENV" -ForegroundColor Green
    
    # 检查依赖是否已安装
    $packages = pip list | Select-String "fastapi"
    if (-not $packages) {
        Write-Host "正在安装依赖..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
    
    # 启动服务
    Write-Host "正在启动后端服务..." -ForegroundColor Green
    python run.py
} else {
    Write-Host "虚拟环境激活失败！" -ForegroundColor Red
    Write-Host "请手动执行: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}
