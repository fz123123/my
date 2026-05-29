# -*- coding: utf-8 -*-
from core.data_fetcher import DataFetcher

f = DataFetcher()
df = f.get_stock_data('600519.SH')

if df is not None:
    print('数据获取成功!')
    print(f'数据长度: {len(df)}')
    print(f'最近日期: {df.index[-1].date()}')
    print(f'最新价格: {df["close"].iloc[-1]}')
else:
    print('获取失败')