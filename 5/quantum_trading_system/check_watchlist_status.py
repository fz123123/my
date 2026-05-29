#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查自选股加载状态，识别潜在问题
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("  📋 自选股加载状态检查")
print("="*80)
print()

# 读取通达信原文件
print("📂 [1/4] 读取通达信原始文件...")
TDX_PATH = r"C:\new_tdx\T0002\blocknew"
zxg_path = os.path.join(TDX_PATH, "zxg.blk")

if not os.path.exists(zxg_path):
    print(f"❌ 通达信文件不存在: {zxg_path}")
    sys.exit(1)

import re
with open(zxg_path, 'rb') as f:
    data = f.read()
text = data.decode('gbk', errors='ignore')
tdx_codes = re.findall(r'\d{6}', text)
print(f"✅ 通达信原始数据: {len(tdx_codes)} 个代码")

# 读取监控文件
print("\n📂 [2/4] 读取监控系统文件...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    monitor_stocks = [line.strip() for line in f if line.strip()]
print(f"✅ 监控系统加载: {len(monitor_stocks)} 只")

# 读取配置文件
print("\n📂 [3/4] 读取系统配置文件...")
import json
config_file = Path(__file__).parent / 'system_config.json'
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    config_stocks = config.get('watchlist', [])
    print(f"✅ 系统配置加载: {len(config_stocks)} 只")
else:
    config_stocks = []
    print(f"⚠️ 配置文件不存在")

# 分析状态
print("\n📊 [4/4] 分析加载状态...")
print()

# 分类检查
issues = {
    'missing_from_monitor': [],
    'missing_from_config': [],
    'invalid_format': [],
    'duplicate': []
}

# 检查监控文件
monitor_codes = set()
for stock in monitor_stocks:
    code = stock.replace('.SH', '').replace('.SZ', '')
    if not re.match(r'^\d{6}$', code):
        issues['invalid_format'].append(stock)
    monitor_codes.add(stock)

# 检查配置文件
config_codes = set(config_stocks)

# 找出差异
missing_from_monitor = set(tdx_codes) - monitor_codes
missing_from_config = set(monitor_codes) - config_codes

# 检查重复
if len(monitor_stocks) != len(monitor_codes):
    issues['duplicate'].extend([s for s in monitor_stocks if monitor_stocks.count(s) > 1])

print("="*80)
print("  📋 加载状态报告")
print("="*80)
print()

# 1. 通达信原始数据
print(f"📁 通达信原始数据: {len(tdx_codes)} 个股票代码")
print()

# 2. 监控系统加载
print(f"📦 监控系统加载: {len(monitor_stocks)} 只")
if len(monitor_stocks) != len(set(monitor_stocks)):
    print(f"   ⚠️ 发现重复: {len(monitor_stocks) - len(set(monitor_stocks))} 个")
print()

# 3. 系统配置
print(f"⚙️ 系统配置加载: {len(config_stocks)} 只")
print()

# 4. 差异对比
print("-"*80)
print("  🔍 差异分析")
print("-"*80)
print()

if missing_from_monitor:
    print(f"⚠️  通达信有但监控系统缺少: {len(missing_from_monitor)} 个")
    print("   代码列表:")
    for code in sorted(list(missing_from_monitor)[:30]):
        print(f"     - {code}")
    if len(missing_from_monitor) > 30:
        print(f"     ... 还有 {len(missing_from_monitor) - 30} 个")
    print()

if missing_from_config:
    print(f"⚠️  监控系统有但系统配置缺少: {len(missing_from_config)} 个")
    print("   代码列表:")
    for stock in sorted(list(missing_from_config))[:20]:
        print(f"     - {stock}")
    if len(missing_from_config) > 20:
        print(f"     ... 还有 {len(missing_from_config) - 20} 个")
    print()

if issues['invalid_format']:
    print(f"❌ 格式错误: {len(issues['invalid_format'])} 个")
    for stock in issues['invalid_format']:
        print(f"     - {stock}")
    print()

# 5. 自选股构成
print("="*80)
print("  📈 自选股构成分析")
print("="*80)
print()

stock_count = 0
fund_count = 0
bond_count = 0
other_count = 0

for stock in monitor_stocks:
    code = stock.split('.')[0]
    if code.startswith(('000', '001', '002', '300', '600', '601', '688')):
        stock_count += 1
    elif code.startswith(('16', '5', '4', '1')):
        fund_count += 1
    elif 'SH' in stock and len(code) == 6:
        bond_count += 1
    else:
        other_count += 1

print(f"📊 自选股类型分布:")
print(f"   - A股股票: {stock_count} 只")
print(f"   - 基金: {fund_count} 只")
print(f"   - 债券: {bond_count} 只")
print(f"   - 其他: {other_count} 只")
print()

# 6. 市场分布
sh_count = sum(1 for s in monitor_stocks if '.SH' in s)
sz_count = sum(1 for s in monitor_stocks if '.SZ' in s)

print(f"📊 市场分布:")
print(f"   - 上海(SH): {sh_count} 只")
print(f"   - 深圳(SZ): {sz_count} 只")
print()

print("="*80)
print("  ✅ 检查完成")
print("="*80)
print()

# 保存详细报告
report_file = Path(__file__).parent / 'data' / 'watchlist_check_report.txt'
report_file.parent.mkdir(parents=True, exist_ok=True)

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(f"自选股加载状态检查报告\n")
    f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"通达信原始数据: {len(tdx_codes)} 个\n")
    f.write(f"监控系统加载: {len(monitor_stocks)} 只\n")
    f.write(f"系统配置加载: {len(config_stocks)} 只\n\n")
    
    if missing_from_monitor:
        f.write(f"通达信有但监控系统缺少: {len(missing_from_monitor)} 个\n")
        for code in sorted(list(missing_from_monitor)):
            f.write(f"  - {code}\n")
        f.write("\n")
    
    if missing_from_config:
        f.write(f"监控系统有但系统配置缺少: {len(missing_from_config)} 个\n")
        for stock in sorted(list(missing_from_config)):
            f.write(f"  - {stock}\n")
        f.write("\n")
    
    f.write(f"自选股构成:\n")
    f.write(f"  - A股股票: {stock_count} 只\n")
    f.write(f"  - 基金: {fund_count} 只\n")
    f.write(f"  - 债券: {bond_count} 只\n")
    f.write(f"  - 其他: {other_count} 只\n")

print(f"📁 详细报告已保存: {report_file}")
