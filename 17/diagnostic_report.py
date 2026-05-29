import pandas as pd
import numpy as np
import os
from datetime import datetime


def create_diagnostic_report():
    print("=" * 70)
    print("量化交易系统完整诊断报告")
    print("=" * 70)
    
    report = []
    report.append("\n生成时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    report.append("=" * 70)
    
    report.append("\n1. 系统环境信息")
    report.append("-" * 50)
    report.append(f"Python版本: {os.sys.version}")
    report.append(f"工作目录: {os.getcwd()}")
    report.append(f"虚拟环境: {'是' if hasattr(os, 'sys') and 'venv' in os.environ.get('VIRTUAL_ENV', '') else '否'}")
    
    report.append("\n2. 已安装的数据获取库")
    report.append("-" * 50)
    
    data_sources = {
        'yfinance': '1.3.0',
        'akshare': '1.18.60',
        'baostock': '0.9.1',
        'tushare': '1.4.29',
        'pandas_datareader': '0.10.0'
    }
    
    for lib, version in data_sources.items():
        try:
            module = __import__(lib.replace('-', '_'))
            actual_version = getattr(module, '__version__', version)
            report.append(f"✓ {lib:20s} 版本: {actual_version}")
        except ImportError:
            report.append(f"✗ {lib:20s} 未安装")
        except Exception as e:
            report.append(f"? {lib:20s} 检查失败: {str(e)}")
    
    report.append("\n3. 数据源对比分析")
    report.append("-" * 50)
    
    report.append("\n   数据源对比:")
    report.append("   " + "-" * 66)
    report.append("   | 数据源         | 优点                     | 缺点                     |")
    report.append("   |" + "-" * 18 + "+" + "-" * 25 + "+" + "-" * 25 + "|")
    report.append("   | yfinance       | 美股数据全面，免费        | 有速率限制，可能被封      |")
    report.append("   | akshare        | 中文A股数据，无需API      | 数据质量不稳定            |")
    report.append("   | baostock       | A股数据，免费稳定         | 数据字段有限             |")
    report.append("   | tushare        | 数据全面，质量高          | 需要注册API Token        |")
    report.append("   |" + "-" * 18 + "+" + "-" * 25 + "+" + "-" * 25 + "|")
    
    report.append("\n4. 当前数据获取代码分析")
    report.append("-" * 50)
    
    try:
        with open('data_fetcher.py', 'r', encoding='utf-8') as f:
            fetcher_code = f.read()
            report.append("✓ data_fetcher.py 存在")
            report.append(f"  代码长度: {len(fetcher_code)} 字符")
            
            if 'yfinance' in fetcher_code:
                report.append("  ✓ 使用 yfinance 获取数据")
            if 'akshare' in fetcher_code:
                report.append("  ✓ 使用 akshare 获取数据")
            if 'baostock' in fetcher_code:
                report.append("  ✓ 使用 baostock 获取数据")
    except Exception as e:
        report.append(f"✗ 读取 data_fetcher.py 失败: {e}")
    
    report.append("\n5. 日志文件分析")
    report.append("-" * 50)
    
    try:
        with open('backtest.log', 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
            report.append(f"✓ backtest.log 存在")
            report.append(f"  总行数: {len(log_lines)}")
            
            error_lines = [line for line in log_lines if 'ERROR' in line]
            warning_lines = [line for line in log_lines if 'WARNING' in line]
            
            report.append(f"  错误记录: {len(error_lines)} 条")
            report.append(f"  警告记录: {len(warning_lines)} 条")
            
            if error_lines:
                report.append("\n  错误详情:")
                for line in error_lines[:5]:
                    report.append(f"    - {line.strip()}")
    except Exception as e:
        report.append(f"✗ 读取 backtest.log 失败: {e}")
    
    report.append("\n6. 配置文件建议")
    report.append("-" * 50)
    
    config_template = """# 数据源配置文件 (config.py)
class DataSourceConfig:
    # 当前使用的数据源
    CURRENT_SOURCE = "yfinance"
    
    # 各数据源配置
    SOURCES = {
        "yfinance": {
            "enabled": True,
            "rate_limit_wait": 60,  # 速率限制等待时间（秒）
            "retry_times": 3,
            "timeout": 30,
        },
        "akshare": {
            "enabled": True,
            "use_cache": True,
            "cache_duration": 300,  # 缓存时间（秒）
        },
        "baostock": {
            "enabled": True,
            "use_cache": True,
        },
        "tushare": {
            "enabled": True,
            "token": "YOUR_TUSHARE_TOKEN",  # 需要替换
        }
    }
    
    # 数据质量阈值
    QUALITY_THRESHOLDS = {
        "max_price_diff_pct": 1.0,  # 最大价格差异百分比
        "max_volume_diff_pct": 5.0,  # 最大成交量差异百分比
        "min_data_points": 100,       # 最少数据点数
    }
"""
    
    report.append("\n建议创建配置文件管理数据源:")
    report.append(config_template)
    
    report.append("\n7. 改进建议")
    report.append("-" * 50)
    report.append("""
   1. 数据源切换方案:
      - 实现多数据源自动切换机制
      - 主数据源失败时自动切换到备用数据源
      - 添加数据源健康检查

   2. 缓存策略:
      - 实现本地缓存避免重复请求
      - 设置合理的缓存过期时间
      - 定期清理过期缓存

   3. 错误处理:
      - 实现重试机制
      - 添加详细的错误日志
      - 记录失败的数据源和原因

   4. 数据验证:
      - 与多个数据源交叉验证
      - 设置数据质量阈值报警
      - 自动检测异常数据

   5. 网络优化:
      - 使用代理池（如需要）
      - 优化请求频率
      - 实现连接池复用
""")
    
    report.append("\n" + "=" * 70)
    report.append("诊断完成")
    report.append("=" * 70)
    
    report_text = "\n".join(report)
    
    with open('diagnostic_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(report_text)
    
    print("\n✓ 完整报告已保存到: diagnostic_report.txt")
    
    return report_text


def create_multi_source_fetcher():
    config_code = '''# config.py - 数据源配置
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
        print(f"\\n成功获取数据: {len(data)} 行")
        print(data.head())
    except Exception as e:
        print(f"\\n获取失败: {e}")
    
    print("\\n获取日志:")
    for log in fetcher.fetch_log:
        print(log)
'''
    
    with open('multi_source_fetcher.py', 'w', encoding='utf-8') as f:
        f.write(config_code)
    
    print("✓ 已创建多数据源获取器: multi_source_fetcher.py")


if __name__ == "__main__":
    create_diagnostic_report()
    create_multi_source_fetcher()
