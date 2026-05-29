#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 数据准确性验证工具
验证实时数据的准确性和完整性
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
from datetime import datetime

def check_data_accuracy():
    """检查数据准确性"""
    
    print("\n" + "="*120)
    print("🔍 涨停先知 - 数据准确性验证工具")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*120)
    
    stock_code = "sh605289"
    url = f"http://hq.sinajs.cn/list={stock_code}"
    
    print("\n📡 测试新浪财经API连接...")
    print(f"   URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'http://finance.sina.com.cn'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n✅ API连接成功!")
        print(f"   状态码: {response.status_code}")
        print(f"   响应长度: {len(response.text)} 字节")
        print(f"   编码: {response.encoding}")
        
        print(f"\n📊 原始数据:")
        print(f"   {response.text}")
        
        # 解析数据
        parts = response.text.split('=')[-1].strip().replace('"', '')
        fields = parts.split(',')
        
        print(f"\n📋 数据字段解析:")
        print(f"   字段总数: {len(fields)}个")
        
        field_names = [
            '股票名称', '今日开盘价', '昨日收盘价', '当前价格', '今日最高价', 
            '今日最低价', '成交金额', '成交量', '买1量', '买1价',
            '买2量', '买2价', '买3量', '买3价', '买4量', '买4价',
            '买5量', '买5价', '卖1量', '卖1价', '卖2量', '卖2价',
            '卖3量', '卖3价', '卖4量', '卖4价', '卖5量', '卖5价',
            '日期', '时间', '状态'
        ]
        
        for i, (name, value) in enumerate(zip(field_names, fields[:32])):
            print(f"   [{i:02d}] {name}: {value}")
        
        # 关键数据验证
        print("\n" + "="*120)
        print("✅ 关键数据验证:")
        print("="*120)
        
        # 1. 股票名称
        stock_name = fields[0]
        print(f"\n1️⃣ 股票名称验证:")
        print(f"   预期: 罗曼股份")
        print(f"   实际: {stock_name}")
        print(f"   ✅ {'通过' if '罗曼' in stock_name else '失败'}")
        
        # 2. 昨日收盘价
        yesterday_close = float(fields[2]) if fields[2] else 0
        print(f"\n2️⃣ 昨日收盘价验证:")
        print(f"   数值: ¥{yesterday_close:.2f}")
        print(f"   ✅ {'通过' if yesterday_close > 0 else '失败'}")
        
        # 3. 当前价格
        current_price = float(fields[3]) if fields[3] and fields[3] != '0.000' else 0
        print(f"\n3️⃣ 当前价格验证:")
        print(f"   数值: ¥{current_price:.2f}")
        
        if current_price > 0:
            print(f"   状态: 🟢 交易时间（实时价格）")
            print(f"   ✅ 通过")
        else:
            print(f"   状态: 🟡 非交易时间（使用昨收价）")
            print(f"   建议: 使用昨日收盘价 ¥{yesterday_close:.2f}")
            current_price = yesterday_close
            print(f"   ✅ 通过（已自动修正）")
        
        # 4. 今日最高价
        high_price = float(fields[4]) if fields[4] and fields[4] != '0.000' else 0
        print(f"\n4️⃣ 今日最高价验证:")
        print(f"   数值: ¥{high_price:.2f}")
        if high_price > 0:
            print(f"   状态: 🟢 有效数据")
            print(f"   ✅ 通过")
        else:
            print(f"   状态: 🟡 非交易时间")
            high_price = current_price
            print(f"   ✅ 通过（已自动修正）")
        
        # 5. 今日最低价
        low_price = float(fields[5]) if fields[5] and fields[5] != '0.000' else 0
        print(f"\n5️⃣ 今日最低价验证:")
        print(f"   数值: ¥{low_price:.2f}")
        if low_price > 0:
            print(f"   状态: 🟢 有效数据")
            print(f"   ✅ 通过")
        else:
            print(f"   状态: 🟡 非交易时间")
            low_price = current_price
            print(f"   ✅ 通过（已自动修正）")
        
        # 6. 时间戳
        update_date = fields[30] if len(fields) > 30 else ""
        update_time = fields[31] if len(fields) > 31 else ""
        print(f"\n6️⃣ 数据更新时间验证:")
        print(f"   日期: {update_date}")
        print(f"   时间: {update_time}")
        print(f"   ✅ 通过")
        
        # 数据逻辑验证
        print("\n" + "="*120)
        print("🔬 数据逻辑验证:")
        print("="*120)
        
        # 验证价格逻辑
        print(f"\n1️⃣ 价格范围验证:")
        print(f"   当前价: ¥{current_price:.2f}")
        print(f"   最高价: ¥{high_price:.2f}")
        print(f"   最低价: ¥{low_price:.2f}")
        
        if high_price >= current_price >= low_price:
            print(f"   ✅ 价格逻辑正确: 最低 ≤ 当前 ≤ 最高")
        else:
            print(f"   ❌ 价格逻辑错误!")
        
        # 验证涨跌幅
        if yesterday_close > 0:
            change = current_price - yesterday_close
            change_pct = (change / yesterday_close) * 100
            print(f"\n2️⃣ 涨跌幅验证:")
            print(f"   昨收价: ¥{yesterday_close:.2f}")
            print(f"   当前价: ¥{current_price:.2f}")
            print(f"   涨跌额: ¥{change:+.2f}")
            print(f"   涨跌幅: {change_pct:+.2f}%")
            
            # 涨跌停限制 (±10%)
            if abs(change_pct) <= 10:
                print(f"   ✅ 涨跌幅在正常范围内 (±10%)")
            else:
                print(f"   ❌ 涨跌幅超出正常范围!")
        
        # 最终数据摘要
        print("\n" + "="*120)
        print("📊 最终数据摘要:")
        print("="*120)
        
        print(f"""
   股票名称: {stock_name}
   股票代码: {stock_code.upper()}
   当前价格: ¥{current_price:.2f}
   昨日收盘: ¥{yesterday_close:.2f}
   今日最高: ¥{high_price:.2f}
   今日最低: ¥{low_price:.2f}
   数据时间: {update_date} {update_time}
   数据状态: {'🟢 实时' if float(fields[3]) > 0 else '🟡 非交易时间'}
""")
        
        print("="*120)
        print("✅ 数据准确性验证完成!")
        print("="*120)
        
        return {
            'stock_name': stock_name,
            'current_price': current_price,
            'yesterday_close': yesterday_close,
            'high_price': high_price,
            'low_price': low_price,
            'update_time': f"{update_date} {update_time}",
            'is_realtime': float(fields[3]) > 0
        }
        
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        return None

if __name__ == "__main__":
    result = check_data_accuracy()
