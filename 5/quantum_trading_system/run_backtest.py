#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
量子量化平台 - 策略回测分析脚本
测试所有策略在历史数据上的表现
"""
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

from backtest.engine import BacktestEngine


def generate_backtest_data(days=500, trend='up'):
    """生成回测用的价格数据"""
    np.random.seed(42)
    
    dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
    
    if trend == 'up':
        base_prices = np.linspace(100, 200, days)
    elif trend == 'down':
        base_prices = np.linspace(200, 100, days)
    elif trend == 'range':
        base_prices = 150 + np.sin(np.linspace(0, 10*np.pi, days)) * 30
    else:
        base_prices = 100 + np.random.normal(0, 5, days).cumsum()
    
    noise = np.random.normal(0, 3, days)
    close_prices = base_prices + noise
    
    high_prices = close_prices + np.random.uniform(0, 6, days)
    low_prices = close_prices - np.random.uniform(0, 6, days)
    open_prices = low_prices + np.random.uniform(0, high_prices - low_prices, days)
    volumes = np.random.randint(500000, 5000000, days)
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    return df


def run_strategy_backtest(strategy, df, strategy_name):
    """运行单个策略的回测"""
    print(f"\n{'='*70}")
    print(f"回测策略: {strategy_name}")
    print(f"{'='*70}")
    
    try:
        signals = strategy.generate_signals(df)
        
        if signals is None or len(signals) == 0:
            print("  [SKIP] 没有生成信号")
            return None
        
        engine = BacktestEngine(initial_capital=100000)
        result = engine.run_backtest(df, signals)
        
        if result is None:
            print("  [SKIP] 回测结果为空")
            return None
        
        print(f"  总收益率: {result['total_return_pct']:+.2f}%")
        print(f"  最终权益: {result['final_equity']:,.2f}")
        print(f"  夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"  最大回撤: {result['max_drawdown_pct']:.2f}%")
        print(f"  交易次数: {result['total_trades']}")
        print(f"  胜率: {result['win_rate_pct']:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"  [ERROR] 回测失败: {e}")
        return None


def main():
    """主函数"""
    print("="*80)
    print("🐉 量子量化平台 - 策略回测分析")
    print("="*80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"初始资金: 100,000 元")
    print("="*80)
    
    # 生成测试数据（包含多种市场状态）
    print("\n📊 生成回测数据...")
    df_bull = generate_backtest_data(days=500, trend='up')
    df_bear = generate_backtest_data(days=300, trend='down')
    df_range = generate_backtest_data(days=400, trend='range')
    
    # 合并数据模拟真实市场周期
    df = pd.concat([df_bull, df_bear, df_range]).sort_index()
    print(f"  数据时间范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"  数据天数: {len(df)}")
    print(f"  价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    # 策略列表
    strategies = [
        ("均线交叉策略", StrategyMaCross()),
        ("RSI基础策略", StrategyRsi()),
        ("RSI增强策略", StrategyRsiEnhanced()),
        ("RSI自适应策略", StrategyRsiAdaptive()),
        ("布林带策略", StrategyBollinger()),
        ("多因子策略", StrategyMultiFactor()),
        ("网格基础策略", StrategyGrid()),
        ("网格进阶策略", StrategyGridAdvanced()),
        ("网格高频策略", StrategyGridScalping()),
    ]
    
    # 运行所有策略回测
    results = []
    for name, strategy in strategies:
        result = run_strategy_backtest(strategy, df, name)
        if result:
            results.append({
                'name': name,
                'total_return_pct': result['total_return_pct'],
                'sharpe_ratio': result['sharpe_ratio'],
                'max_drawdown_pct': result['max_drawdown_pct'],
                'total_trades': result['total_trades'],
                'win_rate_pct': result['win_rate_pct'],
            })
    
    # 输出综合排名
    print("\n" + "="*80)
    print("🏆 策略回测综合排名")
    print("="*80)
    
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('total_return_pct', ascending=False)
        
        print(f"{'排名':<6} {'策略名称':<15} {'收益率':<12} {'夏普比率':<10} {'最大回撤':<10} {'交易次数':<8} {'胜率':<8}")
        print("-"*80)
        
        for i, (_, row) in enumerate(results_df.iterrows(), 1):
            rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"  {i}."
            print(f"{rank_icon:<6} {row['name']:<15} {row['total_return_pct']:>+.2f}%{''*4} {row['sharpe_ratio']:>6.2f}{' '*4} {row['max_drawdown_pct']:>6.2f}%{' '*4} {row['total_trades']:>8} {row['win_rate_pct']:>6.1f}%")
        
        print("-"*80)
        
        # 统计分析
        avg_return = results_df['total_return_pct'].mean()
        best_return = results_df['total_return_pct'].max()
        worst_return = results_df['total_return_pct'].min()
        avg_sharpe = results_df['sharpe_ratio'].mean()
        avg_drawdown = results_df['max_drawdown_pct'].mean()
        
        print(f"\n📈 统计摘要:")
        print(f"   平均收益率: {avg_return:+.2f}%")
        print(f"   最高收益率: {best_return:+.2f}%")
        print(f"   最低收益率: {worst_return:+.2f}%")
        print(f"   平均夏普比率: {avg_sharpe:.2f}")
        print(f"   平均最大回撤: {avg_drawdown:.2f}%")
        
        # 推荐策略
        best_strategy = results_df.iloc[0]
        print(f"\n🎯 推荐策略: {best_strategy['name']}")
        print(f"   收益率: {best_strategy['total_return_pct']:+.2f}%")
        print(f"   夏普比率: {best_strategy['sharpe_ratio']:.2f}")
        print(f"   最大回撤: {best_strategy['max_drawdown_pct']:.2f}%")
        
    else:
        print("❌ 没有策略回测成功")
    
    print("\n" + "="*80)
    print("📝 回测分析完成")
    print("="*80)
    print("\n💡 优化建议:")
    print("  1. 回测结果仅供参考，实际交易需考虑更多因素")
    print("  2. 建议使用真实历史数据进行验证")
    print("  3. 参数优化可以提升策略表现")
    print("  4. 考虑组合多种策略分散风险")


if __name__ == '__main__':
    main()
