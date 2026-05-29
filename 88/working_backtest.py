#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np

class RealDataBacktester(Backtester):
    def __init__(self, initial_capital=100000, commission=0.0015):
        super().__init__(initial_capital, commission)
        self.data_reader = TDXDataReader()

    def run_backtest_with_real_data(self, market: str, stock_code: str, strategy='combined', years: int = 2):
        print("=" * 80)
        print(f"⚡ 涨停先知 - 真实数据回测 ⚡")
        print("=" * 80)
        print(f"📈 股票: {market.upper()}{stock_code}")
        print(f"📅 回测周期: 近{years}年")
        print(f"💰 初始资金: ¥{self.initial_capital:,}")
        print()

        print("📥 正在加载数据...")
        df = self.data_reader.read_stock_data(market, stock_code, years)
        print(f"✓ 成功加载 {len(df)} 条数据")
        print(f"   时间范围: {df.index.min().date()} ~ {df.index.max().date()}")
        print(f"   最新收盘: ¥{df['close'].iloc[-1]:.2f}")
        print(f"   平均价格: ¥{df['close'].mean():.2f}")
        print()

        print("📊 计算技术指标...")
        df = self.calculate_indicators(df)

        print("🎯 应用策略...")
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

        print(f"   买入信号: {(df['signal'] == 1).sum()} 次")
        print(f"   卖出信号: {(df['signal'] == -1).sum()} 次")
        print()

        print("💹 开始执行回测...")
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
                if cost <= capital and shares > 0:
                    position = shares
                    capital -= cost
                    trades.append({
                        'date': date,
                        'type': 'buy',
                        'price': price,
                        'shares': shares,
                        'cost': cost
                    })
                    print(f"   📈 买入: {date.date()} @ ¥{price:.2f} x {shares}股 = ¥{cost:,.2f}")

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
                print(f"   📉 卖出: {date.date()} @ ¥{price:.2f} x {position}股 = ¥{revenue:,.2f}")
                position = 0

            portfolio_value.append(capital + position * price)

        df = df.copy()
        df['portfolio'] = portfolio_value
        self.results = df
        self.trades = trades

        print(f"\n✓ 回测完成，共执行 {len(trades)} 笔交易")
        print()

        return self.calculate_metrics(df, trades)

if __name__ == "__main__":
    backtester = RealDataBacktester(initial_capital=100000)

    print("\n" + "=" * 80)
    print("🧪 测试: 上证指数 (000001) 真实数据回测")
    print("=" * 80)
    metrics = backtester.run_backtest_with_real_data('sh', '000001', 'combined', 2)
    backtester.print_results(metrics)
