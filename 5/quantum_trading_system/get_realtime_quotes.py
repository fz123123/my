#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取自选股实时行情数据
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("⚠️ akshare 未安装，将使用模拟数据")

print("="*80)
print("  📊 自选股实时行情数据获取")
print("="*80)
print()

# 读取自选股列表
print("📂 读取自选股列表...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    watchlist = [line.strip() for line in f if line.strip()]

print(f"✅ 读取到 {len(watchlist)} 只自选股")
print()

if AKSHARE_AVAILABLE:
    print("🔄 正在获取实时行情数据...")
    
    try:
        # 使用 akshare 获取实时行情
        df = ak.stock_zh_a_spot_em()
        print(f"✅ 成功获取 A 股实时行情，共 {len(df)} 只")
        print()
        
        # 筛选自选股
        watch_codes = [s.replace('.SH', '').replace('.SZ', '') for s in watchlist]
        
        if '代码' in df.columns:
            df_watch = df[df['代码'].isin(watch_codes)]
        elif 'code' in df.columns:
            df_watch = df[df['code'].isin(watch_codes)]
        else:
            print("⚠️ 无法识别代码列，使用全部数据")
            df_watch = df.head(len(watchlist))
        
        print(f"📊 筛选出 {len(df_watch)} 只自选股行情")
        print()
        
        # 显示前20只股票的行情
        print("="*80)
        print("  📈 前20只自选股实时行情")
        print("="*80)
        print()
        
        display_cols = ['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额', '换手率']
        display_cols = [c for c in display_cols if c in df_watch.columns]
        
        if display_cols:
            print(df_watch[display_cols].head(20).to_string(index=False))
        
        # 保存到文件
        output_file = Path(__file__).parent / 'data' / 'realtime_quotes.csv'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df_watch.to_csv(output_file, index=False, encoding='utf-8-sig')
        print()
        print(f"✅ 实时行情已保存到: {output_file}")
        
        # 保存JSON格式
        json_file = Path(__file__).parent / 'data' / 'realtime_quotes.json'
        records = df_watch.to_dict('records')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total': len(records),
                'data': records
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON格式已保存到: {json_file}")
        
    except Exception as e:
        print(f"❌ 获取实时行情失败: {e}")
        import traceback
        traceback.print_exc()

else:
    print("⚠️ 无法获取实时数据，使用模拟数据演示")
    print()
    
    # 创建模拟数据
    import random
    
    print("="*80)
    print("  📈 模拟实时行情数据（前20只）")
    print("="*80)
    print()
    print(f"{'代码':<10} {'名称':<15} {'最新价':<10} {'涨跌幅':<10} {'成交量(手)':<15}")
    print("-" * 80)
    
    for i, stock in enumerate(watchlist[:20], 1):
        code = stock.split('.')[0]
        name = f"股票{i:02d}"
        price = round(random.uniform(10, 100), 2)
        change = round(random.uniform(-5, 5), 2)
        volume = random.randint(10000, 1000000)
        print(f"{code:<10} {name:<15} {price:<10.2f} {change:>+8.2f}% {volume:>15,}")
    
    print()
    print(f"... 还有 {len(watchlist) - 20} 只股票")
    print()
    print("⚠️ 这是模拟数据，请安装 akshare 获取真实数据：")
    print("   pip install akshare")

print()
print("="*80)
print(f"✅ 数据获取完成！时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
