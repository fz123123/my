#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌盘扫描工具 - 独立运行版
"""

import sys
import os
from datetime import datetime
import struct

# 设置控制台编码
if sys.platform.startswith('win'):
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

# ============ 配置区域 ============
TDX_PATH = r"C:\new_tdx"
OUTPUT_DIR = r"C:\Users\Administrator\Documents\trae_projects\33\data\tdx"

# 光模块板块
OPTICAL_MODULE = [
    '300308.SZ',  # 中际旭创 - 光模块龙头
    '300502.SZ',  # 新易盛 - 光模块龙头
    '002281.SZ',  # 光迅科技 - 光器件龙头
    '300548.SZ',  # 博创科技 - 光模块
    '603083.SH',  # 剑桥科技 - 光模块
    '000988.SZ',  # 华工科技 - 光模块
    '002902.SZ',  # 铭普光磁 - 光模块
    '300570.SZ',  # 太辰光 - 光器件
    '300394.SZ',  # 天孚通信 - 光器件
    '688313.SH',  # 仕佳光子 - 光芯片
    '002897.SZ',  # 意华股份 - 光连接器
]

# 光纤光缆
FIBER_CABLE = [
    '600487.SH',  # 亨通光电
    '600522.SH',  # 中天科技
    '600105.SH',  # 永鼎股份
    '300265.SZ',  # 通光线缆
    '000070.SZ',  # 特发信息
    '600776.SH',  # 长江通信
]

# 算力板块
AI_COMPUTING = [
    '300750.SZ',  # 宁德时代 - 储能/算力
    '300124.SZ',  # 汇川技术 - 工业自动化
    '002230.SZ',  # 科大讯飞 - AI
    '300474.SZ',  # 景嘉微 - GPU/显卡
    '688256.SH',  # 寒武纪 - AI芯片
    '603019.SH',  # 中科曙光 - 服务器
    '000977.SZ',  # 浪潮信息 - 服务器
    '600588.SH',  # 用友网络 - SaaS
    '002415.SZ',  # 海康威视 - AI视觉
    '300785.SZ',  # 值得买 - 电商AI
]

# 半导体设备
SEMI_EQUIP = [
    '688012.SH',  # 中微公司 - 刻蚀设备
    '002371.SZ',  # 北方华创 - 半导体设备
    '688396.SH',  # 华润微 - 功率半导体
    '603501.SH',  # 韦尔股份 - 图像传感器
    '688981.SH',  # 中芯国际 - 晶圆代工
    '688599.SH',  # 天合光能 - 光伏
    '600584.SH',  # 长电科技 - 封测
    '002185.SZ',  # 华天科技 - 封测
    '600460.SH',  # 士兰微 - 功率半导体
    '688008.SH',  # 澜起科技 - 内存接口
    '688223.SH',  # 晶科能源 - 光伏
    '300666.SZ',  # 江丰电子 - 靶材
    '688126.SH',  # 沪硅产业 - 硅片
    '002129.SZ',  # 中环股份 - 硅片
    '688396.SH',  # 华润微 - IDM
]

# 半导体设计
SEMI_DESIGN = [
    '688479.SH',  # 歌尔股份 - 传感器
    '002241.SZ',  # 韦尔股份 - 设计
    '300223.SZ',  # 北京君正 - ASIC
    '688521.SH',  # 芯原股份 - IP/设计
    '603160.SH',  # 汇顶科技 - 指纹芯片
    '300456.SZ',  # 赛微电子 - MEMS
    '688220.SH',  # 翱捷科技 - 基带芯片
    '688099.SH',  # 晶晨股份 - 多媒体芯片
    '688048.SH',  # 长光华芯 - 光芯片
    '688234.SH',  # 狄耐克 - 智能家居
]

# AI/算力应用
AI_APPLICATION = [
    '300058.SZ',  # 蓝色光标 - AI营销
    '002236.SZ',  # 大华股份 - AI视觉
    '300024.SZ',  # 机器人 - AI
    '688787.SH',  # 海天瑞声 - AI数据
    '300002.SZ',  # 神州泰岳 - AI
    '300024.SZ',  # 机器人
]

# 汇总所有股票
STOCKS = (OPTICAL_MODULE + FIBER_CABLE + AI_COMPUTING + 
          SEMI_EQUIP + SEMI_DESIGN + AI_APPLICATION)


def read_tdx_day_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        record_size = 32
        num_records = len(data) // record_size

        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []

        for i in range(num_records):
            offset = i * record_size
            record = data[offset:offset+record_size]
            date = struct.unpack('I', record[0:4])[0]
            open_price = struct.unpack('i', record[4:8])[0] / 100.0
            high_price = struct.unpack('i', record[8:12])[0] / 100.0
            low_price = struct.unpack('i', record[12:16])[0] / 100.0
            close_price = struct.unpack('i', record[16:20])[0] / 100.0
            volume = struct.unpack('I', record[20:24])[0]

            dates.append(str(date))
            opens.append(round(open_price, 2))
            highs.append(round(high_price, 2))
            lows.append(round(low_price, 2))
            closes.append(round(close_price, 2))
            volumes.append(volume)

        return list(zip(dates, opens, highs, lows, closes, volumes))
    except Exception as e:
        return None


def get_latest_data(stock_code):
    parts = stock_code.split('.')
    if len(parts) != 2:
        return None

    code = parts[0]
    market = parts[1]

    if market == 'SH':
        day_path = os.path.join(TDX_PATH, 'vipdoc', 'sh', 'lday', f'sh{code}.day')
    else:
        day_path = os.path.join(TDX_PATH, 'vipdoc', 'sz', 'lday', f'sz{code}.day')

    if os.path.exists(day_path):
        data = read_tdx_day_file(day_path)
        if data and len(data) > 0:
            return data[-1]

    return None


def format_date(date_str):
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str


def calculate_panic_score(stock_data):
    date, open_price, high_price, low_price, close_price, volume = stock_data

    drop = (close_price - open_price) / open_price
    max_drop = (low_price - open_price) / open_price
    max_drop = min(drop, max_drop)

    avg_volume = volume * 0.8
    volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0

    score = 0
    reasons = []

    if max_drop <= -0.08:
        score += 50
        reasons.append(f"恐慌性抛售 {abs(max_drop * 100):.2f}%")
    elif max_drop <= -0.06:
        score += 40
        reasons.append(f"大幅下跌 {abs(max_drop * 100):.2f}%")
    elif max_drop <= -0.04:
        score += 30
        reasons.append(f"明显下跌 {abs(max_drop * 100):.2f}%")
    elif max_drop <= -0.03:
        score += 20
        reasons.append(f"中等下跌 {abs(max_drop * 100):.2f}%")
    elif max_drop <= -0.02:
        score += 10
        reasons.append(f"小幅下跌 {abs(max_drop * 100):.2f}%")

    if volume_ratio >= 3.0:
        score += 40
        reasons.append(f"天量恐慌 {volume_ratio:.1f}倍")
    elif volume_ratio >= 2.5:
        score += 35
        reasons.append(f"巨量下跌 {volume_ratio:.1f}倍")
    elif volume_ratio >= 2.0:
        score += 30
        reasons.append(f"明显放量 {volume_ratio:.1f}倍")
    elif volume_ratio >= 1.5:
        score += 20
        reasons.append(f"温和放量 {volume_ratio:.1f}倍")

    if score >= 60:
        recommendation = "强烈建议关注"
    elif score >= 40:
        recommendation = "建议关注"
    elif score >= 20:
        recommendation = "观察等待"
    else:
        recommendation = "暂不推荐"

    return {
        'symbol': '',
        'date': format_date(date),
        'open': open_price,
        'high': high_price,
        'low': low_price,
        'close': close_price,
        'volume': volume,
        'drop': drop,
        'max_drop': max_drop,
        'volume_ratio': volume_ratio,
        'score': score,
        'reasons': reasons,
        'recommendation': recommendation
    }


def scan_panic_stocks():
    results = []

    for stock_code in STOCKS:
        data = get_latest_data(stock_code)
        if data:
            stock_info = calculate_panic_score(data)
            stock_info['symbol'] = stock_code
            results.append(stock_info)

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def print_market_overview(results):
    print("\n" + "=" * 80)
    print("今日市场概况")
    print("=" * 80)

    dates = set(r['date'] for r in results)
    latest_date = max(dates) if dates else "未知"

    print(f"\n数据日期: {latest_date}")
    print(f"股票数量: {len(results)} 只")

    rising = [r for r in results if r['drop'] > 0.01]
    falling = [r for r in results if r['drop'] < -0.01]
    flat = [r for r in results if -0.01 <= r['drop'] <= 0.01]

    print(f"\n上涨: {len(rising)} 只")
    print(f"下跌: {len(falling)} 只")
    print(f"平盘: {len(flat)} 只")

    if falling:
        avg_drop = sum(r['drop'] for r in falling) / len(falling)
        print(f"平均跌幅: {avg_drop * 100:.2f}%")

    print("\n" + "=" * 80)
    print("跌幅榜 TOP 5:")
    print("=" * 80)

    sorted_by_drop = sorted(results, key=lambda x: x['drop'])
    for i, stock in enumerate(sorted_by_drop[:5], 1):
        flag = "*" if stock['drop'] < -0.03 else " "
        print(f"{i}. {flag} {stock['symbol']:12} {stock['drop']*100:+6.2f}%  "
              f"开:{stock['open']:8.2f} 收:{stock['close']:8.2f} 低:{stock['low']:8.2f}")

    print("\n" + "=" * 80)
    print("涨幅榜 TOP 5:")
    print("=" * 80)

    sorted_by_rise = sorted(results, key=lambda x: x['drop'], reverse=True)
    for i, stock in enumerate(sorted_by_rise[:5], 1):
        if stock['drop'] > 0.01:
            flag = "+" if stock['drop'] > 0.02 else " "
            print(f"{i}. {flag} {stock['symbol']:12} {stock['drop']*100:+6.2f}%  "
                  f"开:{stock['open']:8.2f} 收:{stock['close']:8.2f} 高:{stock['high']:8.2f}")


def print_panic_results(results):
    print("\n" + "=" * 80)
    print("恐慌盘扫描结果")
    print("=" * 80)

    panic_stocks = [r for r in results if r['score'] >= 20]

    if not panic_stocks:
        print("\n今日市场无恐慌盘迹象，市场情绪稳定")
        return

    print(f"\n发现 {len(panic_stocks)} 只恐慌抛压股票:\n")

    for i, stock in enumerate(panic_stocks, 1):
        print(f"{i}. [{stock['recommendation']}] {stock['symbol']}")
        print(f"   原因: {' + '.join(stock['reasons'])}")
        print(f"   数据: 开:{stock['open']:.2f} 高:{stock['high']:.2f} 低:{stock['low']:.2f} 收:{stock['close']:.2f}")
        print(f"   评分: {stock['score']}分 | 日内最大跌幅: {stock['max_drop']*100:.2f}% | 量比: {stock['volume_ratio']:.2f}倍")
        print()


def print_investment_suggestions(results):
    print("\n" + "=" * 80)
    print("低吸操作建议")
    print("=" * 80)

    strong = [r for r in results if r['score'] >= 60]
    moderate = [r for r in results if 40 <= r['score'] < 60]

    if strong:
        print("\n强烈关注标的 (可考虑低吸):")
        for stock in strong:
            print(f"  - {stock['symbol']}: {' + '.join(stock['reasons'])}")

    if moderate:
        print("\n建议观察标的:")
        for stock in moderate:
            print(f"  - {stock['symbol']}: {' + '.join(stock['reasons'])}")

    print("\n" + "=" * 80)
    print("低吸策略要点:")
    print("=" * 80)
    print("""
  1. 等待信号：不要盲目追跌，等待缩量企稳后再买入
  2. 仓位控制：分批建仓，首次买入控制在30%-50%仓位
  3. 止损原则：设置止损位，一般不超过6%
  4. 止盈目标：目标收益8%左右及时止盈
  5. 持仓时间：持仓不超过15个交易日
  6. 风险意识：暴跌后可能有反弹，但也要警惕加速下跌风险
    """)

    print("=" * 80)
    print("风险提示:")
    print("=" * 80)
    print("""
  * 恐慌盘可能意味着市场整体下跌，不宜单独操作
  * 需结合大盘走势、市场情绪综合判断
  * 分散投资，不要把所有资金押注在单一标的上
  * 以上分析仅供参考，不构成投资建议
    """)


def main():
    print("\n" + "=" * 80)
    print("恐慌盘自动扫描系统")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\n数据源: {TDX_PATH}")
    print(f"待扫描股票: {len(STOCKS)} 只")

    if not os.path.exists(TDX_PATH):
        print(f"\n错误: 通达信数据目录不存在: {TDX_PATH}")
        print("\n请检查:")
        print("  1. 通达信是否已安装并下载了数据")
        print("  2. TDX_PATH 配置是否正确")
        return

    print("\n正在扫描恐慌盘信号...")

    results = scan_panic_stocks()

    if not results:
        print("\n未能读取任何股票数据！")
        print("\n请检查:")
        print("  1. 通达信是否已下载并保存了数据")
        print("  2. 网络连接是否正常")
        print("  3. 尝试重新打开通达信下载数据")
        return

    print(f"成功扫描 {len(results)} 只股票")

    print_market_overview(results)
    print_panic_results(results)
    print_investment_suggestions(results)

    print("\n" + "=" * 80)
    print("扫描完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
