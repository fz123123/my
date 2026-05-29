#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动触发立即更新所有项目实时数据
"""

import sys
import os
sys.path.append('C:/Users/Administrator/Documents/trae_projects/88')

from tdx_data_reader import TDXDataReader
from datetime import datetime
import pandas as pd

def main():
    print('='*70)
    print('    🚀 手动触发立即更新所有项目实时数据')
    print('='*70)
    print(f'⏰ 触发时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*70)

    tdx = TDXDataReader()

    watchlist = [
        ('sh', '688981', '中芯国际'),
        ('sz', '300750', '宁德时代'),
        ('sh', '601318', '中国平安'),
        ('sh', '600519', '贵州茅台'),
        ('sz', '002371', '北方华创'),
        ('sh', '600036', '招商银行'),
        ('sz', '000333', '美的集团'),
        ('sh', '600276', '恒瑞医药'),
        ('sz', '000858', '五粮液'),
        ('sh', '601899', '紫金矿业'),
    ]

    print('\n📊 正在更新项目88自选股数据...')
    results = []
    success_count = 0

    for market, code, name in watchlist:
        try:
            df = tdx.read_stock_data(market, code, 2)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                current_price = latest.get('close', 0)
                date_str = str(latest.name) if hasattr(latest, 'name') else 'Unknown'
                print(f'   ✅ {name} ({market.upper()}{code}): ¥{current_price:.2f} | 日期: {date_str}')
                results.append({
                    'market': market,
                    'code': code,
                    'name': name,
                    'current': current_price,
                    'date': date_str
                })
                success_count += 1
            else:
                print(f'   ❌ {name} ({market.upper()}{code}): 无数据')
        except Exception as e:
            print(f'   ❌ {name} ({market.upper()}{code}): 读取失败 - {str(e)}')

    output_file = 'C:/Users/Administrator/Documents/trae_projects/88/watchlist_realtime.csv'
    df_output = pd.DataFrame(results)
    df_output.to_csv(output_file, index=False, encoding='utf-8')
    print(f'✅ 项目88: 保存 {len(results)} 条数据到 watchlist_realtime.csv')

    print('\n📊 正在更新项目33恐慌盘扫描数据...')
    sh_path = r'C:\new_tdx\vipdoc\sh\lday'
    sz_path = r'C:\new_tdx\vipdoc\sz\lday'

    scan_results = []
    file_count = 0

    for market, path in [('SH', sh_path), ('SZ', sz_path)]:
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.day')]
            print(f'   🔍 扫描市场 {market}: {len(files)} 个文件')
            for f in files[:100]:
                try:
                    code = f[2:-4]
                    df = tdx.read_stock_data('sh' if market == 'SH' else 'sz', code, 1)
                    if df is not None and not df.empty:
                        latest = df.iloc[-1]
                        scan_results.append({
                            'market': market,
                            'code': code,
                            'close': latest.get('close', 0),
                            'date': str(latest.name) if hasattr(latest, 'name') else ''
                        })
                        file_count += 1
                except:
                    pass

    scan_file = 'C:/Users/Administrator/Documents/trae_projects/33/data/tdx/today_data.csv'
    os.makedirs(os.path.dirname(scan_file), exist_ok=True)
    df_scan = pd.DataFrame(scan_results)
    df_scan.to_csv(scan_file, index=False, encoding='utf-8')
    print(f'✅ 项目33: 保存 {len(scan_results)} 条数据到 today_data.csv')

    print('\n' + '='*70)
    print('    ✅ 手动更新完成！')
    print(f'    ⏰ 完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*70)

if __name__ == '__main__':
    main()
