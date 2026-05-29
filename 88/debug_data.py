#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tdx_data_reader import TDXDataReader
import pandas as pd

reader = TDXDataReader()

print("加载贵州茅台数据...")
df = reader.read_stock_data('sh', '600519', 2)

print(f"\n数据概况:")
print(f"总行数: {len(df)}")
print(f"时间范围: {df.index.min()} ~ {df.index.max()}")
print(f"\n前10行数据:")
print(df.head(10))

print(f"\n最后10行数据:")
print(df.tail(10))

print(f"\n数据统计:")
print(df[['open', 'high', 'low', 'close', 'volume']].describe())
