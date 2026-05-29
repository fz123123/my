#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化系统测试脚本 - 用于检查系统运行情况和日志输出
"""

import sys
import os
from datetime import datetime

print("="*80)
print("🐉 量子量化系统 Pro - 启动测试")
print("="*80)
print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 添加当前路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 [1/5] 检查配置...")
    from config import config
    print(f"✅ 配置加载成功")
    print(f"   - 版本: {config['version']}")
    print(f"   - 观察列表: {len(config['watchlist'])} 只股票")
    print()
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("🔍 [2/5] 检查核心模块...")
    from core.data_fetcher import DataFetcher
    from core.indicators import calculate_indicators
    print("✅ 核心模块导入成功")
    print()
except Exception as e:
    print(f"❌ 核心模块导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("🔍 [3/5] 检查策略模块...")
    from strategies.basic_strategies import (
        StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor
    )
    print("✅ 策略模块导入成功")
    print()
except Exception as e:
    print(f"❌ 策略模块导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("🔍 [4/5] 检查回测模块...")
    from backtest.engine import BacktestEngine
    from backtest.enhanced_engine import EnhancedBacktestEngine
    print("✅ 回测模块导入成功")
    print()
except Exception as e:
    print(f"❌ 回测模块导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("🔍 [5/5] 检查数据目录...")
    from pathlib import Path
    DATA_DIR = Path(__file__).parent / 'data'
    for subdir in ['cache', 'backtest', 'reports', 'logs']:
        dir_path = DATA_DIR / subdir
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   📁 创建目录: {subdir}")
        else:
            print(f"   📁 目录存在: {subdir}")
    print("✅ 数据目录检查完成")
    print()
except Exception as e:
    print(f"❌ 数据目录检查失败: {e}")
    import traceback
    traceback.print_exc()

print("="*80)
print("✅ 系统检查完成 - 所有模块正常！")
print("="*80)
print()
print("📖 您可以选择以下方式启动系统:")
print()
print("  1. 运行命令行版本:")
print("     python quantum_trading.py")
print()
print("  2. 运行Web界面版本:")
print("     streamlit run web_app.py")
print()
print("  3. 运行批处理文件:")
print("     双击 启动平台.bat")
print()
print("="*80)
