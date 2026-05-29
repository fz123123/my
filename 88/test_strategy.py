#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd

reader = TDXDataReader()
backtester = Backtester()

print("加载贵州茅台数据...")
df = reader.read_stock_data('sh', '600519', 2)
print(f"✓ 加载了 {len(df)} 条数据\n")

print("计算技术指标...")
df = backtester.calculate_indicators(df)
print("✓ 技术指标计算完成\n")

print("应用组合策略...")
df = backtester.strategy_combined(df)
print("✓ 策略应用完成\n")

print("信号统计:")
print(f"总天数: {len(df)}")
print(f"买入信号: {(df['signal'] == 1).sum()} 次")
print(f"卖出信号: {(df['signal'] == -1).sum()} 次")
print(f"无信号: {(df['signal'] == 0).sum()} 次")

print("\n查看最近30天的信号:")
recent = df.tail(30)[['close', 'signal_macd', 'signal_kdj', 'signal_ma', 'signal_rsi', 'signal']]
print(recent)
