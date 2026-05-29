#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出通达信数据到CSV - 读取今日最新数据
"""

import sys
import os
from datetime import datetime
import struct


TDX_PATH = r"C:\new_tdx"
OUTPUT_FILE = r"C:\Users\Administrator\Documents\trae_projects\33\data\tdx\today_data.csv"


def read_tdx_day_file(file_path):
    """读取通达信日线数据文件"""
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
    """获取单只股票的最新数据"""
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
            return data[-1]  # 返回最新一条

    return None


def format_date(date_str):
    """格式化日期"""
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str


def main():
    print("=" * 80)
    print("📊 通达信数据导出工具")
    print("=" * 80)

    # 热门股票列表
    stocks = [
        '000001.SZ',  # 平安银行
        '000002.SZ',  # 万科A
        '000858.SZ',  # 五粮液
        '600519.SH',  # 贵州茅台
        '601318.SH',  # 中国平安
        '300750.SZ',  # 宁德时代
        '002594.SZ',  # 比亚迪
        '601012.SH',  # 隆基绿能
        '002475.SZ',  # 立讯精密
        '603501.SH',  # 韦尔股份
        '000725.SZ',  # 京东方A
        '300059.SZ',  # 东方财富
        '000333.SZ',  # 美的集团
        '600036.SH',  # 招商银行
        '601166.SH',  # 兴业银行
        '600900.SH',  # 长江电力
    ]

    print(f"\n📂 数据源: {TDX_PATH}")
    print(f"📝 股票数量: {len(stocks)} 只")

    results = []
    success_count = 0

    print("\n🔍 正在读取数据...")

    for stock_code in stocks:
        data = get_latest_data(stock_code)
        if data:
            date, open_price, high_price, low_price, close_price, volume = data
            formatted_date = format_date(date)

            results.append({
                'symbol': stock_code,
                'date': formatted_date,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
            success_count += 1

    if success_count == 0:
        print("\n❌ 未能读取任何数据！")
        print("\n请检查：")
        print(f"  1. 通达信数据路径是否正确: {TDX_PATH}")
        print("  2. 通达信是否已下载并保存了数据")
        print("  3. 尝试重新下载数据到通达信")
        return

    print(f"\n✅ 成功读取 {success_count} 只股票数据")

    # 写入CSV文件
    print(f"\n💾 正在保存到: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        file.write("股票代码,日期,开盘,最高,最低,收盘,成交量\n")
        for stock in results:
            line = f"{stock['symbol']},{stock['date']},{stock['open']},{stock['high']},{stock['low']},{stock['close']},{stock['volume']}\n"
            file.write(line)

    print(f"✅ 数据已保存到: {OUTPUT_FILE}")

    # 显示数据预览
    print("\n" + "=" * 80)
    print("📊 数据预览")
    print("=" * 80)

    for stock in results[:5]:
        print(f"{stock['symbol']:12} | {stock['date']} | 开:{stock['open']:8.2f} 高:{stock['high']:8.2f} 低:{stock['low']:8.2f} 收:{stock['close']:8.2f} 量:{stock['volume']:>10}")

    if len(results) > 5:
        print(f"... 还有 {len(results) - 5} 只股票")

    print("\n" + "=" * 80)
    print("✅ 数据导出完成！")
    print("=" * 80)

    print("\n💡 下一步:")
    print("  1. 运行 'npm run scan-panic' 扫描恐慌盘")
    print("  2. 运行 'npm run market' 查看市场概况")
    print("  3. 运行 'npm run panic' 回测策略表现")


if __name__ == "__main__":
    main()
