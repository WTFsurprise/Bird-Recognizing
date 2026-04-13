@echo off
REM 鸟类识别API启动脚本 (Windows)

set "SCRIPT_DIR=%~dp0"
set "ROOT_REQUIREMENTS=%SCRIPT_DIR%..\requirements.txt"

chcp 65001 >nul
cls

echo.
echo ==========================================
echo 鸟类识别API启动脚本
echo ==========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请确保已安装Python并添加到系统PATH中
    pause
    exit /b 1
)

echo ✅ Python版本:
python --version

REM 检查必要的文件
if not exist "swin_bird_stage2_best.pth" (
    echo.
    echo ❌ 错误: 模型权重文件不存在
    echo 请确保 swin_bird_stage2_best.pth 在当前目录
    pause
    exit /b 1
)

if not exist "class_mapping.json" (
    echo.
    echo ❌ 错误: 类别映射文件不存在
    echo 请确保 class_mapping.json 在当前目录
    pause
    exit /b 1
)

echo ✅ 模型文件检查通过
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 📦 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo 📦 检查和安装依赖...
pip list | find /i "fastapi" >nul
if errorlevel 1 (
    echo 安装依赖中，请稍候...
    if not exist "%ROOT_REQUIREMENTS%" (
        echo ❌ 未找到根目录 requirements.txt
        pause
        exit /b 1
    )
    pip install -q -r "%ROOT_REQUIREMENTS%"
)

echo.
echo ==========================================
echo 🌐 启动API服务器...
echo ==========================================
echo.
echo 📍 API地址: http://localhost:8000
echo 📖 API文档: http://localhost:8000/docs
echo 📖 备用文档: http://localhost:8000/redoc
echo.
echo 按 Ctrl+C 停止服务器
echo.

python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

pause
