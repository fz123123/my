#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tdx_data_reader import TDXDataReader
from backtester import Backtester
import pandas as pd
import numpy as np

reader = TDXDataReader()
backtester = Backtester()

print("加载上证指数数据...")
df = reader.read_stock_data('sh', '000001', 2)
print(f"✓ 加载 {len(df)} 条数据\n")

df = backtester.calculate_indicators(df)
df = backtester.strategy_combined(df)

print("手动模拟第一笔买入交易:")
first_buy_idx = df[df['signal'] == 1].index[0]
first_buy_row = df.loc[first_buy_idx]

print(f"第一笔买入日期: {first_buy_idx}")
print(f"收盘价: ¥{first_buy_row['close']:.2f}")
print(f"信号: {first_buy_row['signal']}")
print(f"position: 0 (初始)")
print(f"初始资金: ¥100000")

shares = int(100000 / first_buy_row['close'] / 100) * 100
cost = shares * first_buy_row['close'] * 1.0015

print(f"可买入股数: {shares}")
print(f"买入成本: ¥{cost:,.2f}")
print(f"条件 cost <= 100000: {cost <= 100000}")
print(f"条件 shares > 0: {shares > 0}")

print("\n检查前5个买入信号:")
for i, (date, row) in enumerate(df[df['signal'] == 1].head(5).iterrows()):
    shares = int(100000 / row['close'] / 100) * 100
    print(f"{i+1}. {date.date()}: ¥{row['close']:.2f} -> 可买 {shares} 股")
