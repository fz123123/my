@echo off
chcp 65001 >nul
title 实时数据更新服务

echo ================================================
echo          实时数据更新服务启动器
echo ================================================
echo.
echo 请选择操作：
echo 1. 单次更新所有项目数据
echo 2. 启动实时监控服务(每5分钟刷新)
echo 3. 启动项目88盯盘服务
echo 4. 启动项目33恐慌盘扫描
echo 5. 退出
echo.

set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" (
    python "%~dp0update_all_realtime_data.py"
    pause
) else if "%choice%"=="2" (
    python "%~dp0update_all_realtime_data.py" -c
    pause
) else if "%choice%"=="3" (
    cd "c:\Users\Administrator\Documents\trae_projects\88"
    python real_time_monitor.py
    pause
) else if "%choice%"=="4" (
    cd "c:\Users\Administrator\Documents\trae_projects\33"
    python realtime_scanner.py
    pause
) else if "%choice%"=="5" (
    exit
) else (
    echo 无效选择，请重新输入
    pause
    start %0
)