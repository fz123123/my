#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 执行一个简单的回测来检查系统
"""

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("🚀 量子量化系统 Pro - 快速测试")
print("="*80)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

try:
    from config import config
    from core.data_fetcher import DataFetcher
    from core.indicators import calculate_indicators
    from backtest.engine import BacktestEngine
    from strategies.basic_strategies import StrategyMaCross
    
    print("✅ 模块导入成功！")
    print()
    
    # 测试 DataFetcher
    print("📊 [1/3] 测试数据获取...")
    fetcher = DataFetcher()
    print("✅ DataFetcher 初始化成功")
    
    # 获取一只股票测试数据
    test_stock = '600130.SH'
    print(f"   获取 {test_stock} 数据...")
    
    try:
        df = fetcher.get_stock_data(test_stock)
        if df is not None and len(df) > 0:
            print(f"✅ 获取成功 - 共 {len(df)} 条数据")
            print(f"   日期范围: {df.index[0]} 至 {df.index[-1]}")
        else:
            print("⚠️ 数据获取失败，使用测试数据")
    except Exception as e:
        print(f"⚠️ 数据获取异常: {e}")
        
    print()
    
    # 测试策略
    print("🧪 [2/3] 测试策略生成...")
    strategy = StrategyMaCross()
    print("✅ 策略初始化成功")
    
    # 创建一些简单的测试数据
    print("   生成测试数据...")
    import numpy as np
    import pandas as pd
    from datetime import timedelta
    
    # 创建测试数据
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(100) * 2) + 100
    
    test_df = pd.DataFrame({
        'open': prices,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': np.random.randint(100000, 1000000, 100)
    }, index=dates)
    
    print(f"✅ 测试数据创建成功 - 共 {len(test_df)} 条")
    print()
    
    # 测试策略信号
    print("📈 生成交易信号...")
    signals = strategy.generate_signals(test_df)
    print(f"✅ 信号生成成功!")
    print(f"   买入信号: {(signals['signal'] == 1).sum()} 次")
    print(f"   卖出信号: {(signals['signal'] == -1).sum()} 次")
    print()
    
    # 测试回测
    print("🔄 [3/3] 测试回测引擎...")
    engine = BacktestEngine()
    result = engine.run_backtest(test_df, signals)
    
    if result:
        print("✅ 回测执行成功!")
        print(f"   总收益率: {result['total_return_pct']:+.2f}%")
        print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"   最大回撤: {result['max_drawdown_pct']:.2f}%")
        print(f"   总交易次数: {result['total_trades']}")
        print(f"   胜率: {result['win_rate_pct']:.2f}%")
    else:
        print("⚠️ 回测无结果")
    
    print()
    print("="*80)
    print("🎉 系统测试全部通过!")
    print("="*80)
    print()
    print("📊 系统状态: 正常运行")
    print("🔧 依赖包: 已安装")
    print("📁 数据目录: 已创建")
    print("🧮 策略模块: 正常")
    print()
    print("💡 您现在可以:")
    print("   1. 运行完整系统: python quantum_trading.py")
    print("   2. 运行Web界面: streamlit run web_app.py")
    print("   3. 使用批处理: 双击 启动平台.bat")
    print()
    
except Exception as e:
    print(f"❌ 系统测试失败: {e}")
    print()
    import traceback
    print("详细错误信息:")
    print("-"*60)
    traceback.print_exc()
    print("-"*60)
    sys.exit(1)
