#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单回测分析 - 项目0
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\0')

from backtest import BackTest
from strategy import Strategy
from data_processor import DataProcessor

def simple_backtest():
    """简单回测分析"""
    
    print("\n" + "="*80)
    print("    📊 简单回测分析 - 项目0")
    print(f"    分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 初始化组件
    data_processor = DataProcessor()
    strategy = Strategy()
    backtest = BackTest()
    
    # 测试数据文件
    test_files = ['AAPL_daily_data.csv', 'MSFT_daily_data.csv', 'GOOGL_daily_data.csv']
    results = []
    
    for file in test_files:
        file_path = f'C:\\Users\\Administrator\\Documents\\trae_projects\\0\\{file}'
        if os.path.exists(file_path):
            print(f"\n📈 正在回测 {file}...")
            
            try:
                # 读取数据
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                
                if len(df) < 30:
                    print(f"   ⚠️ 数据不足")
                    continue
                
                # 运行回测
                result = backtest.run(df, strategy)
                
                if result:
                    print(f"   ✅ 回测完成")
                    print(f"      收益率: {result.get('return', 0):+.2f}%")
                    print(f"      交易次数: {result.get('trades', 0)}次")
                    
                    results.append({
                        'symbol': file.replace('_daily_data.csv', ''),
                        'return': result.get('return', 0),
                        'trades': result.get('trades', 0),
                        'sharpe': result.get('sharpe', 0)
                    })
            except Exception as e:
                print(f"   ❌ 回测失败: {str(e)}")
        else:
            print(f"\n⚠️ 文件不存在: {file}")
    
    # 输出结果
    if results:
        print("\n" + "="*80)
        print("    📊 回测结果汇总")
        print("="*80)
        
        for res in results:
            color = "🟢" if res['return'] >= 0 else "🔴"
            print(f"   {color} {res['symbol']}: 收益率 {res['return']:+.2f}%, 交易 {res['trades']}次")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    simple_backtest()
