#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 完整策略优化系统 v2.0
ZTB Seer - Complete Strategy Optimization System
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime

class EnhancedOptimizer:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.test_stocks = [
            ('sz', '300750', '宁德时代'),
            ('sh', '601318', '中国平安'),
            ('sz', '002371', '北方华创'),
            ('sh', '688981', '中芯国际'),
            ('sh', '600276', '恒瑞医药'),
        ]

    def run_complete_optimization(self):
        print("="*100)
        print("⚡ 涨停先知 - 完整策略优化系统 ⚡")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)

        all_results = []

        for market, code, name in self.test_stocks:
            print(f"\n{'='*100}")
            print(f"🎯 优化: {name} ({market.upper()}{code})")
            print(f"{'='*100}")

            try:
                df = self.tdx_reader.read_stock_data(market, code, 2)
                if df.empty or len(df) < 100:
                    continue

                backtester = Backtester()
                df = backtester.calculate_indicators(df)

                original_result = self.backtest_strategy(df, 'original', name)
                optimized_ma_result = self.backtest_optimized_ma(df, name)
                enhanced_result = self.backtest_enhanced(df, name)

                results = []
                if original_result: results.append(original_result)
                if optimized_ma_result: results.append(optimized_ma_result)
                if enhanced_result: results.append(enhanced_result)

                if results:
                    best_result = max(results, key=lambda x: x['total_return'])
                    print(f"\n🏆 最佳策略: {best_result['strategy_type']}")
                    print(f"   最佳收益: {best_result['total_return']:+.2f}%")
                    best_result['stock_name'] = name
                    best_result['stock_code'] = code
                    best_result['market'] = market
                    all_results.append(best_result)

            except Exception as e:
                print(f"✗ 优化失败: {e}")
                continue

        if all_results:
            self.print_final_summary(all_results)

    def backtest_strategy(self, df, strategy_type, name):
        try:
            df = df.copy()
            backtester = Backtester()
            df = backtester.strategy_combined(df)
            df['signal'] = df['signal']
            result = self._execute_backtest(df)
            if result:
                result['strategy_type'] = strategy_type
                result['params'] = 'Original'
                return result
            return None
        except Exception as e:
            return None

    def backtest_optimized_ma(self, df, name):
        try:
            best_return = -float('inf')
            best_params = None

            for short_ma in [5, 8, 10, 12, 15]:
                for long_ma in [20, 25, 30, 40, 50]:
                    df_test = df.copy()
                    df_test['MA_short'] = df_test['close'].rolling(window=short_ma).mean()
                    df_test['MA_long'] = df_test['close'].rolling(window=long_ma).mean()

                    df_test['signal'] = np.where(
                        (df_test['MA_short'] > df_test['MA_long']) &
                        (df_test['MA_short'].shift(1) <= df_test['MA_long'].shift(1)),
                        1,
                        np.where(
                            (df_test['MA_short'] < df_test['MA_long']) &
                            (df_test['MA_short'].shift(1) >= df_test['MA_long'].shift(1)),
                            -1,
                            0
                        )
                    )

                    result = self._execute_backtest(df_test)
                    if result and result['total_return'] > best_return:
                        best_return = result['total_return']
                        best_params = (short_ma, long_ma)
                        best_result = result

            if best_params:
                best_result['strategy_type'] = 'Optimized MA'
                best_result['params'] = f"MA{best_params[0]}/MA{best_params[1]}"
                return best_result
            return None
        except Exception as e:
            return None

    def backtest_enhanced(self, df, name):
        try:
            df_test = df.copy()

            df_test['RSI'] = self._calculate_rsi(df_test['close'], 14)
            df_test['volume_ma'] = df_test['volume'].rolling(window=20).mean()

            df_test['signal'] = np.where(
                (df_test['RSI'] < 30) & (df_test['volume'] > df_test['volume_ma'] * 1.2),
                1,
                np.where(
                    (df_test['RSI'] > 70) & (df_test['volume'] > df_test['volume_ma'] * 1.2),
                    -1,
                    0
                )
            )

            result = self._execute_backtest(df_test)
            if result:
                result['strategy_type'] = 'Enhanced RSI+Volume'
                result['params'] = 'RSI+Volume'
                return result
            return None
        except Exception as e:
            return None

    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _execute_backtest(self, df):
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
        except Exception as e:
            return None

    def print_final_summary(self, all_results):
        print("\n" + "="*100)
        print("🏆 完整策略优化最终汇总")
        print("="*100)

        df_summary = pd.DataFrame(all_results)
        df_summary = df_summary.sort_values('total_return', ascending=False)

        print(f"\n{'排名':<4} {'股票':<12} {'代码':<10} {'最佳策略':<20} {'参数':<15} {'收益':<12}")
        print("-"*85)
        for i, (idx, row) in enumerate(df_summary.iterrows(), 1):
            return_color = "🟢" if row['total_return'] > 0 else "🔴"
            print(f"{i:<4} {row['stock_name']:<12} {row['market'].upper()}{row['stock_code']:<10} {row['strategy_type']:<20} {row['params']:<15} {return_color}{row['total_return']:>+9.2f}%")

        print(f"\n{'='*100}")
        print("✅ 完整策略优化完成！")
        print(f"{'='*100}")

if __name__ == "__main__":
    optimizer = EnhancedOptimizer()
    optimizer.run_complete_optimization()
