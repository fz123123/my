#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股光模块股票实时行情查询
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import pandas as pd
from datetime import datetime

def get_us_stock_data(symbols):
    """获取美股实时数据"""
    # 使用Yahoo Finance API
    base_url = "https://query1.finance.yahoo.com/v7/finance/quote"
    
    params = {
        'symbols': ','.join(symbols),
        'fields': 'regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketOpen,regularMarketDayHigh,regularMarketDayLow,regularMarketVolume,previousClose'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        data = response.json()
        
        results = []
        for quote in data.get('quoteResponse', {}).get('result', []):
            symbol = quote.get('symbol', '')
            price = quote.get('regularMarketPrice', 0)
            change = quote.get('regularMarketChange', 0)
            change_percent = quote.get('regularMarketChangePercent', 0)
            open_price = quote.get('regularMarketOpen', 0)
            high = quote.get('regularMarketDayHigh', 0)
            low = quote.get('regularMarketDayLow', 0)
            volume = quote.get('regularMarketVolume', 0)
            prev_close = quote.get('previousClose', 0)
            
            results.append({
                'symbol': symbol,
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'open': open_price,
                'high': high,
                'low': low,
                'volume': volume,
                'prev_close': prev_close
            })
        
        return results
    except Exception as e:
        print(f"获取数据失败: {e}")
        return []

def main():
    print("\n" + "="*80)
    print("    📈 美股光模块股票实时行情")
    print(f"    查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 光模块相关美股
    stocks = {
        'LITE': 'Lumentum Holdings',
        'AVGO': 'Broadcom',
        'CSCO': 'Cisco',
        'ANET': 'Arista Networks',
        'JNPR': 'Juniper Networks',
        'NPTN': 'NeoPhotonics',
        'INFN': 'Infinera',
        'CIEN': 'Ciena'
    }
    
    print(f"\n📡 正在获取 {len(stocks)} 只光模块相关股票数据...")
    
    data = get_us_stock_data(list(stocks.keys()))
    
    if not data:
        print("\n❌ 无法获取数据")
        return
    
    # 整理数据
    df = pd.DataFrame(data)
    df['name'] = df['symbol'].map(stocks)
    df = df[['symbol', 'name', 'price', 'change', 'change_percent', 'open', 'high', 'low', 'volume']]
    
    # 按涨跌幅排序
    df = df.sort_values('change_percent', ascending=False)
    
    print("\n" + "="*80)
    print(f"{'代码':<8} {'名称':<20} {'最新价':>10} {'涨跌额':>10} {'涨跌幅':>10} {'成交量':>12}")
    print("-"*80)
    
    total_up = 0
    total_down = 0
    
    for _, row in df.iterrows():
        change_color = "🟢" if row['change_percent'] >= 0 else "🔴"
        change_sign = "+" if row['change_percent'] >= 0 else ""
        
        print(f"{row['symbol']:<8} {row['name']:<20} ${row['price']:>9.2f} {change_color} {change_sign}{row['change']:>8.2f} {change_sign}{row['change_percent']:>9.2f}%  {row['volume']:>12,}")
        
        if row['change_percent'] > 0:
            total_up += 1
        elif row['change_percent'] < 0:
            total_down += 1
    
    print("-"*80)
    
    # 统计
    print(f"\n📊 涨跌统计:")
    print(f"   🟢 上涨: {total_up} 只")
    print(f"   🔴 下跌: {total_down} 只")
    print(f"   ➡️ 持平: {len(df) - total_up - total_down} 只")
    
    # 强势股票
    strong_stocks = df[df['change_percent'] > 2]
    if not strong_stocks.empty:
        print(f"\n🚀 强势上涨 (>2%):")
        for _, row in strong_stocks.iterrows():
            print(f"   • {row['name']} ({row['symbol']}): +{row['change_percent']:.2f}%")
    
    # 弱势股票
    weak_stocks = df[df['change_percent'] < -2]
    if not weak_stocks.empty:
        print(f"\n⚠️ 弱势下跌 (<-2%):")
        for _, row in weak_stocks.iterrows():
            print(f"   • {row['name']} ({row['symbol']}): {row['change_percent']:.2f}%")
    
    # 行业判断
    avg_change = df['change_percent'].mean()
    print(f"\n📈 光模块板块整体表现:")
    if avg_change > 1:
        print(f"   🟢 板块强势上涨 (+{avg_change:.2f}%)")
    elif avg_change > 0:
        print(f"   🟡 板块小幅上涨 (+{avg_change:.2f}%)")
    elif avg_change < -1:
        print(f"   🔴 板块弱势下跌 ({avg_change:.2f}%)")
    else:
        print(f"   ⚪ 板块小幅波动 ({avg_change:.2f}%)")
    
    print("\n" + "="*80)
    print("💡 注: 数据来自Yahoo Finance，仅供参考")
    print("="*80)

if __name__ == "__main__":
    main()
