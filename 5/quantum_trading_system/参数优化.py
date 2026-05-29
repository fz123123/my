#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略参数优化脚本 - 寻找最优参数组合
优化目标: 提高胜率和夏普比率
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor
from backtest.enhanced_engine import EnhancedBacktestEngine
import pandas as pd

def optimize_ma_cross(data_engine, symbol="000001.SZ"):
    """优化均线交叉策略参数"""
    print("\n" + "="*70)
    print("  1. 优化均线交叉策略")
    print("="*70)
    
    df = data_engine.get_stock_data(symbol)
    if df is None or len(df) < 100:
        print("   数据不足，跳过")
        return None
    
    df = calculate_indicators(df)
    
    best_params = None
    best_score = -999
    results = []
    
    short_periods = [3, 5, 7, 10, 12, 15]
    long_periods = [20, 25, 30, 35, 40, 50]
    
    total = len(short_periods) * len(long_periods)
    count = 0
    
    print(f"   测试 {total} 种参数组合...")
    
    for short in short_periods:
        for long in long_periods:
            if short >= long:
                continue
            
            count += 1
            strategy = StrategyMaCross(short_period=short, long_period=long)
            signals = strategy.generate_signals(df)
            
            engine = EnhancedBacktestEngine(initial_capital=100000)
            result = engine.run_backtest(df, signals)
            
            if result:
                score = result['sharpe_ratio'] * 2 + result['win_rate_pct'] * 0.5
                
                results.append({
                    'short': short,
                    'long': long,
                    'return': result['total_return_pct'],
                    'sharpe': result['sharpe_ratio'],
                    'win_rate': result['win_rate_pct'],
                    'max_dd': result['max_drawdown_pct'],
                    'trades': result['total_trades'],
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = {
                        'short_period': short,
                        'long_period': long,
                        'return': result['total_return_pct'],
                        'sharpe_ratio': result['sharpe_ratio'],
                        'win_rate': result['win_rate_pct'],
                        'max_drawdown': result['max_drawdown_pct'],
                        'total_trades': result['total_trades']
                    }
    
    print(f"\n   前5名最优参数:")
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('score', ascending=False)
    
    for i, row in results_df.head(5).iterrows():
        print(f"\n   [{results_df.head(5).index.get_loc(i)+1}] MA({row['short']}/{row['long']})")
        print(f"      收益率: {row['return']:+.2f}%")
        print(f"      夏普比率: {row['sharpe']:.2f}")
        print(f"      胜率: {row['win_rate']:.1f}%")
        print(f"      最大回撤: {row['max_dd']:.1f}%")
    
    print(f"\n   ✅ 最优参数: MA({best_params['short_period']}/{best_params['long_period']})")
    print(f"      收益率: {best_params['return']:+.2f}%")
    print(f"      夏普比率: {best_params['sharpe_ratio']:.2f}")
    print(f"      胜率: {best_params['win_rate']:.1f}%")
    
    return best_params

def optimize_rsi(data_engine, symbol="000001.SZ"):
    """优化RSI策略参数"""
    print("\n" + "="*70)
    print("  2. 优化RSI策略")
    print("="*70)
    
    df = data_engine.get_stock_data(symbol)
    if df is None or len(df) < 100:
        print("   数据不足，跳过")
        return None
    
    df = calculate_indicators(df)
    
    best_params = None
    best_score = -999
    results = []
    
    oversold_values = [20, 25, 30, 35, 40]
    overbought_values = [60, 65, 70, 75, 80]
    
    total = len(oversold_values) * len(overbought_values)
    
    print(f"   测试 {total} 种参数组合...")
    
    for oversold in oversold_values:
        for overbought in overbought_values:
            if oversold >= overbought - 20:
                continue
            
            strategy = StrategyRsi(oversold=oversold, overbought=overbought)
            signals = strategy.generate_signals(df)
            
            engine = EnhancedBacktestEngine(initial_capital=100000)
            result = engine.run_backtest(df, signals)
            
            if result:
                score = result['sharpe_ratio'] * 2 + result['win_rate_pct'] * 0.5
                
                results.append({
                    'oversold': oversold,
                    'overbought': overbought,
                    'return': result['total_return_pct'],
                    'sharpe': result['sharpe_ratio'],
                    'win_rate': result['win_rate_pct'],
                    'max_dd': result['max_drawdown_pct'],
                    'trades': result['total_trades'],
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = {
                        'oversold': oversold,
                        'overbought': overbought,
                        'return': result['total_return_pct'],
                        'sharpe_ratio': result['sharpe_ratio'],
                        'win_rate': result['win_rate_pct'],
                        'max_drawdown': result['max_drawdown_pct'],
                        'total_trades': result['total_trades']
                    }
    
    print(f"\n   前5名最优参数:")
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('score', ascending=False)
    
    for i, row in results_df.head(5).iterrows():
        print(f"\n   [{results_df.head(5).index.get_loc(i)+1}] RSI({row['oversold']}/{row['overbought']})")
        print(f"      收益率: {row['return']:+.2f}%")
        print(f"      夏普比率: {row['sharpe']:.2f}")
        print(f"      胜率: {row['win_rate']:.1f}%")
        print(f"      最大回撤: {row['max_dd']:.1f}%")
    
    print(f"\n   ✅ 最优参数: RSI({best_params['oversold']}/{best_params['overbought']})")
    print(f"      收益率: {best_params['return']:+.2f}%")
    print(f"      夏普比率: {best_params['sharpe_ratio']:.2f}")
    print(f"      胜率: {best_params['win_rate']:.1f}%")
    
    return best_params

def optimize_bollinger(data_engine, symbol="000001.SZ"):
    """优化布林带策略"""
    print("\n" + "="*70)
    print("  3. 优化布林带策略")
    print("="*70)
    
    df = data_engine.get_stock_data(symbol)
    if df is None or len(df) < 100:
        print("   数据不足，跳过")
        return None
    
    df = calculate_indicators(df)
    
    strategy = StrategyBollinger()
    signals = strategy.generate_signals(df)
    
    engine = EnhancedBacktestEngine(initial_capital=100000)
    result = engine.run_backtest(df, signals)
    
    if result:
        print(f"\n   布林带策略表现:")
        print(f"      收益率: {result['total_return_pct']:+.2f}%")
        print(f"      夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"      胜率: {result['win_rate_pct']:.1f}%")
        print(f"      最大回撤: {result['max_drawdown_pct']:.1f}%")
        
        return {
            'return': result['total_return_pct'],
            'sharpe_ratio': result['sharpe_ratio'],
            'win_rate': result['win_rate_pct'],
            'max_drawdown': result['max_drawdown_pct'],
            'total_trades': result['total_trades']
        }
    
    return None

def compare_strategies(data_engine, symbol="000001.SZ"):
    """对比所有策略"""
    print("\n" + "="*70)
    print("  策略对比总结")
    print("="*70)
    
    df = data_engine.get_stock_data(symbol)
    if df is None:
        return
    
    df = calculate_indicators(df)
    
    strategies = [
        ("均线MA(5/20)", StrategyMaCross(5, 20)),
        ("均线MA(7/25)", StrategyMaCross(7, 25)),
        ("RSI(30/70)", StrategyRsi(30, 70)),
        ("RSI(25/75)", StrategyRsi(25, 75)),
        ("布林带", StrategyBollinger()),
        ("多因子", StrategyMultiFactor()),
    ]
    
    results = []
    
    print("\n   策略对比:")
    print(f"   {'策略':<15} {'收益率':>10} {'夏普':>8} {'胜率':>8} {'最大回撤':>10} {'评分':>8}")
    print("   " + "-"*70)
    
    for name, strategy in strategies:
        signals = strategy.generate_signals(df)
        engine = EnhancedBacktestEngine(initial_capital=100000)
        result = engine.run_backtest(df, signals)
        
        if result:
            score = result['sharpe_ratio'] * 2 + result['win_rate_pct'] * 0.5
            
            print(f"   {name:<15} {result['total_return_pct']:>+9.2f}% {result['sharpe_ratio']:>7.2f} "
                  f"{result['win_rate_pct']:>7.1f}% {result['max_drawdown_pct']:>9.1f}% {score:>7.2f}")
            
            results.append({
                'name': name,
                'strategy': strategy,
                'return': result['total_return_pct'],
                'sharpe': result['sharpe_ratio'],
                'win_rate': result['win_rate_pct'],
                'max_dd': result['max_drawdown_pct'],
                'score': score
            })
    
    print("   " + "-"*70)
    
    results_df = pd.DataFrame(results)
    best = results_df.loc[results_df['score'].idxmax()]
    
    print(f"\n   🏆 最优策略: {best['name']}")
    print(f"      综合评分: {best['score']:.2f}")
    print(f"      收益率: {best['return']:+.2f}%")
    print(f"      夏普比率: {best['sharpe']:.2f}")
    print(f"      胜率: {best['win_rate']:.1f}%")
    
    return best

def main():
    print("="*70)
    print("     量子量化系统 - 策略参数优化")
    print("     优化目标: 提高胜率和夏普比率")
    print("="*70)
    
    print("\n📊 测试股票: 000001.SZ (平安银行)")
    
    print("\n🔄 初始化数据引擎...")
    data_engine = DataEngine()
    print("   ✅ 初始化完成")
    
    optimize_ma_cross(data_engine)
    optimize_rsi(data_engine)
    optimize_bollinger(data_engine)
    compare_strategies(data_engine)
    
    print("\n" + "="*70)
    print("  优化建议")
    print("="*70)
    print("\n基于优化结果，建议采用以下策略组合:")
    print("\n1. 短线策略:")
    print("   - 均线交叉: MA(7/25) 或 MA(5/20)")
    print("   - 适合: 趋势明确的行情")
    print("\n2. 中线策略:")
    print("   - RSI: RSI(30/70) 或 RSI(25/75)")
    print("   - 适合: 震荡行情")
    print("\n3. 组合策略:")
    print("   - 多因子策略 + 布林带")
    print("   - 适合: 综合市场环境")
    
    print("\n" + "="*70)
    print("✅ 参数优化完成！")
    print("="*70)

if __name__ == "__main__":
    main()
