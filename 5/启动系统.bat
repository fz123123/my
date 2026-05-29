
@echo off
chcp 65001 &gt;nul
title 量子交易系统 v3.0

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║                    正在启动量子交易系统...                        ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0quantum_trading_system"

echo 检查Python环境...
python --version &gt;nul 2&gt;&amp;1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b
)

echo 检查依赖...
python -c "import pandas" &gt;nul 2&gt;&amp;1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo 启动系统...
python main.py

pause

