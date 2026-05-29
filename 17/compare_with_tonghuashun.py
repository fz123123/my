import pandas as pd
import numpy as np
from data_fetcher import DataFetcher
from data_cleaner import DataCleaner


def compare_tonghuashun_data():
    print("=" * 70)
    print("同花顺数据对比分析")
    print("=" * 70)
    
    print("\n1. 读取同花顺导出的数据...")
    print("-" * 50)
    
    try:
        ths_data = pd.read_csv("trading_software_data.csv", parse_dates=['Date'])
        print(f"✓ 成功读取 {len(ths_data)} 行数据")
        print(f"  日期范围: {ths_data['Date'].min().date()} 至 {ths_data['Date'].max().date()}")
        print(f"  股票代码: {ths_data['symbol'].iloc[0] if 'symbol' in ths_data.columns else 'N/A'}")
        print(f"  列名: {list(ths_data.columns)}")
    except Exception as e:
        print(f"✗ 读取失败: {e}")
        return
    
    print("\n2. 尝试从yfinance获取数据...")
    print("-" * 50)
    
    fetcher = DataFetcher()
    cleaner = DataCleaner()
    
    symbol = ths_data['symbol'].iloc[0] if 'symbol' in ths_data.columns else 'AAPL'
    start_date = ths_data['Date'].min().strftime('%Y-%m-%d')
    end_date = (ths_data['Date'].max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        yf_data = fetcher.fetch_stock_data(symbol, start_date, end_date)
        yf_cleaned = cleaner.clean_data(yf_data)
        print(f"✓ yfinance 数据获取成功: {len(yf_cleaned)} 行")
        yf_available = True
    except Exception as e:
        print(f"✗ yfinance 获取失败: {e}")
        print("  将使用模拟数据进行对比演示")
        yf_available = False
        yf_cleaned = None
    
    print("\n3. 同花顺数据统计分析...")
    print("-" * 50)
    
    print(f"  总交易日数: {len(ths_data)}")
    print(f"  平均收盘价: ${ths_data['Close'].mean():.2f}")
    print(f"  收盘价范围: ${ths_data['Close'].min():.2f} - ${ths_data['Close'].max():.2f}")
    print(f"  平均成交量: {ths_data['Volume'].mean():,.0f}")
    print(f"  成交量范围: {ths_data['Volume'].min():,.0f} - {ths_data['Volume'].max():,.0f}")
    
    ths_data_sorted = ths_data.sort_values('Date')
    total_return = (ths_data_sorted['Close'].iloc[-1] / ths_data_sorted['Close'].iloc[0] - 1) * 100
    volatility = ths_data_sorted['Close'].pct_change().std() * 100
    
    print(f"  总收益率: {total_return:.2f}%")
    print(f"  日波动率: {volatility:.2f}%")
    
    print("\n4. 数据质量检查...")
    print("-" * 50)
    
    issues = []
    
    if (ths_data['High'] < ths_data['Low']).any():
        issues.append("存在 High < Low 的异常数据")
    
    if (ths_data['Open'] < ths_data['Low']).any():
        issues.append("存在 Open < Low 的异常数据")
    
    if (ths_data['Open'] > ths_data['High']).any():
        issues.append("存在 Open > High 的异常数据")
    
    if (ths_data['Close'] < ths_data['Low']).any():
        issues.append("存在 Close < Low 的异常数据")
    
    if (ths_data['Close'] > ths_data['High']).any():
        issues.append("存在 Close > High 的异常数据")
    
    if (ths_data['Volume'] < 0).any():
        issues.append("存在负成交量")
    
    missing_count = ths_data[['Open', 'High', 'Low', 'Close', 'Volume']].isna().sum().sum()
    if missing_count > 0:
        issues.append(f"存在 {missing_count} 个缺失值")
    
    if issues:
        print("  ⚠️ 发现以下问题:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✓ 数据质量良好，未发现明显问题")
    
    if yf_available and yf_cleaned is not None:
        print("\n5. 与yfinance数据对比...")
        print("-" * 50)
        
        merged = pd.merge(
            ths_data[['Date', 'Close', 'Volume']].rename(columns={'Close': 'THS_Close', 'Volume': 'THS_Volume'}),
            yf_cleaned[['Date', 'Close', 'Volume']].rename(columns={'Close': 'YF_Close', 'Volume': 'YF_Volume'}),
            on='Date',
            how='inner'
        )
        
        if len(merged) > 0:
            merged['Price_Diff'] = merged['YF_Close'] - merged['THS_Close']
            merged['Price_Diff_Pct'] = (merged['YF_Close'] - merged['THS_Close']) / merged['THS_Close'] * 100
            merged['Volume_Diff_Pct'] = (merged['YF_Volume'] - merged['THS_Volume']) / merged['THS_Volume'] * 100
            
            print(f"  匹配交易日数: {len(merged)}")
            print(f"  价格差异统计:")
            print(f"    平均差异: ${merged['Price_Diff'].mean():.2f}")
            print(f"    最大差异: ${merged['Price_Diff'].abs().max():.2f}")
            print(f"    平均差异百分比: {merged['Price_Diff_Pct'].abs().mean():.2f}%")
            print(f"  成交量差异统计:")
            print(f"    平均差异百分比: {merged['Volume_Diff_Pct'].abs().mean():.2f}%")
            print(f"    最大差异百分比: {merged['Volume_Diff_Pct'].abs().max():.2f}%")
            
            significant_diff = merged[merged['Price_Diff_Pct'].abs() > 1.0]
            if len(significant_diff) > 0:
                print(f"\n  显著价格差异 (>1%): {len(significant_diff)} 天")
                print("  日期          同花顺    yfinance   差异")
                print("  " + "-" * 45)
                for _, row in significant_diff.head(10).iterrows():
                    print(f"  {row['Date'].date()}  ${row['THS_Close']:.2f}   ${row['YF_Close']:.2f}   {row['Price_Diff_Pct']:+.2f}%")
        else:
            print("  ⚠️ 无匹配日期进行对比")
    
    print("\n6. 与同花顺软件的差异可能原因...")
    print("-" * 50)
    print("  • 除权复权方式不同（前复权/后复权/不复权）")
    print("  • 数据更新频率和时间点差异")
    print("  • 成交量的统计口径差异")
    print("  • 时区处理方式不同")
    print("  • 数据源的品质和完整性差异")
    print("  • 股票代码标识方式不同（如沪深A股代码格式）")
    
    print("\n" + "=" * 70)
    print("对比分析完成")
    print("=" * 70)
    
    return ths_data


if __name__ == "__main__":
    compare_tonghuashun_data()
