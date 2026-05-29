@echo off
REM ========================================================
REM 量子量化平台 - Git钩子安装脚本
REM ========================================================
echo ================================================
echo 量子量化平台 - Git钩子安装
echo ================================================
echo.

REM 检查是否在Git仓库中
if not exist ".git" (
    echo ❌ 未找到Git仓库
    echo    请先运行: git init
    pause
    exit /b 1
)

REM 检查Git钩子目录
if not exist ".git\hooks" (
    echo ⚠️  未找到Git hooks目录，正在创建...
    mkdir ".git\hooks"
)

REM 复制pre-commit钩子
echo 安装pre-commit钩子...
copy "scripts\git_hooks\pre-commit.bat" ".git\hooks\pre-commit.bat" >nul
copy "scripts\git_hooks\pre-commit" ".git\hooks\pre-commit" >nul

echo.
echo ================================================
echo ✅ Git钩子安装成功！
echo ================================================
echo.
echo 每次提交代码前会自动运行测试。
echo.
pause
