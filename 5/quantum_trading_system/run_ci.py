#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quantum Trading System - CI/CD Runner
替代批处理脚本，避免Windows命令行编码问题
"""
import os
import sys
import subprocess


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"[CI] Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    print("=" * 70)
    print("[CI] Quantum Trading System - Local CI/CD Pipeline")
    print("=" * 70)
    print()
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    core_passed = False
    
    # Stage 1: Check Python
    print("[CI] ================================================")
    print("[CI] Stage 0: Environment Check")
    print("[CI] ================================================")
    
    success, stdout, stderr = run_command("python --version")
    if success:
        print(f"[CI] [OK] Python environment: {stdout.strip()}")
    else:
        print("[CI] [FAIL] Python not found")
        sys.exit(1)
    
    # Check project structure
    if os.path.exists(os.path.join(project_dir, "strategies", "basic_strategies.py")):
        print("[CI] [OK] Strategy files exist")
    else:
        print("[CI] [FAIL] Strategy files not found")
        sys.exit(1)
    
    if os.path.exists(os.path.join(project_dir, "tests", "run_tests.py")):
        print("[CI] [OK] Test files exist")
    else:
        print("[CI] [FAIL] Test files not found")
        sys.exit(1)
    
    # Check dependencies
    success, stdout, stderr = run_command("pip show pandas")
    if success:
        print("[CI] [OK] Dependencies installed")
    else:
        print("[CI] [WARN] Dependencies not installed, installing...")
        run_command("pip install -r requirements.txt", cwd=project_dir)
    
    print()
    
    # Stage 1: Core tests
    print("[CI] ================================================")
    print("[CI] Stage 1: Core Function Tests")
    print("[CI] ================================================")
    
    success, stdout, stderr = run_command("python tests/run_tests.py", cwd=project_dir)
    print(stdout)
    if stderr:
        print(f"[CI] [ERROR] {stderr}")
    core_passed = success
    
    print()
    
    # Stage 2: Edge case tests
    print("[CI] ================================================")
    print("[CI] Stage 2: Edge Case Tests")
    print("[CI] ================================================")
    
    success, stdout, stderr = run_command("python tests/test_edge_cases.py", cwd=project_dir)
    print(stdout)
    if stderr:
        print(f"[CI] [ERROR] {stderr}")
    
    print()
    
    # Stage 3: Code quality
    print("[CI] ================================================")
    print("[CI] Stage 3: Code Quality Check")
    print("[CI] ================================================")
    
    success, stdout, stderr = run_command("pip show flake8")
    if success:
        print("[CI] Running flake8...")
        success, stdout, stderr = run_command("flake8 strategies/ --max-line-length=120 --ignore=E501,W503", cwd=project_dir)
        print(stdout)
        if stderr:
            print(f"[CI] [WARN] {stderr}")
    else:
        print("[CI] [WARN] flake8 not installed, skipping quality check")
        print("[CI]        To install: pip install flake8")
    
    print()
    
    # Summary
    print("[CI] ================================================")
    print("[CI] CI/CD Pipeline Summary")
    print("[CI] ================================================")
    
    if core_passed:
        print("[CI] [SUCCESS] All core tests passed!")
        print("[CI] ================================================")
        sys.exit(0)
    else:
        print("[CI] [FAIL] Core tests failed")
        print("[CI] ================================================")
        sys.exit(1)


if __name__ == '__main__':
    main()
