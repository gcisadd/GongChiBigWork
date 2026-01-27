# PowerShell 依赖安装脚本
# 使用方法：在 PowerShell 中执行 .\安装依赖.ps1

Write-Host "正在升级 pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "正在安装依赖包..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "依赖安装成功！" -ForegroundColor Green
    Write-Host "可以使用 'python run.py' 启动服务" -ForegroundColor Green
} else {
    Write-Host "依赖安装失败，请检查错误信息" -ForegroundColor Red
    Write-Host "尝试逐个安装包..." -ForegroundColor Yellow
    
    # 逐个安装包
    $packages = @(
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "alembic==1.12.1",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "email-validator==2.1.0"
    )
    
    foreach ($package in $packages) {
        Write-Host "正在安装: $package" -ForegroundColor Cyan
        pip install $package
        if ($LASTEXITCODE -ne 0) {
            Write-Host "安装失败: $package" -ForegroundColor Red
        }
    }
}
