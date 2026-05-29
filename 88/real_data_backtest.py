#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 真实数据回测系统
ZTB Seer - Real Data Backtesting System
使用通达信真实历史数据
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RealDataBacktester(Backtester):
    def __init__(self, initial_capital=100000, commission=0.0015):
        super().__init__(initial_capital, commission)
        self.data_reader = TDXDataReader()

    def load_real_data(self, market: str, stock_code: str, years: int = 3) -> pd.DataFrame:
        """加载真实股票数据"""
        print(f"📥 正在加载 {market.upper()}{stock_code} 近{years}年数据...")

        try:
            df = self.data_reader.read_stock_data(market, stock_code, years)

            if df.empty:
                raise ValueError("数据为空")

            print(f"✅ 成功加载 {len(df)} 条数据")
            print(f"   时间范围: {df.index.min().date()} ~ {df.index.max().date()}")
            print(f"   最新收盘: ¥{df['close'].iloc[-1]:.2f}")

            df = self.calculate_indicators(df)

            return df

        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            print("   尝试使用上证指数数据...")
            df = self.data_reader.get_index_data('000001', years)
            df = self.calculate_indicators(df)
            return df

    def run_real_backtest(self, market: str, stock_code: str, strategy='combined', years: int = 3):
        """使用真实数据运行回测"""
        print("=" * 80)
        print(f"⚡ 涨停先知 - 真实数据回测 ⚡")
        print("=" * 80)
        print(f"📈 股票: {market.upper()}{stock_code}")
        print(f"📅 回测周期: 近{years}年")
        print(f"💰 初始资金: ¥{self.initial_capital:,}")
        print()

        data = self.load_real_data(market, stock_code, years)

        if strategy == 'macd':
            data = self.strategy_macd_gold(data)
            data['signal'] = data['signal_macd']
        elif strategy == 'kdj':
            data = self.strategy_kdj(data)
            data['signal'] = data['signal_kdj']
        elif strategy == 'ma':
            data = self.strategy_ma_crossover(data)
            data['signal'] = data['signal_ma']
        elif strategy == 'rsi':
            data = self.strategy_rsi(data)
            data['signal'] = data['signal_rsi']
        else:
            data = self.strategy_combined(data)

        capital = self.initial_capital
        position = 0
        trades = []
        portfolio_value = []

        for date, row in data.iterrows():
            if pd.isna(row['signal']):
                continue

            price = row['close']

            if row['signal'] == 1 and position == 0:
                shares = int(capital / price / 100) * 100
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

        data['portfolio'] = portfolio_value
        self.results = data
        self.trades = trades

        return self.calculate_metrics(data, trades)

    def find_best_stocks(self, market: str, strategy='combined', years: int = 2, top_n: int = 10):
        """寻找最佳股票"""
        print("=" * 80)
        print(f"⚡ 涨停先知 - 智能选股 ⚡")
        print("=" * 80)
        print(f"📈 市场: {market.upper()}")
        print(f"📅 回测周期: 近{years}年")
        print(f"🎯 筛选数量: Top {top_n}")
        print()

        stocks = self.data_reader.get_available_stocks(market)[:100]

        results = []

        for i, stock in enumerate(stocks, 1):
            try:
                print(f"\r扫描中... {i}/{len(stocks)}", end='', flush=True)

                metrics = self.run_real_backtest(
                    stock['market'],
                    stock['code'],
                    strategy,
                    years
                )

                if metrics and metrics['total_trades'] >= 5:
                    results.append({
                        'code': stock['code'],
                        'name': stock['name'],
                        'market': stock['market'],
                        **metrics
                    })

            except Exception as e:
                continue

        print("\n")

        if not results:
            print("❌ 未找到符合条件的股票")
            return []

        df_results = pd.DataFrame(results)

        print("\n" + "=" * 80)
        print("🏆 最佳股票排行榜")
        print("=" * 80)
        print()

        df_sorted = df_results.sort_values('total_return', ascending=False)

        print(f"{'排名':<4} {'代码':<10} {'名称':<15} {'总收益':<10} {'年化':<10} {'回撤':<10} {'胜率':<8} {'交易次数':<8}")
        print("-" * 80)

        for i, (_, row) in enumerate(df_sorted.head(top_n).iterrows(), 1):
            print(f"{i:<4} {row['market'].upper()}{row['code']:<6} {row['name']:<15} {row['total_return']:>8.2f}% {row['annualized_return']:>8.2f}% {row['max_drawdown']:>8.2f}% {row['win_rate']:>6.2f}% {row['total_trades']:>6.0f}")

        return df_sorted.head(top_n).to_dict('records')

def main():
    backtester = RealDataBacktester(initial_capital=100000)

    print("=" * 80)
    print("⚡ 涨停先知 - 真实数据量化系统 ⚡")
    print("=" * 80)
    print()
    print("请选择功能:")
    print("1. 单只股票回测")
    print("2. 智能选股（寻找最佳股票）")
    print("3. 多策略对比")
    print()

    choice = input("请输入选择 (1/2/3): ").strip()

    if choice == '1':
        print("\n单只股票回测")
        print("-" * 40)
        market = input("请输入市场 (sh/sz/bj): ").strip().lower()
        stock_code = input("请输入股票代码 (如: 600519): ").strip()
        strategy = input("请输入策略 (macd/kdj/ma/rsi/combined): ").strip().lower() or 'combined'
        years = int(input("请输入回测年数 (默认3): ").strip() or '3')

        if not stock_code:
            print("❌ 股票代码不能为空")
            return

        print()
        metrics = backtester.run_real_backtest(market, stock_code, strategy, years)
        backtester.print_results(metrics)

    elif choice == '2':
        print("\n智能选股")
        print("-" * 40)
        market = input("请输入市场 (sh/sz): ").strip().lower() or 'sz'
        strategy = input("请输入策略 (macd/kdj/ma/rsi/combined): ").strip().lower() or 'combined'
        years = int(input("请输入回测年数 (默认2): ").strip() or '2')
        top_n = int(input("请输入筛选数量 (默认10): ").strip() or '10')

        print()
        best_stocks = backtester.find_best_stocks(market, strategy, years, top_n)

        if best_stocks:
            print("\n是否要对最佳股票进行详细回测?")
            choice = input("请输入股票编号 (1-10) 或按回车跳过: ").strip()

            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(best_stocks):
                    stock = best_stocks[idx]
                    print()
                    metrics = backtester.run_real_backtest(
                        stock['market'],
                        stock['code'],
                        strategy,
                        years
                    )
                    backtester.print_results(metrics)

    elif choice == '3':
        print("\n多策略对比")
        print("-" * 40)
        market = input("请输入市场 (sh/sz): ").strip().lower() or 'sz'
        stock_code = input("请输入股票代码 (如: 000001): ").strip() or '000001'
        years = int(input("请输入回测年数 (默认3): ").strip() or '3')

        print()
        print("正在对比各策略表现...")
        print()

        backtester.run_real_backtest(market, stock_code, 'combined', years)
        backtester.compare_strategies()

    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
