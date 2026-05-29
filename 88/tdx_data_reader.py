#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 通达信数据读取模块
ZTB Seer - TongDaXin Data Reader
读取通达信 .day 文件格式
"""

import struct
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import os

class TDXDataReader:
    """通达信日线数据读取器"""

    def __init__(self, data_path: str = r"C:\new_tdx\vipdoc"):
        self.data_path = Path(data_path)
        self.market_map = {
            'sh': '上海市场',
            'sz': '深圳市场',
            'bj': '北京市场',
            'hk': '港股市场'
        }

    def read_day_file(self, file_path: str) -> pd.DataFrame:
        """读取单个.day文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        records = []

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(32)
                if not data or len(data) < 32:
                    break

                try:
                    date, open_price, high, low, close, amount, volume, _ = struct.unpack('<IIIIIfII', data)

                    if date == 0:
                        continue

                    year = date // 10000
                    month = (date % 10000) // 100
                    day = date % 100

                    date_str = f"{year:04d}-{month:02d}-{day:02d}"

                    records.append({
                        'date': date_str,
                        'open': open_price / 100.0,
                        'high': high / 100.0,
                        'low': low / 100.0,
                        'close': close / 100.0,
                        'volume': volume,
                        'amount': amount / 1000.0
                    })
                except Exception as e:
                    continue

        df = pd.DataFrame(records)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()

        return df

    def read_stock_data(self, market: str, stock_code: str, years: Optional[int] = None) -> pd.DataFrame:
        """读取指定股票的数据"""
        market = market.lower()
        file_path = self.data_path / market / 'lday' / f"{market}{stock_code}.day"

        if not file_path.exists():
            raise FileNotFoundError(f"股票数据文件不存在: {file_path}")

        df = self.read_day_file(str(file_path))

        if years and not df.empty:
            cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
            df = df[df.index >= cutoff_date]

        return df

    def get_available_stocks(self, market: str) -> List[Dict[str, str]]:
        """获取指定市场所有可用的股票列表"""
        market = market.lower()
        lday_path = self.data_path / market / 'lday'

        if not lday_path.exists():
            return []

        stocks = []
        for file_path in lday_path.glob('*.day'):
            code = file_path.stem[2:]
            stocks.append({
                'code': code,
                'market': market,
                'name': self.get_stock_name(code, market),
                'file': str(file_path)
            })

        return sorted(stocks, key=lambda x: x['code'])

    def get_stock_name(self, code: str, market: str) -> str:
        """尝试从code2name.ini获取股票名称"""
        try:
            code2name_path = self.data_path / 'T0002' / 'hq_cache' / 'code2name.ini'
            if code2name_path.exists():
                with open(code2name_path, 'r', encoding='gbk') as f:
                    for line in f:
                        if line.startswith(f"{market.upper()}{code},"):
                            return line.split(',')[1].strip()
        except:
            pass
        return code

    def search_stocks(self, keyword: str, market: Optional[str] = None) -> List[Dict]:
        """搜索股票"""
        results = []
        markets = [market] if market else ['sh', 'sz', 'bj']

        for m in markets:
            if m not in self.market_map:
                continue

            stocks = self.get_available_stocks(m)
            for stock in stocks:
                if keyword.upper() in stock['code'] or keyword.upper() in stock['name'].upper():
                    results.append(stock)

        return results

    def get_index_data(self, index_code: str = '000001', years: Optional[int] = None) -> pd.DataFrame:
        """获取指数数据"""
        return self.read_stock_data('sh', index_code, years)

    def batch_read_stocks(self, stock_list: List[tuple], years: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """批量读取多只股票数据"""
        data_dict = {}

        for market, code in stock_list:
            try:
                df = self.read_stock_data(market, code, years)
                if not df.empty:
                    data_dict[f"{market.upper()}{code}"] = df
            except Exception as e:
                print(f"读取 {market.upper()}{code} 失败: {e}")
                continue

        return data_dict

    def get_data_summary(self) -> Dict:
        """获取数据汇总信息"""
        summary = {}

        for market, name in self.market_map.items():
            lday_path = self.data_path / market / 'lday'
            if lday_path.exists():
                stock_count = len(list(lday_path.glob('*.day')))

                sample_files = list(lday_path.glob('*.day'))[:3]
                date_ranges = []

                for file_path in sample_files:
                    try:
                        df = self.read_day_file(str(file_path))
                        if not df.empty:
                            date_ranges.append((df.index.min(), df.index.max()))
                    except:
                        continue

                summary[market] = {
                    'name': name,
                    'stock_count': stock_count,
                    'sample_range': date_ranges if date_ranges else None
                }

        return summary

if __name__ == "__main__":
    reader = TDXDataReader()

    print("=" * 80)
    print("⚡ 通达信数据读取器 - 测试")
    print("=" * 80)

    print("\n📊 数据总览:")
    summary = reader.get_data_summary()
    for market, info in summary.items():
        print(f"  {info['name']} ({market}): {info['stock_count']} 只股票")
        if info['sample_range']:
            for start, end in info['sample_range'][:2]:
                print(f"    样本范围: {start.date()} ~ {end.date()}")

    print("\n🔍 测试读取上证指数:")
    try:
        df = reader.get_index_data('000001', years=1)
        print(f"  上证指数最近1年数据: {len(df)} 条")
        print(f"  最新数据: {df.index[-1].date()}")
        print(f"  最新收盘价: ¥{df['close'].iloc[-1]:.2f}")
        print(f"\n  最近5天行情:")
        print(df[['open', 'high', 'low', 'close', 'volume']].tail())
    except Exception as e:
        print(f"  读取失败: {e}")

    print("\n🔍 测试读取一只深证股票:")
    try:
        df = reader.read_stock_data('sz', '000001', years=1)
        print(f"  深证成指最近1年数据: {len(df)} 条")
        print(f"  最新数据: {df.index[-1].date()}")
    except Exception as e:
        print(f"  读取失败: {e}")

    print("\n🔍 搜索包含'茅台'的股票:")
    results = reader.search_stocks('茅台')
    for stock in results[:5]:
        print(f"  {stock['market'].upper()}{stock['code']} - {stock['name']}")

    print("\n" + "=" * 80)
    print("✅ 通达信数据读取器测试完成")
    print("=" * 80)
