#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 你的自选股分析系统
ZTB Seer - Your Watchlist Analysis
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime

class YourWatchlistAnalyzer:
    def __init__(self):
        self.tdx_reader = TDXDataReader()

        self.your_watchlist = [
            ('sh', '600130', '波导股份'),
            ('sh', '601138', '工业富联'),
            ('sz', '301275', '汉翔科技'),
            ('sh', '603118', '共进股份'),
            ('sh', '603660', '苏州科达'),
            ('sz', '002079', '苏州固锝'),
            ('sh', '603688', '石英股份'),
            ('sh', '603778', '国晟科技'),
            ('sh', '603681', '永冠新材'),
            ('sz', '002222', '福晶科技'),
            ('sh', '603045', '福达合金'),
            ('sz', '001339', '智微智能'),
            ('sz', '002276', '万马股份'),
            ('sh', '603738', '泰晶科技'),
            ('sz', '002918', '蒙娜丽莎'),
            ('sh', '603007', '花王股份'),
            ('sh', '600530', '交大昂立'),
            ('sh', '600076', '唐饮新材'),
            ('sh', '600736', '苏州高新'),
            ('sz', '002229', '鸿博股份'),
            ('sh', '601991', '大唐发电'),
            ('sz', '002685', '华东重机'),
            ('sz', '002491', '通鼎互联'),
            ('sz', '002655', '共达电声'),
            ('sz', '000977', '浪潮信息'),
            ('sh', '605289', '罗曼股份'),
        ]

    def analyze_all(self):
        print("="*120)
        print("ZTBS - YOUR WATCHLIST ANALYSIS")
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)

        print(f"\n[ANALYZING YOUR {len(self.your_watchlist)} WATCHLIST STOCKS...")
        print("-"*120)

        all_results = []

        for market, code, name in self.your_watchlist:
            try:
                result = self.analyze_single(market, code, name)
                if result:
                    all_results.append(result)
                    print(f"[OK] {name} ({market.upper()}{code}) - Price: {result['latest_price']:.2f}")
            except Exception as e:
                print(f"[ERR] {name} ({market.upper()}{code})")

        if all_results:
            self.print_summary(all_results)

    def analyze_single(self, market, code, name):
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)
            if df.empty or len(df) < 50:
                return None

            backtester = Backtester()
            df = backtester.calculate_indicators(df)
            df = backtester.strategy_combined(df)

            buy_signals = (df['signal'] == 1).sum()
            sell_signals = (df['signal'] == -1).sum()
            current_signal = df['signal'].iloc[-1]

            backtest_result = self._backtest(df)

            return {
                'name': name,
                'code': code,
                'market': market,
                'latest_price': df['close'].iloc[-1],
                'latest_date': df.index[-1].date(),
                'current_signal': current_signal,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'backtest_return': backtest_result['total_return'] if backtest_result else 0,
                'data_count': len(df),
            }
        except Exception as e:
            return None

    def _backtest(self, df):
        try:
            capital = 100000
            position = 0

            for date, row in df.iterrows():
                if pd.isna(row['signal']):
                    continue

                price = row['close']

                if row['signal'] == 1 and position == 0:
                    max_shares = int(capital / price)
                    shares = (max_shares // 100) * 100
                    cost = shares * price * 1.0015
                    if cost <= capital and shares >= 100:
                        position = shares
                        capital -= cost

                elif row['signal'] == -1 and position > 0:
                    revenue = position * price * 0.9985
                    capital += revenue
                    position = 0

            final_value = capital + position * df['close'].iloc[-1]
            total_return = (final_value - 100000) / 100000 * 100

            return {
                'total_return': total_return,
                'final_value': final_value,
            }
        except Exception:
            return None

    def print_summary(self, all_results):
        df_results = pd.DataFrame(all_results)
        df_results = df_results.sort_values('backtest_return', ascending=False)

        print("\n" + "="*120)
        print("SUMMARY - YOUR WATCHLIST PERFORMANCE")
        print("="*120)

        print(f"\n{'RANK':<5} {'NAME':<12} {'CODE':<12} {'PRICE':<12} {'RETURN':<12} {'SIGNAL':<12} {'BUY_SIG':<10} {'SELL_SIG':<10}")
        print("-"*100)

        for i, (idx, row) in enumerate(df_results.iterrows(), 1):
            return_str = f"{row['backtest_return']:+.2f}%"
            signal_str = ""

            if row['current_signal'] == 1:
                signal_str = "[BUY]"
            elif row['current_signal'] == -1:
                signal_str = "[SELL]"
            else:
                signal_str = "[HOLD]"

            print(f"{i:<5} {row['name']:<12} {row['market'].upper()}{row['code']:<12} {row['latest_price']:<12.2f} {return_str:<12} {signal_str:<12} {row['buy_signals']:<10} {row['sell_signals']:<10}")

        buy_signals_now = df_results[df_results['current_signal'] == 1]
        sell_signals_now = df_results[df_results['current_signal'] == -1]

        print("\n" + "="*120)

        if len(buy_signals_now) > 0:
            print("\n[CURRENT BUY SIGNALS]")
            print("-"*120)
            for i, (idx, row) in enumerate(buy_signals_now.iterrows(), 1):
                print(f"{i}. {row['name']} ({row['market'].upper()}{row['code']}) - Price: {row['latest_price']:.2f}")

        if len(sell_signals_now) > 0:
            print("\n[CURRENT SELL SIGNALS]")
            print("-"*120)
            for i, (idx, row) in enumerate(sell_signals_now.iterrows(), 1):
                print(f"{i}. {row['name']} ({row['market'].upper()}{row['code']}) - Price: {row['latest_price']:.2f}")

        top_5 = df_results.head(5)
        print("\n" + "="*120)
        print("[TOP 5 BEST PERFORMERS (2-YEAR BACKTEST)")
        print("="*120)
        for i, (idx, row) in enumerate(top_5.iterrows(), 1):
            print(f"{i}. {row['name']} ({row['market'].upper()}{row['code']}) - Return: {row['backtest_return']:+.2f}% - Price: {row['latest_price']:.2f}")

        print("\n" + "="*120)
        print(f"Analysis complete! {len(all_results)}/{len(self.your_watchlist)} stocks analyzed.")
        print("="*120)

if __name__ == "__main__":
    analyzer = YourWatchlistAnalyzer()
    analyzer.analyze_all()
