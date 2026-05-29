#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 自动监控提醒系统
ZTB Seer - Auto Monitor & Alert System
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

class AutoMonitorAlert:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.backtester = Backtester()

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

        self.alert_file = "C:\\Users\\Administrator\\Documents\\trae_projects\\88\\signals_alert.txt"

    def analyze_all(self, check_id):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("\n" + "="*120)
        print(f"[AUTO CHECK #{check_id}] {timestamp} - MONITORING {len(self.all_stocks)} STOCKS")
        print("="*120)

        all_results = []
        buy_signals = []
        sell_signals = []

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

        self.print_summary(all_results, buy_signals, sell_signals, check_id, timestamp)
        self.save_alerts(buy_signals, sell_signals, check_id, timestamp)

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

            return {
                'total_return': total_return,
                'final_value': final_value,
            }
        except Exception:
            return None

    def print_summary(self, all_results, buy_signals, sell_signals, check_id, timestamp):
        df_results = pd.DataFrame(all_results)
        df_results = df_results.sort_values('backtest_return', ascending=False)

        print(f"\n[TOTAL RESULTS] {len(all_results)} stocks analyzed")
        print(f"[BUY SIGNALS] {len(buy_signals)} stocks")
        print(f"[SELL SIGNALS] {len(sell_signals)} stocks")

        if buy_signals:
            print(f"\n{'='*120}")
            print(f"[BUY ALERTS - {timestamp}]")
            print(f"{'='*120}")
            for i, signal in enumerate(buy_signals, 1):
                new_mark = " [NEW!]" if signal['new_signal'] else ""
                print(f"{i}. {signal['name']} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:.2f} - Return: {signal['backtest_return']:+.2f}%{new_mark}")

        if sell_signals:
            print(f"\n{'='*120}")
            print(f"[SELL ALERTS - {timestamp}]")
            print(f"{'='*120}")
            for i, signal in enumerate(sell_signals, 1):
                new_mark = " [NEW!]" if signal['new_signal'] else ""
                print(f"{i}. {signal['name']} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:.2f} - Return: {signal['backtest_return']:+.2f}%{new_mark}")

        top_10 = df_results.head(10)
        print(f"\n{'='*120}")
        print(f"[TOP 10 PERFORMERS - {timestamp}]")
        print(f"{'='*120}")
        for i, (idx, row) in enumerate(top_10.iterrows(), 1):
            print(f"{i}. {row['name']} ({row['market'].upper()}{row['code']}) - {row['backtest_return']:+.2f}% - Price: {row['latest_price']:.2f}")

    def save_alerts(self, buy_signals, sell_signals, check_id, timestamp):
        with open(self.alert_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*120}\n")
            f.write(f"[AUTO CHECK #{check_id}] {timestamp}\n")
            f.write(f"{'='*120}\n")

            if buy_signals:
                f.write(f"\n[BUY SIGNALS]\n")
                for signal in buy_signals:
                    new_mark = " [NEW]" if signal['new_signal'] else ""
                    f.write(f"  {signal['name']} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:.2f} - Return: {signal['backtest_return']:+.2f}%{new_mark}\n")

            if sell_signals:
                f.write(f"\n[SELL SIGNALS]\n")
                for signal in sell_signals:
                    new_mark = " [NEW]" if signal['new_signal'] else ""
                    f.write(f"  {signal['name']} ({signal['market'].upper()}{signal['code']}) - Price: {signal['latest_price']:.2f} - Return: {signal['backtest_return']:+.2f}%{new_mark}\n")

            f.write(f"\n[STATS] Buy: {len(buy_signals)}, Sell: {len(sell_signals)}\n")

    def run_continuous_monitor(self, interval_minutes=30):
        print("="*120)
        print("ZTB Seer - AUTO MONITORING ALERT SYSTEM")
        print("="*120)
        print(f"Monitoring {len(self.all_stocks)} stocks")
        print(f"Check interval: {interval_minutes} minutes")
        print(f"Alert file: {self.alert_file}")
        print(f"\nStarting continuous monitoring... (Press Ctrl+C to stop)\n")

        check_id = 1
        try:
            while True:
                self.analyze_all(check_id)

                check_id += 1
                print(f"\n[WAITING] Next check in {interval_minutes} minutes... ({datetime.now().strftime('%H:%M:%S')})")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            print("\n\n[STOPPED] Monitoring stopped by user.")

    def run_single_check(self):
        print("="*120)
        print("ZTB Seer - SINGLE SIGNAL CHECK")
        print("="*120)

        self.analyze_all(1)

        print(f"\n[CHECK COMPLETE] Alerts saved to: {self.alert_file}")
        print(f"\n[REMINDER] Tomorrow, run this script again to get the latest signals!")

if __name__ == "__main__":
    monitor = AutoMonitorAlert()

    print("="*120)
    print("ZTB SEER - AUTOMATIC MONITORING SYSTEM")
    print("="*120)
    print("\nPlease select mode:")
    print("1. Single check now (Recommended for checking tomorrow's signals)")
    print("2. Continuous monitoring (Runs every 30 minutes)")
    print("\n" + "="*120)

    choice = "1"
    monitor.run_single_check()
