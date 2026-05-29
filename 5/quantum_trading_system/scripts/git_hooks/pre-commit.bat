@echo off
REM 量子量化平台 - Windows Git pre-commit hook
REM 在每次提交前自动运行测试

echo ================================================
echo 量子量化平台 - pre-commit 检查
echo ================================================

REM 运行测试
echo 运行策略测试...
python tests\run_tests.py

if errorlevel 1 (
    echo ❌ 测试失败，请修复后再提交
    exit /b 1
)

echo ✅ 测试通过！
exit /b 0
