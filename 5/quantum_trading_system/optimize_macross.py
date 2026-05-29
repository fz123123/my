#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
均线交叉策略参数优化
测试不同均线周期组合，找到最佳参数配置
"""
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.basic_strategies import StrategyMaCross
from backtest.engine import BacktestEngine


def generate_test_data(days=500):
    """生成测试数据"""
    np.random.seed(42)
    
    dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
    
    phase1 = np.linspace(100, 150, 150)
    phase2 = 150 + np.sin(np.linspace(0, 6*np.pi, 200)) * 20
    phase3 = np.linspace(150, 120, 150)
    
    base_prices = np.concatenate([phase1, phase2, phase3])
    
    noise = np.random.normal(0, 2, len(base_prices))
    close_prices = base_prices + noise
    
    high_prices = close_prices + np.random.uniform(0, 4, len(base_prices))
    low_prices = close_prices - np.random.uniform(0, 4, len(base_prices))
    open_prices = low_prices + np.random.uniform(0, high_prices - low_prices, len(base_prices))
    volumes = np.random.randint(500000, 5000000, len(base_prices))
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates[:len(base_prices)])
    
    return df


def optimize_macross_parameters(df, short_periods, long_periods):
    """优化均线交叉策略参数"""
    results = []
    
    print(f"开始参数优化...")
    print(f"测试组合: {len(short_periods) * len(long_periods)} 种")
    print("-" * 80)
    
    for short_period in short_periods:
        for long_period in long_periods:
            if short_period >= long_period:
                continue
            
            try:
                strategy = StrategyMaCross(short_period=short_period, long_period=long_period)
                signals = strategy.generate_signals(df)
                
                if signals is None or len(signals) == 0:
                    continue
                
                engine = BacktestEngine(initial_capital=100000)
                result = engine.run_backtest(df, signals)
                
                if result is not None and result['total_trades'] > 0:
                    results.append({
                        'short_period': short_period,
                        'long_period': long_period,
                        'total_return_pct': result['total_return_pct'],
                        'sharpe_ratio': result['sharpe_ratio'],
                        'max_drawdown_pct': result['max_drawdown_pct'],
                        'total_trades': result['total_trades'],
                        'win_rate_pct': result['win_rate_pct'],
                    })
                    
                    print(f"MA({short_period},{long_period}) | 收益率: {result['total_return_pct']:+.2f}% | 夏普: {result['sharpe_ratio']:.2f} | 回撤: {result['max_drawdown_pct']:.2f}% | 交易: {result['total_trades']}")
            
            except Exception as e:
                continue
    
    return results


def main():
    """主函数"""
    print("=" * 80)
    print("🐉 均线交叉策略参数优化")
    print("=" * 80)
    
    # 生成测试数据
    df = generate_test_data(days=500)
    print(f"测试数据: {len(df)} 天")
    
    # 定义参数搜索范围
    short_periods = range(3, 21)  # 短期均线: 3-20日
    long_periods = range(10, 61)  # 长期均线: 10-60日
    
    # 运行优化
    results = optimize_macross_parameters(df, short_periods, long_periods)
    
    # 分析结果
    if results:
        results_df = pd.DataFrame(results)
        
        # 按收益率排序
        results_df = results_df.sort_values('total_return_pct', ascending=False)
        
        print("\n" + "=" * 80)
        print("🏆 参数优化结果排名")
        print("=" * 80)
        
        print(f"{'排名':<6} {'参数组合':<15} {'收益率':<12} {'夏普比率':<10} {'最大回撤':<10} {'交易次数':<8} {'胜率':<8}")
        print("-" * 80)
        
        top_n = min(10, len(results_df))
        for i, (_, row) in enumerate(results_df.head(top_n).iterrows(), 1):
            rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"  {i}."
            print(f"{rank_icon:<6} MA({row['short_period']},{row['long_period']}){' '*5} {row['total_return_pct']:>+.2f}%{''*4} {row['sharpe_ratio']:>6.2f}{' '*4} {row['max_drawdown_pct']:>6.2f}%{' '*4} {row['total_trades']:>8} {row['win_rate_pct']:>6.1f}%")
        
        print("-" * 80)
        
        # 最佳参数
        best_result = results_df.iloc[0]
        print(f"\n🎯 最佳参数组合: MA({best_result['short_period']}, {best_result['long_period']})")
        print(f"   收益率: {best_result['total_return_pct']:+.2f}%")
        print(f"   夏普比率: {best_result['sharpe_ratio']:.2f}")
        print(f"   最大回撤: {best_result['max_drawdown_pct']:.2f}%")
        print(f"   交易次数: {best_result['total_trades']}")
        print(f"   胜率: {best_result['win_rate_pct']:.1f}%")
        
        # 对比原参数
        print("\n📊 参数对比:")
        original_params = results_df[(results_df['short_period'] == 5) & (results_df['long_period'] == 20)]
        if len(original_params) > 0:
            original = original_params.iloc[0]
            improvement = best_result['total_return_pct'] - original['total_return_pct']
            print(f"   原参数 MA(5,20): 收益率 {original['total_return_pct']:+.2f}%")
            print(f"   新参数 MA({best_result['short_period']},{best_result['long_period']}): 收益率 {best_result['total_return_pct']:+.2f}%")
            print(f"   收益率提升: {improvement:+.2f}%")
        
        # 参数热力图数据
        print("\n🔥 参数热力图摘要:")
        pivot = results_df.pivot(index='short_period', columns='long_period', values='total_return_pct')
        print("   收益率最高的参数区域:")
        for short in [5, 10, 15]:
            row_max = pivot.loc[short].max()
            col_max = pivot.loc[short].idxmax()
            print(f"   - 短期{short}日: 最佳长期周期{col_max}日, 收益率{row_max:+.2f}%")
        
    else:
        print("❌ 没有找到有效参数组合")
    
    print("\n" + "=" * 80)
    print("优化完成")
    print("=" * 80)


if __name__ == '__main__':
    main()
