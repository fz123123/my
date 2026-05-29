# -*- coding: utf-8 -*-
"""
通达信数据导出工具 - 完善版
支持多种本地数据路径
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import struct

def load_watchlist():
    """读取自选股列表"""
    monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
    
    if not monitor_file.exists():
        print(f"❌ 自选股文件不存在: {monitor_file}")
        return []
    
    with open(monitor_file, 'r', encoding='utf-8') as f:
        stocks = [line.strip() for line in f if line.strip()]
    
    return stocks

def read_day_file(file_path):
    """读取.day文件的最后一条数据"""
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'rb') as f:
            # 获取文件大小
            f.seek(0, 2)
            file_size = f.tell()
            
            if file_size < 32:
                return None
            
            # 读取最后一条记录
            f.seek(-32, 2)
            data = f.read(32)
            
            if len(data) < 32:
                return None
            
            date, open_price, high, low, close, amount, volume, _ = struct.unpack('<IIIIIfII', data)
            
            if date == 0:
                return None
            
            year = date // 10000
            month = (date % 10000) // 100
            day = date % 100
            
            return {
                'date': f"{year:04d}-{month:02d}-{day:02d}",
                'open': open_price / 100.0,
                'high': high / 100.0,
                'low': low / 100.0,
                'close': close / 100.0,
                'volume': volume,
                'amount': amount / 1000.0
            }
    except Exception as e:
        return None

def find_day_file_paths(market, code):
    """查找.day文件的可能路径"""
    base_paths = [
        r"C:\new_tdx\vipdoc",
        r"C:\通达信\vipdoc",
        r"C:\tdx\vipdoc",
        r"C:\Program Files\tdx\vipdoc",
        r"C:\new_tdx2\vipdoc",
    ]
    
    possible_paths = []
    
    for base in base_paths:
        # 标准路径
        path1 = Path(base) / market / 'lday' / f"{market}{code}.day"
        possible_paths.append(path1)
        
        # 其他可能路径
        path2 = Path(base) / market / f"{market}{code}.day"
        possible_paths.append(path2)
        
        # 直接在base下的路径
        path3 = Path(base) / f"{market}{code}.day"
        possible_paths.append(path3)
    
    return possible_paths

def get_stock_data_from_local_files(stocks):
    """从本地文件获取股票数据"""
    print("\n📂 从本地文件获取数据...")
    
    all_data = {}
    success_count = 0
    failed_stocks = []
    
    for stock in stocks:
        code = stock.replace('.SH', '').replace('.SZ', '')
        market = 'sh' if '.SH' in stock else 'sz'
        
        # 尝试所有可能的路径
        possible_paths = find_day_file_paths(market, code)
        
        day_data = None
        for path in possible_paths:
            if path.exists():
                day_data = read_day_file(str(path))
                if day_data:
                    break
        
        if day_data:
            all_data[stock] = {
                'code': code,
                'name': code,  # 本地文件没有名称
                'close': day_data['close'],
                'open': day_data['open'],
                'high': day_data['high'],
                'low': day_data['low'],
                'volume': day_data['volume'],
                'amount': day_data['amount'],
                'date': day_data['date'],
                'change_pct': 0,
                'change_amount': 0,
                'source': '本地文件'
            }
            success_count += 1
        else:
            failed_stocks.append(stock)
    
    print(f"✅ 成功获取: {success_count} 只")
    print(f"❌ 获取失败: {len(failed_stocks)} 只")
    
    return all_data, failed_stocks

def get_tdx_realtime(stocks):
    """获取通达信实时行情"""
    try:
        from pytdx.hq import TdxHq_API
    except ImportError:
        print("❌ pytdx未安装")
        return {}, stocks
    
    print("\n📡 尝试获取通达信实时行情...")
    
    api = TdxHq_API(heartbeat=True)
    realtime_data = {}
    
    # 服务器列表
    servers = [
        ('61.152.107.141', 7709),
        ('59.36.14.50', 7709),
        ('101.227.73.26', 7709),
    ]
    
    connected = False
    for ip, port in servers:
        try:
            print(f"   尝试连接 {ip}:{port}...")
            api.connect(ip, port)
            connected = True
            print(f"✅ 连接成功!")
            break
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            continue
    
    if not connected:
        print("❌ 无法连接到通达信服务器")
        return {}, stocks
    
    try:
        # 获取上海股票
        sh_stocks = [(0, s.replace('.SH', '')) for s in stocks if '.SH' in s]
        print(f"📥 获取上海股票 ({len(sh_stocks)}只)...")
        
        for i in range(0, len(sh_stocks), 50):
            batch = sh_stocks[i:i+50]
            try:
                data = api.get_security_quotes(batch)
                
                for stock, quote in zip(batch, data):
                    if quote and isinstance(quote, dict) and quote.get('price', 0) > 0:
                        code_str = quote.get('code', '')
                        full_code = f"{code_str}.SH"
                        realtime_data[full_code] = {
                            'code': code_str,
                            'name': quote.get('name', ''),
                            'close': quote.get('price', 0),
                            'open': quote.get('open', 0),
                            'high': quote.get('high', 0),
                            'low': quote.get('low', 0),
                            'volume': quote.get('vol', 0),
                            'amount': quote.get('amount', 0),
                            'change_pct': quote.get('price_change', 0),
                            'change_amount': quote.get('change', 0),
                            'source': '通达信实时'
                        }
            except Exception as e:
                print(f"   ⚠️ 批次 {i//50 + 1} 失败: {e}")
        
        # 获取深圳股票
        sz_stocks = [(1, s.replace('.SZ', '')) for s in stocks if '.SZ' in s]
        print(f"📥 获取深圳股票 ({len(sz_stocks)}只)...")
        
        for i in range(0, len(sz_stocks), 50):
            batch = sz_stocks[i:i+50]
            try:
                data = api.get_security_quotes(batch)
                
                for stock, quote in zip(batch, data):
                    if quote and isinstance(quote, dict) and quote.get('price', 0) > 0:
                        code_str = quote.get('code', '')
                        full_code = f"{code_str}.SZ"
                        realtime_data[full_code] = {
                            'code': code_str,
                            'name': quote.get('name', ''),
                            'close': quote.get('price', 0),
                            'open': quote.get('open', 0),
                            'high': quote.get('high', 0),
                            'low': quote.get('low', 0),
                            'volume': quote.get('vol', 0),
                            'amount': quote.get('amount', 0),
                            'change_pct': quote.get('price_change', 0),
                            'change_amount': quote.get('change', 0),
                            'source': '通达信实时'
                        }
            except Exception as e:
                print(f"   ⚠️ 批次 {i//50 + 1} 失败: {e}")
        
        api.disconnect()
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        try:
            api.disconnect()
        except:
            pass
    
    return realtime_data, [s for s in stocks if s not in realtime_data]

def main():
    print("="*80)
    print("  📡 通达信数据导出工具（完善版）")
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
    
    # 统计分类
    sh_count = sum(1 for s in stocks if '.SH' in s)
    sz_count = sum(1 for s in stocks if '.SZ' in s)
    
    print(f"\n📊 自选股构成:")
    print(f"   - 上海: {sh_count} 只")
    print(f"   - 深圳: {sz_count} 只")
    print()
    
    all_data = {}
    
    # 方法1: 通达信实时行情
    print("="*80)
    print("  方法1: 通达信实时行情")
    print("="*80)
    
    realtime_data, missing_stocks = get_tdx_realtime(stocks)
    all_data.update(realtime_data)
    
    print(f"✅ 实时行情获取: {len(realtime_data)} 只")
    print()
    
    # 方法2: 本地文件补充
    if missing_stocks:
        print("="*80)
        print("  方法2: 本地文件补充")
        print("="*80)
        
        local_data, failed_stocks = get_stock_data_from_local_files(missing_stocks)
        all_data.update(local_data)
    
    # 显示结果
    print()
    print("="*80)
    print("  📊 最终结果")
    print("="*80)
    print()
    
    total = len(stocks)
    success = len(all_data)
    failed = total - success
    success_rate = (success / total * 100) if total > 0 else 0
    
    print(f"📊 自选股总数: {total} 只")
    print(f"✅ 成功获取: {success} 只")
    print(f"❌ 未能获取: {failed} 只")
    print(f"📈 成功率: {success_rate:.1f}%")
    print()
    
    # 按数据源统计
    sources = {}
    for data in all_data.values():
        source = data.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    if sources:
        print(f"📡 数据来源:")
        for source, count in sources.items():
            print(f"   - {source}: {count} 只")
        print()
    
    # 显示成功的数据
    if all_data:
        print("="*80)
        print("  📋 成功获取的行情数据（前20只）")
        print("="*80)
        print()
        
        print(f"{'代码':<12} {'名称':<10} {'最新价':>10} {'日期':<12} {'来源':<10}")
        print("-" * 60)
        
        for stock, data in list(all_data.items())[:20]:
            code = stock
            name = data.get('name', '')[:8]
            close = data.get('close', 0)
            date = data.get('date', '')[:10]
            source = data.get('source', '')[:8]
            
            close_str = f"{close:.2f}" if close else "N/A"
            
            print(f"{code:<12} {name:<10} {close_str:>10} {date:<12} {source:<10}")
        
        if len(all_data) > 20:
            print(f"... 还有 {len(all_data) - 20} 只")
    
    # 显示失败的股票
    if failed > 0:
        failed_stocks = [s for s in stocks if s not in all_data]
        
        print()
        print("="*80)
        print(f"  ⚠️  未能获取行情的 {len(failed_stocks)} 只股票")
        print("="*80)
        print()
        
        print("💡 可能原因:")
        print("   1. 通达信服务器连接失败")
        print("   2. 本地.day文件不存在")
        print("   3. 网络连接问题")
        print()
        
        print("📝 建议:")
        print("   1. 检查通达信安装路径")
        print("   2. 确认网络连接正常")
        print("   3. 交易时间可能获取更多数据")
    
    # 保存结果
    print()
    print("="*80)
    print("  💾 保存结果")
    print("="*80)
    print()
    
    output_file = Path(__file__).parent / 'data' / 'tdx_realtime_quotes.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 实时行情已保存: {output_file}")
    
    print()
    print("="*80)
    print(f"✅ 数据获取完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()
