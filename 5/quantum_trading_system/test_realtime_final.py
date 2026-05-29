#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极版：179只股票行情获取测试
包含多种数据源和备用方案
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import time
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("  📊 179只股票实时行情获取测试（终极版）")
print("="*80)
print()

# 读取自选股
print("📂 读取179只自选股...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    watchlist = [line.strip() for line in f if line.strip()]

print(f"✅ 加载完成: {len(watchlist)} 只")

# 分类
fund_stocks = [s for s in watchlist if s.split('.')[0].startswith(('16', '5'))]
stock_stocks = [s for s in watchlist if not s.split('.')[0].startswith(('16', '5'))]

print(f"\n📊 自选股分类:")
print(f"   - 基金: {len(fund_stocks)} 只")
print(f"   - A股股票: {len(stock_stocks)} 只")
print()

real_data = {}
success_sources = []

# 方法1: 直接使用东方财富API
print("🔄 方法1: 东方财富实时行情API...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quote.eastmoney.com/'
    }
    
    # 东方财富股票行情接口
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    
    # 获取沪深A股
    params = {
        'pn': 1,
        'pz': 5000,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',
        'fs': 'm:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23',
        'fields': 'f12,f14,f2,f3,f4,f5,f6'
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('data') and data['data'].get('diff'):
            quotes_map = {}
            for item in data['data']['diff']:
                code = item.get('f12', '')
                quotes_map[code] = item
            
            # 匹配自选股中的A股
            em_count = 0
            for stock in stock_stocks:
                code = stock.split('.')[0]
                if code in quotes_map:
                    item = quotes_map[code]
                    real_data[stock] = {
                        'code': code,
                        'name': item.get('f14', ''),
                        'close': item.get('f2', 0),
                        'change_pct': item.get('f3', 0),
                        'change_amount': item.get('f4', 0),
                        'volume': item.get('f5', 0),
                        'amount': item.get('f6', 0),
                        'source': '东方财富'
                    }
                    em_count += 1
            
            success_sources.append(f'东方财富(股票): {em_count}只')
            print(f"✅ 东方财富股票成功: {em_count} 只")
    
except Exception as e:
    print(f"⚠️ 东方财富股票接口失败: {e}")

# 方法2: 基金行情
print("\n🔄 方法2: 东方财富基金行情API...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://fund.eastmoney.com/'
    }
    
    # 基金行情接口
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': 1,
        'pz': 5000,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',
        'fs': 'm:1+t:5,m:1+t:6,m:1+t:7,m:1+t:8,m:1+t:10,m:1+t:11,m:1+t:12,m:1+t:13,m:1+t:14,m:1+t:17,m:1+t:18,m:1+t:19,m:1+t:20,m:1+t:21,m:1+t:22,m:1+t:23,m:1+t:24,m:1+t:25,m:1+t:26,m:1+t:27,m:1+t:28,m:1+t:30,m:1+t:31,m:1+t:32,m:1+t:33,m:1+t:34,m:1+t:35,m:1+t:36,m:1+t:37,m:1+t:38,m:1+t:39,m:1+t:40,m:1+t:41,m:1+t:42,m:1+t:43,m:1+t:44,m:1+t:45,m:1+t:46,m:1+t:47,m:1+t:48,m:1+t:49,m:1+t:50,m:1+t:51,m:1+t:52,m:1+t:53,m:1+t:54,m:1+t:55,m:1+t:56,m:1+t:57,m:1+t:58,m:1+t:59,m:1+t:60,m:1+t:61,m:1+t:62,m:1+t:63,m:1+t:64,m:1+t:65,m:1+t:66,m:1+t:67,m:1+t:68,m:1+t:69,m:1+t:70,m:1+t:71,m:1+t:72,m:1+t:73,m:1+t:74,m:1+t:75,m:1+t:76,m:1+t:77,m:1+t:78,m:1+t:79,m:1+t:80,m:1+t:81,m:1+t:82,m:1+t:83,m:1+t:84,m:1+t:85,m:1+t:86,m:1+t:87,m:1+t:88,m:1+t:89,m:1+t:90,m:1+t:91,m:1+t:92,m:1+t:93,m:1+t:94,m:1+t:95,m:1+t:96,m:1+t:97,m:1+t:98,m:1+t:99',
        'fields': 'f12,f14,f2,f3,f4,f5,f6'
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('data') and data['data'].get('diff'):
            quotes_map = {}
            for item in data['data']['diff']:
                code = item.get('f12', '')
                quotes_map[code] = item
            
            # 匹配自选股中的基金
            fund_count = 0
            for stock in fund_stocks:
                code = stock.split('.')[0]
                if code in quotes_map:
                    item = quotes_map[code]
                    real_data[stock] = {
                        'code': code,
                        'name': item.get('f14', ''),
                        'close': item.get('f2', 0),
                        'change_pct': item.get('f3', 0),
                        'change_amount': item.get('f4', 0),
                        'volume': item.get('f5', 0),
                        'amount': item.get('f6', 0),
                        'source': '东方财富(基金)'
                    }
                    fund_count += 1
            
            success_sources.append(f'东方财富(基金): {fund_count}只')
            print(f"✅ 东方财富基金成功: {fund_count} 只")
    
except Exception as e:
    print(f"⚠️ 东方财富基金接口失败: {e}")

# 方法3: baostock 补充
print("\n🔄 方法3: baostock 补充...")
try:
    import baostock as bs
    from datetime import timedelta
    
    lg = bs.login()
    if lg.error_code == '0':
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        bs_count = 0
        # 只测试未能获取的股票
        for stock in watchlist:
            if stock in real_data:
                continue
            
            code = stock.replace('.SH', '').replace('.SZ', '')
            market = 'sh' if '.SH' in stock else 'sz'
            full_code = f"{market}.{code}"
            
            try:
                rs = bs.query_history_k_data_plus(
                    full_code,
                    "date,open,high,low,close,volume",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs.error_code == '0':
                    data_list = []
                    while rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list:
                        latest = data_list[-1]
                        real_data[stock] = {
                            'date': latest[0],
                            'close': float(latest[5]) if latest[5] else 0,
                            'source': 'baostock'
                        }
                        bs_count += 1
                        
            except:
                pass
        
        bs.logout()
        
        if bs_count > 0:
            success_sources.append(f'baostock: {bs_count}只')
            print(f"✅ baostock 补充: {bs_count} 只")
            
except Exception as e:
    print(f"⚠️ baostock 失败: {e}")

print()
print("="*80)
print("  📊 最终测试结果")
print("="*80)
print()

# 统计结果
total = len(watchlist)
success = len(real_data)
failed = total - success
success_rate = (success / total * 100) if total > 0 else 0

print(f"📊 自选股总数: {total} 只")
print(f"✅ 成功获取: {success} 只")
print(f"❌ 未能获取: {failed} 只")
print(f"📈 成功率: {success_rate:.1f}%")
print()

if success_sources:
    print(f"📡 数据来源:")
    for source in success_sources:
        print(f"   - {source}")
    print()

# 显示成功获取的数据
if real_data:
    print("="*80)
    print(f"  📋 成功获取的行情数据 (共{len(real_data)}只)")
    print("="*80)
    print()
    
    print(f"{'代码':<12} {'名称':<12} {'最新价':>10} {'涨跌幅':>10} {'来源':<15}")
    print("-" * 65)
    
    for stock, data in list(real_data.items())[:20]:
        code = stock
        name = data.get('name', data.get('code', ''))[:10]
        close = data.get('close', data.get('最新价', 0))
        change_pct = data.get('change_pct', data.get('涨跌幅', 0))
        source = data.get('source', 'unknown')[:13]
        
        close_str = f"{close:.2f}" if isinstance(close, (int, float)) and close else "N/A"
        change_str = f"{change_pct:+.2f}%" if isinstance(change_pct, (int, float)) else "N/A"
        
        print(f"{code:<12} {name:<12} {close_str:>10} {change_str:>10} {source:<15}")
    
    if len(real_data) > 20:
        print(f"... 还有 {len(real_data) - 20} 只")

# 显示未能获取的股票
if failed > 0:
    failed_stocks = [s for s in watchlist if s not in real_data]
    
    print()
    print("="*80)
    print(f"  ❌ 未能获取行情的 {len(failed_stocks)} 只股票")
    print("="*80)
    print()
    
    print("💡 未能获取的可能原因:")
    print("   1. 基金代码格式特殊（如16xxxxx）")
    print("   2. 今日非交易日")
    print("   3. 网络连接不稳定")
    print("   4. 数据源接口限制")
    print()

# 保存结果
result = {
    'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total': total,
    'success': success,
    'failed': failed,
    'success_rate': f"{success_rate:.1f}%",
    'sources': success_sources,
    'failed_count': len(failed_stocks) if failed > 0 else 0
}

output_file = Path(__file__).parent / 'data' / 'realtime_final_result.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 同时保存完整的行情数据
quotes_file = Path(__file__).parent / 'data' / 'realtime_quotes.json'
with open(quotes_file, 'w', encoding='utf-8') as f:
    json.dump(real_data, f, ensure_ascii=False, indent=2)

print("="*80)
print(f"✅ 测试完成！")
print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📁 结果已保存: {output_file}")
print(f"📁 行情数据: {quotes_file}")
print("="*80)
