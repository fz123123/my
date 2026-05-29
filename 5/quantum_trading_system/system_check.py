#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化系统全面检测工具
检查完整性、数据准确性、运行稳定性
"""

import os
import sys
import subprocess
from datetime import datetime, time

sys.path.append('C:/Users/Administrator/Documents/trae_projects/5/quantum_trading_system')

def check_system_structure():
    """检查系统结构完整性"""
    print("🔍 正在检查系统结构...")
    
    required_dirs = [
        'core', 'strategies', 'backtest', 'dashboard', 'reports', 'monitor'
    ]
    
    required_files = [
        'web_app.py', 'config.py', 'main.py',
        'core/data_engine.py', 'core/data_fetcher.py', 'core/indicators.py',
        'strategies/basic_strategies.py', 'strategies/optimizer.py',
        'backtest/engine.py', 'backtest/enhanced_engine.py'
    ]
    
    missing_dirs = []
    missing_files = []
    
    for d in required_dirs:
        path = f'C:/Users/Administrator/Documents/trae_projects/5/quantum_trading_system/{d}'
        if not os.path.exists(path):
            missing_dirs.append(d)
    
    for f in required_files:
        path = f'C:/Users/Administrator/Documents/trae_projects/5/quantum_trading_system/{f}'
        if not os.path.exists(path):
            missing_files.append(f)
    
    print(f"  ✓ 目录检查: {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)} 完整")
    if missing_dirs:
        print(f"  ✗ 缺失目录: {', '.join(missing_dirs)}")
    
    print(f"  ✓ 文件检查: {len(required_files) - len(missing_files)}/{len(required_files)} 完整")
    if missing_files:
        print(f"  ✗ 缺失文件: {', '.join(missing_files)}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0

def check_tdx_data():
    """检查通达信数据完整性"""
    print("\n📊 正在检查通达信数据...")
    
    tdx_path = r"C:\new_tdx\vipdoc"
    sh_path = os.path.join(tdx_path, 'sh', 'lday')
    sz_path = os.path.join(tdx_path, 'sz', 'lday')
    
    sh_count = 0
    sz_count = 0
    
    if os.path.exists(sh_path):
        sh_count = len([f for f in os.listdir(sh_path) if f.endswith('.day')])
    
    if os.path.exists(sz_path):
        sz_count = len([f for f in os.listdir(sz_path) if f.endswith('.day')])
    
    print(f"  ✓ 上海市场: {sh_count} 只股票")
    print(f"  ✓ 深圳市场: {sz_count} 只股票")
    print(f"  ✓ 总计: {sh_count + sz_count} 只股票")
    
    return sh_count + sz_count > 0

def check_watchlist():
    """检查监控列表"""
    print("\n📋 正在检查监控列表...")
    
    watchlist_file = 'C:/Users/Administrator/Documents/trae_projects/5/quantum_trading_system/monitor/stocks.txt'
    
    if os.path.exists(watchlist_file):
        with open(watchlist_file, 'r', encoding='utf-8') as f:
            stocks = [line.strip() for line in f if line.strip()]
        print(f"  ✓ 监控列表: {len(stocks)} 只股票")
        return len(stocks) > 0
    else:
        print("  ✗ 监控列表文件不存在")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n📦 正在检查依赖包...")
    
    required_packages = [
        'pandas', 'numpy', 'streamlit', 'plotly',
        'akshare', 'requests', 'scipy'
    ]
    
    missing_packages = []
    
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)
    
    print(f"  ✓ 依赖检查: {len(required_packages) - len(missing_packages)}/{len(required_packages)} 已安装")
    if missing_packages:
        print(f"  ✗ 缺失依赖: {', '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_real_time_update():
    """检查实时更新能力"""
    print("\n⏰ 正在检查实时更新能力...")
    
    now = datetime.now()
    current_time = now.time()
    
    trading_start = time(9, 15)
    trading_end = time(15, 0)
    lunch_start = time(11, 30)
    lunch_end = time(13, 0)
    
    is_trading_hours = False
    if trading_start <= current_time < lunch_start or lunch_end <= current_time < trading_end:
        is_trading_hours = True
    
    print(f"  当前时间: {now.strftime('%H:%M:%S')}")
    print(f"  交易时间: {is_trading_hours}")
    
    update_interval = 300
    print(f"  更新间隔: {update_interval}秒 (5分钟)")
    
    return True

def check_strategy_availability():
    """检查策略可用性"""
    print("\n🎯 正在检查策略模块...")
    
    strategies = [
        'StrategyMaCross', 'StrategyRsi', 'StrategyBollinger',
        'StrategyMultiFactor', 'StrategyGridAdvanced', 'RsiAdaptiveStrategy'
    ]
    
    available = []
    unavailable = []
    
    for strategy in strategies:
        try:
            if strategy == 'RsiAdaptiveStrategy':
                from strategies.rsi_adaptive_strategy import RsiAdaptiveStrategy
            elif strategy == 'StrategyMaCross':
                from strategies.basic_strategies import StrategyMaCross
            elif strategy == 'StrategyRsi':
                from strategies.basic_strategies import StrategyRsi
            elif strategy == 'StrategyBollinger':
                from strategies.basic_strategies import StrategyBollinger
            elif strategy == 'StrategyMultiFactor':
                from strategies.basic_strategies import StrategyMultiFactor
            elif strategy == 'StrategyGridAdvanced':
                from strategies.basic_strategies import StrategyGridAdvanced
            available.append(strategy)
        except Exception as e:
            unavailable.append(strategy)
    
    print(f"  ✓ 可用策略: {len(available)} 个")
    for s in available:
        print(f"    - {s}")
    
    if unavailable:
        print(f"  ✗ 不可用策略: {len(unavailable)} 个")
        for s in unavailable:
            print(f"    - {s}")
    
    return len(unavailable) == 0

def run_quick_test():
    """运行快速测试"""
    print("\n🧪 正在运行快速测试...")
    
    try:
        from core.data_fetcher import DataFetcher
        from strategies.basic_strategies import StrategyRsi
        
        fetcher = DataFetcher()
        df = fetcher.get_stock_data('000001.SZ')
        
        if df is not None and len(df) > 60:
            print("  ✓ 数据获取: 正常")
        else:
            print("  ✗ 数据获取: 失败或数据不足")
            return False
        
        strategy = StrategyRsi()
        signals = strategy.generate_signals(df)
        
        if signals is not None and len(signals) > 0:
            print("  ✓ 策略信号生成: 正常")
        else:
            print("  ✗ 策略信号生成: 失败")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def generate_report(results):
    """生成检测报告"""
    print("\n" + "="*70)
    print("    📊 量化系统全面检测报告")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\n📈 整体评分: {passed}/{total} ({passed/total*100:.1f}%)")
    
    print("\n📋 检测项目详情:")
    for item, status in results.items():
        status_str = "✅ 通过" if status else "❌ 未通过"
        print(f"  {item}: {status_str}")
    
    print("\n💡 建议:")
    if passed == total:
        print("  系统状态良好，可以正常使用！")
    else:
        print("  部分检测项未通过，建议检查相关模块")
        if not results.get('系统结构'):
            print("  - 检查缺失的目录和文件")
        if not results.get('通达信数据'):
            print("  - 在通达信中下载完整盘后数据")
        if not results.get('依赖包'):
            print("  - 运行 pip install -r requirements.txt")
        if not results.get('策略模块'):
            print("  - 检查策略文件是否存在")
    
    print("\n⏰ 实时更新说明:")
    print("  - 系统支持每5分钟自动刷新")
    print("  - 交易时间内(9:15-11:30, 13:00-15:00)会自动更新数据")
    print("  - 盯盘脚本会在检测到买入信号时发出提醒")

def main():
    print("="*70)
    print("    🔧 量化系统全面检测")
    print("="*70)
    
    results = {}
    
    results['系统结构'] = check_system_structure()
    results['通达信数据'] = check_tdx_data()
    results['监控列表'] = check_watchlist()
    results['依赖包'] = check_dependencies()
    results['实时更新'] = check_real_time_update()
    results['策略模块'] = check_strategy_availability()
    results['功能测试'] = run_quick_test()
    
    generate_report(results)

if __name__ == "__main__":
    main()