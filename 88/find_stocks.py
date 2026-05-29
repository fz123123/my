#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tdx_data_reader import TDXDataReader
import pandas as pd

reader = TDXDataReader()

print("寻找价格合适的股票...")
print("=" * 80)

stocks = reader.get_available_stocks('sz')[:50]

print(f"检查前50只深圳股票的价格范围...\n")

for stock in stocks[:10]:
    try:
        df = reader.read_stock_data('sz', stock['code'], 1)
        if not df.empty:
            avg_price = df['close'].mean()
            latest_price = df['close'].iloc[-1]
            print(f"{stock['market'].upper()}{stock['code']}: 最新价 ¥{latest_price:.2f}, 平均价 ¥{avg_price:.2f}")
    except:
        continue

print("\n" + "=" * 80)
print("💡 提示: 需要选择价格 < ¥1000 的股票才能用10万资金交易")
print("=" * 80)
