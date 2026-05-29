
@echo off
chcp 65001 >nul
title 量子量化平台 Pro - 启动中

echo.
echo ========================================
echo     量子量化平台 Pro - 启动器
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/3] 检查依赖包...
python -c "import pandas, numpy, requests, akshare, streamlit, plotly" >nul 2>&1
if errorlevel 1 (
    echo [提示] 缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [3/3] 启动服务...
echo.

choice /C 12 /M "选择启动模式: [1] Web界面  [2] 命令行"

if errorlevel 2 (
    echo.
    echo 启动命令行版本...
    python main.py
) else (
    echo.
    echo 启动 Web 界面...
    echo.
    echo 浏览器访问: http://localhost:8501
    echo 按 Ctrl+C 停止服务
    echo.
    streamlit run web_app.py --server.headless false
)

pause
