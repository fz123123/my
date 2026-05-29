#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 最佳股票详情回测
ZTB Seer - Top Stock Detailed Backtest
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np

class DetailedBacktester(Backtester):
    def __init__(self, initial_capital=100000, commission=0.0015):
        super().__init__(initial_capital, commission)
        self.data_reader = TDXDataReader()

    def run_detailed_backtest(self, market: str, stock_code: str, strategy='combined', years: int = 2):
        print("=" * 80)
        print(f"⚡ {market.upper()}{stock_code} - 详细回测")
        print("=" * 80)

        df = self.data_reader.read_stock_data(market, stock_code, years)
        print(f"\n📥 数据加载成功: {len(df)} 条数据")
        print(f"   时间范围: {df.index.min().date()} ~ {df.index.max().date()}")
        print(f"   起始价格: ¥{df['close'].iloc[0]:.2f}")
        print(f"   结束价格: ¥{df['close'].iloc[-1]:.2f}")
        print(f"   价格波动: {(df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100:.2f}%\n")

        df = self.calculate_indicators(df)
        df = self.strategy_combined(df)

        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()

        print(f"📊 策略信号统计:")
        print(f"   买入信号: {buy_signals} 次")
        print(f"   卖出信号: {sell_signals} 次\n")

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
        self.results = df
        self.trades = trades

        metrics = self.calculate_metrics(df, trades)

        print("💹 完整交易记录:")
        print("-" * 80)
        print(f"{'编号':<4} {'日期':<12} {'类型':<5} {'价格':<10} {'数量':<10} {'金额':<15} {'盈亏':<12}")
        print("-" * 80)

        for i, trade in enumerate(trades, 1):
            if i % 2 == 1:
                print(f"{i:<4} {trade['date'].date()} {'买入':<5} ¥{trade['price']:<8.2f} {trade['shares']:<10} ¥{trade['cost']:>13,.2f}")
            else:
                prev_buy = trades[i-2]
                profit = trade['revenue'] - prev_buy['cost']
                profit_pct = profit / prev_buy['cost'] * 100
                profit_str = f"+{profit:,.2f}" if profit > 0 else f"{profit:,.2f}"
                print(f"{i:<4} {trade['date'].date()} {'卖出':<5} ¥{trade['price']:<8.2f} {trade['shares']:<10} ¥{trade['revenue']:>13,.2f} {profit_str} ({profit_pct:+.2f}%)")

        print()
        print("=" * 80)
        self.print_results(metrics)
        print()

def main():
    backtester = DetailedBacktester(initial_capital=100000)

    print("\n" + "=" * 80)
    print("🏆 最佳股票详细回测")
    print("=" * 80)

    top_stocks = [
        ('sz', '000034', "SZ000034 - 收益 +192.96%"),
        ('sz', '000007', "SZ000007 - 收益 +117.91%"),
        ('sz', '000014', "SZ000014 - 收益 +76.76%"),
    ]

    for market, code, name in top_stocks:
        print(f"\n{'=' * 80}")
        print(f"🎯 {name}")
        print(f"{'=' * 80}\n")
        backtester.run_detailed_backtest(market, code, 'combined', 2)

    print("\n" + "=" * 80)
    print("✅ 详细回测完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
