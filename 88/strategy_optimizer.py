#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 策略优化和开发系统
ZTB Seer - Strategy Optimization and Development
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime

class StrategyOptimizer:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.test_stocks = [
            ('sz', '300750', '宁德时代'),
            ('sz', '002371', '北方华创'),
            ('sh', '600036', '招商银行'),
            ('sh', '601318', '中国平安'),
            ('sz', '000333', '美的集团'),
        ]

    def optimize_strategy(self, market, code, name, param_range):
        """对单只股票进行策略参数优化"""
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)

            if df.empty or len(df) < 100:
                return None

            best_result = None
            best_params = None

            backtester = Backtester()
            df_base = backtester.calculate_indicators(df)

            for short_ma in param_range['short_ma']:
                for long_ma in param_range['long_ma']:
                    try:
                        df = df_base.copy()

                        df['MA_short'] = df['close'].rolling(window=short_ma).mean()
                        df['MA_long'] = df['close'].rolling(window=long_ma).mean()

                        df['signal_ma'] = np.where(
                            (df['MA_short'] > df['MA_long']) &
                            (df['MA_short'].shift(1) <= df['MA_long'].shift(1)),
                            1,
                            np.where(
                                (df['MA_short'] < df['MA_long']) &
                                (df['MA_short'].shift(1) >= df['MA_long'].shift(1)),
                                -1,
                                0
                            )
                        )

                        df['signal'] = df['signal_ma']

                        result = self._run_backtest(df)

                        if result:
                            if not best_result or result['total_return'] > best_result['total_return']:
                                best_result = result
                                best_params = (short_ma, long_ma)

                    except Exception as e:
                        continue

            if best_result:
                return {
                    'name': name,
                    'code': code,
                    'market': market,
                    'best_short_ma': best_params[0],
                    'best_long_ma': best_params[1],
                    **best_result
                }
            return None

        except Exception as e:
            print(f"   ✗ 优化失败: {e}")
            return None

    def _run_backtest(self, df):
        try:
            capital = 100000
            position = 0
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

                elif row['signal'] == -1 and position > 0:
                    revenue = position * price * 0.9985
                    capital += revenue
                    position = 0

                portfolio_value.append(capital + position * price)

            final_value = capital + position * df['close'].iloc[-1]
            total_return = (final_value - 100000) / 100000 * 100

            return {
                'total_return': total_return,
                'final_value': final_value,
            }
        except Exception as e:
            return None

    def run_new_strategy(self, market, code, name):
        """运行新的改进策略"""
        try:
            df = self.tdx_reader.read_stock_data(market, code, 2)
            if df.empty or len(df) < 100:
                return None

            backtester = Backtester()
            df = backtester.calculate_indicators(df)

            df = self.strategy_enhanced(df)

            result = self._run_backtest(df)

            if result:
                return {
                    'name': name,
                    'code': code,
                    'market': market,
                    'strategy': 'Enhanced',
                    **result
                }
            return None
        except Exception as e:
            print(f"   ✗ 策略失败: {e}")
            return None

    def strategy_enhanced(self, df):
        """增强策略 - 结合RSI和成交量确认"""
        df['signal_rsi'] = np.where(
            (df['RSI'] < 30),
            1,
            np.where(
                (df['RSI'] > 70),
                -1,
                0
            )
        )

        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_confirm'] = df['volume'] > df['volume_ma'] * 1.2

        df['signal'] = np.where(
            (df['signal_rsi'] == 1) & df['volume_confirm'],
            1,
            np.where(
                (df['signal_rsi'] == -1) & df['volume_confirm'],
                -1,
                0
            )
        )

        return df

    def run(self):
        print("="*100)
        print("⚡ 涨停先知 - 策略优化和开发系统 ⚡")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)

        print("\n🚀 第一阶段: 参数优化")
        print("-"*100)

        param_range = {
            'short_ma': [5, 8, 10, 15],
            'long_ma': [20, 25, 30, 40, 50],
        }

        optimization_results = []
        for market, code, name in self.test_stocks:
            print(f"\n优化 {name} ({market.upper()}{code})...")
            result = self.optimize_strategy(market, code, name, param_range)
            if result:
                optimization_results.append(result)
                print(f"   ✓ 最佳参数: MA{result['best_short_ma']}/MA{result['best_long_ma']}")
                print(f"   ✓ 最佳收益: {result['total_return']:+.2f}%")

        print("\n" + "="*100)
        print("🏆 参数优化结果")
        print("="*100)

        if optimization_results:
            df_opt = pd.DataFrame(optimization_results)
            df_opt = df_opt.sort_values('total_return', ascending=False)

            print(f"\n{'排名':<4} {'股票':<12} {'代码':<10} {'最佳参数':<15} {'收益':<12}")
            print("-"*70)
            for i, (idx, row) in enumerate(df_opt.iterrows(), 1):
                param_str = f"MA{row['best_short_ma']}/MA{row['best_long_ma']}"
                return_color = "🟢" if row['total_return'] > 0 else "🔴"
                print(f"{i:<4} {row['name']:<12} {row['market'].upper()}{row['code']:<10} {param_str:<15} {return_color}{row['total_return']:>+9.2f}%")

        print("\n" + "="*100)
        print("🚀 第二阶段: 新增强策略测试")
        print("="*100)

        enhanced_results = []
        for market, code, name in self.test_stocks:
            print(f"\n测试 {name} ({market.upper()}{code})...")
            result = self.run_new_strategy(market, code, name)
            if result:
                enhanced_results.append(result)
                print(f"   ✓ 策略收益: {result['total_return']:+.2f}%")

        if enhanced_results:
            df_enhanced = pd.DataFrame(enhanced_results)
            df_enhanced = df_enhanced.sort_values('total_return', ascending=False)

            print("\n🏆 增强策略结果")
            print("="*100)
            print(f"\n{'排名':<4} {'股票':<12} {'代码':<10} {'策略':<15} {'收益':<12}")
            print("-"*70)
            for i, (idx, row) in enumerate(df_enhanced.iterrows(), 1):
                return_color = "🟢" if row['total_return'] > 0 else "🔴"
                print(f"{i:<4} {row['name']:<12} {row['market'].upper()}{row['code']:<10} {row['strategy']:<15} {return_color}{row['total_return']:>+9.2f}%")

        print("\n" + "="*100)
        print("✅ 策略优化完成！")
        print("="*100)

if __name__ == "__main__":
    optimizer = StrategyOptimizer()
    optimizer.run()
