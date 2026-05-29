@echo off
chcp 65001 >nul 2>&1
title 每日收盘分析

echo ======================================================================
echo      每日收盘分析
echo ======================================================================
echo.

echo [1/3] 检查项目目录...
if not exist "c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system" (
    echo [错误] 项目目录不存在！
    echo 请检查路径: c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system
    pause
    exit /b 1
)
echo [OK] 项目目录存在

echo.
echo [2/3] 检查Python脚本...
if not exist "c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system\每日收盘分析_缓存版.py" (
    echo [错误] Python脚本不存在！
    pause
    exit /b 1
)
echo [OK] Python脚本存在

echo.
echo [3/3] 启动分析程序...
echo.

cd /d "c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system"

python 每日收盘分析_缓存版.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败！
    echo 请检查Python环境是否正确安装
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo 分析完成！按任意键退出...
echo ======================================================================
pause
