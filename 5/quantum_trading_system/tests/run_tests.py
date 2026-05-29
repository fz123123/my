# -*- coding: utf-8 -*-
"""
策略模块测试脚本
不依赖pytest，可以直接运行
"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目路径
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
    StrategyGridScalping,
)


def generate_test_data(days=100, trend='up'):
    """生成测试用的价格数据"""
    np.random.seed(42)
    
    dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
    
    if trend == 'up':
        base_prices = np.linspace(100, 150, days)
    elif trend == 'down':
        base_prices = np.linspace(150, 100, days)
    else:
        base_prices = 125 + np.sin(np.linspace(0, 4*np.pi, days)) * 20
    
    noise = np.random.normal(0, 2, days)
    close_prices = base_prices + noise
    
    high_prices = close_prices + np.random.uniform(0, 5, days)
    low_prices = close_prices - np.random.uniform(0, 5, days)
    open_prices = low_prices + np.random.uniform(0, high_prices - low_prices, days)
    volumes = np.random.randint(100000, 1000000, days)
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    return df


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def assert_true(self, condition, message):
        """断言条件为真"""
        try:
            if condition:
                self.passed += 1
                self.results.append(('PASS', message))
                print("[OK] " + message)
            else:
                self.failed += 1
                self.results.append(('FAIL', message))
                print("[FAIL] " + message)
        except Exception as e:
            self.failed += 1
            self.results.append(('FAIL', "%s: %s" % (message, e)))
            print("[FAIL] %s: %s" % (message, e))
    
    def assert_isinstance(self, obj, cls, message):
        """断言对象类型"""
        self.assert_true(isinstance(obj, cls), message)
    
    def run_test(self, test_name, test_func):
        """运行单个测试"""
        print("\n" + "="*70)
        print("测试: " + test_name)
        print("="*70)
        try:
            test_func()
        except Exception as e:
            self.failed += 1
            self.results.append(('ERROR', "%s: %s" % (test_name, e)))
            print("[ERROR] 测试出错: %s" % e)
    
    def summary(self):
        """打印测试总结"""
        print("\n" + "="*70)
        print("测试总结")
        print("="*70)
        print("通过: %d" % self.passed)
        print("失败: %d" % self.failed)
        print("总计: %d" % (self.passed + self.failed))
        if self.failed == 0:
            print("\nAll tests passed!")
        return self.failed == 0


def test_strategy_macross():
    """测试均线交叉策略"""
    runner = TestRunner()
    
    strategy = StrategyMaCross(short_period=5, long_period=20)
    runner.assert_true(strategy.short_period == 5, "短期周期设置正确")
    runner.assert_true(strategy.long_period == 20, "长期周期设置正确")
    
    df = generate_test_data(days=100, trend='up')
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    runner.assert_true(len(signals) == len(df), "信号长度匹配")
    
    df_down = generate_test_data(days=100, trend='down')
    signals_down = strategy.generate_signals(df_down)
    runner.assert_isinstance(signals_down, pd.Series, "下跌趋势也能生成信号")
    
    return runner


def test_strategy_rsi():
    """测试RSI策略"""
    runner = TestRunner()
    
    strategy = StrategyRsi(oversold=30, overbought=70)
    runner.assert_true(strategy.oversold == 30, "超卖阈值设置正确")
    runner.assert_true(strategy.overbought == 70, "超买阈值设置正确")
    
    df = generate_test_data(days=100, trend='range')
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    unique_signals = set(signals.unique())
    runner.assert_true(unique_signals.issubset({0, 1, -1}), "信号值合理")
    
    return runner


def test_strategy_rsi_enhanced():
    """测试增强RSI策略"""
    runner = TestRunner()
    
    strategy = StrategyRsiEnhanced(
        oversold=30,
        overbought=70,
        stop_loss_pct=0.08,
        take_profit_pct=0.20,
        max_holding_days=60,
        use_trend_filter=True
    )
    
    runner.assert_true(strategy.stop_loss_pct == 0.08, "止损设置正确")
    runner.assert_true(strategy.take_profit_pct == 0.20, "止盈设置正确")
    
    df = generate_test_data(days=100)
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    return runner


def test_strategy_rsi_adaptive():
    """测试自适应RSI策略"""
    runner = TestRunner()
    
    strategy = StrategyRsiAdaptive(
        oversold=30,
        overbought=70,
        bull_stop_loss=0.10,
        bear_stop_loss=0.05,
        use_atr_tp=True,
        use_trailing_stop=True
    )
    
    runner.assert_true(strategy.bull_stop_loss == 0.10, "牛市止损正确")
    runner.assert_true(strategy.bear_stop_loss == 0.05, "熊市止损正确")
    
    df = generate_test_data(days=100)
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    return runner


def test_strategy_bollinger():
    """测试布林带策略"""
    runner = TestRunner()
    
    strategy = StrategyBollinger()
    runner.assert_true(strategy is not None, "策略初始化成功")
    
    df = generate_test_data(days=100, trend='range')
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    return runner


def test_strategy_multifactor():
    """测试多因子策略"""
    runner = TestRunner()
    
    strategy = StrategyMultiFactor()
    runner.assert_true(strategy is not None, "策略初始化成功")
    
    df = generate_test_data(days=100)
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    return runner


def test_strategy_grid():
    """测试网格策略"""
    runner = TestRunner()
    
    strategy = StrategyGrid(grid_levels=5, grid_range_pct=0.10)
    runner.assert_true(strategy.grid_levels == 5, "网格层级正确")
    
    df = generate_test_data(days=60)
    grid_lines = strategy.calculate_grid_lines(df)
    runner.assert_isinstance(grid_lines, list, "网格线是列表")
    
    df_full = generate_test_data(days=100)
    signals = strategy.generate_signals(df_full)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    info = strategy.get_grid_info()
    runner.assert_isinstance(info, dict, "网格信息是字典")
    
    return runner


def test_strategy_grid_advanced():
    """测试进阶网格策略"""
    runner = TestRunner()
    
    strategy = StrategyGridAdvanced(
        grid_levels=5,
        grid_range_pct=0.10,
        volume_filter=True,
        rsi_filter=True,
        take_profit_pct=0.02
    )
    
    runner.assert_true(strategy.volume_filter is True, "成交量过滤启用")
    runner.assert_true(strategy.take_profit_pct == 0.02, "止盈设置正确")
    
    df = generate_test_data(days=100)
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    info = strategy.get_grid_info()
    runner.assert_true('volume_filter' in info, "网格信息包含字段")
    
    return runner


def test_strategy_grid_scalping():
    """测试网格高频策略"""
    runner = TestRunner()
    
    strategy = StrategyGridScalping(
        tick_size=0.01,
        profit_target=0.002,
        loss_limit=0.005,
        min_volume=100
    )
    
    runner.assert_true(strategy.profit_target == 0.002, "盈利目标正确")
    
    df = generate_test_data(days=100)
    signals = strategy.generate_signals(df)
    runner.assert_isinstance(signals, pd.Series, "返回值是Series")
    
    return runner


def test_all_strategies_compatibility():
    """测试所有策略兼容性"""
    runner = TestRunner()
    
    df = generate_test_data(days=100)
    
    strategies = [
        StrategyMaCross(),
        StrategyRsi(),
        StrategyRsiEnhanced(),
        StrategyRsiAdaptive(),
        StrategyBollinger(),
        StrategyMultiFactor(),
        StrategyGrid(),
        StrategyGridAdvanced(),
        StrategyGridScalping(),
    ]
    
    for i, strategy in enumerate(strategies):
        strategy_name = strategy.__class__.__name__
        try:
            signals = strategy.generate_signals(df)
            runner.assert_isinstance(signals, pd.Series, "%s 返回值类型正确" % strategy_name)
            runner.assert_true(len(signals) == len(df), "%s 信号长度匹配" % strategy_name)
        except Exception as e:
            runner.assert_true(False, "%s 运行出错: %s" % (strategy_name, e))
    
    return runner


def main():
    """主函数"""
    print("=" * 70)
    print("Quantum Trading System - Strategy Unit Tests")
    print("=" * 70)
    
    all_results = []
    
    tests = [
        ("MA Cross Strategy", test_strategy_macross),
        ("Basic RSI Strategy", test_strategy_rsi),
        ("Enhanced RSI Strategy", test_strategy_rsi_enhanced),
        ("Adaptive RSI Strategy", test_strategy_rsi_adaptive),
        ("Bollinger Bands Strategy", test_strategy_bollinger),
        ("Multi-Factor Strategy", test_strategy_multifactor),
        ("Basic Grid Strategy", test_strategy_grid),
        ("Advanced Grid Strategy", test_strategy_grid_advanced),
        ("Grid Scalping Strategy", test_strategy_grid_scalping),
        ("All Strategies Compatibility", test_all_strategies_compatibility),
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            total_passed += result.passed
            total_failed += result.failed
            all_results.append((test_name, result.passed, result.failed))
        except Exception as e:
            print("\n[ERROR] %s test error: %s" % (test_name, e))
            total_failed += 1
            all_results.append((test_name, 0, 1))
    
    print("\n" + "="*70)
    print("Final Test Summary")
    print("="*70)
    print("%-20s %-10s %-10s %-10s" % ("Strategy", "Passed", "Failed", "Status"))
    print("-" * 70)
    for name, passed, failed in all_results:
        status = "PASS" if failed == 0 else "FAIL"
        print("%-20s %-10d %-10d %-10s" % (name, passed, failed, status))
    print("-" * 70)
    final_status = "ALL PASSED" if total_failed == 0 else "HAS FAILURES"
    print("%-20s %-10d %-10d %-10s" % ("Total", total_passed, total_failed, final_status))
    
    return total_failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
