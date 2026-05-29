#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
盘中实时盯盘脚本 - 监控恐慌盘出现
支持东方财富实时接口和本地通达信数据
"""

import sys
import os
import time
import json
import pandas as pd
from datetime import datetime
import urllib.request
import urllib.error

# 设置控制台编码
if sys.platform.startswith('win'):
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

# ============ 配置区域 ============

# 光模块 + 算力 + 半导体 板块龙头
STOCKS = {
    # 光模块
    '300308.SZ': '中际旭创',
    '300502.SZ': '新易盛',
    '002281.SZ': '光迅科技',
    '300548.SZ': '博创科技',
    '603083.SH': '剑桥科技',
    '000988.SZ': '华工科技',
    '002902.SZ': '铭普光磁',
    '300570.SZ': '太辰光',
    '300394.SZ': '天孚通信',
    '688313.SH': '仕佳光子',
    '002897.SZ': '意华股份',
    # 光纤光缆
    '600487.SH': '亨通光电',
    '600522.SH': '中天科技',
    '600105.SH': '永鼎股份',
    '300265.SZ': '通光线缆',
    '000070.SZ': '特发信息',
    '600776.SH': '长江通信',
    # 算力
    '300750.SZ': '宁德时代',
    '002230.SZ': '科大讯飞',
    '300474.SZ': '景嘉微',
    '688256.SH': '寒武纪',
    '603019.SH': '中科曙光',
    '000977.SZ': '浪潮信息',
    '002415.SZ': '海康威视',
    # 半导体
    '688012.SH': '中微公司',
    '002371.SZ': '北方华创',
    '688396.SH': '华润微',
    '603501.SH': '韦尔股份',
    '688981.SH': '中芯国际',
    '600584.SH': '长电科技',
    '002185.SZ': '华天科技',
    '600460.SH': '士兰微',
    '688008.SH': '澜起科技',
    '688126.SH': '沪硅产业',
    '002129.SZ': '中环股份',
    # 半导体设计
    '688479.SH': '歌尔股份',
    '300223.SZ': '北京君正',
    '688521.SH': '芯原股份',
    '603160.SZ': '汇顶科技',
    '300456.SZ': '赛微电子',
    '688220.SH': '翱捷科技',
    '688099.SH': '晶晨股份',
    '688048.SH': '长光华芯',
}

# 恐慌盘阈值设置
DROP_THRESHOLD = 3.0  # 跌幅超过3%触发关注
PANIC_THRESHOLD = 5.0  # 跌幅超过5%为恐慌盘
VOLUME_THRESHOLD = 1.5  # 量比超过1.5倍

# 刷新间隔（秒）
REFRESH_INTERVAL = 30  # 每30秒刷新一次

# 本地数据文件路径
LOCAL_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'tdx', 'today_data.csv')


def is_market_open():
    """检查当前是否在交易时间"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    # 周六日休市
    if now.weekday() >= 5:
        return False

    # 9:30-11:30 上午交易时段
    if (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute <= 30):
        return True

    # 13:00-15:00 下午交易时段
    if (hour == 13) or (hour == 14) or (hour == 15 and minute == 0):
        return True

    return False


def get_realtime_data(stock_codes):
    """从东方财富获取实时行情"""
    if not stock_codes:
        return []

    eastmoney_codes = []
    for code in stock_codes:
        if code.endswith('.SZ'):
            eastmoney_codes.append(f"0.{code[:6]}")
        elif code.endswith('.SH'):
            eastmoney_codes.append(f"1.{code[:6]}")

    codes_str = ','.join(eastmoney_codes)
    url = f"http://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18&secids={codes_str}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('data') and data['data'].get('diff'):
            return data['data']['diff']
    except Exception as e:
        print(f"获取网络数据失败: {e}")

    return []


def get_local_data(stock_codes):
    """从本地文件获取数据"""
    if not os.path.exists(LOCAL_DATA_FILE):
        return []

    try:
        df = pd.read_csv(LOCAL_DATA_FILE, encoding='utf-8')
        results = []
        
        for code in stock_codes:
            row = df[df['股票代码'] == code]
            if not row.empty:
                results.append({
                    'f12': code,
                    'f14': STOCKS.get(code, code),
                    'f2': row['收盘'].iloc[0],
                    'f3': 0,  # 涨跌幅需要计算
                    'f5': 0,  # 量比
                    'f15': row['开盘'].iloc[0],
                    'f16': row['最高'].iloc[0],
                    'f17': row['最低'].iloc[0],
                })
        return results
    except Exception as e:
        print(f"读取本地数据失败: {e}")
        return []


def update_local_data():
    """更新本地数据文件"""
    print("\n🔄 正在更新本地数据...")
    os.system(f'python "{os.path.dirname(__file__)}\\..\\update_all_realtime_data.py"')
    print("✅ 本地数据更新完成")


def calculate_panic_score(drop, volume_ratio):
    """计算恐慌盘评分"""
    score = 0
    reasons = []

    if drop <= -8:
        score += 50
        reasons.append(f"恐慌性抛售 {abs(drop):.2f}%")
    elif drop <= -6:
        score += 40
        reasons.append(f"大幅下跌 {abs(drop):.2f}%")
    elif drop <= -4:
        score += 30
        reasons.append(f"明显下跌 {abs(drop):.2f}%")
    elif drop <= -3:
        score += 20
        reasons.append(f"中等下跌 {abs(drop):.2f}%")
    elif drop <= -2:
        score += 10
        reasons.append(f"小幅下跌 {abs(drop):.2f}%")

    if volume_ratio >= 2.0:
        score += 30
        reasons.append(f"明显放量 {volume_ratio:.2f}倍")
    elif volume_ratio >= 1.5:
        score += 20
        reasons.append(f"温和放量 {volume_ratio:.2f}倍")

    return score, reasons


def format_realtime_data(raw_data):
    """格式化实时数据"""
    results = []

    for item in raw_data:
        try:
            code = item.get('f12', '')
            name = STOCKS.get(code, item.get('f14', code))
            current_price = item.get('f2', 0)
            change_percent = item.get('f3', 0)
            volume_ratio = item.get('f5', 0)
            today_open = item.get('f15', 0)
            today_high = item.get('f16', 0)
            today_low = item.get('f17', 0)

            if today_open > 0 and today_low > 0:
                intraday_max_drop = ((today_low - today_open) / today_open) * 100
            else:
                intraday_max_drop = change_percent

            results.append({
                'code': code,
                'name': name,
                'price': current_price,
                'change_percent': change_percent,
                'volume_ratio': volume_ratio,
                'open': today_open,
                'high': today_high,
                'low': today_low,
                'intraday_max_drop': intraday_max_drop
            })
        except Exception as e:
            continue

    return results


def scan_panic_stocks(data):
    """扫描恐慌盘标的"""
    panic_stocks = []

    for stock in data:
        drop = stock['change_percent']
        volume_ratio = stock['volume_ratio']
        intraday_drop = stock['intraday_max_drop']

        max_drop = min(drop, intraday_drop)

        score, reasons = calculate_panic_score(max_drop, volume_ratio)

        if score >= 20:
            panic_stocks.append({
                'code': stock['code'],
                'name': stock['name'],
                'price': stock['price'],
                'drop': drop,
                'max_drop': max_drop,
                'volume_ratio': volume_ratio,
                'open': stock['open'],
                'high': stock['high'],
                'low': stock['low'],
                'score': score,
                'reasons': reasons,
                'recommendation': '🔥 强烈关注' if score >= 50 else '📊 建议关注' if score >= 30 else '👀 观察'
            })

    panic_stocks.sort(key=lambda x: x['score'], reverse=True)
    return panic_stocks


def print_header():
    """打印表头"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "=" * 100)
    print(f"🚀 盘中实时盯盘系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"监控股票数量: {len(STOCKS)} 只")
    print(f"恐慌盘阈值: 跌幅 >= {PANIC_THRESHOLD}%")
    print(f"刷新间隔: {REFRESH_INTERVAL} 秒")
    print("=" * 100)


def print_market_overview(data):
    """打印市场概况"""
    if not data:
        print("\n暂无数据")
        return

    rising = [s for s in data if s['change_percent'] > 0]
    falling = [s for s in data if s['change_percent'] < 0]
    limit_up = [s for s in data if s['change_percent'] >= 9.9]
    limit_down = [s for s in data if s['change_percent'] <= -9.9]

    print(f"\n市场概况: 涨 {len(rising)} | 跌 {len(falling)} | 涨停 {len(limit_up)} | 跌停 {len(limit_down)}")

    if limit_down:
        print(f"\n⚠️ 跌停股票:")
        for stock in limit_down[:5]:
            print(f"  - {stock['name']} ({stock['code']}): {stock['change_percent']:.2f}%")


def print_panic_results(panic_stocks):
    """打印恐慌盘结果"""
    if not panic_stocks:
        print("\n✅ 当前暂无恐慌盘迹象，市场稳定")
        return

    print(f"\n🚨 发现 {len(panic_stocks)} 只恐慌抛压股票:")
    print("-" * 100)
    print(f"{'排名':<4} {'代码':<10} {'名称':<10} {'现价':>8} {'涨跌幅':>8} {'日内最大':>8} {'量比':>6} {'评分':>4} {'状态'}")
    print("-" * 100)

    for i, stock in enumerate(panic_stocks[:20], 1):
        flag = "🔴" if stock['max_drop'] <= -5 else "🟠" if stock['max_drop'] <= -3 else "👀"
        print(f"{i:<4} {stock['code']:<10} {stock['name']:<10} "
              f"{stock['price']:>8.2f} {stock['drop']:>+7.2f}% {stock['max_drop']:>+7.2f}% "
              f"{stock['volume_ratio']:>6.2f} {stock['score']:>4} {flag}")

    if len(panic_stocks) > 20:
        print(f"\n... 还有 {len(panic_stocks) - 20} 只")


def print_top_movers(data):
    """打印涨跌幅排行"""
    if not data:
        return

    sorted_by_drop = sorted(data, key=lambda x: x['change_percent'])

    print("\n" + "-" * 80)
    print("📉 跌幅前5:")
    for stock in sorted_by_drop[:5]:
        print(f"  {stock['name']:<10} {stock['change_percent']:>+7.2f}%  (低:{stock['low']:.2f})")

    print("\n📈 涨幅前5:")
    for stock in sorted_by_drop[-5:][::-1]:
        if stock['change_percent'] > 0:
            print(f"  {stock['name']:<10} {stock['change_percent']:>+7.2f}%  (高:{stock['high']:.2f})")


def print_opportunity_alert(panic_stocks):
    """打印机会提醒"""
    strong = [s for s in panic_stocks if s['score'] >= 50]
    moderate = [s for s in panic_stocks if 30 <= s['score'] < 50]

    if strong:
        print("\n" + "=" * 80)
        print("🔥 紧急关注 - 可能出现低吸机会:")
        print("=" * 80)
        for stock in strong[:5]:
            print(f"  {stock['name']} ({stock['code']}): ")
            print(f"    当前跌幅: {stock['drop']:+.2f}% | 日内最大跌幅: {stock['max_drop']:+.2f}%")
            print(f"    原因: {' + '.join(stock['reasons'])}")

    if moderate:
        print("\n📊 建议观察:")
        for stock in moderate[:5]:
            print(f"  {stock['name']} ({stock['code']}): {stock['max_drop']:+.2f}%")


def main():
    """主函数"""
    print("\n" + "=" * 100)
    print("盘中实时盯盘系统")
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    print("\n请选择数据源：")
    print("1. 网络实时数据（东方财富）")
    print("2. 本地数据（通达信）")
    print("3. 自动模式（优先网络，失败用本地）")
    
    choice = input("\n请输入选择 (1/2/3，默认3): ").strip() or "3"
    
    use_network = choice in ["1", "3"]
    use_local = choice in ["2", "3"]

    if not is_market_open():
        print("\n当前非交易时间（9:30-11:30, 13:00-15:00）")
        print("脚本将继续运行，可获取最新报价数据")
        print("\n按 Ctrl+C 退出")
        input("\n按回车键开始监控...")
    else:
        print("\n市场已开市，开始实时监控...")

    print(f"\n监控板块: 光模块 + 算力 + 半导体细分龙头")
    print(f"股票数量: {len(STOCKS)} 只")
    print(f"刷新间隔: {REFRESH_INTERVAL} 秒")
    print("\n按 Ctrl+C 停止监控\n")

    stock_codes = list(STOCKS.keys())
    run_count = 0

    try:
        while True:
            run_count += 1
            print_header()

            raw_data = []
            
            # 获取数据
            if use_network:
                raw_data = get_realtime_data(stock_codes)
            
            # 如果网络数据失败，尝试本地数据
            if not raw_data and use_local:
                print("\n⚠️ 网络数据获取失败，尝试使用本地数据")
                update_local_data()
                raw_data = get_local_data(stock_codes)

            if raw_data:
                data = format_realtime_data(raw_data)
                panic_stocks = scan_panic_stocks(data)

                print_market_overview(data)
                print_panic_results(panic_stocks)
                print_top_movers(data)
                print_opportunity_alert(panic_stocks)

                print("\n" + "=" * 100)
                print(f"第 {run_count} 次扫描完成 | 下次刷新: {REFRESH_INTERVAL}秒后 | {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 100)
            else:
                print("\n❌ 获取数据失败，请检查网络连接或本地数据")
                print("5秒后重试...")
                time.sleep(5)
                continue

            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n监控已停止")
        print(f"共运行 {run_count} 次扫描")
        print(f"停止时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()