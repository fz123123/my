#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股光模块股票实时行情查询 - 使用新浪财经数据源
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

def get_us_stock_data():
    """获取美股光模块相关股票数据"""
    # 新浪财经美股接口
    stocks = {
        'LITE': {'name': 'Lumentum Holdings', 'code': 'LITE'},
        'AVGO': {'name': 'Broadcom', 'code': 'AVGO'},
        'CSCO': {'name': 'Cisco', 'code': 'CSCO'},
        'ANET': {'name': 'Arista Networks', 'code': 'ANET'},
        'JNPR': {'name': 'Juniper Networks', 'code': 'JNPR'},
        'NPTN': {'name': 'NeoPhotonics', 'code': 'NPTN'},
        'INFN': {'name': 'Infinera', 'code': 'INFN'},
        'CIEN': {'name': 'Ciena', 'code': 'CIEN'}
    }
    
    results = []
    
    for symbol, info in stocks.items():
        try:
            url = f"https://hq.sinajs.cn/list=gb_{symbol.lower()}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            data = response.text
            if '=' in data:
                parts = data.split('=')[-1].strip().replace('"', '')
                fields = parts.split(',')
                
                if len(fields) >= 5:
                    price = float(fields[1]) if fields[1] else 0
                    change = float(fields[2]) if fields[2] else 0
                    change_percent = float(fields[3]) if fields[3] else 0
                    high = float(fields[4]) if fields[4] else 0
                    low = float(fields[5]) if fields[5] else 0
                    
                    results.append({
                        'symbol': symbol,
                        'name': info['name'],
                        'price': price,
                        'change': change,
                        'change_percent': change_percent,
                        'high': high,
                        'low': low
                    })
        except Exception as e:
            continue
    
    return results

def main():
    print("\n" + "="*80)
    print("    📈 美股光模块股票实时行情")
    print(f"    查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    print(f"\n📡 正在获取光模块相关股票数据...")
    
    data = get_us_stock_data()
    
    if not data:
        print("\n❌ 无法获取数据，让我尝试另一种方式...")
        
        # 模拟数据演示
        data = [
            {'symbol': 'LITE', 'name': 'Lumentum Holdings', 'price': 78.50, 'change': 2.35, 'change_percent': 3.08, 'high': 79.20, 'low': 76.80},
            {'symbol': 'AVGO', 'name': 'Broadcom', 'price': 875.20, 'change': 12.50, 'change_percent': 1.45, 'high': 880.00, 'low': 865.00},
            {'symbol': 'CSCO', 'name': 'Cisco', 'price': 48.75, 'change': -0.35, 'change_percent': -0.71, 'high': 49.20, 'low': 48.50},
            {'symbol': 'ANET', 'name': 'Arista Networks', 'price': 225.80, 'change': 8.20, 'change_percent': 3.77, 'high': 228.00, 'low': 218.50},
            {'symbol': 'JNPR', 'name': 'Juniper Networks', 'price': 35.40, 'change': -0.85, 'change_percent': -2.35, 'high': 36.50, 'low': 35.20},
            {'symbol': 'NPTN', 'name': 'NeoPhotonics', 'price': 8.25, 'change': 0.15, 'change_percent': 1.85, 'high': 8.40, 'low': 8.05},
            {'symbol': 'INFN', 'name': 'Infinera', 'price': 18.90, 'change': 0.45, 'change_percent': 2.44, 'high': 19.10, 'low': 18.50},
            {'symbol': 'CIEN', 'name': 'Ciena', 'price': 42.30, 'change': 1.10, 'change_percent': 2.67, 'high': 42.80, 'low': 41.50}
        ]
        print("⚠️ 使用模拟数据演示")
    
    # 整理数据
    df = pd.DataFrame(data)
    df = df.sort_values('change_percent', ascending=False)
    
    print("\n" + "="*80)
    print(f"{'代码':<8} {'名称':<20} {'最新价':>10} {'涨跌额':>10} {'涨跌幅':>10} {'最高/最低':>15}")
    print("-"*80)
    
    total_up = 0
    total_down = 0
    
    for _, row in df.iterrows():
        change_color = "🟢" if row['change_percent'] >= 0 else "🔴"
        change_sign = "+" if row['change_percent'] >= 0 else ""
        
        print(f"{row['symbol']:<8} {row['name']:<20} ${row['price']:>9.2f} {change_color} {change_sign}{row['change']:>8.2f} {change_sign}{row['change_percent']:>9.2f}%  ${row['high']:.2f}/${row['low']:.2f}")
        
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
    print("💡 注: 数据仅供参考，实际交易请以实时行情为准")
    print("="*80)

if __name__ == "__main__":
    main()
