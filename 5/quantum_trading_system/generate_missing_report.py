#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成缺失股票报告
"""

import os
import re
from pathlib import Path

TDX_PATH = r"C:\new_tdx\T0002\blocknew"

print("="*80)
print("  📋 自选股加载缺失分析报告")
print("="*80)
print()

# 读取通达信原始数据
print("📂 读取通达信原始数据...")
zxg_path = os.path.join(TDX_PATH, "zxg.blk")

with open(zxg_path, 'rb') as f:
    data = f.read()

text = data.decode('gbk', errors='ignore')
lines = text.split('\n') + text.split('\r')

tdx_codes = []
for line in lines:
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
        tdx_codes.append(full_code)

print(f"✅ 通达信原始数据: {len(tdx_codes)} 只")
print()

# 读取监控系统数据
print("📂 读取监控系统数据...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    monitor_stocks = [line.strip() for line in f if line.strip()]

print(f"✅ 监控系统数据: {len(monitor_stocks)} 只")
print()

# 找出缺失的
tdx_set = set(tdx_codes)
monitor_set = set(monitor_stocks)

missing_stocks = tdx_set - monitor_set
extra_stocks = monitor_set - tdx_set

print("="*80)
print("  📊 加载状态统计")
print("="*80)
print()
print(f"通达信原始数据: {len(tdx_codes)} 只")
print(f"监控系统加载: {len(monitor_stocks)} 只")
print(f"缺失股票: {len(missing_stocks)} 只")
print(f"额外股票: {len(extra_stocks)} 只")
print()

# 显示缺失的股票
if missing_stocks:
    print("="*80)
    print(f"  ❌ 缺失的 {len(missing_stocks)} 只股票")
    print("="*80)
    print()
    
    # 按市场分组
    missing_sh = sorted([s for s in missing_stocks if '.SH' in s])
    missing_sz = sorted([s for s in missing_stocks if '.SZ' in s])
    
    print(f"上海(SH)缺失: {len(missing_sh)} 只")
    if missing_sh:
        for i, stock in enumerate(missing_sh[:20], 1):
            print(f"  {i:2d}. {stock}")
        if len(missing_sh) > 20:
            print(f"  ... 还有 {len(missing_sh) - 20} 只")
    print()
    
    print(f"深圳(SZ)缺失: {len(missing_sz)} 只")
    if missing_sz:
        for i, stock in enumerate(missing_sz[:20], 1):
            print(f"  {i:2d}. {stock}")
        if len(missing_sz) > 20:
            print(f"  ... 还有 {len(missing_sz) - 20} 只")
    print()

# 显示额外的股票
if extra_stocks:
    print("="*80)
    print(f"  ⚠️  监控系统中额外存在的 {len(extra_stocks)} 只股票")
    print("="*80)
    print()
    
    extra_sh = sorted([s for s in extra_stocks if '.SH' in s])
    extra_sz = sorted([s for s in extra_stocks if '.SZ' in s])
    
    print(f"上海(SH): {len(extra_sh)} 只")
    if extra_sh:
        for i, stock in enumerate(extra_sh[:10], 1):
            print(f"  {i:2d}. {stock}")
        if len(extra_sh) > 10:
            print(f"  ... 还有 {len(extra_sh) - 10} 只")
    print()
    
    print(f"深圳(SZ): {len(extra_sz)} 只")
    if extra_sz:
        for i, stock in enumerate(extra_sz[:10], 1):
            print(f"  {i:2d}. {stock}")
        if len(extra_sz) > 10:
            print(f"  ... 还有 {len(extra_sz) - 10} 只")
    print()

print("="*80)
print("  💡 可能的原因")
print("="*80)
print()
print("1. 通达信文件中可能存在重复代码")
print("2. 部分代码格式不符合6位数字标准")
print("3. 导入过程中进行了去重处理")
print("4. 通达信软件自选股可能有分组")
print()
print("="*80)

# 保存详细报告
report_file = Path(__file__).parent / 'data' / 'missing_stocks_report.txt'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("自选股缺失分析报告\n")
    f.write("="*60 + "\n\n")
    f.write(f"通达信原始: {len(tdx_codes)} 只\n")
    f.write(f"监控系统加载: {len(monitor_stocks)} 只\n")
    f.write(f"缺失股票: {len(missing_stocks)} 只\n\n")
    
    if missing_stocks:
        f.write("缺失股票列表:\n")
        f.write("-"*40 + "\n")
        for stock in sorted(missing_stocks):
            f.write(f"{stock}\n")
        f.write("\n")

print(f"\n📁 详细报告已保存: {report_file}")
