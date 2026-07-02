@echo off
chcp 65001 >nul
echo ========================================
echo   研报智库 - AI研报分析系统
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请安装Python 3.9+
    pause
    exit /b 1
)

:: Create venv if not exists
if not exist "venv" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies
echo [2/3] 安装依赖...
pip install -r requirements.txt -q

:: Check .env
if not exist ".env" (
    echo [提示] 未找到.env文件，复制.env.example...
    copy .env.example .env
    echo [提示] 请编辑.env文件配置DEEPSEEK_API_KEY
    echo.
)

:: Start app
echo [3/3] 启动服务器...
echo.
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo ========================================
python app.py

pause
