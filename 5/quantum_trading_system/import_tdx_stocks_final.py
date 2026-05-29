# -*- coding: utf-8 -*-
"""
最终版：通达信自选股导入工具
正确解析7位格式：6位代码 + 1位市场代码
"""

import os
import re

TDX_PATH = r"C:\new_tdx\T0002\blocknew"

def read_tdx_self_stocks():
    """读取通达信自选股"""
    zxg_path = os.path.join(TDX_PATH, "zxg.blk")
    if not os.path.exists(zxg_path):
        print(f"❌ 自选股文件不存在: {zxg_path}")
        return []
    
    stocks = []
    seen = set()
    
    try:
        with open(zxg_path, 'rb') as f:
            data = f.read()
        
        text = data.decode('gbk', errors='ignore')
        
        # 按行解析，每行格式：6位代码 + 1位市场代码
        lines = text.split('\n') + text.split('\r')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配7位数字
            match = re.match(r'^(\d{6})(\d)$', line)
            if not match:
                continue
            
            code = match.group(1)
            market_code = match.group(2)
            
            # 避免重复
            if code in seen:
                continue
            seen.add(code)
            
            # 判断市场
            # 0=深圳, 1=上海, 2=深圳, 3=深圳, 4=?, 5=上海, 6=?, 7=深圳, 8=深圳, 9=?
            if market_code in ('1', '5'):
                market = 'SH'  # 上海
            else:
                market = 'SZ'  # 深圳
            
            full_code = f"{code}.{market}"
            if full_code not in stocks:
                stocks.append(full_code)
        
        print(f"✅ 从通达信读取到 {len(stocks)} 只自选股")
        
        # 显示前20个
        if stocks:
            print(f"\n前20只自选股:")
            for i, stock in enumerate(stocks[:20], 1):
                print(f"  {i:2d}. {stock}")
            
            if len(stocks) > 20:
                print(f"  ... 还有 {len(stocks) - 20} 只")
        
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        import traceback
        traceback.print_exc()
    
    return stocks

def main():
    print("="*60)
    print("    通达信自选股导入工具 (最终版)")
    print("="*60)
    
    print("\n📂 读取自选股...")
    stocks = read_tdx_self_stocks()
    
    if stocks:
        # 分类统计
        sh_count = sum(1 for s in stocks if '.SH' in s)
        sz_count = sum(1 for s in stocks if '.SZ' in s)
        
        print(f"\n📊 自选股构成:")
        print(f"   - 上海(SH): {sh_count} 只")
        print(f"   - 深圳(SZ): {sz_count} 只")
        print(f"   - 合计: {len(stocks)} 只")
        
        print("\n正在导入到监控系统...")
        save_to_monitor(stocks)
        print(f"\n✅ 已成功导入 {len(stocks)} 只股票到监控列表！")
        
        print(f"\n📁 文件保存位置: monitor/stocks.txt")
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
