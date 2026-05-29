# -*- coding: utf-8 -*-
"""
通达信数据导出工具
使用 pytdx 库连接通达信获取实时行情数据
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# 自动安装 pytdx
try:
    from pytdx.hq import TdxHq_API
    from pytdx.exhq import TdxExHq_API
except ImportError:
    print("📦 正在安装 pytdx 库...")
    os.system("pip install pytdx -q")
    from pytdx.hq import TdxHq_API
    from pytdx.exhq import TdxExHq_API

# 读取自选股
def load_watchlist():
    """读取自选股列表"""
    monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
    
    if not monitor_file.exists():
        print(f"❌ 自选股文件不存在: {monitor_file}")
        return []
    
    with open(monitor_file, 'r', encoding='utf-8') as f:
        stocks = [line.strip() for line in f if line.strip()]
    
    return stocks

def get_tdx_market(code):
    """判断通达信市场代码"""
    code = code.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
    
    if code.startswith(('60', '688')):
        return 0  # 上海
    elif code.startswith(('000', '001', '002', '300')):
        return 1  # 深圳
    elif code.startswith(('8', '4')):  # 北交所
        return 0  # 北交所用上海
    else:
        return 1  # 默认深圳

def fetch_realtime_data_tdx(stocks):
    """使用通达信接口获取实时行情"""
    print("="*80)
    print("  📡 正在连接通达信...")
    print("="*80)
    print()
    
    api = TdxHq_API(heartbeat=True, auto_retry=True)
    realtime_data = {}
    success_count = 0
    failed_stocks = []
    
    try:
        # 连接通达信（常用服务器）
        print("🔄 尝试连接通达信服务器...")
        
        # 尝试多个服务器
        servers = [
            ('宁波电信', '61.152.107.141', 7709),
            ('深圳电信', '59.36.14.50', 7709),
            ('上海电信', '101.227.73.26', 7709),
        ]
        
        connected = False
        for name, ip, port in servers:
            try:
                print(f"   尝试 {name} ({ip}:{port})...")
                api.connect(ip, port)
                connected = True
                print(f"✅ 成功连接 {name}")
                break
            except Exception as e:
                print(f"   ❌ {name} 连接失败: {e}")
                continue
        
        if not connected:
            print("\n❌ 无法连接到通达信服务器")
            return {}, stocks
        
        print()
        
        # 分类处理
        sh_stocks = [(s, s.replace('.SH', '')) for s in stocks if '.SH' in s]
        sz_stocks = [(s, s.replace('.SZ', '')) for s in stocks if '.SZ' in s]
        
        # 获取上海股票（批量50只）
        print(f"📥 获取上海股票行情 ({len(sh_stocks)}只)...")
        for i in range(0, len(sh_stocks), 50):
            batch = sh_stocks[i:i+50]
            codes = [(0, code) for _, code in batch]  # 0=上海
            
            try:
                data = api.get_security_quotes(codes)
                
                for stock, quote in zip(batch, data):
                    if quote and quote.get('price', 0) > 0:
                        realtime_data[stock] = {
                            'code': quote.get('code', ''),
                            'name': quote.get('name', ''),
                            'open': quote.get('open', 0),
                            'high': quote.get('high', 0),
                            'low': quote.get('low', 0),
                            'close': quote.get('price', 0),
                            'volume': quote.get('vol', 0),
                            'amount': quote.get('amount', 0),
                            'change_pct': quote.get('price_change', 0),
                            'change_amount': quote.get('change', 0),
                            'bid1': quote.get('bid1', 0),
                            'ask1': quote.get('ask1', 0),
                            'source': '通达信'
                        }
                        success_count += 1
                    else:
                        failed_stocks.append(stock)
                        
            except Exception as e:
                print(f"   ⚠️ 批次 {i//50 + 1} 获取失败: {e}")
                failed_stocks.extend([s for s, _ in batch])
        
        # 获取深圳股票
        print(f"📥 获取深圳股票行情 ({len(sz_stocks)}只)...")
        for i in range(0, len(sz_stocks), 50):
            batch = sz_stocks[i:i+50]
            codes = [(1, code) for _, code in batch]  # 1=深圳
            
            try:
                data = api.get_security_quotes(codes)
                
                for stock, quote in zip(batch, data):
                    if quote and quote.get('price', 0) > 0:
                        realtime_data[stock] = {
                            'code': quote.get('code', ''),
                            'name': quote.get('name', ''),
                            'open': quote.get('open', 0),
                            'high': quote.get('high', 0),
                            'low': quote.get('low', 0),
                            'close': quote.get('price', 0),
                            'volume': quote.get('vol', 0),
                            'amount': quote.get('amount', 0),
                            'change_pct': quote.get('price_change', 0),
                            'change_amount': quote.get('change', 0),
                            'bid1': quote.get('bid1', 0),
                            'ask1': quote.get('ask1', 0),
                            'source': '通达信'
                        }
                        success_count += 1
                    else:
                        failed_stocks.append(stock)
                        
            except Exception as e:
                print(f"   ⚠️ 批次 {i//50 + 1} 获取失败: {e}")
                failed_stocks.extend([s for s, _ in batch])
        
        api.disconnect()
        
    except Exception as e:
        print(f"\n❌ 通达信接口出错: {e}")
        import traceback
        traceback.print_exc()
    
    return realtime_data, failed_stocks

def save_results(realtime_data, failed_stocks):
    """保存结果"""
    print()
    print("="*80)
    print("  💾 保存结果")
    print("="*80)
    print()
    
    # 保存到JSON
    output_file = Path(__file__).parent / 'data' / 'tdx_realtime_quotes.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(realtime_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 实时行情已保存: {output_file}")
    
    # 保存失败列表
    if failed_stocks:
        failed_file = Path(__file__).parent / 'data' / 'tdx_failed_stocks.txt'
        with open(failed_file, 'w', encoding='utf-8') as f:
            for stock in failed_stocks:
                f.write(f"{stock}\n")
        print(f"⚠️ 失败股票列表: {failed_file}")

def main():
    print("="*80)
    print("  📡 通达信数据导出工具")
    print("="*80)
    print()
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 读取自选股
    print("📂 读取自选股列表...")
    stocks = load_watchlist()
    
    if not stocks:
        print("❌ 没有找到自选股")
        return
    
    print(f"✅ 加载完成: {len(stocks)} 只")
    print()
    
    # 统计分类
    sh_count = sum(1 for s in stocks if '.SH' in s)
    sz_count = sum(1 for s in stocks if '.SZ' in s)
    
    print(f"📊 自选股构成:")
    print(f"   - 上海: {sh_count} 只")
    print(f"   - 深圳: {sz_count} 只")
    print()
    
    # 获取实时数据
    realtime_data, failed_stocks = fetch_realtime_data_tdx(stocks)
    
    # 显示结果
    print()
    print("="*80)
    print("  📊 数据获取结果")
    print("="*80)
    print()
    
    total = len(stocks)
    success = len(realtime_data)
    failed = len(failed_stocks)
    success_rate = (success / total * 100) if total > 0 else 0
    
    print(f"📊 自选股总数: {total} 只")
    print(f"✅ 成功获取: {success} 只")
    print(f"❌ 未能获取: {failed} 只")
    print(f"📈 成功率: {success_rate:.1f}%")
    print()
    
    # 显示成功的数据
    if realtime_data:
        print("="*80)
        print("  📋 成功获取的行情数据")
        print("="*80)
        print()
        
        print(f"{'代码':<12} {'名称':<10} {'最新价':>10} {'涨跌幅':>10} {'来源':<8}")
        print("-" * 60)
        
        for stock, data in list(realtime_data.items())[:20]:
            code = stock
            name = data.get('name', '')[:8]
            close = data.get('close', 0)
            change_pct = data.get('change_pct', 0)
            source = data.get('source', '')[:6]
            
            close_str = f"{close:.2f}" if close else "N/A"
            change_str = f"{change_pct:+.2f}%" if change_pct else "N/A"
            
            print(f"{code:<12} {name:<10} {close_str:>10} {change_str:>10} {source:<8}")
        
        if len(realtime_data) > 20:
            print(f"... 还有 {len(realtime_data) - 20} 只")
    
    # 显示失败的数据
    if failed_stocks:
        print()
        print("="*80)
        print(f"  ⚠️ 未能获取行情的 {len(failed_stocks)} 只股票")
        print("="*80)
        print()
        
        print("💡 可能原因:")
        print("   1. 通达信软件未运行")
        print("   2. 网络连接问题")
        print("   3. 服务器拒绝连接")
        print("   4. 股票代码格式不支持")
        print()
        
        print("📝 建议:")
        print("   1. 确认通达信软件已启动")
        print("   2. 检查网络连接")
        print("   3. 稍后重试")
    
    # 保存结果
    save_results(realtime_data, failed_stocks)
    
    print()
    print("="*80)
    print(f"✅ 通达信数据导出完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()
