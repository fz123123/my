# config.py - 数据源配置
class DataSourceConfig:
    """数据源配置类"""
    
    # 默认数据源优先级
    SOURCE_PRIORITY = ["yfinance", "akshare", "baostock"]
    
    # 各数据源配置
    SOURCES = {
        "yfinance": {
            "enabled": True,
            "rate_limit_wait": 60,
            "retry_times": 3,
            "timeout": 30,
            "description": "Yahoo Finance - 美股数据"
        },
        "akshare": {
            "enabled": True,
            "use_cache": True,
            "cache_duration": 300,
            "description": "AKShare - 中文A股数据"
        },
        "baostock": {
            "enabled": True,
            "use_cache": True,
            "description": "Baostock - A股免费数据"
        }
    }
    
    # 数据质量阈值
    QUALITY_THRESHOLDS = {
        "max_price_diff_pct": 1.0,
        "max_volume_diff_pct": 5.0,
        "min_data_points": 100,
    }


# multi_source_fetcher.py - 多数据源获取器
import pandas as pd
import time
from datetime import datetime


class MultiSourceDataFetcher:
    """多数据源数据获取器"""
    
    def __init__(self, config=None):
        self.config = config or DataSourceConfig()
        self.fetch_log = []
    
    def fetch_with_fallback(self, symbol, start_date, end_date):
        """使用备用机制获取数据"""
        
        for source in self.config.SOURCE_PRIORITY:
            source_config = self.config.SOURCES.get(source, {})
            
            if not source_config.get("enabled", False):
                continue
            
            try:
                self.log(f"尝试从 {source} 获取数据...")
                data = self._fetch_from_source(source, symbol, start_date, end_date)
                
                if self._validate_data(data):
                    self.log(f"✓ 成功从 {source} 获取数据: {len(data)} 行")
                    return data
                else:
                    self.log(f"✗ {source} 数据验证失败")
                    
            except Exception as e:
                self.log(f"✗ {source} 获取失败: {str(e)}")
                
                if source_config.get("rate_limit_wait"):
                    wait_time = source_config["rate_limit_wait"]
                    self.log(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        raise RuntimeError("所有数据源都获取失败")
    
    def _fetch_from_source(self, source, symbol, start_date, end_date):
        """从指定数据源获取数据"""
        
        if source == "yfinance":
            return self._fetch_yfinance(symbol, start_date, end_date)
        elif source == "akshare":
            return self._fetch_akshare(symbol, start_date, end_date)
        elif source == "baostock":
            return self._fetch_baostock(symbol, start_date, end_date)
        else:
            raise ValueError(f"未知数据源: {source}")
    
    def _fetch_yfinance(self, symbol, start_date, end_date):
        """从yfinance获取数据"""
        import yfinance as yf
        data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)
        data = data.round(2)
        data['symbol'] = symbol
        data.reset_index(inplace=True)
        return data
    
    def _fetch_akshare(self, symbol, start_date, end_date):
        """从akshare获取数据"""
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date.replace('-', ''), 
                                end_date=end_date.replace('-', ''), adjust="qfq")
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude']
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df['Date'] = pd.to_datetime(df['Date'])
        df['symbol'] = symbol
        return df
    
    def _fetch_baostock(self, symbol, start_date, end_date):
        """从baostock获取数据"""
        import baostock as bs
        bs.login()
        rs = bs.query_history_k_data_plus(
            symbol,
            "date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d"
        )
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        bs.logout()
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        df['Open'] = df['open'].astype(float)
        df['High'] = df['high'].astype(float)
        df['Low'] = df['low'].astype(float)
        df['Close'] = df['close'].astype(float)
        df['Volume'] = df['volume'].astype(float)
        df['Date'] = pd.to_datetime(df['date'])
        df['symbol'] = symbol
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'symbol']]
    
    def _validate_data(self, data):
        """验证数据质量"""
        if data is None or data.empty:
            return False
        
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            return False
        
        if len(data) < self.config.QUALITY_THRESHOLDS["min_data_points"]:
            return False
        
        return True
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.fetch_log.append(log_entry)
        print(log_entry)


if __name__ == "__main__":
    fetcher = MultiSourceDataFetcher()
    try:
        data = fetcher.fetch_with_fallback("AAPL", "2020-01-01", "2020-06-01")
        print(f"\n成功获取数据: {len(data)} 行")
        print(data.head())
    except Exception as e:
        print(f"\n获取失败: {e}")
    
    print("\n获取日志:")
    for log in fetcher.fetch_log:
        print(log)
