@echo off
REM ========================================================
REM 量子量化平台 - Git仓库初始化脚本
REM ========================================================
echo ================================================
echo 量子量化平台 - Git仓库初始化
echo ================================================
echo.

REM 检查是否已初始化
if exist ".git" (
    echo ⚠️  Git仓库已存在
    echo.
    echo 跳过初始化，请手动运行:
    echo   - git add .
    echo   - git commit -m "initial commit"
    echo.
    pause
    exit /b 0
)

REM 初始化Git仓库
echo [1/5] 初始化Git仓库...
git init
if errorlevel 1 (
    echo ❌ Git初始化失败
    pause
    exit /b 1
)
echo ✅ Git仓库初始化成功
echo.

REM 创建.gitignore文件
echo [2/5] 创建.gitignore文件...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo env/
echo venv/
echo ENV/
echo *.egg-info/
echo dist/
echo build/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # 数据
echo data/
echo *.csv
echo *.xlsx
echo !test*.csv
echo.
echo # 日志
echo *.log
echo logs/
echo.
echo # 备份
echo *.bak
echo backups/
echo.
echo # 临时文件
echo *.tmp
echo temp/
) > .gitignore
echo ✅ .gitignore创建成功
echo.

REM 添加所有文件
echo [3/5] 添加文件到暂存区...
git add .
echo ✅ 文件添加成功
echo.

REM 首次提交
echo [4/5] 进行首次提交...
git commit -m "Initial commit: Quantum Trading System v3.0"
echo ✅ 首次提交成功
echo.

REM 安装Git钩子
echo [5/5] 安装Git钩子...
call scripts\setup_git_hooks.bat
echo.

echo ================================================
echo 🎉 Git仓库初始化完成！
echo ================================================
echo.
echo 下一步操作:
echo   - 连接远程仓库: git remote add origin ^<你的仓库URL^>
echo   - 推送到远程: git push -u origin main
echo.
echo 或者使用GitHub/GitLab托管，请参考 CI_README.md
echo.
pause
