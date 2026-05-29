#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 实时数据 + 历史回测 综合系统
ZTB Seer - Real-time + Historical Backtest System
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
import requests
from datetime import datetime

class IntegratedAnalyzer:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.realtime_url = "http://hq.sinajs.cn/list="

        self.stock_list = [
            ('600584', 'sh', '长电科技'),
            ('600519', 'sh', '贵州茅台'),
            ('000858', 'sz', '五粮液'),
            ('300750', 'sz', '宁德时代'),
            ('002594', 'sz', '比亚迪'),
            ('600036', 'sh', '招商银行'),
            ('601318', 'sh', '中国平安'),
            ('600030', 'sh', '中信证券'),
            ('688981', 'sh', '中芯国际'),
            ('002371', 'sz', '北方华创'),
            ('601012', 'sh', '隆基绿能'),
            ('603501', 'sh', '韦尔股份'),
            ('000333', 'sz', '美的集团'),
            ('600276', 'sh', '恒瑞医药'),
            ('300015', 'sz', '爱尔眼科'),
        ]

    def get_realtime_data(self, code, market):
        """获取实时行情数据"""
        try:
            full_code = f"{market}{code}"
            url = f"{self.realtime_url}{full_code}"
            response = requests.get(url, timeout=5)
            response.encoding = 'gb2312'
            data = response.text

            if '=' not in data:
                return None

            parts = data.split('=')[-1].strip().replace('"', '')
            fields = parts.split(',')

            if len(fields) >= 11:
                return {
                    'price': float(fields[3]),
                    'open': float(fields[1]),
                    'high': float(fields[4]),
                    'low': float(fields[5]),
                    'change_pct': float(fields[5]),
                    'volume': int(fields[8]) / 100,
                    'update_time': fields[30] if len(fields) > 30 else datetime.now().strftime('%H:%M:%S')
                }
        except Exception as e:
            print(f"   获取实时数据失败: {e}")
        return None

    def backtest_single_stock(self, code, market, name):
        """回测单只股票"""
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)

            if df.empty or len(df) < 100:
                return None

            backtester = Backtester()
            df = backtester.calculate_indicators(df)
            df = backtester.strategy_combined(df)

            capital = 100000
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
                    cost = shares * price * 1.0015
                    if cost <= capital and shares >= 100:
                        position = shares
                        capital -= cost
                        trades.append({'date': date, 'type': 'buy', 'price': price})

                elif row['signal'] == -1 and position > 0:
                    revenue = position * price * 0.9985
                    capital += revenue
                    trades.append({'date': date, 'type': 'sell', 'price': price})
                    position = 0

                portfolio_value.append(capital + position * price)

            final_value = capital + position * df['close'].iloc[-1]
            total_return = (final_value - 100000) / 100000 * 100

            return {
                'code': code,
                'market': market,
                'name': name,
                'total_return': total_return,
                'total_trades': len(trades) // 2,
                'latest_price': df['close'].iloc[-1],
                'data_count': len(df),
                'has_buy_signal': (df['signal'] == 1).iloc[-1],
                'has_sell_signal': (df['signal'] == -1).iloc[-1],
            }
        except Exception as e:
            print(f"   回测失败: {e}")
            return None

    def run(self):
        print("=" * 100)
        print("⚡ 涨停先知 - 实时数据 + 历史回测 综合分析系统 ⚡")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)

        print("\n📊 开始分析股票列表...")
        print("-" * 100)

        results = []

        for code, market, name in self.stock_list:
            print(f"\n{'=' * 100}")
            print(f"🎯 分析: {name} ({market.upper()}{code})")
            print(f"{'=' * 100}")

            print("\n📡 获取实时行情...")
            realtime_data = self.get_realtime_data(code, market)
            if realtime_data:
                print(f"   ✓ 实时价格: ¥{realtime_data['price']:.2f}")
                print(f"   ✓ 涨跌幅: {realtime_data['change_pct']:+.2f}%")
                print(f"   ✓ 成交量: {realtime_data['volume']/10000:.1f}万手")
                print(f"   ✓ 更新时间: {realtime_data['update_time']}")
            else:
                print("   ✗ 实时数据获取失败，使用历史数据")
                realtime_data = None

            print("\n🔄 运行历史回测...")
            backtest_result = self.backtest_single_stock(code, market, name)

            if backtest_result:
                results.append(backtest_result)
                print(f"   ✓ 回测完成")
                print(f"   ✓ 历史收益: {backtest_result['total_return']:+.2f}%")
                print(f"   ✓ 交易次数: {backtest_result['total_trades']} 次")
                print(f"   ✓ 最新收盘价: ¥{backtest_result['latest_price']:.2f}")

                if backtest_result['has_buy_signal']:
                    print(f"   🟢 【信号】出现买入信号！")
                elif backtest_result['has_sell_signal']:
                    print(f"   🔴 【信号】出现卖出信号！")
                else:
                    print(f"   ⚪ 【信号】无交易信号")
            else:
                print("   ✗ 回测失败")

        print("\n" + "=" * 100)
        print("🏆 综合分析结果汇总")
        print("=" * 100)

        if results:
            df_summary = pd.DataFrame(results)
            df_summary = df_summary.sort_values('total_return', ascending=False)

            print(f"\n{'排名':<4} {'股票':<12} {'代码':<10} {'历史收益':<12} {'交易次数':<10} {'最新价格':<12} {'信号':<10}")
            print("-" * 100)

            for i, (idx, row) in enumerate(df_summary.iterrows(), 1):
                return_color = "🟢" if row['total_return'] > 0 else "🔴"

                signal = ""
                if row['has_buy_signal']:
                    signal = "🟢 买入"
                elif row['has_sell_signal']:
                    signal = "🔴 卖出"
                else:
                    signal = "⚪ 无"

                print(f"{i:<4} {row['name']:<12} {row['market'].upper()}{row['code']:<10} {return_color}{row['total_return']:>+9.2f}% {row['total_trades']:<10} ¥{row['latest_price']:<10.2f} {signal:<10}")

            print("\n📈 买入信号股票:")
            buy_signals = df_summary[df_summary['has_buy_signal']]
            if len(buy_signals) > 0:
                for idx, row in buy_signals.iterrows():
                    print(f"   🟢 {row['name']} ({row['market'].upper()}{row['code']}) - 历史收益: {row['total_return']:+.2f}%")
            else:
                print("   暂无买入信号")

            print("\n💾 详细结果已完成！")
        else:
            print("   暂无有效结果")

        print("\n" + "=" * 100)
        print("✅ 综合分析完成！")
        print("=" * 100)

if __name__ == "__main__":
    analyzer = IntegratedAnalyzer()
    analyzer.run()
