# -*- coding: utf-8 -*-
"""
同花顺远航版数据读取工具
"""

import os
import pandas as pd
import struct

THS_BASE = r"C:\同花顺远航版\transaction"

def read_basket_file():
    """读取自选股文件"""
    basket_path = os.path.join(THS_BASE, "data", "basket.dat")
    if not os.path.exists(basket_path):
        return []
    
    stocks = []
    try:
        with open(basket_path, 'rb') as f:
            data = f.read()
        
        offset = 0
        while offset < len(data):
            code = data[offset:offset+6].decode('gbk', errors='ignore').strip()
            if code and code.isdigit():
                stocks.append(code)
            offset += 16
    except Exception as e:
        print(f"读取自选股失败: {e}")
    
    return stocks

def get_ths_day_files():
    """获取同花顺远航版的所有日线数据文件"""
    day_files = []
    
    ths_data_paths = [
        os.path.join(THS_BASE, "data"),  # 同花顺远航版主数据目录
    ]
    
    for data_path in ths_data_paths:
        if os.path.exists(data_path):
            for root, dirs, files in os.walk(data_path):
                for file in files:
                    if file.endswith('.day'):
                        day_files.append(os.path.join(root, file))
    
    return day_files

def parse_ths_day_file(file_path):
    """解析同花顺远航版日线文件"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        records = []
        offset = 0
        record_size = 32
        
        while offset + record_size <= len(content):
            record = content[offset:offset+record_size]
            
            date = struct.unpack('I', record[0:4])[0]
            open_p = struct.unpack('i', record[4:8])[0] / 100.0
            high_p = struct.unpack('i', record[8:12])[0] / 100.0
            low_p = struct.unpack('i', record[12:16])[0] / 100.0
            close_p = struct.unpack('i', record[16:20])[0] / 100.0
            volume = struct.unpack('I', record[20:24])[0]
            
            if open_p > 0 and close_p > 0:
                records.append({
                    'date': str(date),
                    'open': open_p,
                    'high': high_p,
                    'low': low_p,
                    'close': close_p,
                    'volume': volume
                })
            
            offset += record_size
        
        if records:
            df = pd.DataFrame(records)
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df = df.set_index('date').sort_index()
            return df
        
    except Exception as e:
        print(f"解析文件失败 {file_path}: {e}")
    
    return None

def main():
    print("="*60)
    print("    同花顺远航版数据读取工具")
    print("="*60)
    
    print("\n📊 读取自选股...")
    stocks = read_basket_file()
    print(f"找到 {len(stocks)} 只自选股")
    
    if stocks:
        print(f"前10只: {', '.join(stocks[:10])}")
    
    print("\n📁 扫描日线数据...")
    day_files = get_ths_day_files()
    print(f"找到 {len(day_files)} 个数据文件")
    
    if day_files:
        sample = parse_ths_day_file(day_files[0])
        if sample is not None:
            print(f"\n示例数据 ({os.path.basename(day_files[0])}):")
            print(f"  数据条数: {len(sample)}")
            print(f"  最新日期: {sample.index[-1].date()}")
            print(f"  最新价格: {sample['close'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()