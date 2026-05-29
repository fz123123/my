#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一测试运行脚本 - 用于本地和CI/CD环境
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 设置UTF-8编码支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECTS = ['0', '17', '33', '88']
BASE_DIR = Path(__file__).parent

class TestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
    
    def run_python_tests(self, project_dir: Path) -> bool:
        """运行Python项目测试"""
        test_dir = project_dir / 'tests'
        if not test_dir.exists():
            print(f"⚠️  {project_dir.name}: 测试目录不存在")
            return True
        
        all_passed = True
        test_files = list(test_dir.glob('test_*.py'))
        
        if not test_files:
            print(f"⚠️  {project_dir.name}: 没有找到测试文件")
            return True
        
        print(f"📁 {project_dir.name}: 发现 {len(test_files)} 个测试文件")
        
        for test_file in test_files:
            print(f"   ▶️  运行: {test_file.name}")
            try:
                # 使用UTF-8编码运行子进程
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=300,
                    env=env
                )
                if result.returncode == 0:
                    print(f"   ✅ {test_file.name}: 通过")
                else:
                    print(f"   ❌ {test_file.name}: 失败")
                    print(f"   标准输出:\n{result.stdout}")
                    print(f"   错误输出:\n{result.stderr}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {test_file.name}: 运行出错 - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_typescript_tests(self, project_dir: Path) -> bool:
        """运行TypeScript项目测试"""
        test_dir = project_dir / 'tests'
        if not test_dir.exists():
            print(f"⚠️  {project_dir.name}: 测试目录不存在")
            return True
        
        all_passed = True
        ts_test_files = list(test_dir.glob('*.test.ts')) + list(test_dir.glob('*.spec.ts'))
        
        if not ts_test_files:
            print(f"⚠️  {project_dir.name}: 没有找到TypeScript测试文件")
            return True
        
        print(f"📁 {project_dir.name}: 发现 {len(ts_test_files)} 个测试文件")
        
        # 检查 package.json
        package_json = project_dir / 'package.json'
        if package_json.exists():
            try:
                print("   📦 安装依赖...")
                subprocess.run(
                    ['npm', 'ci'], 
                    cwd=str(project_dir), 
                    check=True, 
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                print("   🔨 构建项目...")
                subprocess.run(
                    ['npm', 'run', 'build'], 
                    cwd=str(project_dir), 
                    check=True, 
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            except Exception as e:
                print(f"   ⚠️ 构建阶段跳过: {str(e)}")
        
        for test_file in ts_test_files:
            print(f"   ▶️  运行: {test_file.name}")
            try:
                result = subprocess.run(
                    ['npx', 'ts-node', str(test_file)],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=300
                )
                if result.returncode == 0:
                    print(f"   ✅ {test_file.name}: 通过")
                else:
                    print(f"   ❌ {test_file.name}: 失败")
                    print(f"   标准输出:\n{result.stdout}")
                    print(f"   错误输出:\n{result.stderr}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {test_file.name}: 运行出错 - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """运行所有项目测试"""
        print("=" * 70)
        print("🚀 开始运行所有项目单元测试")
        print(f"⏰ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        for project in PROJECTS:
            project_dir = BASE_DIR / project
            print(f"\n{'=' * 70}")
            print(f"📍 项目: {project}")
            print('=' * 70)
            
            if project == '33':
                passed = self.run_typescript_tests(project_dir)
            else:
                passed = self.run_python_tests(project_dir)
            
            self.results[project] = passed
        
        # 生成总结
        self.generate_summary()
    
    def generate_summary(self):
        """生成测试总结"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed_count = sum(1 for v in self.results.values() if v)
        total_count = len(self.results)
        
        print("\n" + "=" * 70)
        print("📊 测试执行总结")
        print("=" * 70)
        print(f"⏰ 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  总耗时: {duration:.1f} 秒")
        print("\n项目结果:")
        
        for project, passed in self.results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"   项目 {project}: {status}")
        
        print(f"\n📈 通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.0f}%)")
        
        if passed_count == total_count:
            print("\n🎉 所有测试通过！")
            return 0
        else:
            print("\n❌ 部分测试失败！")
            return 1

if __name__ == "__main__":
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)
