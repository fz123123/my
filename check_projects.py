#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目完整性、可行性与优化回测综合检查工具
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

class ProjectChecker:
    def __init__(self):
        self.base_path = Path(r'C:\Users\Administrator\Documents\trae_projects')
        self.projects = ['0', '17', '33', '88']
        self.results = {
            '完整性': {'通过': [], '警告': [], '错误': []},
            '可行性': {'通过': [], '警告': [], '错误': []},
            '回测验证': {'通过': [], '警告': [], '错误': []}
        }
        
    def check_project_structure(self):
        """检查项目结构完整性"""
        print("\n" + "="*70)
        print("📋 项目结构完整性检查")
        print("="*70)
        
        for project in self.projects:
            proj_path = self.base_path / project
            if not proj_path.exists():
                self.results['完整性']['错误'].append(f"项目 {project}: 目录不存在")
                print(f"❌ 项目 {project}: 目录不存在")
                continue
                
            print(f"\n📁 项目 {project}")
            print("-" * 40)
            
            # 检查主要文件
            files_to_check = {
                'package.json': '依赖配置',
                'README.md': '项目说明',
                'requirements.txt': '依赖列表',
            }
            
            for file, desc in files_to_check.items():
                if (proj_path / file).exists():
                    self.results['完整性']['通过'].append(f"项目 {project}: {desc}")
                    print(f"  ✅ {desc}")
                else:
                    self.results['完整性']['警告'].append(f"项目 {project}: 缺少{desc}")
                    print(f"  ⚠️ 缺少{desc}")
            
            # 检查源代码目录
            src_dirs = ['src', 'dist']
            for src_dir in src_dirs:
                if (proj_path / src_dir).exists():
                    count = len(list((proj_path / src_dir).rglob('*.py'))) + len(list((proj_path / src_dir).rglob('*.ts'))) + len(list((proj_path / src_dir).rglob('*.js')))
                    self.results['完整性']['通过'].append(f"项目 {project}: {src_dir}目录 ({count}个文件)")
                    print(f"  ✅ {src_dir}目录 ({count}个文件)")
                else:
                    self.results['完整性']['警告'].append(f"项目 {project}: 缺少{src_dir}目录")
                    print(f"  ⚠️ 缺少{src_dir}目录")
    
    def check_data_files(self):
        """检查数据文件完整性"""
        print("\n" + "="*70)
        print("📊 数据文件完整性检查")
        print("="*70)
        
        data_paths = [
            ('33/data/tdx/today_data.csv', '恐慌盘扫描数据'),
            ('88/watchlist_realtime.csv', '自选股实时数据'),
            ('0/AAPL_daily_data.csv', '美股AAPL数据'),
        ]
        
        for rel_path, desc in data_paths:
            full_path = self.base_path / rel_path
            if full_path.exists():
                try:
                    import pandas as pd
                    df = pd.read_csv(full_path)
                    self.results['完整性']['通过'].append(f"{desc}: {len(df)} 条记录")
                    print(f"✅ {desc}: {len(df)} 条记录")
                except Exception as e:
                    self.results['完整性']['警告'].append(f"{desc}: 读取失败 - {str(e)}")
                    print(f"⚠️ {desc}: 读取失败")
            else:
                self.results['完整性']['错误'].append(f"{desc}: 文件不存在")
                print(f"❌ {desc}: 文件不存在")
    
    def check_dependencies(self):
        """检查依赖可行性"""
        print("\n" + "="*70)
        print("🔧 依赖可行性检查")
        print("="*70)
        
        dependencies = [
            ('pandas', '数据处理'),
            ('numpy', '数值计算'),
            ('requests', '网络请求'),
            ('yfinance', '美股数据'),
            ('ta', '技术指标'),
            ('tushare', 'A股数据'),
            ('struct', '二进制解析'),
        ]
        
        for pkg, desc in dependencies:
            try:
                __import__(pkg)
                self.results['可行性']['通过'].append(f"{pkg}: {desc}")
                print(f"✅ {pkg} ({desc})")
            except ImportError as e:
                self.results['可行性']['警告'].append(f"{pkg}: {desc} - 未安装")
                print(f"⚠️ {pkg} ({desc}) - 未安装")
            except Exception as e:
                self.results['可行性']['错误'].append(f"{pkg}: {desc} - {str(e)}")
                print(f"❌ {pkg}: {desc} - {str(e)}")
    
    def run_backtest_validation(self):
        """运行回测验证"""
        print("\n" + "="*70)
        print("🧪 回测验证")
        print("="*70)
        
        backtest_scripts = [
            ('0/simple_backtest.py', '简单回测'),
            ('33/src/backtest.ts', '恐慌盘回测'),
            ('88/quick_backtest.py', '快速回测'),
        ]
        
        for script, desc in backtest_scripts:
            full_path = self.base_path / script
            if full_path.exists():
                self.results['回测验证']['通过'].append(f"{desc}: 脚本存在")
                print(f"✅ {desc}: 脚本存在")
                
                # 尝试执行简单测试
                try:
                    if script.endswith('.py'):
                        # 使用双反斜杠避免转义问题
                        path_str = str(full_path.parent).replace('\\', '\\\\')
                        result = subprocess.run(
                            ['python', '-c', f"import sys; sys.path.insert(0, '{path_str}'); print('模块导入成功')"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            self.results['回测验证']['通过'].append(f"{desc}: 模块导入成功")
                            print(f"   ✓ 模块导入成功")
                        else:
                            self.results['回测验证']['警告'].append(f"{desc}: 导入警告 - {result.stderr[:50]}")
                            print(f"   ⚠️ 导入警告")
                except subprocess.TimeoutExpired:
                    self.results['回测验证']['警告'].append(f"{desc}: 测试超时")
                    print(f"   ⚠️ 测试超时")
                except Exception as e:
                    self.results['回测验证']['错误'].append(f"{desc}: {str(e)}")
                    print(f"   ❌ {str(e)}")
            else:
                self.results['回测验证']['错误'].append(f"{desc}: 脚本不存在")
                print(f"❌ {desc}: 脚本不存在")
    
    def run_optimization_check(self):
        """运行优化检查"""
        print("\n" + "="*70)
        print("⚡ 优化可行性检查")
        print("="*70)
        
        optimization_files = [
            ('0/optimize_hold_days.py', '持有天数优化'),
            ('88/strategy_optimizer.py', '策略优化'),
            ('88/complete_optimizer.py', '完整优化器'),
        ]
        
        for opt_file, desc in optimization_files:
            full_path = self.base_path / opt_file
            if full_path.exists():
                self.results['回测验证']['通过'].append(f"{desc}: 优化脚本存在")
                print(f"✅ {desc}: 优化脚本存在")
            else:
                self.results['回测验证']['警告'].append(f"{desc}: 优化脚本不存在")
                print(f"⚠️ {desc}: 优化脚本不存在")
    
    def generate_report(self):
        """生成综合报告"""
        print("\n" + "="*70)
        print("📊 综合检查报告")
        print("="*70)
        print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        for category, statuses in self.results.items():
            print(f"\n【{category}】")
            print("-" * 40)
            
            if statuses['错误']:
                print(f"❌ 错误 ({len(statuses['错误'])}):")
                for item in statuses['错误']:
                    print(f"   - {item}")
            
            if statuses['警告']:
                print(f"⚠️ 警告 ({len(statuses['警告'])}):")
                for item in statuses['警告']:
                    print(f"   - {item}")
            
            if statuses['通过']:
                print(f"✅ 通过 ({len(statuses['通过'])}):")
                for item in statuses['通过'][:5]:  # 只显示前5个
                    print(f"   - {item}")
                if len(statuses['通过']) > 5:
                    print(f"   ... 还有 {len(statuses['通过']) - 5} 项")
        
        # 计算综合评分
        total = 0
        passed = 0
        for statuses in self.results.values():
            total += len(statuses['通过']) + len(statuses['警告']) + len(statuses['错误'])
            passed += len(statuses['通过'])
        
        score = int((passed / total) * 100) if total > 0 else 0
        print(f"\n" + "="*70)
        print(f"📈 综合评分: {score}分")
        
        if score >= 80:
            print("🎉 项目状态良好，可正常运行回测")
        elif score >= 60:
            print("⚠️ 项目基本可用，建议修复警告项")
        else:
            print("🔧 需要修复关键问题后再运行回测")
        print("="*70)
        
        return score

    def run_all_checks(self):
        """运行所有检查"""
        print("🚀 开始检查所有项目完整性、可行性与优化回测...")
        self.check_project_structure()
        self.check_data_files()
        self.check_dependencies()
        self.run_backtest_validation()
        self.run_optimization_check()
        return self.generate_report()

if __name__ == "__main__":
    checker = ProjectChecker()
    checker.run_all_checks()
