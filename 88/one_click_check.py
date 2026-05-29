#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 一键信号检查系统
ZTB Seer - One-Click Signal Check
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime

class OneClickSignalCheck:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.backtester = Backtester()
        self.alert_file = "C:\\Users\\Administrator\\Documents\\trae_projects\\88\\signals_today.txt"

        self.all_stocks = [
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
            ('sz', '002361', '神剑股份'),
            ('sz', '002291', '遥望科技'),
            ('sh', '605399', '晨光新材'),
            ('sh', '600152', '维科技术'),
            ('sz', '002602', '世纪华通'),
            ('sh', '603618', '杭电股份'),
            ('sh', '600584', '长电科技'),
            ('sz', '002363', '隆基机械'),
            ('sh', '600900', '长江电力'),
            ('sh', '601985', '中国核电'),
            ('sh', '605299', '舒华体育'),
            ('sz', '002553', '南方精工'),
            ('sh', '601088', '中国神华'),
            ('sz', '002565', '顺灏股份'),
            ('sh', '603890', '春秋电子'),
            ('sh', '603933', '睿能科技'),
            ('sz', '002217', '合力泰'),
        ]

    def run_check(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("="*120)
        print("ZTB SEER - YOUR SIGNALS")
        print(f"CHECK TIME: {timestamp}")
        print("="*120)

        all_results = []
        buy_signals = []
        sell_signals = []

        print(f"\n[ANALYZING {len(self.all_stocks)} STOCKS...]\n")

        for market, code, name in self.all_stocks:
            try:
                result = self.analyze_single(market, code, name)
                if result:
                    all_results.append(result)
                    if result['current_signal'] == 1:
                        buy_signals.append(result)
                    elif result['current_signal'] == -1:
                        sell_signals.append(result)
            except Exception:
                pass

        self.print_results(all_results, buy_signals, sell_signals, timestamp)
        self.save_alerts(buy_signals, sell_signals, timestamp)

        return buy_signals, sell_signals

    def analyze_single(self, market, code, name):
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)
            if df.empty or len(df) < 50:
                return None

            df = self.backtester.calculate_indicators(df)
            df = self.backtester.strategy_combined(df)

            current_signal = df['signal'].iloc[-1]
            previous_signal = df['signal'].iloc[-2] if len(df) > 2 else 0
            new_signal = current_signal != previous_signal

            backtest_result = self._backtest(df)

            return {
                'name': name,
                'code': code,
                'market': market,
                'latest_price': df['close'].iloc[-1],
                'latest_date': df.index[-1].date(),
                'current_signal': current_signal,
                'previous_signal': previous_signal,
                'new_signal': new_signal,
                'backtest_return': backtest_result['total_return'] if backtest_result else 0,
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

            return {'total_return': total_return, 'final_value': final_value}
        except Exception:
            return None

    def print_results(self, all_results, buy_signals, sell_signals, timestamp):
        df_results = pd.DataFrame(all_results)
        df_results = df_results.sort_values('backtest_return', ascending=False)

        print(f"\n{'='*120}")
        print(f"[SIGNAL SUMMARY] Total: {len(all_results)}, Buy: {len(buy_signals)}, Sell: {len(sell_signals)}")
        print(f"{'='*120}")

        if buy_signals:
            print(f"\n[BUY SIGNALS - {len(buy_signals)} stocks]")
            print("-"*120)
            for i, signal in enumerate(buy_signals, 1):
                new_mark = " [NEW!]" if signal['new_signal'] else ""
                print(f"{i:2d}. {signal['name']:12s} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:8.2f} - Return: {signal['backtest_return']:+8.2f}%{new_mark}")

        if sell_signals:
            print(f"\n[SELL SIGNALS - {len(sell_signals)} stocks]")
            print("-"*120)
            for i, signal in enumerate(sell_signals, 1):
                new_mark = " [NEW!]" if signal['new_signal'] else ""
                print(f"{i:2d}. {signal['name']:12s} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:8.2f} - Return: {signal['backtest_return']:+8.2f}%{new_mark}")

        top_15 = df_results.head(15)
        print(f"\n{'='*120}")
        print(f"[TOP 15 PERFORMERS - 2 YEAR BACKTEST]")
        print(f"{'='*120}")
        for i, (idx, row) in enumerate(top_15.iterrows(), 1):
            print(f"{i:2d}. {row['name']:12s} ({row['market'].upper()}{row['code']}) - {row['backtest_return']:+8.2f}% - Price: {row['latest_price']:8.2f}")

    def save_alerts(self, buy_signals, sell_signals, timestamp):
        with open(self.alert_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*120}\n")
            f.write(f"ZTB SEER - YOUR TRADING SIGNALS\n")
            f.write(f"CHECK TIME: {timestamp}\n")
            f.write(f"{'='*120}\n")

            f.write(f"\n[BUY SIGNALS - {len(buy_signals)} stocks]\n")
            if buy_signals:
                for signal in buy_signals:
                    new_mark = " [NEW]" if signal['new_signal'] else ""
                    f.write(f"  {signal['name']} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:.2f} - Return: {signal['backtest_return']:+.2f}%{new_mark}\n")
            else:
                f.write("  No buy signals now.\n")

            f.write(f"\n[SELL SIGNALS - {len(sell_signals)} stocks]\n")
            if sell_signals:
                for signal in sell_signals:
                    new_mark = " [NEW]" if signal['new_signal'] else ""
                    f.write(f"  {signal['name']} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:.2f} - Return: {signal['backtest_return']:+.2f}%{new_mark}\n")
            else:
                f.write("  No sell signals now.\n")

if __name__ == "__main__":
    checker = OneClickSignalCheck()
    buy, sell = checker.run_check()

    print(f"\n{'='*120}")
    print(f"Check complete! Alerts saved to: {checker.alert_file}")
    print(f"\n[REMINDER] Tomorrow, double-click 'check_signals.bat' to get the latest signals!")
    print(f"{'='*120}")
