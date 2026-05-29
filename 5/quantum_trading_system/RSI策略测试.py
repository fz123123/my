#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSI(35/80)策略测试 - 构造测试数据验证策略有效性
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategies.basic_strategies import StrategyRsi
from backtest.enhanced_engine import EnhancedBacktestEngine
from core.indicators import calculate_indicators

def generate_test_data(days=365, initial_price=100, trend='random', volatility=0.02):
    """
    生成测试数据
    
    参数:
    - days: 数据天数
    - initial_price: 初始价格
    - trend: 'up' (上涨), 'down' (下跌), 'sideways' (震荡), 'random' (随机)
    - volatility: 波动率
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    prices = [initial_price]
    
    if trend == 'up':
        for i in range(1, days):
            change = np.random.normal(0.0005, volatility)
            prices.append(prices[-1] * (1 + change))
    
    elif trend == 'down':
        for i in range(1, days):
            change = np.random.normal(-0.0005, volatility)
            prices.append(prices[-1] * (1 + change))
    
    elif trend == 'sideways':
        for i in range(1, days):
            change = np.random.normal(0, volatility * 0.8)
            prices.append(prices[-1] * (1 + change))
    
    else:  # random
        for i in range(1, days):
            change = np.random.normal(0, volatility)
            prices.append(prices[-1] * (1 + change))
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, volatility/2))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, volatility/2))) for p in prices],
        'close': prices,
        'volume': [1000000 * (1 + abs(np.random.normal(0, 0.3))) for _ in prices]
    })
    
    df.set_index('date', inplace=True)
    return df

def generate_realistic_data(days=365, initial_price=100):
    """
    生成更真实的市场数据 - 包含多个阶段
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    prices = []
    current_price = initial_price
    
    for i in range(days):
        if i < days * 0.2:
            change = np.random.normal(0.001, 0.015)
        elif i < days * 0.4:
            change = np.random.normal(-0.0005, 0.02)
        elif i < days * 0.6:
            change = np.random.normal(0.0008, 0.018)
        elif i < days * 0.8:
            change = np.random.normal(0.0003, 0.025)
        else:
            change = np.random.normal(0.001, 0.02)
        
        current_price = current_price * (1 + change)
        prices.append(current_price)
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
        'close': prices,
        'volume': [1000000 * (1 + abs(np.random.normal(0, 0.2))) for _ in prices]
    })
    
    df.set_index('date', inplace=True)
    return df

def test_rsi_strategy(df, strategy_name, oversold=35, overbought=80):
    """测试RSI策略"""
    print(f"\n{'='*70}")
    print(f"  {strategy_name}")
    print(f"{'='*70}")
    
    print(f"\n   数据概览:")
    print(f"   - 数据条数: {len(df)} 天")
    print(f"   - 起始价格: {df['close'].iloc[0]:.2f}")
    print(f"   - 结束价格: {df['close'].iloc[-1]:.2f}")
    print(f"   - 价格变化: {((df['close'].iloc[-1]/df['close'].iloc[0])-1)*100:+.2f}%")
    
    df = calculate_indicators(df)
    
    strategy = StrategyRsi(oversold=oversold, overbought=overbought)
    signals = strategy.generate_signals(df)
    
    buy_signals = (signals == 1).sum()
    sell_signals = (signals == -1).sum()
    
    print(f"\n   信号统计:")
    print(f"   - 买入信号: {buy_signals} 次")
    print(f"   - 卖出信号: {sell_signals} 次")
    
    engine = EnhancedBacktestEngine(initial_capital=100000)
    result = engine.run_backtest(df, signals)
    
    if result:
        print(f"\n   回测结果:")
        print(f"   📈 收益指标:")
        print(f"      总收益率: {result['total_return_pct']:+.2f}%")
        print(f"      夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"   📊 风险指标:")
        print(f"      最大回撤: {result['max_drawdown_pct']:.2f}%")
        print(f"   🎯 交易统计:")
        print(f"      总交易次数: {result['total_trades']}")
        print(f"      胜率: {result['win_rate_pct']:.1f}%")
        
        return result
    
    return None

def main():
    print("="*70)
    print("     RSI(35/80) 策略测试")
    print("     构造多种市场环境验证策略有效性")
    print("="*70)
    
    results = {}
    
    print("\n\n" + "🔧 " + "="*68)
    print("   测试场景1: 上涨趋势市场")
    print("="*70)
    df_up = generate_test_data(days=365, initial_price=100, trend='up', volatility=0.015)
    result_up = test_rsi_strategy(df_up, "上涨趋势市场 - RSI(35/80)")
    results['上涨趋势'] = result_up
    
    print("\n\n" + "🔧 " + "="*68)
    print("   测试场景2: 下跌趋势市场")
    print("="*70)
    df_down = generate_test_data(days=365, initial_price=100, trend='down', volatility=0.015)
    result_down = test_rsi_strategy(df_down, "下跌趋势市场 - RSI(35/80)")
    results['下跌趋势'] = result_down
    
    print("\n\n" + "🔧 " + "="*68)
    print("   测试场景3: 震荡市场")
    print("="*70)
    df_sideways = generate_test_data(days=365, initial_price=100, trend='sideways', volatility=0.02)
    result_sideways = test_rsi_strategy(df_sideways, "震荡市场 - RSI(35/80)")
    results['震荡市场'] = result_sideways
    
    print("\n\n" + "🔧 " + "="*68)
    print("   测试场景4: 真实市场模拟")
    print("="*70)
    df_realistic = generate_realistic_data(days=365, initial_price=100)
    result_realistic = test_rsi_strategy(df_realistic, "真实市场模拟 - RSI(35/80)")
    results['真实市场'] = result_realistic
    
    print("\n\n" + "="*70)
    print("     综合对比报告")
    print("="*70)
    
    print("\n\n📊 各市场环境下的策略表现:")
    print(f"\n   {'市场环境':<12} {'收益率':>10} {'夏普比率':>8} {'胜率':>8} {'最大回撤':>10} {'评分':>8}")
    print("   " + "-"*70)
    
    for name, result in results.items():
        if result:
            score = result['sharpe_ratio'] * 2 + result['win_rate_pct'] * 0.5
            print(f"   {name:<12} {result['total_return_pct']:>+9.2f}% {result['sharpe_ratio']:>7.2f} "
                  f"{result['win_rate_pct']:>7.1f}% {result['max_drawdown_pct']:>9.2f}% {score:>7.2f}")
    
    print("\n\n" + "="*70)
    print("     结论与建议")
    print("="*70)
    
    valid_results = {k: v for k, v in results.items() if v}
    
    if valid_results:
        avg_return = np.mean([r['total_return_pct'] for r in valid_results.values()])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in valid_results.values()])
        avg_win_rate = np.mean([r['win_rate_pct'] for r in valid_results.values()])
        
        print(f"\n   平均表现:")
        print(f"   - 平均收益率: {avg_return:+.2f}%")
        print(f"   - 平均夏普比率: {avg_sharpe:.2f}")
        print(f"   - 平均胜率: {avg_win_rate:.1f}%")
        
        print(f"\n   💡 结论:")
        if avg_return > 0 and avg_sharpe > 0.5:
            print(f"   ✅ RSI(35/80) 策略表现优秀")
            print(f"   ✅ 在多种市场环境下都能获得正收益")
            print(f"   ✅ 夏普比率超过0.5，风险调整后收益良好")
        elif avg_return > 0:
            print(f"   ⚠️ RSI(35/80) 策略基本有效")
            print(f"   ⚠️ 建议配合止损止盈使用")
        else:
            print(f"   ❌ RSI(35/80) 策略在当前参数下表现不佳")
            print(f"   ❌ 建议调整参数或更换策略")
        
        best_name = max(valid_results.keys(), key=lambda k: valid_results[k]['sharpe_ratio'])
        print(f"\n   🏆 最佳表现市场: {best_name}")
    
    print("\n" + "="*70)
    print("✅ RSI(35/80) 策略测试完成！")
    print("="*70)

if __name__ == "__main__":
    main()
