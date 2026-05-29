# -*- coding: utf-8 -*-
"""
验证通达信数据连接
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_fetcher import DataFetcher

def main():
    print("="*60)
    print("    通达信数据连接验证工具")
    print("="*60)
    
    fetcher = DataFetcher()
    
    print(f"\n📡 通达信路径: {fetcher.tdx_path}")
    print(f"📡 同花顺路径: {fetcher.ths_path}")
    
    test_stocks = [
        '600519.SH',  # 贵州茅台
        '000858.SZ',  # 五粮液
        '601318.SH',  # 中国平安
    ]
    
    print("\n📊 测试数据获取...")
    success_count = 0
    
    for symbol in test_stocks:
        print(f"\n测试: {symbol}")
        df = fetcher.get_stock_data(symbol)
        if df is not None and len(df) > 0:
            print(f"  ✅ 成功获取 {len(df)} 条数据")
            print(f"  最新日期: {df.index[-1].date()}")
            print(f"  最新价格: {df['close'].iloc[-1]:.2f}")
            success_count += 1
        else:
            print(f"  ❌ 获取失败")
    
    print(f"\n成功: {success_count}/{len(test_stocks)}")
    
    if success_count == len(test_stocks):
        print("\n✅ 通达信数据连接正常！")
        print("系统将使用通达信数据进行深度分析和实时监控。")
    else:
        print("\n⚠️ 部分数据获取失败，请检查通达信安装和数据文件。")

if __name__ == "__main__":
    main()