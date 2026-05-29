# -*- coding: utf-8 -*-
"""
同花顺远航版自选股导入工具
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_fetcher import DataFetcher

THS_YUANHANG_PATH = r"C:\同花顺远航版\transaction"

def read_ths_basket():
    """读取同花顺远航版自选股"""
    basket_path = os.path.join(THS_YUANHANG_PATH, "data", "basket.dat")
    if not os.path.exists(basket_path):
        print(f"自选股文件不存在: {basket_path}")
        return []
    
    stocks = []
    try:
        with open(basket_path, 'rb') as f:
            content = f.read()
        
        length = len(content)
        i = 0
        while i < length - 6:
            code_bytes = content[i:i+6]
            try:
                code = code_bytes.decode('gbk').strip()
                if code and code.isdigit() and len(code) == 6:
                    market_byte = content[i + 6:i + 8]
                    if len(market_byte) >= 1:
                        market_val = market_byte[0]
                        if market_val == 0 or market_val == 1:
                            market = 'SH' if market_val == 0 else 'SZ'
                            full_code = f"{code}.{market}"
                            if full_code not in stocks:
                                stocks.append(full_code)
            except:
                pass
            i += 16
        
        print(f"从同花顺远航版读取到 {len(stocks)} 只自选股")
        
    except Exception as e:
        print(f"读取失败: {e}")
    
    return stocks

def import_stocks_to_monitor(stocks):
    """导入股票到监控列表"""
    if not stocks:
        return
    
    fetcher = DataFetcher()
    valid_stocks = []
    
    print("\n验证股票数据...")
    for symbol in stocks:
        df = fetcher.get_stock_data(symbol)
        if df is not None and len(df) >= 60:
            valid_stocks.append(symbol)
            print(f"  ✅ {symbol} - {len(df)}条数据")
        else:
            print(f"  ❌ {symbol} - 数据不足")
    
    if valid_stocks:
        save_watchlist(valid_stocks)
        print(f"\n✅ 成功导入 {len(valid_stocks)} 只股票到监控列表")
    else:
        print("\n❌ 没有有效的股票数据")

def save_watchlist(stocks):
    """保存监控列表"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        watchlist_started = False
        
        for line in lines:
            if 'WATCHLIST' in line or 'watch_list' in line:
                watchlist_started = True
                new_lines.append(line)
                if '=' in line:
                    code_part = line.split('=', 1)[1].strip()
                    if code_part.startswith('['):
                        watchlist_started = False
            elif watchlist_started and line.strip().startswith(']'):
                new_lines.append(line)
                watchlist_started = False
            elif watchlist_started and not line.strip().startswith('"') and not line.strip().startswith("'"):
                pass
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"监控列表已保存")
        
    except Exception as e:
        print(f"保存失败: {e}")

def main():
    print("="*60)
    print("    同花顺远航版自选股导入工具")
    print("="*60)
    
    stocks = read_ths_basket()
    
    if stocks:
        print("\n自选股列表:")
        for i, stock in enumerate(stocks[:20], 1):
            print(f"  {i}. {stock}")
        if len(stocks) > 20:
            print(f"  ... 还有 {len(stocks) - 20} 只")
        
        print("\n是否导入到监控列表? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            import_stocks_to_monitor(stocks)
    else:
        print("\n未找到自选股数据")
        print("请确认同花顺远航版中已添加自选股")

if __name__ == "__main__":
    main()