import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def test_akshare():
    """测试akshare数据源"""
    print("\n测试 akshare 数据源...")
    try:
        import akshare as ak
        
        stock_code = "AAPL"  # 美股代码
        print(f"  尝试获取 {stock_code} 的历史数据...")
        
        # akshare获取美股历史数据
        df = ak.stock_us_hist(symbol=stock_code, period="daily", 
                              start_date="20200101", end_date="20200601", adjust="qfq")
        
        if df is not None and not df.empty:
            print(f"  ✓ akshare 成功获取 {len(df)} 行数据")
            print(f"  列名: {list(df.columns)}")
            print(f"  前3行:")
            print(df.head(3))
            return df
        else:
            print(f"  ✗ akshare 返回空数据")
            return None
            
    except ImportError:
        print("  ✗ akshare 未安装")
        return None
    except Exception as e:
        print(f"  ✗ akshare 获取失败: {e}")
        return None


def test_baostock():
    """测试baostock数据源"""
    print("\n测试 baostock 数据源...")
    try:
        import baostock as bs
        
        stock_code = "AAPL"  # baostock使用完整代码
        print(f"  尝试获取 {stock_code} 的历史数据...")
        
        bs.login()
        
        rs = bs.query_history_k_data_plus(
            stock_code,
            "date,open,high,low,close,volume,turn",
            start_date='2020-01-01',
            end_date='2020-06-01',
            frequency="d",
            adjustflag="3"  # 不复权
        )
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        bs.logout()
        
        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            print(f"  ✓ baostock 成功获取 {len(df)} 行数据")
            print(f"  前3行:")
            print(df.head(3))
            return df
        else:
            print(f"  ✗ baostock 返回空数据")
            return None
            
    except ImportError:
        print("  ✗ baostock 未安装")
        return None
    except Exception as e:
        print(f"  ✗ baostock 获取失败: {e}")
        return None


def test_yfinance():
    """测试yfinance数据源（带重试）"""
    print("\n测试 yfinance 数据源（带重试机制）...")
    try:
        import yfinance as yf
        
        stock_code = "AAPL"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"  第 {attempt + 1} 次尝试获取 {stock_code}...")
                
                data = yf.download(
                    stock_code, 
                    start='2020-01-01', 
                    end='2020-06-01',
                    auto_adjust=True,
                    timeout=30
                )
                
                if data is not None and not data.empty:
                    data = data.round(2)
                    data['symbol'] = stock_code
                    data.reset_index(inplace=True)
                    
                    print(f"  ✓ yfinance 成功获取 {len(data)} 行数据")
                    print(f"  前3行:")
                    print(data.head(3))
                    return data
                else:
                    print(f"  第 {attempt + 1} 次返回空数据")
                    
            except Exception as e:
                print(f"  第 {attempt + 1} 次失败: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30
                    print(f"  等待 {wait_time} 秒后重试...")
                    import time
                    time.sleep(wait_time)
        
        print(f"  ✗ yfinance 所有尝试均失败")
        return None
        
    except ImportError:
        print("  ✗ yfinance 未安装")
        return None


def compare_data_sources():
    """对比不同数据源的数据"""
    print("=" * 70)
    print("多数据源对比测试")
    print("=" * 70)
    
    results = {}
    
    # 测试各数据源
    results['yfinance'] = test_yfinance()
    results['akshare'] = test_akshare()
    results['baostock'] = test_baostock()
    
    print("\n" + "=" * 70)
    print("数据源对比结果")
    print("=" * 70)
    
    for source, data in results.items():
        if data is not None and not data.empty:
            print(f"\n{source}:")
            print(f"  行数: {len(data)}")
            if 'Close' in data.columns:
                print(f"  平均收盘价: ${data['Close'].mean():.2f}")
            print(f"  数据质量: 正常")
        else:
            print(f"\n{source}:")
            print(f"  数据获取: 失败")
    
    # 建议使用的数据源
    print("\n" + "=" * 70)
    print("数据源使用建议")
    print("=" * 70)
    print("""
   1. 美股数据:
      • 首选: yfinance（数据全面，但可能有速率限制）
      • 备选: akshare（美股数据较少）
      
   2. A股数据:
      • 首选: baostock（免费稳定）
      • 备选: akshare（数据丰富）
      • 高质量: tushare（需要API Token）
      
   3. 数据验证:
      • 建议与同花顺/东方财富数据对比
      • 检查价格和成交量的合理性
      • 验证数据的时间连续性
    """)
    
    return results


if __name__ == "__main__":
    compare_data_sources()
