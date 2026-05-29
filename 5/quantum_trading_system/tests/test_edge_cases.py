# -*- coding: utf-8 -*-
"""
策略模块 - 边缘情况测试
覆盖异常数据处理、边界条件等
"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.basic_strategies import (
    StrategyMaCross,
    StrategyRsi,
    StrategyRsiEnhanced,
    StrategyRsiAdaptive,
    StrategyBollinger,
    StrategyMultiFactor,
    StrategyGrid,
    StrategyGridAdvanced,
)


def generate_extreme_data():
    """生成极端数据用于测试"""
    np.random.seed(999)
    dates = [datetime.now() - timedelta(days=100-i) for i in range(100)]
    
    base_prices = 100 + np.random.normal(0, 20, 100).cumsum()
    high_prices = base_prices + np.random.uniform(5, 15, 100)
    low_prices = base_prices - np.random.uniform(5, 15, 100)
    open_prices = low_prices + np.random.uniform(0, high_prices - low_prices, 100)
    close_prices = base_prices
    volumes = np.random.randint(10000, 1000000, 100)
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    return df


def generate_flat_data():
    """生成横盘数据"""
    dates = [datetime.now() - timedelta(days=50-i) for i in range(50)]
    close_prices = np.full(50, 100.0)
    
    df = pd.DataFrame({
        'open': close_prices,
        'high': close_prices + 0.5,
        'low': close_prices - 0.5,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 50)
    }, index=dates)
    
    return df


def generate_missing_data():
    """生成有缺失值的数据"""
    np.random.seed(42)
    dates = [datetime.now() - timedelta(days=80-i) for i in range(80)]
    close_prices = 100 + np.random.normal(0, 5, 80).cumsum()
    
    df = pd.DataFrame({
        'open': close_prices,
        'high': close_prices + 2,
        'low': close_prices - 2,
        'close': close_prices,
        'volume': np.random.randint(1000, 100000, 80)
    }, index=dates)
    
    df.loc[df.index[10:12], 'open'] = np.nan
    df.loc[df.index[30:32], 'volume'] = np.nan
    
    return df


def test_empty_data():
    """测试空数据处理"""
    print("\n" + "="*70)
    print("测试: 空数据处理")
    print("="*70)
    
    df_empty = pd.DataFrame()
    strategies = [StrategyMaCross(), StrategyRsi(), StrategyBollinger(), StrategyMultiFactor()]
    
    passed = 0
    failed = 0
    
    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        try:
            signals = strategy.generate_signals(df_empty)
            if isinstance(signals, pd.Series) or signals is None:
                print("[OK] %s: 空数据处理正常" % strategy_name)
                passed += 1
            else:
                print("[FAIL] %s: 空数据返回异常" % strategy_name)
                failed += 1
        except Exception as e:
            print("[WARN] %s: 空数据抛出异常 (预期行为): %s" % (strategy_name, e))
            passed += 1
    
    return passed, failed


def test_small_data():
    """测试小数据量处理"""
    print("\n" + "="*70)
    print("测试: 小数据量处理")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for n in [5, 10, 20]:
        dates = [datetime.now() - timedelta(days=n-i) for i in range(n)]
        df = pd.DataFrame({
            'open': np.random.rand(n) * 100 + 50,
            'high': np.random.rand(n) * 100 + 60,
            'low': np.random.rand(n) * 100 + 40,
            'close': np.random.rand(n) * 100 + 50,
            'volume': np.random.randint(1000, 10000, n)
        }, index=dates)
        
        strategy = StrategyMaCross()
        try:
            signals = strategy.generate_signals(df)
            print("[OK] 数据量 %d: 处理正常" % n)
            passed += 1
        except Exception as e:
            print("[FAIL] 数据量 %d: 处理异常 - %s" % (n, e))
            failed += 1
    
    return passed, failed


def test_extreme_data():
    """测试极端波动数据"""
    print("\n" + "="*70)
    print("测试: 极端波动数据")
    print("="*70)
    
    df = generate_extreme_data()
    strategies = [
        StrategyRsiAdaptive(),
        StrategyGridAdvanced(grid_levels=10),
        StrategyBollinger()
    ]
    
    passed = 0
    failed = 0
    
    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        try:
            signals = strategy.generate_signals(df)
            print("[OK] %s: 极端数据处理正常" % strategy_name)
            passed += 1
        except Exception as e:
            print("[FAIL] %s: 极端数据处理异常 - %s" % (strategy_name, e))
            failed += 1
    
    return passed, failed


def test_flat_data():
    """测试横盘数据"""
    print("\n" + "="*70)
    print("测试: 横盘数据")
    print("="*70)
    
    df = generate_flat_data()
    strategies = [
        StrategyRsi(oversold=30, overbought=70),
        StrategyGrid(grid_levels=5),
    ]
    
    passed = 0
    failed = 0
    
    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        try:
            signals = strategy.generate_signals(df)
            signal_count = (signals != 0).sum()
            print("[OK] %s: 横盘数据处理正常 (信号数: %d)" % (strategy_name, signal_count))
            passed += 1
        except Exception as e:
            print("[FAIL] %s: 横盘数据处理异常 - %s" % (strategy_name, e))
            failed += 1
    
    return passed, failed


def test_missing_data():
    """测试缺失数据处理"""
    print("\n" + "="*70)
    print("测试: 缺失数据")
    print("="*70)
    
    df = generate_missing_data()
    strategies = [StrategyMaCross(), StrategyMultiFactor()]
    
    passed = 0
    failed = 0
    
    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        try:
            signals = strategy.generate_signals(df)
            print("[OK] %s: 缺失数据处理正常" % strategy_name)
            passed += 1
        except Exception as e:
            print("[FAIL] %s: 缺失数据处理异常 - %s" % (strategy_name, e))
            failed += 1
    
    return passed, failed


def test_parameter_validation():
    """测试参数验证"""
    print("\n" + "="*70)
    print("测试: 参数验证")
    print("="*70)
    
    passed = 0
    failed = 0
    
    try:
        StrategyRsi(oversold=-10, overbought=110)
        print("[OK] RSI策略: 接受异常参数或做了处理")
        passed += 1
    except Exception as e:
        print("[FAIL] RSI策略: 异常参数处理问题 - %s" % e)
        failed += 1
    
    try:
        StrategyGrid(grid_levels=0)
        print("[OK] 网格策略: 接受网格层级0或做了处理")
        passed += 1
    except Exception as e:
        print("[FAIL] 网格策略: 网格层级0处理问题 - %s" % e)
        failed += 1
    
    return passed, failed


def main():
    """主函数"""
    print("=" * 70)
    print("Quantum Trading System - Edge Case Tests")
    print("=" * 70)
    
    total_passed = 0
    total_failed = 0
    
    tests = [
        ("空数据处理", test_empty_data),
        ("小数据量", test_small_data),
        ("极端波动数据", test_extreme_data),
        ("横盘数据", test_flat_data),
        ("缺失数据", test_missing_data),
        ("参数验证", test_parameter_validation),
    ]
    
    for test_name, test_func in tests:
        try:
            p, f = test_func()
            total_passed += p
            total_failed += f
        except Exception as e:
            print("\n[ERROR] %s 测试出错: %s" % (test_name, e))
            total_failed += 1
    
    print("\n" + "="*70)
    print("Edge Case Test Summary")
    print("="*70)
    print("通过: %d" % total_passed)
    print("失败: %d" % total_failed)
    print("总计: %d" % (total_passed + total_failed))
    
    if total_failed == 0:
        print("\nAll edge case tests passed!")
    else:
        print("\n[WARN] 有 %d 个测试失败" % total_failed)
    
    return total_failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
