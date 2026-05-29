#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 盯盘股票 详细回测分析系统
ZTB Seer - Detailed Backtest Analysis
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime

class WatchlistAnalyzer:
    def __init__(self):
        self.tdx_reader = TDXDataReader()

        self.stock_list = [
            ('sz', '300750', '宁德时代'),
            ('sz', '002371', '北方华创'),
            ('sh', '688981', '中芯国际'),
            ('sh', '600276', '恒瑞医药'),
            ('sh', '601318', '中国平安'),
            ('sh', '600030', '中信证券'),
            ('sh', '600036', '招商银行'),
            ('sz', '000333', '美的集团'),
        ]

    def detailed_backtest(self, market, code, name):
        """对单只股票进行详细回测"""
        try:
            print(f"\n{'='*100}")
            print(f"🎯 详细分析: {name} ({market.upper()}{code})")
            print(f"{'='*100}")

            df = self.tdx_reader.read_stock_data(market, code, 2)
            if df.empty or len(df) < 100:
                print("✗ 数据不足")
                return None

            print(f"\n📊 数据概况:")
            print(f"   时间范围: {df.index.min().date()} ~ {df.index.max().date()}")
            print(f"   数据点: {len(df)} 条")
            print(f"   起始价: ¥{df['close'].iloc[0]:.2f}")
            print(f"   最新价: ¥{df['close'].iloc[-1]:.2f}")
            print(f"   价格波动: {(df['close'].iloc[-1] - df['close'].iloc[0])/df['close'].iloc[0]*100:+.2f}%")

            backtester = Backtester()
            df = backtester.calculate_indicators(df)
            df = backtester.strategy_combined(df)

            buy_count = (df['signal'] == 1).sum()
            sell_count = (df['signal'] == -1).sum()
            print(f"\n📡 信号统计:")
            print(f"   买入信号: {buy_count} 次")
            print(f"   卖出信号: {sell_count} 次")

            capital = 100000
            position = 0
            trades = []
            portfolio_value = []

            print(f"\n💹 完整交易记录:")
            print(f"   {'序号':<4} {'日期':<12} {'类型':<4} {'价格':<10} {'数量':<8} {'金额':<15} {'盈亏':<12}")
            print(f"   {''.join(['-'] * 70)}")

            for date, row in df.iterrows():
                if pd.isna(row['signal']):
                    portfolio_value.append(capital + position * row['close'])
                    continue

                price = row['close']

                if row['signal'] == 1 and position == 0:
                    max_shares = int(capital / price)
                    shares = (max_shares // 100) * 100
                    cost = shares * price * 1.0015
                    if cost <= capital and shares >= 100:
                        position = shares
                        capital -= cost
                        trades.append({'date': date, 'type': 'buy', 'price': price, 'shares': shares, 'cost': cost})
                        print(f"   {len(trades):<4} {date.date():<12} 买入  ¥{price:<9.2f} {shares:<8} ¥{cost:>12,.2f}")

                elif row['signal'] == -1 and position > 0:
                    revenue = position * price * 0.9985
                    prev_cost = trades[-1]['cost']
                    profit = revenue - prev_cost
                    profit_pct = profit / prev_cost * 100
                    capital += revenue
                    trades.append({'date': date, 'type': 'sell', 'price': price, 'shares': position, 'revenue': revenue})
                    profit_str = f"+{profit:,.2f}" if profit > 0 else f"{profit:,.2f}"
                    print(f"   {len(trades):<4} {date.date():<12} 卖出  ¥{price:<9.2f} {position:<8} ¥{revenue:>12,.2f} {profit_str} ({profit_pct:+.2f}%)")
                    position = 0

                portfolio_value.append(capital + position * price)

            df = df.copy()
            df['portfolio'] = portfolio_value

            final_value = capital + position * df['close'].iloc[-1]
            total_return = (final_value - 100000) / 100000 * 100

            print(f"\n{'='*100}")
            print("📈 回测结果汇总")
            print(f"{'='*100}")
            print(f"   初始资金: ¥100,000")
            print(f"   最终资金: ¥{final_value:,.2f}")
            print(f"   总收益: {total_return:+.2f}%")
            print(f"   交易次数: {len(trades)//2} 次")

            if trades:
                win_count = 0
                total_profit = 0
                for i in range(0, len(trades), 2):
                    if i + 1 < len(trades):
                        profit = trades[i+1]['revenue'] - trades[i]['cost']
                        total_profit += profit
                        if profit > 0:
                            win_count += 1
                if (len(trades)//2) > 0:
                    win_rate = win_count / (len(trades)//2) * 100
                    avg_profit = total_profit / (len(trades)//2)
                    print(f"   胜率: {win_rate:.2f}%")
                    print(f"   平均盈亏: ¥{avg_profit:,.2f}")

            return {
                'name': name,
                'code': code,
                'market': market,
                'total_return': total_return,
                'total_trades': len(trades)//2,
            }

        except Exception as e:
            print(f"✗ 分析失败: {e}")
            return None

    def run(self):
        print("="*100)
        print("⚡ 涨停先知 - 盯盘股票详细回测分析系统 ⚡")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        print("\n🔍 正在分析你关注的股票列表...")

        all_results = []
        for market, code, name in self.stock_list:
            result = self.detailed_backtest(market, code, name)
            if result:
                all_results.append(result)

        if all_results:
            print("\n" + "="*100)
            print("🏆 所有股票表现汇总")
            print(f"{'='*100}")
            df_summary = pd.DataFrame(all_results)
            df_summary = df_summary.sort_values('total_return', ascending=False)

            print(f"\n{'排名':<4} {'股票':<12} {'代码':<10} {'总收益':<12} {'交易次数':<10}")
            print(f"{''.join(['-'] * 60)}")
            for i, (idx, row) in enumerate(df_summary.iterrows(), 1):
                return_color = "🟢" if row['total_return'] > 0 else "🔴"
                print(f"{i:<4} {row['name']:<12} {row['market'].upper()}{row['code']:<10} {return_color}{row['total_return']:>+9.2f}% {row['total_trades']:<10}")

            print(f"\n{'='*100}")
            print("✅ 分析完成！")
            print(f"{'='*100}")

if __name__ == "__main__":
    analyzer = WatchlistAnalyzer()
    analyzer.run()
