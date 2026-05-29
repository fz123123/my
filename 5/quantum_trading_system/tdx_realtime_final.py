# -*- coding: utf-8 -*-
"""
通达信实时行情获取工具（综合版）
结合实时行情接口和本地数据
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import struct

# 自动安装 pytdx
try:
    from pytdx.hq import TdxHq_API
except ImportError:
    print("📦 正在安装 pytdx 库...")
    os.system("pip install pytdx -q")
    from pytdx.hq import TdxHq_API

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
    else:
        return 1  # 默认深圳

def fetch_realtime_via_tdx(stocks):
    """使用通达信实时行情接口"""
    print("\n📡 尝试连接通达信实时行情接口...")
    
    api = TdxHq_API(heartbeat=True)
    realtime_data = {}
    
    # 服务器列表
    servers = [
        ('61.152.107.141', 7709),  # 宁波电信
        ('59.36.14.50', 7709),     # 深圳电信
        ('101.227.73.26', 7709),   # 上海电信
        ('112.74.214.147', 7709),  # 阿里云
    ]
    
    for ip, port in servers:
        try:
            print(f"   尝试 {ip}:{port}...")
            api.connect(ip, port)  # 去掉timeouts参数
            
            # 获取上海股票
            sh_stocks = [(0, s.replace('.SH', '')) for s in stocks if '.SH' in s]
            for i in range(0, len(sh_stocks), 50):
                batch = sh_stocks[i:i+50]
                try:
                    data = api.get_security_quotes(batch)
                    for stock, quote in zip(batch, data):
                        if quote and quote.get('price', 0) > 0:
                            code = f"{quote.get('code', '')}.SH"
                            realtime_data[code] = {
                                'code': quote.get('code', ''),
                                'name': quote.get('name', ''),
                                'close': quote.get('price', 0),
                                'change_pct': quote.get('price_change', 0),
                                'change_amount': quote.get('change', 0),
                                'high': quote.get('high', 0),
                                'low': quote.get('low', 0),
                                'open': quote.get('open', 0),
                                'volume': quote.get('vol', 0),
                                'amount': quote.get('amount', 0),
                                'source': '通达信实时'
                            }
                except:
                    pass
            
            # 获取深圳股票
            sz_stocks = [(1, s.replace('.SZ', '')) for s in stocks if '.SZ' in s]
            for i in range(0, len(sz_stocks), 50):
                batch = sz_stocks[i:i+50]
                try:
                    data = api.get_security_quotes(batch)
                    for stock, quote in zip(batch, data):
                        if quote and quote.get('price', 0) > 0:
                            code = f"{quote.get('code', '')}.SZ"
                            realtime_data[code] = {
                                'code': quote.get('code', ''),
                                'name': quote.get('name', ''),
                                'close': quote.get('price', 0),
                                'change_pct': quote.get('price_change', 0),
                                'change_amount': quote.get('change', 0),
                                'high': quote.get('high', 0),
                                'low': quote.get('low', 0),
                                'open': quote.get('open', 0),
                                'volume': quote.get('vol', 0),
                                'amount': quote.get('amount', 0),
                                'source': '通达信实时'
                            }
                except:
                    pass
            
            api.disconnect()
            print(f"✅ 通达信连接成功！")
            return realtime_data
            
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            try:
                api.disconnect()
            except:
                pass
            continue
    
    return realtime_data

def read_local_day_file(market, code):
    """读取本地.day文件的最后一条数据"""
    data_path = Path(r"C:\new_tdx\vipdoc")
    file_path = data_path / market / 'lday' / f"{market}{code}.day"
    
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'rb') as f:
            f.seek(-32, 2)  # 读取最后一条
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
    except:
        return None

def fetch_from_local_files(stocks):
    """从本地文件获取数据"""
    print("\n📂 尝试从本地文件获取数据...")
    
    local_data = {}
    
    for stock in stocks:
        code = stock.replace('.SH', '').replace('.SZ', '')
        market = 'sh' if '.SH' in stock else 'sz'
        
        day_data = read_local_day_file(market, code)
        
        if day_data:
            local_data[stock] = {
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
    
    print(f"✅ 从本地文件获取了 {len(local_data)} 条数据")
    return local_data

def main():
    print("="*80)
    print("  📡 通达信实时行情获取工具（综合版）")
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
    
    # 方法1: 尝试通达信实时行情
    print("="*80)
    print("  方法1: 通达信实时行情")
    print("="*80)
    realtime_data = fetch_realtime_via_tdx(stocks)
    
    if realtime_data:
        all_data.update(realtime_data)
        print(f"✅ 实时行情获取成功: {len(realtime_data)} 只")
    else:
        print("❌ 实时行情获取失败")
    
    print()
    
    # 方法2: 从本地文件补充
    print("="*80)
    print("  方法2: 本地文件补充")
    print("="*80)
    
    missing_stocks = [s for s in stocks if s not in all_data]
    
    if missing_stocks:
        print(f"还有 {len(missing_stocks)} 只股票需要补充...")
        local_data = fetch_from_local_files(missing_stocks)
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
    
    # 按数据源分类统计
    sources = {}
    for data in all_data.values():
        source = data.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
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
        
        print(f"{'代码':<12} {'名称':<10} {'最新价':>10} {'涨跌幅':>10} {'来源':<12}")
        print("-" * 60)
        
        for stock, data in list(all_data.items())[:20]:
            code = stock
            name = data.get('name', '')[:8]
            close = data.get('close', 0)
            change_pct = data.get('change_pct', 0)
            source = data.get('source', '')[:10]
            
            close_str = f"{close:.2f}" if close else "N/A"
            change_str = f"{change_pct:+.2f}%" if change_pct else "N/A"
            
            print(f"{code:<12} {name:<10} {close_str:>10} {change_str:>10} {source:<12}")
        
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
        print("   2. 本地文件不存在")
        print("   3. 网络连接问题")
        print()
        
        print("📝 建议:")
        print("   1. 检查网络连接")
        print("   2. 确保通达信软件已启动")
        print("   3. 稍后重试")
    
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
    
    # 保存失败列表
    if failed > 0:
        failed_file = Path(__file__).parent / 'data' / 'tdx_failed_stocks.txt'
        with open(failed_file, 'w', encoding='utf-8') as f:
            for stock in failed_stocks:
                f.write(f"{stock}\n")
        print(f"⚠️ 失败股票列表: {failed_file}")
    
    print()
    print("="*80)
    print(f"✅ 数据获取完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()
