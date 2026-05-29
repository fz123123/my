#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 实时盯盘和信号生成系统
ZTB Seer - Real-time Monitoring and Signal Generation
支持实时数据更新和自动刷新
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
import requests
import time
import os
from datetime import datetime, timedelta

class RealTimeMonitor:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.backtester = Backtester()
        
        self.watchlist = [
            ('sh', '688981', '中芯国际'),
            ('sz', '300750', '宁德时代'),
            ('sz', '002371', '北方华创'),
            ('sh', '601318', '中国平安'),
            ('sh', '600036', '招商银行'),
            ('sz', '000333', '美的集团'),
            ('sh', '600276', '恒瑞医药'),
            ('sh', '600519', '贵州茅台'),
            ('sz', '000858', '五粮液'),
            ('sh', '601899', '紫金矿业'),
        ]

        self.optimized_params = {
            '688981': ('sh', 5, 20),
            '300750': ('sz', 15, 40),
            '601318': ('sh', 15, 50),
            '600519': ('sh', 10, 60),
        }
        
        self.realtime_data_file = os.path.join(os.path.dirname(__file__), 'watchlist_realtime.csv')
        
    def get_realtime_quote(self, code, market):
        """获取实时行情（新浪接口）"""
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
            print(f"获取 {market}{code} 实时数据失败: {e}")
        return None

    def calculate_signals(self, market, code, name):
        """计算技术信号"""
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)
            if df.empty:
                return None

            df = self.backtester.calculate_indicators(df)

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
                df = self.backtester.strategy_combined(df)

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
            print(f"计算 {name} 信号失败: {e}")
            return None

    def load_realtime_data(self):
        """从文件加载实时数据"""
        if os.path.exists(self.realtime_data_file):
            try:
                df = pd.read_csv(self.realtime_data_file, encoding='utf-8')
                return df
            except Exception as e:
                print(f"加载实时数据文件失败: {e}")
        return None

    def update_realtime_data(self):
        """更新实时数据文件"""
        print("\n🔄 正在更新实时数据...")
        os.system(f'python "{os.path.dirname(__file__)}\\..\\update_all_realtime_data.py"')
        print("✅ 实时数据更新完成")

    def run_monitor(self, use_realtime_file=False):
        """运行监控器"""
        print("="*120)
        print("⚡ 涨停先知 - 实时盯盘和信号生成系统 ⚡")
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)

        print("\n📊 正在初始化...")
        print(f"📈 监控股票数量: {len(self.watchlist)} 只")
        print("🔄 信号刷新间隔: 实时模式")
        print("\n" + "-"*120)
        print(f"{'股票名称':<12} {'代码':<12} {'最新价':<12} {'信号':<15} {'变化':<10} {'状态':<20}")
        print("-"*120)

        all_signals = []

        # 从文件加载实时数据（如果启用）
        realtime_df = self.load_realtime_data() if use_realtime_file else None

        for market, code, name in self.watchlist:
            # 优先使用文件中的实时数据
            price = 0
            if realtime_df is not None:
                row = realtime_df[(realtime_df['market'] == market) & (realtime_df['code'] == code)]
                if not row.empty:
                    price = row['current'].iloc[0]
            
            # 计算信号
            signal_info = self.calculate_signals(market, code, name)
            
            if signal_info:
                price = signal_info['current_price'] if price == 0 else price

            signal_str = ""
            signal_status = ""

            if signal_info:
                if signal_info['signal'] == 1:
                    signal_str = "🟢 买入"
                elif signal_info['signal'] == -1:
                    signal_str = "🔴 卖出"
                else:
                    signal_str = "⚪ 持有"

                change_str = "🔄 新信号" if signal_info['change_detected'] else "维持"
                signal_status = "信号正常"
                all_signals.append(signal_info)
            else:
                signal_str = "⚪ -"
                change_str = "-"
                signal_status = "信号缺失"

            print(f"{name:<12} {market.upper()}{code:<12} ¥{price:<11.2f} {signal_str:<15} {change_str:<10} {signal_status:<20}")

        print("\n" + "="*120)

        buy_signals = [s for s in all_signals if s['signal'] == 1]
        sell_signals = [s for s in all_signals if s['signal'] == -1]

        if buy_signals:
            print("\n🟢 【买入信号】")
            print("-"*120)
            for s in buy_signals:
                change_flag = "🔄" if s['change_detected'] else "  "
                print(f"{change_flag} {s['name']} ({s['market'].upper()}{s['code']}) - 现价: ¥{s['current_price']:.2f}")

        if sell_signals:
            print("\n🔴 【卖出信号】")
            print("-"*120)
            for s in sell_signals:
                change_flag = "🔄" if s['change_detected'] else "  "
                print(f"{change_flag} {s['name']} ({s['market'].upper()}{s['code']}) - 现价: ¥{s['current_price']:.2f}")

        print("\n" + "="*120)
        print(f"✅ 信号生成完成！")
        print(f"⏰ 信号时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)

        return all_signals

    def run_continuous_monitor(self, interval=60, auto_update=True):
        """连续监控模式"""
        print("="*120)
        print("⚡ 涨停先知 - 连续监控模式")
        print(f"⏰ 刷新间隔: {interval}秒")
        print(f"🔄 自动更新数据: {'开启' if auto_update else '关闭'}")
        print("="*120)

        try:
            while True:
                print(f"\n{'='*120}")
                print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 自动更新数据
                if auto_update:
                    self.update_realtime_data()
                
                self.run_monitor(use_realtime_file=True)

                print(f"\n💤 等待 {interval} 秒...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止！")

def main():
    monitor = RealTimeMonitor()
    print("请选择模式：")
    print("1. 单次信号检测 (推荐)")
    print("2. 连续监控模式")
    print("3. 更新实时数据后检测")

    choice = input("\n请输入选择 (1/2/3，默认1): ").strip() or "1"

    if choice == "2":
        interval = input("请输入刷新间隔(秒，默认60): ").strip()
        interval = int(interval) if interval.isdigit() else 60
        monitor.run_continuous_monitor(interval)
    elif choice == "3":
        monitor.update_realtime_data()
        monitor.run_monitor(use_realtime_file=True)
    else:
        monitor.run_monitor()

if __name__ == "__main__":
    main()