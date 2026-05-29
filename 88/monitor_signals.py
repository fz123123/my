#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 实时盯盘和信号生成系统
ZTB Seer - Real-time Monitoring and Signal Generation
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta

class RealTimeMonitor:
    def __init__(self):
        self.tdx_reader = TDXDataReader()

        self.watchlist = [
            ('sh', '688981', '中芯国际'),
            ('sz', '300750', '宁德时代'),
            ('sz', '002371', '北方华创'),
            ('sh', '601318', '中国平安'),
            ('sh', '600036', '招商银行'),
            ('sz', '000333', '美的集团'),
            ('sh', '600276', '恒瑞医药'),
        ]

        self.optimized_params = {
            '688981': ('sh', 5, 20),
            '300750': ('sz', 15, 40),
            '601318': ('sh', 15, 50),
        }

    def get_realtime_quote(self, code, market):
        try:
            url = f"http://hq.sinajs.cn/list={market}{code}"
            response = requests.get(url, timeout=5)
            response.encoding = 'gb2312'
            data = response.text

            if '=' in data:
                parts = data.split('=')[-1].strip().replace('"', '')
                fields = parts.split(',')
                if len(fields) >= 10:
                    return {
                        'code': code,
                        'name': fields[0] if fields[0] else code,
                        'open': float(fields[1]) if fields[1] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0,
                        'current': float(fields[3]) if fields[3] else 0,
                        'volume': int(float(fields[8])) if fields[8] else 0,
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    }
        except Exception as e:
            pass
        return None

    def calculate_signals(self, market, code, name):
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)
            if df.empty:
                return None

            backtester = Backtester()
            df = backtester.calculate_indicators(df)

            if code in self.optimized_params:
                short_ma = self.optimized_params[code][1]
                long_ma = self.optimized_params[code][2]
                df['MA_short'] = df['close'].rolling(window=short_ma).mean()
                df['MA_long'] = df['close'].rolling(window=long_ma).mean()
                df['signal_ma'] = np.where(
                    (df['MA_short'] > df['MA_long']) & (df['MA_short'].shift(1) <= df['MA_long'].shift(1)),
                    1,
                    np.where(
                        (df['MA_short'] < df['MA_long']) & (df['MA_short'].shift(1) >= df['MA_long'].shift(1)),
                        -1,
                        0
                    )
                )
                df['signal'] = df['signal_ma']
            else:
                df = backtester.strategy_combined(df)

            current_signal = df['signal'].iloc[-1]
            last_signal = df['signal'].iloc[-2] if len(df) > 1 else 0

            return {
                'name': name,
                'code': code,
                'market': market,
                'current_price': df['close'].iloc[-1],
                'signal': current_signal,
                'last_signal': last_signal,
                'change_detected': current_signal != last_signal,
                'latest_date': df.index[-1].date(),
            }
        except Exception as e:
            return None

    def run_monitor(self):
        print("="*120)
        print("ZTBS - Real-time Monitoring and Signal Generation")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)

        print("\n[INITIALIZING...")
        print(f"Monitoring: {len(self.watchlist)} stocks")
        print("\n" + "-"*120)
        print(f"{'NAME':<12} {'CODE':<12} {'PRICE':<12} {'SIGNAL':<15} {'CHANGE':<10} {'STATUS':<20}")
        print("-"*120)

        all_signals = []

        for market, code, name in self.watchlist:
            quote = self.get_realtime_quote(code, market)
            signal_info = self.calculate_signals(market, code, name)

            price = signal_info['current_price'] if signal_info else (quote['current'] if quote else 0)

            signal_str = ""
            change_str = ""
            signal_status = ""

            if signal_info:
                if signal_info['signal'] == 1:
                    signal_str = "[BUY]"
                elif signal_info['signal'] == -1:
                    signal_str = "[SELL]"
                else:
                    signal_str = "[HOLD]"

                if signal_info['change_detected']:
                    change_str = "[NEW]"
                else:
                    change_str = "维持"

                signal_status = "OK"
                all_signals.append(signal_info)
            else:
                signal_str = "---"
                change_str = "---"
                signal_status = "ERROR"

            print(f"{name:<12} {market.upper()}{code:<12} {price:<12.2f} {signal_str:<15} {change_str:<10} {signal_status:<20}")

        print("\n" + "="*120)

        buy_signals = [s for s in all_signals if s['signal'] == 1]
        sell_signals = [s for s in all_signals if s['signal'] == -1]

        if buy_signals:
            print("\n[BUY SIGNALS]")
            print("-"*120)
            for s in buy_signals:
                change_flag = "[NEW]" if s['change_detected'] else "     "
                print(f"{change_flag} {s['name']} ({s['market'].upper()}{s['code']}) - Price: {s['current_price']:.2f}")

        if sell_signals:
            print("\n[SELL SIGNALS]")
            print("-"*120)
            for s in sell_signals:
                change_flag = "[NEW]" if s['change_detected'] else "     "
                print(f"{change_flag} {s['name']} ({s['market'].upper()}{s['code']}) - Price: {s['current_price']:.2f}")

        print("\n" + "="*120)
        print(f"Signals generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)

        return all_signals

if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    monitor = RealTimeMonitor()
    print("Select Mode:")
    print("1. One-time signal check (Recommended)")
    print("2. Continuous monitoring")

    choice = "1"
    monitor.run_monitor()
