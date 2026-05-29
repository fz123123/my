#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np

reader = TDXDataReader()
backtester = Backtester()

print("加载数据...")
df = reader.read_stock_data('sh', '600519', 2)

print("\n检查signal列:")
print(f"信号列数据类型: {df['signal'].dtype if 'signal' in df.columns else '不存在'}")

df = backtester.calculate_indicators(df)
df = backtester.strategy_combined(df)

print(f"\n信号列存在: {'signal' in df.columns}")
print(f"信号列数据类型: {df['signal'].dtype}")
print(f"信号列前30个值:")
print(df['signal'].head(30).tolist())

print(f"\n检查非NaN的信号:")
df_with_signal = df[df['signal'].notna()]
print(f"有信号的天数: {len(df_with_signal)}")

print(f"\n检查买入信号:")
df_buy = df[df['signal'] == 1]
print(f"买入信号天数: {len(df_buy)}")
if len(df_buy) > 0:
    print(f"第一个买入信号日期: {df_buy.index[0]}")
    print(f"第一个买入信号收盘价: {df_buy.iloc[0]['close']}")

print(f"\n手动检查第一笔买入:")
print(f"初始资金: 100000")
print(f"股票价格: {df_buy.iloc[0]['close'] if len(df_buy) > 0 else 'N/A'}")
shares = int(100000 / df_buy.iloc[0]['close'] / 100) * 100
cost = shares * df_buy.iloc[0]['close'] * 1.0015
print(f"可买入股数: {shares}")
print(f"买入成本: {cost}")
print(f"是否 <= 100000: {cost <= 100000}")
