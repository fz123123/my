#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 baostock 获取股票数据
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("  📊 自选股行情数据获取（baostock方案）")
print("="*80)
print()

# 读取自选股列表
print("📂 读取自选股列表...")
monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
with open(monitor_file, 'r', encoding='utf-8') as f:
    watchlist = [line.strip() for line in f if line.strip()]

print(f"✅ 读取到 {len(watchlist)} 只自选股")
print()

try:
    import baostock as bs
    print("🔄 正在连接 baostock...")
    lg = bs.login()
    
    if lg.error_code == '0':
        print(f"✅ 连接成功: {lg.error_msg}")
        print()
        
        # 获取最近交易日
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        all_data = []
        success_count = 0
        
        print(f"📥 正在获取最近30个交易日数据...")
        print()
        
        for i, stock in enumerate(watchlist[:20], 1):  # 先获取前20只作为演示
            code = stock.replace('.SH', '').replace('.SZ', '')
            market = 'sh' if '.SH' in stock else 'sz'
            full_code = f"{market}.{code}"
            
            try:
                rs = bs.query_history_k_data_plus(
                    full_code,
                    "date,code,open,high,low,close,volume,amount",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs.error_code == '0':
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list:
                        df = pd.DataFrame(data_list, columns=rs.fields)
                        df['name'] = stock
                        all_data.append(df)
                        success_count += 1
                        
                        if i <= 5:
                            print(f"✅ {i}. {stock} - 最新价: {df.iloc[-1]['close']}")
                else:
                    print(f"⚠️ {stock} 获取失败: {rs.error_msg}")
                    
            except Exception as e:
                print(f"❌ {stock} 异常: {str(e)[:50]}")
            
            if (i + 1) % 5 == 0:
                print(f"   进度: {i}/{min(20, len(watchlist))}")
        
        bs.logout()
        
        print()
        if all_data:
            # 合并数据
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 保存数据
            output_file = Path(__file__).parent / 'data' / 'realtime_quotes.csv'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"✅ 数据已保存到: {output_file}")
            
            # 保存JSON
            json_file = Path(__file__).parent / 'data' / 'realtime_quotes.json'
            records = combined_df.to_dict('records')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'data_source': 'baostock',
                    'total_stocks': len(all_data),
                    'total_records': len(records),
                    'sample_data': records[:50]
                }, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON已保存到: {json_file}")
            
            print()
            print("="*80)
            print("  📈 最新行情（前5只）")
            print("="*80)
            print()
            for i, (_, row) in enumerate(combined_df.groupby('name').last().head(5).iterrows(), 1):
                print(f"{i}. {row['name']}: 收盘价 {row['close']}")
            
            print()
            print(f"✅ 成功获取 {success_count} 只股票数据")
        else:
            print("❌ 未能获取任何数据")
            
    else:
        print(f"❌ 连接失败: {lg.error_msg}")

except ImportError:
    print("❌ baostock 未安装")
    print()
    print("请运行以下命令安装:")
    print("  pip install baostock")
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print(f"✅ 数据获取完成！时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
