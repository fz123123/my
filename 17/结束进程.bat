@echo off
echo ========================================
echo 结束 PowerShell 进程
echo ========================================
echo.
echo 正在运行的 PowerShell 进程:
tasklist | findstr /i "powershell"
echo.
echo ========================================
echo 选择操作:
echo 1. 结束所有 PowerShell 进程
echo 2. 结束内存占用最大的进程
echo 3. 退出
echo ========================================
set /p choice="请输入选项 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 正在结束所有 PowerShell 进程...
    taskkill /F /IM powershell.exe
    echo 完成！
)

if "%choice%"=="2" (
    echo.
    echo 正在结束内存占用最大的进程...
    taskkill /F /PID 14080
    taskkill /F /PID 1880
    taskkill /F /PID 14516
    taskkill /F /PID 15472
    taskkill /F /PID 6440
    echo 完成！
)

if "%choice%"=="3" (
    echo 退出...
    exit
)

echo.
echo ========================================
echo 操作完成！
echo 请重新打开 PowerShell 或 CMD
echo ========================================
pause
