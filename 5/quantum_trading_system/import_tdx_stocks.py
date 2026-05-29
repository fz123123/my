# -*- coding: utf-8 -*-
"""
修正版：通达信自选股导入工具
"""

import os

TDX_PATH = r"C:\new_tdx\T0002\blocknew"

def read_tdx_self_stocks():
    """读取通达信自选股（修正版）"""
    zxg_path = os.path.join(TDX_PATH, "zxg.blk")
    if not os.path.exists(zxg_path):
        print(f"自选股文件不存在: {zxg_path}")
        return []
    
    stocks = []
    try:
        with open(zxg_path, 'rb') as f:
            data = f.read()
        
        lines = data.decode('gbk', errors='ignore').split('\r\n')
        
        for line in lines:
            line = line.strip()
            if len(line) >= 7 and line[:7].isdigit():
                code_part = line[:6]
                market_code = line[6]
                
                if market_code == '5':
                    market = 'SH'
                    if code_part.startswith('1'):
                        code = '6' + code_part[1:]
                    else:
                        code = code_part
                else:
                    market = 'SZ'
                    code = code_part
                
                if code.isdigit() and len(code) == 6:
                    full_code = f"{code}.{market}"
                    if full_code not in stocks:
                        stocks.append(full_code)
        
        print(f"从通达信读取到 {len(stocks)} 只自选股")
        
    except Exception as e:
        print(f"读取失败: {e}")
    
    return stocks

def main():
    print("="*60)
    print("    通达信自选股导入工具 (修正版)")
    print("="*60)
    
    print("\n📂 读取自选股...")
    stocks = read_tdx_self_stocks()
    
    if stocks:
        print(f"\n前10只自选股:")
        for i, stock in enumerate(stocks[:10], 1):
            print(f"  {i:2d}. {stock}")
        
        if len(stocks) > 10:
            print(f"  ... 还有 {len(stocks) - 10} 只")
        
        print(f"\n✅ 共找到 {len(stocks)} 只自选股")
        
        print("\n正在导入到监控系统...")
        save_to_monitor(stocks)
        print(f"\n✅ 已成功导入 {len(stocks)} 只股票到监控列表！")
        
        print(f"\n文件保存位置: monitor/stocks.txt")
    else:
        print("\n❌ 未找到自选股数据")

def save_to_monitor(stocks):
    """保存到监控列表"""
    monitor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monitor')
    os.makedirs(monitor_dir, exist_ok=True)
    
    stocks_file = os.path.join(monitor_dir, 'stocks.txt')
    
    with open(stocks_file, 'w', encoding='utf-8') as f:
        for stock in stocks:
            f.write(f"{stock}\n")
    
    print(f"已保存到: {stocks_file}")

if __name__ == "__main__":
    main()