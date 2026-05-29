#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速回测分析 - 使用通达信数据
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from datetime import datetime

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester

def quick_backtest():
    """快速回测分析"""
    
    print("\n" + "="*80)
    print("    🦅 鹰眼压金 - 快速回测分析")
    print(f"    分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    tdx_reader = TDXDataReader()
    backtester = Backtester()
    
    # 选择几只热门股票进行回测
    test_stocks = [
        {'market': 'sz', 'code': '002952', 'name': '亚世光电'},
        {'market': 'sh', 'code': '600618', 'name': '氯碱化工'},
        {'market': 'sz', 'code': '000001', 'name': '平安银行'},
        {'market': 'sh', 'code': '601318', 'name': '中国平安'},
        {'market': 'sz', 'code': '000858', 'name': '五粮液'}
    ]
    
    results = []
    
    for stock in test_stocks:
        print(f"\n📊 正在回测 {stock['name']} ({stock['market'].upper()}{stock['code']})...")
        
        # 获取数据
        df = tdx_reader.read_stock_data(stock['market'], stock['code'], years=1)
        
        if df is None or len(df) < 60:
            print(f"   ❌ 数据不足")
            continue
        
        # 计算指标
        df = backtester.calculate_indicators(df)
        
        # 运行策略回测
        result = backtester.run_backtest(df, strategy='combined')
        
        if result:
            print(f"   ✅ 回测完成")
            print(f"      初始资金: ¥100,000")
            print(f"      最终资金: ¥{result['final_balance']:,.2f}")
            print(f"      总收益率: {result['total_return']:+.2f}%")
            print(f"      最大回撤: {result['max_drawdown']:.2f}%")
            print(f"      交易次数: {result['trade_count']}次")
            
            results.append({
                'name': stock['name'],
                'code': f"{stock['market'].upper()}{stock['code']}",
                'final_balance': result['final_balance'],
                'total_return': result['total_return'],
                'max_drawdown': result['max_drawdown'],
                'trade_count': result['trade_count'],
                'win_rate': result.get('win_rate', 0)
            })
    
    # 输出汇总
    print("\n" + "="*80)
    print("    📈 回测结果汇总")
    print("="*80)
    
    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('total_return', ascending=False)
        
        print(f"\n{'排名':<4} {'股票名称':<10} {'代码':<10} {'最终资金':>12} {'收益率':>10} {'最大回撤':>10} {'交易次数':>8}")
        print("-"*80)
        
        for i, (_, row) in enumerate(df_results.iterrows(), 1):
            color = "🟢" if row['total_return'] >= 0 else "🔴"
            print(f"{i:<4} {row['name']:<10} {row['code']:<10} ¥{row['final_balance']:>11,.2f} {color} {row['total_return']:>+9.2f}% {row['max_drawdown']:>9.2f}% {row['trade_count']:>8}")
        
        print("-"*80)
        
        avg_return = df_results['total_return'].mean()
        print(f"\n📊 平均收益率: {'🟢 +' if avg_return >= 0 else '🔴 '}{avg_return:.2f}%")
        
    print("\n" + "="*80)
    print("⚠️ 风险提示: 回测结果仅供参考，不代表未来收益")
    print("="*80)

if __name__ == "__main__":
    quick_backtest()
