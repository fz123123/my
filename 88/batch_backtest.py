#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 批量回测系统
ZTB Seer - Batch Backtesting System
回测多只股票并进行综合分析
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime
import time

class BatchBacktester(Backtester):
    def __init__(self, initial_capital=100000, commission=0.0015):
        super().__init__(initial_capital, commission)
        self.data_reader = TDXDataReader()
        self.results = []

    def backtest_single_stock(self, market: str, stock_code: str, strategy='combined', years: int = 2):
        try:
            df = self.data_reader.read_stock_data(market, stock_code, years)

            if df.empty or len(df) < 100:
                return None

            df = self.calculate_indicators(df)

            if strategy == 'macd':
                df = self.strategy_macd_gold(df)
                df['signal'] = df['signal_macd']
            elif strategy == 'kdj':
                df = self.strategy_kdj(df)
                df['signal'] = df['signal_kdj']
            elif strategy == 'ma':
                df = self.strategy_ma_crossover(df)
                df['signal'] = df['signal_ma']
            elif strategy == 'rsi':
                df = self.strategy_rsi(df)
                df['signal'] = df['signal_rsi']
            else:
                df = self.strategy_combined(df)

            capital = self.initial_capital
            position = 0
            trades = []
            portfolio_value = []

            for date, row in df.iterrows():
                if pd.isna(row['signal']):
                    portfolio_value.append(capital + position * row['close'])
                    continue

                price = row['close']

                if row['signal'] == 1 and position == 0:
                    max_shares = int(capital / price)
                    shares = (max_shares // 100) * 100
                    cost = shares * price * (1 + self.commission)

                    if cost <= capital and shares >= 100:
                        position = shares
                        capital -= cost
                        trades.append({
                            'date': date,
                            'type': 'buy',
                            'price': price,
                            'shares': shares,
                            'cost': cost
                        })

                elif row['signal'] == -1 and position > 0:
                    revenue = position * price * (1 - self.commission)
                    capital += revenue
                    trades.append({
                        'date': date,
                        'type': 'sell',
                        'price': price,
                        'shares': position,
                        'revenue': revenue
                    })
                    position = 0

                portfolio_value.append(capital + position * price)

            df = df.copy()
            df['portfolio'] = portfolio_value
            self.results.append(df)
            self.trades = trades

            metrics = self.calculate_metrics(df, trades)
            metrics['stock_code'] = f"{market.upper()}{stock_code}"
            metrics['stock_name'] = self.data_reader.get_stock_name(stock_code, market)
            metrics['market'] = market
            metrics['code'] = stock_code
            metrics['data_points'] = len(df)
            metrics['avg_price'] = df['close'].mean()
            metrics['latest_price'] = df['close'].iloc[-1]
            metrics['start_date'] = df.index.min().date()
            metrics['end_date'] = df.index.max().date()

            return metrics

        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return None

def main():
    print("=" * 80)
    print("🚀 涨停先知 - 批量回测系统")
    print("=" * 80)
    print()

    backtester = BatchBacktester(initial_capital=100000)
    reader = TDXDataReader()

    print("📥 获取股票列表...")
    sz_stocks = reader.get_available_stocks('sz')[:30]
    sh_stocks = reader.get_available_stocks('sh')[:30]
    all_stocks = sz_stocks + sh_stocks

    print(f"✓ 找到 {len(all_stocks)} 只股票 (深圳+上海市场)")
    print()

    print("💹 开始批量回测...")
    print("=" * 80)

    results = []
    start_time = time.time()

    for i, stock in enumerate(all_stocks, 1):
        progress = f"[{i:3d}/{len(all_stocks)}]"
        print(f"{progress} 回测 {stock['market'].upper()}{stock['code']}...", end="", flush=True)

        metrics = backtester.backtest_single_stock(stock['market'], stock['code'], 'combined', 2)

        if metrics:
            results.append(metrics)
            status = "✓"
            if metrics['total_return'] > 0:
                status += f" (+{metrics['total_return']:.1f}%)"
            elif metrics['total_return'] < 0:
                status += f" ({metrics['total_return']:.1f}%)"
            else:
                status += " (0.0%)"
            print(f" {status}")
        else:
            print(" ✗ (无有效交易)")

    end_time = time.time()
    elapsed = end_time - start_time

    print()
    print("=" * 80)
    print("📊 批量回测完成！")
    print(f"   测试股票: {len(all_stocks)} 只")
    print(f"   有效回测: {len(results)} 只")
    print(f"   耗时: {elapsed:.1f} 秒")
    print("=" * 80)
    print()

    if results:
        df_results = pd.DataFrame(results)

        print("🏆 综合排行榜 - 按收益率排序")
        print("-" * 130)
        print(f"{'排名':<4} {'股票代码':<12} {'股票名称':<15} {'总收益':<10} {'年化':<10} {'最大回撤':<12} {'胜率':<10} {'交易次数':<10} {'夏普比率':<12}")
        print("-" * 130)

        df_sorted = df_results.sort_values('total_return', ascending=False)

        for i, (idx, row) in enumerate(df_sorted.head(20).iterrows(), 1):
            return_color = "📈" if row['total_return'] > 0 else "📉"
            print(f"{i:<4} {row['stock_code']:<12} {row['stock_name']:<15} {return_color}{row['total_return']:>7.2f}% {row['annualized_return']:>7.2f}% {row['max_drawdown']:>8.2f}% {row['win_rate']:>7.2f}% {row['total_trades']:>8} {row['sharpe_ratio']:>10.2f}")

        print()
        print("=" * 130)
        print()

        print("📈 盈利股票统计")
        print("-" * 80)
        profitable = df_results[df_results['total_return'] > 0]
        print(f"   盈利股票: {len(profitable)} 只 ({len(profitable)/len(results)*100:.1f}%)")
        if len(profitable) > 0:
            print(f"   平均收益: {profitable['total_return'].mean():.2f}%")
            print(f"   最高收益: {profitable['total_return'].max():.2f}%")
            print(f"   最低收益: {profitable['total_return'].min():.2f}%")

        print()
        print("📉 亏损股票统计")
        print("-" * 80)
        losing = df_results[df_results['total_return'] < 0]
        print(f"   亏损股票: {len(losing)} 只 ({len(losing)/len(results)*100:.1f}%)")
        if len(losing) > 0:
            print(f"   平均亏损: {losing['total_return'].mean():.2f}%")
            print(f"   最大亏损: {losing['total_return'].min():.2f}%")

        print()
        print("📊 综合统计")
        print("-" * 80)
        print(f"   平均收益: {df_results['total_return'].mean():.2f}%")
        print(f"   平均胜率: {df_results['win_rate'].mean():.2f}%")
        print(f"   平均夏普: {df_results['sharpe_ratio'].mean():.2f}")
        print(f"   平均交易次数: {df_results['total_trades'].mean():.1f} 次")
        print()

        output_file = "C:\\Users\\Administrator\\Documents\\trae_projects\\88\\batch_backtest_results.csv"
        df_sorted.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"💾 详细结果已保存到: {output_file}")
        print()

        print("=" * 130)
        print("🎯 表现最佳的5只股票:")
        print("-" * 130)
        for i, (idx, row) in enumerate(df_sorted.head(5).iterrows(), 1):
            print(f"\n{i}. {row['stock_code']} - {row['stock_name']}")
            print(f"   总收益: {row['total_return']:.2f}%  | 年化: {row['annualized_return']:.2f}%")
            print(f"   最大回撤: {row['max_drawdown']:.2f}%  | 胜率: {row['win_rate']:.2f}%  | 交易: {row['total_trades']} 次")
            print(f"   夏普比率: {row['sharpe_ratio']:.2f}")

        print()
        print("=" * 130)

    else:
        print("❌ 没有产生有效回测结果的股票")
        print("   可能原因: 数据不足或策略过于保守")

if __name__ == "__main__":
    main()
