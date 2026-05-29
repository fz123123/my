#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版：179只股票实时行情测试
尝试多种数据源
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("  📊 179只股票实时行情获取测试")
print("="*80)
print()

# 读取自选股
print("📂 读取179只自选股...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    watchlist = [line.strip() for line in f if line.strip()]

print(f"✅ 加载完成: {len(watchlist)} 只")

# 分类
sh_stocks = [s for s in watchlist if '.SH' in s]
sz_stocks = [s for s in watchlist if '.SZ' in s]
fund_stocks = [s for s in watchlist if s.split('.')[0].startswith(('16', '5'))]
stock_stocks = [s for s in watchlist if not s.split('.')[0].startswith(('16', '5'))]

print(f"\n📊 自选股分类:")
print(f"   - 上海: {len(sh_stocks)} 只")
print(f"   - 深圳: {len(sz_stocks)} 只")
print(f"   - 基金: {len(fund_stocks)} 只")
print(f"   - A股股票: {len(stock_stocks)} 只")
print()

real_data = {}
failed_stocks = []
success_sources = []

# 方法1: 尝试 baostock (历史K线数据，模拟实时)
try:
    import baostock as bs
    print("🔄 尝试使用 baostock 获取行情数据...")
    
    lg = bs.login()
    if lg.error_code == '0':
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        success_count = 0
        # 测试前30只股票
        for stock in watchlist[:30]:
            code = stock.replace('.SH', '').replace('.SZ', '')
            market = 'sh' if '.SH' in stock else 'sz'
            full_code = f"{market}.{code}"
            
            try:
                rs = bs.query_history_k_data_plus(
                    full_code,
                    "date,open,high,low,close,volume,amount",
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
                            'open': float(latest[1]) if latest[1] else 0,
                            'high': float(latest[2]) if latest[2] else 0,
                            'low': float(latest[3]) if latest[3] else 0,
                            'close': float(latest[4]) if latest[4] else 0,
                            'volume': float(latest[5]) if latest[5] else 0,
                            'amount': float(latest[6]) if latest[6] else 0,
                            'source': 'baostock'
                        }
                        success_count += 1
                        
            except Exception as e:
                pass
        
        bs.logout()
        
        if success_count > 0:
            success_sources.append(f'baostock: {success_count}只')
            print(f"✅ baostock 成功: {success_count} 只")
        
except Exception as e:
    print(f"⚠️ baostock 失败: {e}")

print()

# 方法2: 尝试 akshare (实时行情)
if len(real_data) < len(watchlist) * 0.5:
    try:
        import akshare as ak
        print("🔄 尝试使用 akshare 获取实时行情...")
        
        # 获取A股实时行情
        df = ak.stock_zh_a_spot_em()
        print(f"✅ akshare 成功获取 {len(df)} 只股票")
        
        # 创建代码到行情的映射
        quotes_map = {}
        for _, row in df.iterrows():
            code = str(row.get('代码', ''))
            if code:
                quotes_map[code] = row.to_dict()
        
        # 匹配自选股
        akshare_count = 0
        for stock in watchlist:
            if stock in real_data:
                continue
                
            code = stock.split('.')[0]
            if code in quotes_map:
                real_data[stock] = {
                    'code': code,
                    'name': quotes_map[code].get('名称', ''),
                    'close': quotes_map[code].get('最新价', 0),
                    'open': quotes_map[code].get('今开', 0),
                    'high': quotes_map[code].get('最高', 0),
                    'low': quotes_map[code].get('最低', 0),
                    'volume': quotes_map[code].get('成交量', 0),
                    'amount': quotes_map[code].get('成交额', 0),
                    'change_pct': quotes_map[code].get('涨跌幅', 0),
                    'change_amount': quotes_map[code].get('涨跌额', 0),
                    'source': 'akshare'
                }
                akshare_count += 1
        
        if akshare_count > 0:
            success_sources.append(f'akshare: {akshare_count}只')
            print(f"✅ akshare 匹配成功: {akshare_count} 只")
            
    except Exception as e:
        print(f"⚠️ akshare 失败: {e}")

print()
print("="*80)
print("  📊 测试结果")
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

# 显示成功获取的数据样本
if real_data:
    print("="*80)
    print("  📋 成功获取的行情数据（前10只）")
    print("="*80)
    print()
    
    print(f"{'代码':<12} {'名称':<8} {'最新价':>8} {'涨跌额':>8} {'涨跌幅':>8} {'来源':<10}")
    print("-" * 60)
    
    for i, (stock, data) in enumerate(list(real_data.items())[:10], 1):
        code = stock
        name = data.get('name', data.get('code', ''))
        close = data.get('close', data.get('最新价', 0))
        change = data.get('change_amount', data.get('涨跌额', 0))
        change_pct = data.get('change_pct', data.get('涨跌幅', 0))
        source = data.get('source', 'unknown')
        
        # 格式化显示
        close_str = f"{close:.2f}" if isinstance(close, (int, float)) else str(close)
        change_str = f"{change:+.2f}" if isinstance(change, (int, float)) else str(change)
        change_pct_str = f"{change_pct:+.2f}%" if isinstance(change_pct, (int, float)) else str(change_pct)
        
        print(f"{code:<12} {name:<8} {close_str:>8} {change_str:>8} {change_pct_str:>8} {source:<10}")

# 显示未能获取的股票
if failed > 0:
    failed_stocks = [s for s in watchlist if s not in real_data]
    
    print()
    print("="*80)
    print(f"  ❌ 未能获取行情的 {len(failed_stocks)} 只股票")
    print("="*80)
    print()
    
    # 按市场分组
    failed_sh = [s for s in failed_stocks if '.SH' in s]
    failed_sz = [s for s in failed_stocks if '.SZ' in s]
    
    print(f"📈 上海(SH) - {len(failed_sh)} 只:")
    if failed_sh:
        for stock in failed_sh[:10]:
            print(f"   - {stock}")
        if len(failed_sh) > 10:
            print(f"   ... 还有 {len(failed_sh) - 10} 只")
    print()
    
    print(f"📉 深圳(SZ) - {len(failed_sz)} 只:")
    if failed_sz:
        for stock in failed_sz[:10]:
            print(f"   - {stock}")
        if len(failed_sz) > 10:
            print(f"   ... 还有 {len(failed_sz) - 10} 只")
    print()
    
    print("💡 可能原因:")
    print("   1. 网络连接问题（akshare接口不稳定）")
    print("   2. 部分基金/债券代码不在数据源中")
    print("   3. baostock是历史数据，不是真正的实时行情")
    print("   4. 今日非交易日，获取不到数据")

# 保存结果
result = {
    'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total': total,
    'success': success,
    'failed': failed,
    'success_rate': f"{success_rate:.1f}%",
    'sources': success_sources,
    'failed_stocks': failed_stocks if failed_stocks else [],
    'real_data_count': len(real_data)
}

output_file = Path(__file__).parent / 'data' / 'realtime_test_v2_result.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("="*80)
print(f"✅ 测试完成！")
print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📁 结果已保存: {output_file}")
print("="*80)
