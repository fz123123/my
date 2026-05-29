@echo off
chcp 65001 >nul
echo [CI] ================================================
echo [CI] Quantum Trading System - Local Test Pipeline
echo [CI] ================================================
echo.

set CORE_PASSED=0

echo [CI] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [CI] [FAIL] Python not found
    exit /b 1
)
python --version
echo [CI] [OK] Python environment check passed
echo.

echo [CI] Checking project structure...
if not exist "strategies\basic_strategies.py" (
    echo [CI] [FAIL] Strategy file not found
    exit /b 1
)
if not exist "tests\run_tests.py" (
    echo [CI] [FAIL] Test file not found
    exit /b 1
)
echo [CI] [OK] Project structure check passed
echo.

echo [CI] Checking dependencies...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo [CI] [WARN] Dependencies not installed, installing...
    pip install -r requirements.txt
)
echo [CI] [OK] Dependencies check passed
echo.

echo [CI] ================================================
echo [CI] Stage 1: Core Function Tests
echo [CI] ================================================
python tests\run_tests.py
if errorlevel 1 (
    set CORE_PASSED=0
) else (
    set CORE_PASSED=1
)
echo.

echo [CI] ================================================
echo [CI] Stage 2: Edge Case Tests
echo [CI] ================================================
python tests\test_edge_cases.py >nul 2>&1
python tests\test_edge_cases.py
echo.

echo [CI] ================================================
echo [CI] Stage 3: Code Quality Check
echo [CI] ================================================
pip show flake8 >nul 2>&1
if errorlevel 1 (
    echo [CI] [WARN] flake8 not installed, skipping quality check
    echo [CI]        To install: pip install flake8
) else (
    echo [CI] Running flake8...
    flake8 strategies/ --max-line-length=120 --ignore=E501,W503
)
echo.

echo [CI] ================================================
echo [CI] CI/CD Pipeline Summary
echo [CI] ================================================
if %CORE_PASSED% equ 1 (
    echo [CI] [SUCCESS] All core tests passed!
    echo [CI] ================================================
    exit /b 0
) else (
    echo [CI] [FAIL] Core tests failed
    echo [CI] ================================================
    exit /b 1
)
