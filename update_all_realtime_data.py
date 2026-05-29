#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据更新服务 - 统一数据更新模块
支持通达信本地数据（离线模式）和网络实时接口
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import struct

# 配置日志
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'data_update_{datetime.now().strftime("%Y%m%d")}.log'

# 创建logger
logger = logging.getLogger('DataUpdater')
logger.setLevel(logging.DEBUG)

# 文件handler - 记录所有级别
fh = logging.FileHandler(log_file, encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))

# 控制台handler - 只显示INFO及以上
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'))

logger.addHandler(fh)
logger.addHandler(ch)

import pandas as pd
import requests
import time

class RealTimeDataUpdater:
    def __init__(self, tdx_path=r"C:\new_tdx\vipdoc"):
        logger.info("="*60)
        logger.info("初始化实时数据更新服务")
        logger.info("="*60)
        
        self.tdx_path = Path(tdx_path)
        self.data_dir = Path(__file__).parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        self.network_available = True
        self.data_source = "未知"
        
        logger.info(f"📁 通达信数据路径: {self.tdx_path}")
        logger.info(f"📁 输出数据目录: {self.data_dir}")
        logger.info(f"📁 日志文件: {log_file}")
        
        # 检查通达信路径是否存在
        if self.tdx_path.exists():
            logger.info(f"✅ 通达信路径存在")
        else:
            logger.warning(f"⚠️ 通达信路径不存在: {self.tdx_path}")
        
    def _test_network(self):
        """测试网络是否可用"""
        logger.info("-"*40)
        logger.info("🔍 开始网络连接测试")
        
        test_urls = [
            ('百度', 'http://www.baidu.com'),
            ('新浪', 'http://hq.sinajs.cn'),
            ('东方财富', 'http://push2.eastmoney.com'),
        ]
        
        for name, url in test_urls:
            try:
                logger.debug(f"  测试连接: {name} ({url})")
                start_time = time.time()
                response = requests.get(url, timeout=3)
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"  ✅ {name}: 连接成功 (耗时: {elapsed:.0f}ms, 状态码: {response.status_code})")
            except requests.exceptions.Timeout:
                logger.warning(f"  ⏱️ {name}: 连接超时 (timeout=3s)")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"  ❌ {name}: 连接错误 - {str(e)[:50]}")
            except Exception as e:
                logger.warning(f"  ❌ {name}: 未知错误 - {str(e)[:50]}")
        
        # 最终测试
        try:
            response = requests.get('http://www.baidu.com', timeout=3)
            if response.status_code == 200:
                logger.info("✅ 网络状态: 可用")
                return True
        except:
            pass
        
        logger.warning("⚠️ 网络状态: 不可用，将使用本地数据")
        return False
    
    def get_sina_realtime(self, market, code):
        """从新浪获取实时行情"""
        if not self.network_available:
            logger.debug(f"  网络不可用，跳过新浪接口: {market}{code}")
            return None
            
        try:
            url = f"http://hq.sinajs.cn/list={market}{code}"
            logger.debug(f"  请求新浪接口: {url}")
            
            start_time = time.time()
            response = requests.get(url, timeout=5)
            elapsed = (time.time() - start_time) * 1000
            
            response.encoding = 'gb2312'
            data = response.text
            
            if '=' in data:
                parts = data.split('=')[-1].strip().replace('"', '')
                fields = parts.split(',')
                if len(fields) >= 10:
                    result = {
                        'code': code,
                        'name': fields[0] if fields[0] else code,
                        'open': float(fields[1]) if fields[1] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0,
                        'current': float(fields[3]) if fields[3] else 0,
                        'volume': int(float(fields[8])) if fields[8] else 0,
                        'amount': float(fields[9]) if fields[9] else 0,
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    logger.debug(f"  ✅ 新浪数据获取成功 (耗时: {elapsed:.0f}ms)")
                    return result
            else:
                logger.warning(f"  ⚠️ 新浪返回数据格式异常: {data[:50]}")
        except requests.exceptions.Timeout:
            logger.warning(f"  ⏱️ 新浪接口超时: {market}{code}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"  ❌ 新浪连接错误: {str(e)[:50]}")
        except Exception as e:
            logger.error(f"  ❌ 新浪接口异常: {e}")
        return None
    
    def _read_day_file(self, file_path):
        """读取通达信.day文件"""
        if not os.path.exists(file_path):
            logger.debug(f"  文件不存在: {file_path}")
            return pd.DataFrame()
        
        try:
            records = []
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(32)
                    if not data or len(data) < 32:
                        break
                    try:
                        date, open_p, high, low, close, amount, volume, _ = struct.unpack('<IIIIIfII', data)
                        if date == 0:
                            continue
                        year = date // 10000
                        month = (date % 10000) // 100
                        day = date % 100
                        date_str = f"{year:04d}-{month:02d}-{day:02d}"
                        records.append({
                            'date': date_str,
                            'open': open_p / 100.0,
                            'high': high / 100.0,
                            'low': low / 100.0,
                            'close': close / 100.0,
                            'volume': volume,
                            'amount': amount / 1000.0
                        })
                    except struct.error:
                        continue
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                logger.debug(f"  读取成功: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"  读取文件失败: {file_path}, 错误: {e}")
            return pd.DataFrame()
    
    def get_stock_name_from_tdx(self, code, market):
        """从通达信获取股票名称"""
        try:
            code2name_path = self.tdx_path / 'T0002' / 'hq_cache' / 'code2name.ini'
            if code2name_path.exists():
                with open(code2name_path, 'r', encoding='gbk') as f:
                    for line in f:
                        if line.startswith(f"{market.upper()}{code},"):
                            return line.split(',')[1].strip()
        except Exception as e:
            logger.debug(f"  获取股票名称失败: {e}")
        return code
    
    def update_project88_watchlist(self):
        """更新项目88的自选股数据（使用通达信本地数据）"""
        logger.info("-"*40)
        logger.info("📊 项目88: 开始更新自选股数据")
        
        watchlist = [
            ('sh', '688981', '中芯国际'),
            ('sz', '300750', '宁德时代'),
            ('sz', '002371', '北方华创'),
            ('sh', '601318', '中国平安'),
            ('sh', '600036', '招商银行'),
            ('sz', '000333', '美的集团'),
            ('sh', '600276', '恒瑞医药'),
            ('sh', '600519', '贵州茅台'),
            ('sz', '000858', '五粮液'),
            ('sh', '601899', '紫金矿业'),
        ]
        
        results = []
        success_count = 0
        fail_count = 0
        
        logger.info(f"� 待更新股票数: {len(watchlist)}")
        
        for market, code, name in watchlist:
            file_path = self.tdx_path / market / 'lday' / f"{market}{code}.day"
            logger.debug(f"  处理: {name} ({market}{code})")
            logger.debug(f"    文件路径: {file_path}")
            
            if file_path.exists():
                df = self._read_day_file(str(file_path))
                if not df.empty and len(df) > 0:
                    latest = df.iloc[-1]
                    results.append({
                        'market': market,
                        'code': code,
                        'name': name,
                        'open': latest['open'],
                        'high': latest['high'],
                        'low': latest['low'],
                        'current': latest['close'],
                        'volume': latest['volume'],
                        'amount': latest['amount'],
                        'update_time': latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                    logger.info(f"  ✅ {name} ({market}{code}): ¥{latest['close']:.2f} | 数据日期: {latest.name.strftime('%Y-%m-%d')}")
                    success_count += 1
                else:
                    logger.warning(f"  ❌ {name} ({market}{code}): 数据为空")
                    fail_count += 1
            else:
                logger.warning(f"  ❌ {name} ({market}{code}): 文件不存在")
                fail_count += 1
        
        # 保存到CSV
        if results:
            df = pd.DataFrame(results)
            df = df[['market', 'code', 'name', 'open', 'high', 'low', 'current', 'volume', 'amount', 'update_time']]
            output_file = Path(__file__).parent / '88' / 'watchlist_realtime.csv'
            output_file.parent.mkdir(exist_ok=True)
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"✅ 项目88: 保存 {len(results)} 条数据到 {output_file}")
            logger.info(f"   成功: {success_count}, 失败: {fail_count}")
        else:
            logger.error("⚠️ 项目88: 未获取到任何数据")
        
        return results
    
    def update_project33_panic_data(self):
        """更新项目33的恐慌盘扫描数据"""
        logger.info("-"*40)
        logger.info("📊 项目33: 开始更新恐慌盘扫描数据")
        
        today_data = []
        total_files = 0
        success_count = 0
        
        for market in ['sh', 'sz']:
            lday_path = self.tdx_path / market / 'lday'
            logger.info(f"  扫描市场: {market.upper()} -> {lday_path}")
            
            if lday_path.exists():
                stock_files = list(lday_path.glob('*.day'))[:100]
                total_files += len(stock_files)
                logger.info(f"    找到 {len(stock_files)} 个股票文件")
                
                for file in stock_files:
                    code = file.stem[2:]
                    df = self._read_day_file(str(file))
                    if not df.empty and len(df) > 0:
                        latest = df.iloc[-1]
                        today_data.append({
                            '股票代码': f"{market.upper()}{code}",
                            '日期': latest.name.strftime('%Y-%m-%d'),
                            '开盘': latest['open'],
                            '最高': latest['high'],
                            '最低': latest['low'],
                            '收盘': latest['close'],
                            '成交量': latest['volume'],
                        })
                        success_count += 1
            else:
                logger.warning(f"    ⚠️ 目录不存在: {lday_path}")
        
        # 保存到CSV
        df = pd.DataFrame(today_data)
        output_file = Path(__file__).parent / '33' / 'data' / 'tdx' / 'today_data.csv'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        logger.info(f"✅ 项目33: 保存 {len(today_data)} 条数据到 {output_file}")
        logger.info(f"   扫描文件: {total_files}, 成功: {success_count}")
        
        return df
    
    def update_project17_data(self):
        """更新项目17的对比分析数据"""
        logger.info("-"*40)
        logger.info("📊 项目17: 开始更新对比分析数据")
        
        try:
            import yfinance as yf
            logger.info("  ✅ yfinance模块已加载")
        except ImportError:
            logger.error("  ❌ 需要安装 yfinance: pip install yfinance")
            return False
        
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        logger.info(f"  时间范围: {start_date} ~ {end_date}")
        logger.info(f"  股票列表: {', '.join(symbols)}")
        
        all_data = {}
        success_count = 0
        fail_count = 0
        
        for symbol in symbols:
            try:
                logger.debug(f"  下载: {symbol}")
                data = yf.download(symbol, start=start_date, end=end_date)
                if not data.empty:
                    all_data[symbol] = data
                    logger.info(f"  ✅ {symbol}: {len(data)} 条数据")
                    success_count += 1
                else:
                    logger.warning(f"  ⚠️ {symbol}: 返回空数据")
                    fail_count += 1
            except Exception as e:
                logger.error(f"  ❌ {symbol}: 获取失败 - {e}")
                fail_count += 1
        
        # 保存数据
        output_dir = Path(__file__).parent / '17' / 'data'
        output_dir.mkdir(exist_ok=True)
        
        for symbol, df in all_data.items():
            df.reset_index(inplace=True)
            df['symbol'] = symbol
            output_file = output_dir / f"{symbol}_{start_date.replace('-', '')}_{end_date.replace('-', '')}.csv"
            df.to_csv(output_file, index=False)
            logger.debug(f"  保存: {output_file}")
        
        logger.info(f"✅ 项目17: 保存 {len(all_data)} 只股票数据")
        logger.info(f"   成功: {success_count}, 失败: {fail_count}")
        return True
    
    def run_full_update(self):
        """运行完整的数据更新"""
        logger.info("="*60)
        logger.info("⚡ 实时数据更新服务启动")
        logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # 测试网络连接
        self.network_available = self._test_network()
        if self.network_available:
            self.data_source = "网络+本地"
            logger.info("📡 数据源模式: 网络 + 本地")
        else:
            self.data_source = "仅本地"
            logger.info("📡 数据源模式: 仅本地 (离线模式)")
        
        start_time = time.time()
        
        # 更新项目88
        try:
            self.update_project88_watchlist()
        except Exception as e:
            logger.error(f"项目88更新失败: {e}")
        
        # 更新项目33
        try:
            self.update_project33_panic_data()
        except Exception as e:
            logger.error(f"项目33更新失败: {e}")
        
        # 更新项目17
        try:
            self.update_project17_data()
        except Exception as e:
            logger.error(f"项目17更新失败: {e}")
        
        elapsed = time.time() - start_time
        
        logger.info("="*60)
        logger.info(f"✅ 所有项目数据更新完成！")
        logger.info(f"⏱️ 总耗时: {elapsed:.2f} 秒")
        logger.info(f"📡 数据源: {self.data_source}")
        logger.info(f"📁 日志文件: {log_file}")
        logger.info("="*60)
    
    def run_continuous_update(self, interval_minutes=3):
        """启动持续更新服务"""
        logger.info("="*60)
        logger.info("⚡ 实时数据持续更新服务启动")
        logger.info(f"⏰ 刷新间隔: {interval_minutes} 分钟")
        logger.info("按 Ctrl+C 停止")
        logger.info("="*60)
        
        iteration = 0
        try:
            while True:
                iteration += 1
                logger.info("")
                logger.info("="*60)
                logger.info(f"🔄 第 {iteration} 次更新")
                logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("="*60)
                
                # 测试网络
                prev_network = self.network_available
                self.network_available = self._test_network()
                
                # 网络状态变化通知
                if prev_network != self.network_available:
                    if self.network_available:
                        logger.info("🔔 网络已恢复，切换到在线模式")
                    else:
                        logger.warning("🔔 网络已断开，切换到离线模式")
                
                # 更新数据
                try:
                    self.update_project88_watchlist()
                except Exception as e:
                    logger.error(f"项目88更新失败: {e}")
                
                try:
                    self.update_project33_panic_data()
                except Exception as e:
                    logger.error(f"项目33更新失败: {e}")
                
                logger.info(f"💤 等待 {interval_minutes} 分钟...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("="*60)
            logger.info("👋 实时数据更新服务已停止")
            logger.info(f"📊 共执行 {iteration} 次更新")
            logger.info("="*60)

def main():
    logger.info("程序启动")
    
    updater = RealTimeDataUpdater()
    
    print("\n请选择模式：")
    print("1. 单次更新所有项目数据")
    print("2. 启动实时更新服务(每3分钟)")
    
    choice = input("\n请输入选择 (1/2，默认1): ").strip() or "1"
    logger.info(f"用户选择: 模式{choice}")
    
    if choice == "2":
        updater.run_continuous_update()
    else:
        updater.run_full_update()

if __name__ == "__main__":
    main()