#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌盘扫描脚本 - 自动扫描通达信数据目录中的最新数据
使用方法: python scan_panic.py
"""

import os
import glob
import csv
from datetime import datetime

def scan_tdx_directory():
    """扫描通达信数据目录"""
    # 通达信数据目录 - 根据您的实际路径修改
    tdx_paths = [
        r"C:\Users\Administrator\AppData\Local\VirtualStore\Program Files\tdx",
        r"C:\Users\Administrator\Documents\tdx",
        r"C:\通达信\Vipdoc",
        r"C:\TdxW",
    ]
    
    # 查找所有CSV文件
    all_files = []
    for base_path in tdx_paths:
        if os.path.exists(base_path):
            csv_files = glob.glob(os.path.join(base_path, "**/*.csv"), recursive=True)
            all_files.extend(csv_files)
    
    return all_files

def parse_csv_file(filepath):
    """解析CSV文件"""
    stocks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # 跳过表头
            
            for row in reader:
                if len(row) >= 7:
                    try:
                        stocks.append({
                            'symbol': row[0],
                            'date': row[1],
                            'open': float(row[2]),
                            'high': float(row[3]),
                            'low': float(row[4]),
                            'close': float(row[5]),
                            'volume': int(row[6])
                        })
                    except:
                        pass
    except:
        pass
    
    return stocks

def analyze_panic(stocks):
    """分析恐慌盘"""
    results = []
    
    for stock in stocks:
        drop = (stock['close'] - stock['open']) / stock['open']
        low_drop = (stock['low'] - stock['open']) / stock['open']
        max_drop = min(drop, low_drop)
        
        score = 0
        reasons = []
        
        # 跌幅评分
        if max_drop <= -0.05:
            score += 30
            reasons.append(f"大跌{max_drop*100:.2f}%")
        elif max_drop <= -0.03:
            score += 15
            reasons.append(f"下跌{max_drop*100:.2f}%")
        
        # 放量评分 (假设平均成交量)
        volume_ratio = stock['volume'] / (stock['volume'] * 0.8 + 1)
        if volume_ratio >= 2.0:
            score += 25
            reasons.append(f"放量{volume_ratio:.1f}倍")
        elif volume_ratio >= 1.5:
            score += 15
            reasons.append(f"温和放量{volume_ratio:.1f}倍")
        
        if len(reasons) >= 1 and score >= 15:
            results.append({
                'symbol': stock['symbol'],
                'drop': max_drop,
                'volume_ratio': volume_ratio,
                'reason': ' + '.join(reasons),
                'score': score,
                'recommendation': '强烈建议关注' if score >= 50 else '建议关注'
            })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)

def main():
    print("=" * 80)
    print("🔍 恐慌盘自动扫描系统")
    print("=" * 80)
    
    print("\n📂 扫描通达信数据目录...")
    files = scan_tdx_directory()
    
    if not files:
        print("❌ 未找到通达信数据文件")
        print("\n💡 请检查通达信数据路径，或手动导入数据到 today_data.csv")
        return
    
    print(f"✅ 找到 {len(files)} 个数据文件")
    
    all_stocks = []
    for filepath in files[:5]:  # 只分析前5个文件
        stocks = parse_csv_file(filepath)
        all_stocks.extend(stocks)
    
    if not all_stocks:
        print("❌ 未能解析任何数据")
        return
    
    print(f"📊 共解析 {len(all_stocks)} 条股票数据")
    
    results = analyze_panic(all_stocks)
    
    print("\n" + "=" * 80)
    print("📈 恐慌盘分析结果")
    print("=" * 80)
    
    if not results:
        print("\n✅ 今日市场无恐慌盘迹象，市场情绪稳定")
    else:
        print(f"\n🔥 发现 {len(results)} 只恐慌抛压股票:\n")
        
        for i, stock in enumerate(results[:10], 1):
            emoji = "🔥" if stock['recommendation'] == '强烈建议关注' else "📊"
            print(f"{i}. {emoji} {stock['symbol']}")
            print(f"   {stock['reason']}")
            print(f"   评分: {stock['score']}分 | {stock['recommendation']}")
            print()
        
        print("=" * 80)
        print("💡 操作建议:")
        print("=" * 80)
        print("  1. 等待缩量企稳后再买入")
        print("  2. 分批建仓，控制仓位")
        print("  3. 设置止损位，一般不超过6%")
        print("  4. 目标收益8%左右及时止盈")
        print("  5. 持仓不超过15个交易日")
    
    print("\n" + "=" * 80)
    print(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
