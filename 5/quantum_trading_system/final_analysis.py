#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终分析：准确统计缺失股票
"""

import os
import re
from pathlib import Path

TDX_PATH = r"C:\new_tdx\T0002\blocknew"

print("="*80)
print("  📋 自选股加载最终分析")
print("="*80)
print()

# 读取通达信原始数据
print("📂 读取通达信原始数据...")
zxg_path = os.path.join(TDX_PATH, "zxg.blk")

with open(zxg_path, 'rb') as f:
    data = f.read()

text = data.decode('gbk', errors='ignore')

# 按行读取，去重
tdx_set = set()
for line in text.split('\r\n') if '\r\n' in text else text.split('\n'):
    line = line.strip()
    if not line:
        continue
    
    match = re.match(r'^(\d{6})(\d)$', line)
    if match:
        code = match.group(1)
        market_code = match.group(2)
        
        if market_code in ('1', '5'):
            market = 'SH'
        else:
            market = 'SZ'
        
        full_code = f"{code}.{market}"
        tdx_set.add(full_code)

tdx_codes = sorted(list(tdx_set))
print(f"✅ 通达信去重后: {len(tdx_codes)} 只")
print()

# 读取监控系统数据
print("📂 读取监控系统数据...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    monitor_stocks = [line.strip() for line in f if line.strip()]

print(f"✅ 监控系统数据: {len(monitor_stocks)} 只")
print()

# 找出缺失的
tdx_set_clean = set(tdx_codes)
monitor_set_clean = set(monitor_stocks)

missing_stocks = tdx_set_clean - monitor_set_clean
extra_stocks = monitor_set_clean - tdx_set_clean

print("="*80)
print("  📊 加载状态统计")
print("="*80)
print()
print(f"通达信原始数据: {len(tdx_codes)} 只")
print(f"监控系统加载: {len(monitor_stocks)} 只")
print(f"✅ 成功加载: {len(tdx_set_clean & monitor_set_clean)} 只")
print(f"❌ 缺失股票: {len(missing_stocks)} 只")
print()

# 显示缺失的股票
if missing_stocks:
    print("="*80)
    print(f"  ❌ 未成功加载的 {len(missing_stocks)} 只股票")
    print("="*80)
    print()
    
    # 按市场分组
    missing_sh = sorted([s for s in missing_stocks if '.SH' in s])
    missing_sz = sorted([s for s in missing_stocks if '.SZ' in s])
    
    print(f"📈 上海(SH) - 缺失 {len(missing_sh)} 只:")
    if missing_sh:
        for i, stock in enumerate(missing_sh, 1):
            print(f"  {i:2d}. {stock}")
    print()
    
    print(f"📉 深圳(SZ) - 缺失 {len(missing_sz)} 只:")
    if missing_sz:
        for i, stock in enumerate(missing_sz, 1):
            print(f"  {i:2d}. {stock}")
    print()
else:
    print("✅ 所有自选股都已成功加载！")

print()
print("="*80)
print("  💡 缺失原因分析")
print("="*80)
print()
print(f"缺失数量: {len(missing_stocks)} 只 (占总数的 {len(missing_stocks)/len(tdx_codes)*100:.1f}%)")
print()
print("可能原因:")
print("1. 通达信文件中部分代码格式不符合标准")
print("2. 某些代码在导入时被过滤")
print("3. 文件中存在一些无效数据")
print()

print("="*80)

# 保存详细报告
report_file = Path(__file__).parent / 'data' / 'missing_stocks_final.txt'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(f"自选股加载最终分析\n")
    f.write("="*60 + "\n\n")
    f.write(f"通达信总数: {len(tdx_codes)}\n")
    f.write(f"监控系统加载: {len(monitor_stocks)}\n")
    f.write(f"缺失: {len(missing_stocks)}\n\n")
    
    if missing_stocks:
        f.write("缺失股票列表:\n")
        f.write("-"*40 + "\n")
        for stock in sorted(missing_stocks):
            f.write(f"{stock}\n")

print(f"\n📁 详细报告已保存: {report_file}")
