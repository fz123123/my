import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import json
import time
import struct

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
    URLLIB_AVAILABLE = True
except ImportError:
    URLLIB_AVAILABLE = False


class BaseStockAPI:
    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        raise NotImplementedError
    
    def get_realtime_price(self, symbol):
        raise NotImplementedError


class AkshareAPI(BaseStockAPI):
    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        try:
            if not AKSHARE_AVAILABLE:
                return None
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            df = ak.stock_zh_a_hist(symbol=symbol_code, period=period, 
                                   start_date=start_date, end_date=end_date,
                                   adjust="qfq")
            if not df.empty:
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                })
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                return df
        except Exception as e:
            print(f"AkshareAPI failed for {symbol}: {e}")
        return None

    def get_realtime_price(self, symbol):
        try:
            if not AKSHARE_AVAILABLE:
                return None
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            df = ak.stock_zh_a_spot()
            row = df[df['代码'] == symbol_code]
            if not row.empty:
                return float(row.iloc[0]['最新价'])
        except Exception as e:
            print(f"AkshareAPI realtime failed for {symbol}: {e}")
        return None


class EastmoneyAPI(BaseStockAPI):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/',
            'Accept': 'application/json, text/plain, */*'
        }

    def _request(self, url):
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
            elif URLLIB_AVAILABLE:
                req = Request(url, headers=self.headers)
                with urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"EastmoneyAPI request failed: {e}")
        return None

    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = '0' if symbol.endswith('.SZ') else '1'
            
            url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?" \
                  f"secid={market}.{symbol_code}&ut=fa5fd1943c7b386f172d6893dbfba10b&" \
                  f"fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&" \
                  f"klt={101 if period == 'daily' else 102}&fqt=1&" \
                  f"beg={start_date or '20200101'}&end={end_date or datetime.now().strftime('%Y%m%d')}"
            
            data = self._request(url)
            if data and data.get('data'):
                klines = data['data'].get('klines', [])
                if klines:
                    df = pd.DataFrame([k.split(',') for k in klines], 
                                     columns=['date', 'open', 'close', 'high', 'low', 'volume', 
                                              'amount', 'turnover', 'unknown1', 'unknown2', 'unknown3'])
                    df['date'] = pd.to_datetime(df['date'])
                    for col in ['open', 'close', 'high', 'low', 'volume', 'amount']:
                        df[col] = pd.to_numeric(df[col])
                    df = df.set_index('date').sort_index()
                    return df
        except Exception as e:
            print(f"EastmoneyAPI failed for {symbol}: {e}")
        return None

    def get_realtime_price(self, symbol):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = '0' if symbol.endswith('.SZ') else '1'
            
            url = f"http://push2.eastmoney.com/api/qt/stock/get?" \
                  f"secid={market}.{symbol_code}&fields=f57,f58,f43"
            
            data = self._request(url)
            if data and data.get('data'):
                return float(data['data'].get('f43', 0)) / 100
        except Exception as e:
            print(f"EastmoneyAPI realtime failed for {symbol}: {e}")
        return None


class SinaAPI(BaseStockAPI):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        }

    def _request(self, url):
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
            elif URLLIB_AVAILABLE:
                req = Request(url, headers=self.headers)
                with urlopen(req, timeout=10) as response:
                    return response.read().decode('gbk', errors='ignore')
        except Exception as e:
            print(f"SinaAPI request failed: {e}")
        return None

    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = 'sz' if symbol.endswith('.SZ') else 'sh'
            
            url = f"http://finance.sina.com.cn/stock/api/jsonp.php/var%20_{symbol_code}=" \
                  f"/CN_MarketData.getKLineData?symbol={market}{symbol_code}&scale={240 if period != 'daily' else 1}"
            
            data = self._request(url)
            if data:
                data = data.split('=')[1].strip().rstrip(';')
                data = json.loads(data)
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['day'])
                    df = df.rename(columns={
                        'open': 'open',
                        'close': 'close',
                        'high': 'high',
                        'low': 'low',
                        'volume': 'volume'
                    })
                    for col in ['open', 'close', 'high', 'low', 'volume']:
                        df[col] = pd.to_numeric(df[col])
                    df = df.set_index('date').sort_index()
                    return df
        except Exception as e:
            print(f"SinaAPI failed for {symbol}: {e}")
        return None

    def get_realtime_price(self, symbol):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = 'sz' if symbol.endswith('.SZ') else 'sh'
            
            url = f"http://hq.sinajs.cn/list={market}{symbol_code}"
            data = self._request(url)
            if data:
                parts = data.split(',')
                if len(parts) > 3:
                    return float(parts[3])
        except Exception as e:
            print(f"SinaAPI realtime failed for {symbol}: {e}")
        return None


class TencentAPI(BaseStockAPI):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stock.finance.qq.com/'
        }

    def _request(self, url):
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
            elif URLLIB_AVAILABLE:
                req = Request(url, headers=self.headers)
                with urlopen(req, timeout=10) as response:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"TencentAPI request failed: {e}")
        return None

    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = '1' if symbol.endswith('.SZ') else '0'
            
            url = f"https://qt.gtimg.cn/q={market}{symbol_code}"
            data = self._request(url)
            if data:
                parts = data.split('~')
                if len(parts) > 30:
                    df = pd.DataFrame({
                        'date': [datetime.now().strftime('%Y-%m-%d')],
                        'open': [float(parts[5])],
                        'close': [float(parts[3])],
                        'high': [float(parts[4])],
                        'low': [float(parts[6])],
                        'volume': [int(parts[36])]
                    })
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                    return df
        except Exception as e:
            print(f"TencentAPI failed for {symbol}: {e}")
        return None

    def get_realtime_price(self, symbol):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = '1' if symbol.endswith('.SZ') else '0'
            
            url = f"https://qt.gtimg.cn/q={market}{symbol_code}"
            data = self._request(url)
            if data:
                parts = data.split('~')
                if len(parts) > 3:
                    return float(parts[3])
        except Exception as e:
            print(f"TencentAPI realtime failed for {symbol}: {e}")
        return None


class HexunAPI(BaseStockAPI):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://stock.hexun.com/'
        }

    def _request(self, url):
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
            elif URLLIB_AVAILABLE:
                req = Request(url, headers=self.headers)
                with urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"HexunAPI request failed: {e}")
        return None

    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = '0' if symbol.endswith('.SZ') else '1'
            
            url = f"http://data.stock.hexun.com/zrb/AsynStockMain.aspx?stockcode={symbol_code}&market={market}&type=1"
            data = self._request(url)
            if data and 'Data' in data:
                df = pd.DataFrame(data['Data'])
                if not df.empty:
                    df['date'] = pd.to_datetime(df['time'])
                    df = df.rename(columns={
                        'open': 'open',
                        'close': 'close',
                        'high': 'high',
                        'low': 'low',
                        'volume': 'volume'
                    })
                    df = df.set_index('date').sort_index()
                    return df
        except Exception as e:
            print(f"HexunAPI failed for {symbol}: {e}")
        return None

    def get_realtime_price(self, symbol):
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            market = '0' if symbol.endswith('.SZ') else '1'
            
            url = f"http://data.stock.hexun.com/zrb/AsynStockMain.aspx?stockcode={symbol_code}&market={market}&type=1"
            data = self._request(url)
            if data and 'Data' in data and len(data['Data']) > 0:
                return float(data['Data'][0].get('close', 0))
        except Exception as e:
            print(f"HexunAPI realtime failed for {symbol}: {e}")
        return None


class RetryConfig:
    """重连配置"""
    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # 基础延迟（秒）
    MAX_DELAY = 10.0  # 最大延迟
    BACKOFF_FACTOR = 2.0  # 退避系数
    JITTER = True  # 添加随机抖动

class HealthMonitor:
    """数据源健康监控"""
    def __init__(self):
        self.success_count = {}
        self.fail_count = {}
        self.last_success_time = {}
        self.last_fail_time = {}
        self.total_requests = {}
        self.sources = ['AkshareAPI', 'TencentAPI', 'EastmoneyAPI', 'SinaAPI']
        
        for source in self.sources:
            self.success_count[source] = 0
            self.fail_count[source] = 0
            self.total_requests[source] = 0
    
    def record_success(self, source):
        """记录成功"""
        self.success_count[source] = self.success_count.get(source, 0) + 1
        self.total_requests[source] = self.total_requests.get(source, 0) + 1
        self.last_success_time[source] = datetime.now()
    
    def record_failure(self, source):
        """记录失败"""
        self.fail_count[source] = self.fail_count.get(source, 0) + 1
        self.total_requests[source] = self.total_requests.get(source, 0) + 1
        self.last_fail_time[source] = datetime.now()
    
    def get_health_score(self, source):
        """计算健康分数（0-100）"""
        total = self.total_requests.get(source, 0)
        if total == 0:
            return 50  # 默认中等分数
        
        success = self.success_count.get(source, 0)
        fail = self.fail_count.get(source, 0)
        
        # 基础成功率
        success_rate = success / total * 100
        
        # 时间衰减：最近失败影响更大
        time_penalty = 0
        if source in self.last_fail_time:
            time_since_fail = (datetime.now() - self.last_fail_time[source]).total_seconds()
            if time_since_fail < 300:  # 5分钟内
                time_penalty = 20 * (1 - time_since_fail / 300)
        
        score = max(0, min(100, success_rate - time_penalty))
        return score
    
    def get_best_source(self):
        """获取最健康的数据源"""
        scores = {source: self.get_health_score(source) for source in self.sources}
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def is_source_healthy(self, source, min_success_rate=30):
        """判断数据源是否健康"""
        total = self.total_requests.get(source, 0)
        if total < 3:  # 样本太少，认为健康
            return True
        return self.get_health_score(source) >= min_success_rate
    
    def print_stats(self):
        """打印统计信息"""
        print("\n=== 数据源健康状态 ===")
        print(f"{'数据源':<15} {'请求数':<10} {'成功':<10} {'失败':<10} {'健康分':<10} {'状态'}")
        print("-" * 70)
        for source in self.sources:
            total = self.total_requests.get(source, 0)
            success = self.success_count.get(source, 0)
            fail = self.fail_count.get(source, 0)
            score = self.get_health_score(source)
            status = "正常" if self.is_source_healthy(source) else "不稳定"
            print(f"{source:<15} {total:<10} {success:<10} {fail:<10} {score:<10.1f} {status}")


class SmartDataFetcher:
    """智能数据获取器 - 带自动重连和多源切换"""
    
    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode
        self.cache = {}
        self.health_monitor = HealthMonitor()
        self.retry_config = RetryConfig()
        self.preferred_source = None
        
        self.providers = {
            'AkshareAPI': AkshareAPI(),
            'TencentAPI': TencentAPI(),
            'EastmoneyAPI': EastmoneyAPI(),
            'SinaAPI': SinaAPI()
        }
        
        # 优先级排序（可根据健康状态动态调整）
        self.source_priority = ['TencentAPI', 'EastmoneyAPI', 'AkshareAPI', 'SinaAPI']
        
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'market_data.db')
        self.tdx_path = self._find_tdx_path()
        self.ths_path = self._find_ths_path()
    
    def _calculate_delay(self, attempt):
        """计算重连延迟（指数退避 + 抖动）"""
        delay = min(
            self.retry_config.BASE_DELAY * (self.retry_config.BACKOFF_FACTOR ** attempt),
            self.retry_config.MAX_DELAY
        )
        if self.retry_config.JITTER:
            import random
            delay = delay * (0.5 + random.random())
        return delay
    
    def _is_network_error(self, error):
        """判断是否为网络错误"""
        error_str = str(error).lower()
        network_errors = [
            'connection', 'timeout', 'network', 'remote', 
            'dns', 'socket', 'reset', 'refused'
        ]
        return any(e in error_str for e in network_errors)
    
    def get_stock_data_with_retry(self, symbol, period='daily', start_date=None, end_date=None, 
                                  force_source=None):
        """带重试的数据获取"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        cache_key = f"{symbol}_{period}_{start_date}_{end_date}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 优先尝试指定源或最健康源
        sources_to_try = []
        if force_source:
            sources_to_try = [force_source]
        elif self.preferred_source:
            sources_to_try = [self.preferred_source] + [s for s in self.source_priority if s != self.preferred_source]
        else:
            sources_to_try = self.source_priority.copy()
        
        # 按优先级尝试所有数据源
        for source_name in sources_to_try:
            if source_name not in self.providers:
                continue
            
            provider = self.providers[source_name]
            
            # 检查数据源健康状态
            if not self.health_monitor.is_source_healthy(source_name):
                print(f"跳过不健康的数据源: {source_name}")
                continue
            
            # 指数退避重试
            for attempt in range(self.retry_config.MAX_RETRIES):
                try:
                    df = provider.get_stock_data(symbol, period, start_date, end_date)
                    if df is not None and not df.empty:
                        self.health_monitor.record_success(source_name)
                        self.preferred_source = source_name
                        print(f"[{source_name}] 成功获取 {symbol}")
                        self.cache[cache_key] = df
                        return df
                except Exception as e:
                    if self._is_network_error(e):
                        delay = self._calculate_delay(attempt)
                        print(f"[{source_name}] 网络错误，{delay:.1f}秒后重试 ({attempt+1}/{self.retry_config.MAX_RETRIES})")
                        time.sleep(delay)
                    else:
                        print(f"[{source_name}] 错误: {e}")
                        break
            
            # 记录失败
            self.health_monitor.record_failure(source_name)
        
        # 所有源都失败，尝试本地数据
        df = self._try_local_sources(symbol)
        if df is not None:
            return df
        
        # 严格模式返回None
        if self.strict_mode:
            print(f"[严格模式] 所有数据源不可用: {symbol}")
            return None
        
        # 返回模拟数据
        print(f"使用模拟数据: {symbol}")
        return self._get_mock_data(symbol, start_date, end_date)
    
    def get_realtime_price_smart(self, symbol):
        """智能获取实时价格"""
        # 优先尝试首选源
        sources_to_try = []
        if self.preferred_source:
            sources_to_try = [self.preferred_source] + [s for s in self.source_priority if s != self.preferred_source]
        else:
            # 按健康度排序
            sorted_sources = sorted(self.source_priority, 
                                   key=lambda s: self.health_monitor.get_health_score(s), 
                                   reverse=True)
            sources_to_try = sorted_sources
        
        for source_name in sources_to_try:
            if source_name not in self.providers:
                continue
            
            provider = self.providers[source_name]
            
            for attempt in range(self.retry_config.MAX_RETRIES):
                try:
                    price = provider.get_realtime_price(symbol)
                    if price is not None and price > 0:
                        self.health_monitor.record_success(source_name)
                        self.preferred_source = source_name
                        return price
                except Exception as e:
                    if self._is_network_error(e):
                        delay = self._calculate_delay(attempt)
                        time.sleep(delay)
                    else:
                        break
            
            self.health_monitor.record_failure(source_name)
        
        return None
    
    def _try_local_sources(self, symbol):
        """尝试本地数据源"""
        # 通达信
        df = self._load_from_tdx(symbol)
        if df is not None and len(df) >= 60:
            print(f"使用通达信本地数据: {symbol}")
            return df
        
        # 同花顺远航版
        df = self._load_from_ths_yuanhang(symbol)
        if df is not None and len(df) >= 60:
            return df
        
        # 同花顺
        df = self._load_from_ths(symbol)
        if df is not None and len(df) >= 60:
            return df
        
        # 数据库
        df = self._load_from_db(symbol)
        if df is not None and len(df) >= 60:
            print(f"使用本地数据库: {symbol}")
            return df
        
        return None
    
    def parallel_probe_sources(self, symbols):
        """并行探测所有数据源，获取最佳源"""
        print("\n=== 正在探测数据源健康状态 ===")
        test_symbol = '600519.SH'
        
        for source_name, provider in self.providers.items():
            try:
                price = provider.get_realtime_price(test_symbol)
                if price and price > 0:
                    self.health_monitor.record_success(source_name)
                    print(f"[{source_name}] 探测成功: {price}")
                else:
                    self.health_monitor.record_failure(source_name)
                    print(f"[{source_name}] 探测失败")
            except Exception as e:
                self.health_monitor.record_failure(source_name)
                print(f"[{source_name}] 错误: {e}")
        
        # 更新优先级
        best_source = self.health_monitor.get_best_source()
        self.preferred_source = best_source
        print(f"\n推荐使用的数据源: {best_source}")
        
        self.health_monitor.print_stats()
        return best_source
    
    # 保留原有方法的便捷包装
    def get_stock_data(self, symbol, period='daily', start_date=None, end_date=None):
        """兼容原有接口"""
        return self.get_stock_data_with_retry(symbol, period, start_date, end_date)
    
    def get_realtime_price(self, symbol):
        """兼容原有接口"""
        return self.get_realtime_price_smart(symbol)
    
    def _find_ths_path(self):
        possible_paths = [
            r"C:\同花顺软件\同花顺",
            r"D:\同花顺软件\同花顺",
            r"C:\同花顺远航版\transaction",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _find_ths_yuanhang_path(self):
        path = r"C:\同花顺远航版\transaction"
        if os.path.exists(path):
            return path
        return None

    def _load_from_ths_yuanhang(self, symbol):
        ths_yh_path = self._find_ths_yuanhang_path()
        if not ths_yh_path:
            return None
        
        parts = symbol.split('.')
        if len(parts) != 2:
            return None
        
        code = parts[0]
        market = parts[1]
        
        day_path = os.path.join(ths_yh_path, "data", f"{code}.day")
        if os.path.exists(day_path):
            df = self._read_tdx_day_file(day_path)
            if df is not None and len(df) > 0:
                df['source'] = 'ths_yuanhang'
                print(f"从同花顺远航版获取数据: {symbol}")
                return df
        
        return None

    def _load_from_ths(self, symbol):
        if not self.ths_path:
            return None
        parts = symbol.split('.')
        if len(parts) != 2:
            return None
        code = parts[0]
        market = parts[1]
        if market == 'SH':
            day_path = os.path.join(self.ths_path, 'history', 'shase', 'day', f'{code}.day')
        elif market == 'SZ':
            day_path = os.path.join(self.ths_path, 'history', 'sznse', 'day', f'{code}.day')
        else:
            return None
        if os.path.exists(day_path):
            df = self._read_tdx_day_file(day_path)
            if df is not None and len(df) > 0:
                df['source'] = 'ths'
                print(f"从同花顺获取数据: {symbol}")
                return df
        return None

    def _find_tdx_path(self):
        possible_paths = [
            r"C:\new_tdx",
            r"D:\new_tdx",
            r"C:\tdx",
            r"D:\tdx",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _read_tdx_day_file(self, file_path):
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
            df = pd.DataFrame({
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'volume': volumes
            })
            df = df[(df['open'] > 0) & (df['close'] > 0)]
            df['date'] = pd.to_datetime(dates[:len(df)], format='%Y%m%d')
            df = df.set_index('date').sort_index()
            df['source'] = 'tdx'
            return df
        except Exception as e:
            return None

    def _load_from_tdx(self, symbol):
        if not self.tdx_path:
            return None
        parts = symbol.split('.')
        if len(parts) != 2:
            return None
        code = parts[0]
        market = parts[1]
        if market == 'SH':
            day_path = os.path.join(self.tdx_path, 'vipdoc', 'sh', 'lday', f'sh{code}.day')
        elif market == 'SZ':
            day_path = os.path.join(self.tdx_path, 'vipdoc', 'sz', 'lday', f'sz{code}.day')
        else:
            return None
        if os.path.exists(day_path):
            df = self._read_tdx_day_file(day_path)
            if df is not None and len(df) > 0:
                print(f"从通达信获取数据: {symbol}")
                return df
        return None

    def _load_from_db(self, symbol, limit=365):
        """从本地数据库加载数据"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            query = "SELECT * FROM stock_daily WHERE symbol = ? ORDER BY date DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=[symbol, limit])
            conn.close()
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                return df
        except Exception as e:
            pass
        return None

    def get_crypto_data(self, symbol, interval='1d', limit=365):
        """获取加密货币数据"""
        cache_key = f"{symbol}_{interval}_{limit}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            if REQUESTS_AVAILABLE:
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                        'taker_buy_quote', 'ignore'
                    ])
                    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df = df.set_index('date')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col])
                    df = df.sort_index()
                    self.cache[cache_key] = df
                    return df
        except Exception as e:
            print(f"Failed to fetch {symbol} crypto data: {e}")

        if self.strict_mode:
            print(f"[STRICT MODE] No real data available for {symbol}, skipping")
            return None
        return self._get_mock_data(symbol)

    def _get_mock_data(self, symbol, start_date=None, end_date=None):
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365))
        else:
            start_date = datetime.strptime(start_date, '%Y%m%d')
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y%m%d')

        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(hash(symbol) % 10000)

        base_price = self._get_base_price(symbol)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = base_price * (1 + returns).cumprod()

        df = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
            'high': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
            'low': prices * (1 - np.random.uniform(0, 0.02, len(dates))),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)

        return df

    def _get_base_price(self, symbol):
        price_map = {
            '600519.SH': 1600, '000858.SZ': 160, '601318.SH': 48, '600036.SH': 35,
            '300750.SZ': 200, '002594.SZ': 160, '688981.SH': 55, '002371.SZ': 330,
            '601012.SH': 28, '603501.SH': 130, '000001.SZ': 12, '000002.SZ': 8,
            '002415.SZ': 25, '000333.SZ': 55, '600030.SH': 20, '002222.SZ': 13,
            '002079.SZ': 11, '603688.SH': 160, '002229.SZ': 14, '000977.SZ': 45,
            '002217.SZ': 3.5, '002361.SZ': 20, '002291.SZ': 6, '605399.SH': 14,
            '600152.SH': 14, '002602.SZ': 15, '603618.SH': 40, '600584.SH': 55,
            '002363.SZ': 8, '601985.SH': 9, '605298.SH': 25, '002553.SZ': 22,
            '601088.SH': 45, '002565.SZ': 5, '603890.SH': 20, '603933.SH': 26,
            '600130.SH': 6, '601138.SH': 64, '301275.SZ': 48, '603118.SH': 16,
            '603660.SH': 14, '603778.SH': 25, '603681.SH': 21, '603045.SH': 74,
            '001339.SZ': 104, '002276.SZ': 14, '603738.SH': 54, '002918.SZ': 14,
            '603007.SH': 8, '600530.SZ': 7, '600076.SH': 4, '600736.SH': 10,
            '601991.SH': 7, '600685.SH': 9, '002491.SZ': 25, '002655.SZ': 10,
            '605289.SH': 73
        }
        return price_map.get(symbol, 100)

    def clear_cache(self):
        self.cache = {}
