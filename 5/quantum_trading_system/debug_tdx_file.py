#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试：查看通达信文件的实际内容
"""

import os

TDX_PATH = r"C:\new_tdx\T0002\blocknew"
zxg_path = os.path.join(TDX_PATH, "zxg.blk")

print("="*80)
print("  📋 通达信自选股文件调试")
print("="*80)
print()

print(f"📁 文件路径: {zxg_path}")
print(f"📁 文件存在: {os.path.exists(zxg_path)}")
print()

if not os.path.exists(zxg_path):
    print("❌ 文件不存在！")
    exit(1)

# 读取文件
with open(zxg_path, 'rb') as f:
    data = f.read()

print(f"📊 文件大小: {len(data)} 字节")
print()

# 尝试不同编码
print("🔍 尝试不同编码...")
print()

# GBK编码
try:
    text_gbk = data.decode('gbk')
    print("✅ GBK编码成功:")
    print("-" * 60)
    print(text_gbk[:500])
    print()
    codes_gbk = len([c for c in text_gbk.split() if c.isdigit() and len(c) == 6])
    print(f"   找到 {codes_gbk} 个6位数字代码")
except Exception as e:
    print(f"❌ GBK编码失败: {e}")

print()

# UTF-8编码
try:
    text_utf8 = data.decode('utf-8')
    print("✅ UTF-8编码:")
    print("-" * 60)
    print(text_utf8[:500])
    print()
except Exception as e:
    print(f"❌ UTF-8编码失败: {e}")

print()
print("="*80)
print("  文件内容分析")
print("="*80)
print()

# 分析内容
import re

# 方法1: 找所有6位数字
codes = re.findall(r'\b(\d{6})\b', text_gbk)
print(f"📊 方法1 - 6位数字: {len(codes)} 个")
if codes:
    print(f"   前10个: {codes[:10]}")

print()

# 方法2: 按行分割
lines = text_gbk.split('\n')
print(f"📊 方法2 - 行数: {len(lines)} 行")

# 显示前10行
print(f"\n前10行内容:")
for i, line in enumerate(lines[:10], 1):
    print(f"  {i}: {repr(line)}")

print()
print("="*80)
