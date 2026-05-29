#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试179只股票的实时行情获取
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
print()

# 尝试使用多种数据源
success_sources = []
failed_stocks = []
real_data = {}

# 方法1: 使用 akshare
try:
    import akshare as ak
    print("🔄 尝试使用 akshare 获取实时行情...")
    
    # 获取所有A股实时行情
    df = ak.stock_zh_a_spot_em()
    print(f"✅ 成功获取 {len(df)} 只股票行情")
    
    # 提取代码到行情的映射
    if '代码' in df.columns:
        quotes_map = dict(zip(df['代码'], df.to_dict('records')))
        
        success_count = 0
        for stock in watchlist:
            code = stock.split('.')[0]
            if code in quotes_map:
                real_data[stock] = quotes_map[code]
                success_count += 1
        
        print(f"✅ 匹配到 {success_count}/{len(watchlist)} 只股票")
        success_sources.append(f'akshare: {success_count}只')
        
except Exception as e:
    print(f"❌ akshare 失败: {e}")

print()

# 方法2: 使用 baostock
if len(real_data) < len(watchlist) * 0.8:  # 如果成功率低于80%，尝试baostock
    try:
        import baostock as bs
        print("🔄 尝试使用 baostock 获取补充数据...")
        
        lg = bs.login()
        if lg.error_code == '0':
            from datetime import timedelta
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            # 只测试前20只
            for stock in watchlist[:20]:
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
                            real_data[stock] = {
                                'close': float(data_list[-1][5]) if data_list[-1][5] else 0,
                                'date': data_list[-1][0]
                            }
                except:
                    pass
            
            bs.logout()
            
            baostock_count = len([s for s in watchlist[:20] if s in real_data])
            print(f"✅ baostock 补充: {baostock_count} 只")
            success_sources.append(f'baostock: {baostock_count}只')
            
    except Exception as e:
        print(f"⚠️ baostock 失败: {e}")

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

print(f"📡 数据来源:")
for source in success_sources:
    print(f"   - {source}")
print()

# 显示未能获取的股票
if failed > 0:
    # 找出失败的股票
    failed_stocks = [s for s in watchlist if s not in real_data]
    
    print("="*80)
    print(f"  ❌ 未能获取行情的 {len(failed_stocks)} 只股票")
    print("="*80)
    print()
    
    # 按市场分组
    failed_sh = [s for s in failed_stocks if '.SH' in s]
    failed_sz = [s for s in failed_stocks if '.SZ' in s]
    
    print(f"📈 上海(SH) - {len(failed_sh)} 只:")
    if failed_sh:
        for stock in failed_sh[:15]:
            print(f"   - {stock}")
        if len(failed_sh) > 15:
            print(f"   ... 还有 {len(failed_sh) - 15} 只")
    print()
    
    print(f"📉 深圳(SZ) - {len(failed_sz)} 只:")
    if failed_sz:
        for stock in failed_sz[:15]:
            print(f"   - {stock}")
        if len(failed_sz) > 15:
            print(f"   ... 还有 {len(failed_sz) - 15} 只")
    print()

# 保存结果
result = {
    'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total': total,
    'success': success,
    'failed': failed,
    'success_rate': f"{success_rate:.1f}%",
    'sources': success_sources,
    'failed_stocks': failed_stocks if failed_stocks else [],
    'real_data_sample': {k: v for k, v in list(real_data.items())[:10]}
}

output_file = Path(__file__).parent / 'data' / 'realtime_test_result.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("="*80)
print(f"✅ 测试完成！")
print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📁 结果已保存: {output_file}")
print("="*80)
