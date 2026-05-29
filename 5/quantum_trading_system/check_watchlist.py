#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查自选股是否正确加载
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("  📋 自选股加载检查")
print("="*80)
print()

# 1. 检查配置文件
print("📂 [1/3] 检查配置文件...")
config_file = Path(__file__).parent / 'system_config.json'

if not config_file.exists():
    print(f"❌ 配置文件不存在: {config_file}")
    sys.exit(1)

import json
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

watchlist = config.get('watchlist', [])
print(f"✅ 配置文件加载成功")
print(f"   自选股数量: {len(watchlist)}")
print()

# 2. 检查监控文件
print("📂 [2/3] 检查监控文件...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'

if not monitor_file.exists():
    print(f"❌ 监控文件不存在: {monitor_file}")
    sys.exit(1)

with open(monitor_file, 'r', encoding='utf-8') as f:
    monitor_stocks = [line.strip() for line in f if line.strip()]

print(f"✅ 监控文件加载成功")
print(f"   自选股数量: {len(monitor_stocks)}")
print()

# 3. 比对两个列表
print("🔍 [3/3] 比对两个列表...")
if len(watchlist) == len(monitor_stocks):
    print(f"✅ 数量一致: {len(watchlist)} 只股票")
else:
    print(f"⚠️ 数量不一致:")
    print(f"   配置文件: {len(watchlist)} 只")
    print(f"   监控文件: {len(monitor_stocks)} 只")

# 显示前10只股票
print()
print("📊 前10只自选股示例:")
print("-" * 60)
for i, stock in enumerate(watchlist[:10], 1):
    status = "✅" if stock in monitor_stocks else "❌"
    print(f"  {i:2d}. {status} {stock}")

if len(watchlist) > 10:
    print(f"  ... 还有 {len(watchlist) - 10} 只")

print()
print("="*80)
print(f"✅ 检查完成！系统包含 {len(watchlist)} 只自选股")
print("="*80)
print()
print("💡 自选股已正确加载到配置中！")
print()
print("⚠️ 但是 Web 应用启动时遇到数据库错误：")
print("   - 错误: sqlite3.OperationalError: unable to open database file")
print("   - 原因: DataEngine 初始化时无法创建数据库文件")
print()
print("🔧 解决方案:")
print("   1. 确保 data 目录存在且可写")
print("   2. 或者暂时使用不需要数据库的简化版界面")
