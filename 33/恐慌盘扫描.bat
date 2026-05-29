@echo off
setlocal

:: 设置代码页为UTF-8
chcp 65001 >nul

:: 设置Python路径（根据实际安装路径修改）
set PYTHON_PATH=C:\Python\python.exe

:: 设置工作目录
set WORK_DIR=C:\Users\Administrator\Documents\trae_projects\33

title Panic Scanner

echo.
echo ========================================
echo    Panic Stock Scanner
echo ========================================
echo.

:: 切换到工作目录
cd /d "%WORK_DIR%"

echo [INFO] Starting panic scan...
echo.

:: 检查Python是否存在
if exist "%PYTHON_PATH%" (
    "%PYTHON_PATH%" panic_scanner.py
) else (
    echo [ERROR] Python not found at %PYTHON_PATH%
    echo Please check your Python installation
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Scan completed!
echo ========================================
echo.
pause
