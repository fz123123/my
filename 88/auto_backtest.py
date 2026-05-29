#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 自动策略回测系统
ZTB Seer - Auto Backtesting System
"""

from backtester import Backtester

def main():
    print("=" * 80)
    print("⚡ 涨停先知 - 策略回测系统 ⚡")
    print("=" * 80)
    print(f"⏰ 运行时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 初始资金: ¥100,000")
    print("📈 回测周期: 120个交易日")
    print("💹 手续费: 0.15%")
    print("=" * 80)
    print()
    
    backtester = Backtester(initial_capital=100000, commission=0.0015)
    
    # 运行组合策略回测
    print("🚀 运行组合策略回测...")
    print("-" * 40)
    metrics = backtester.run_backtest(strategy='combined')
    
    print("📊 回测结果")
    print("-" * 40)
    print(f"初始资金: ¥{metrics['initial_capital']:,}")
    print(f"最终资金: ¥{metrics['final_value']:,}")
    print(f"总收益率: {metrics['total_return']}%")
    print(f"年化收益率: {metrics['annualized_return']}%")
    print(f"最大回撤: {metrics['max_drawdown']}%")
    print(f"胜率: {metrics['win_rate']}%")
    print(f"交易次数: {metrics['total_trades']}次")
    print(f"平均盈亏: ¥{metrics['avg_profit']:,}")
    print(f"夏普比率: {metrics['sharpe_ratio']}")
    print()
    
    # 显示交易记录
    print("💹 交易记录")
    print("-" * 40)
    for i, trade in enumerate(backtester.trades):
        trade_type = "🟢 买入" if trade['type'] == 'buy' else "🔴 卖出"
        date_str = trade['date'].strftime('%Y-%m-%d')
        print(f"{i+1}. {date_str} {trade_type}")
        print(f"     价格: ¥{trade['price']:.2f} | 数量: {trade['shares']}股")
        if trade['type'] == 'buy':
            print(f"     成本: ¥{trade['cost']:.2f}")
        else:
            print(f"     收入: ¥{trade['revenue']:.2f}")
    print()
    
    # 收益曲线
    print("📉 收益曲线")
    print("-" * 40)
    portfolio = backtester.results['portfolio']
    normalized = (portfolio - portfolio.min()) / (portfolio.max() - portfolio.min()) * 25
    dates = backtester.results.index
    step = max(1, len(dates) // 20)
    
    for i in range(0, len(dates), step):
        date_str = dates[i].strftime('%m-%d')
        bar = "█" * int(normalized.iloc[i])
        value = f"¥{portfolio.iloc[i]:,.0f}"
        print(f"{date_str}: {bar} {value}")
    print()
    
    # 多策略对比
    print("=" * 80)
    print("🏆 策略对比分析")
    print("=" * 80)
    print()
    
    strategies = ['macd', 'kdj', 'ma', 'rsi', 'combined']
    results = {}
    
    for strategy in strategies:
        metrics = backtester.run_backtest(strategy)
        results[strategy] = metrics
        
    # 排序并显示
    sorted_results = sorted(results.items(), key=lambda x: -x[1]['total_return'])
    
    print(f"{'策略':<10} {'总收益':<10} {'年化':<10} {'最大回撤':<10} {'胜率':<8} {'交易次数':<8} {'夏普比率':<8}")
    print("-" * 70)
    
    for name, metrics in sorted_results:
        print(f"{name.upper():<10} {metrics['total_return']:>8}%   {metrics['annualized_return']:>8}%   {metrics['max_drawdown']:>8}%   {metrics['win_rate']:>6}%   {metrics['total_trades']:>8}   {metrics['sharpe_ratio']:>8}")
    
    print()
    best_return = sorted_results[0]
    print(f"🥇 最优策略: {best_return[0].upper()}")
    print(f"   总收益率: {best_return[1]['total_return']}%")
    print(f"   年化收益: {best_return[1]['annualized_return']}%")
    print(f"   最大回撤: {best_return[1]['max_drawdown']}%")
    print(f"   胜率: {best_return[1]['win_rate']}%")
    print()
    
    print("=" * 80)
    print("✅ 回测完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()