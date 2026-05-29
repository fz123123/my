@echo off
chcp 65001 >nul 2>&1
title 自动复制每日分析报告到桌面

echo ======================================================================
echo      自动复制每日分析报告
echo ======================================================================
echo.

echo [1/4] 检查项目目录...
if not exist "c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system" (
    echo [错误] 项目目录不存在！
    pause
    exit /b 1
)
echo [OK] 项目目录存在

echo.
echo [2/4] 检查分析报告...
if not exist "c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system\每日收盘分析报告.md" (
    echo [错误] 分析报告不存在！
    echo 请先运行每日收盘分析脚本生成报告
    pause
    exit /b 1
)
echo [OK] 分析报告存在

echo.
echo [3/4] 复制报告到桌面...
copy /y "c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system\每日收盘分析报告.md" "c:\Users\Administrator\Desktop\每日收盘分析报告.md"

if errorlevel 1 (
    echo [错误] 复制失败！
    pause
    exit /b 1
)

echo [OK] 报告已复制到桌面

echo.
echo [4/4] 完成！
echo.

echo ======================================================================
echo ✅ 操作完成！
echo ======================================================================
echo.
echo 报告位置: c:\Users\Administrator\Desktop\每日收盘分析报告.md
echo.
echo 是否打开桌面查看？
echo.
choice /c YN /m "输入 Y 打开桌面，N 退出: "

if errorlevel 1 (
    explorer.exe "c:\Users\Administrator\Desktop\每日收盘分析报告.md"
)

echo.
pause
