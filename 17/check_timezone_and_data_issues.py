import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from data_fetcher import DataFetcher
from data_cleaner import DataCleaner


def check_timezone_issues():
    print("=" * 60)
    print("TIMEZONE AND DATA PROCESSING CHECK")
    print("=" * 60)
    
    print("\n1. Current system timezone:")
    print("-" * 30)
    try:
        local_tz = datetime.now().astimezone().tzinfo
        print(f"Local timezone: {local_tz}")
        print(f"UTC offset: {datetime.now().astimezone().utcoffset()}")
    except Exception as e:
        print(f"Error getting timezone: {e}")
    
    print("\n2. Common stock market timezones:")
    print("-" * 30)
    timezones = {
        'NYSE': 'America/New_York',
        'NASDAQ': 'America/New_York',
        'Shanghai': 'Asia/Shanghai',
        'Tokyo': 'Asia/Tokyo',
        'London': 'Europe/London'
    }
    
    for market, tz_name in timezones.items():
        try:
            tz = pytz.timezone(tz_name)
            now_in_tz = datetime.now(tz)
            print(f"{market}: {tz_name} -> {now_in_tz.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        except Exception as e:
            print(f"{market}: {tz_name} -> Error: {e}")


def analyze_data_algorithms():
    print("\n" + "=" * 60)
    print("DATA PROCESSING ALGORITHM ANALYSIS")
    print("=" * 60)
    
    print("\n3. Data cleaning algorithm analysis:")
    print("-" * 30)
    
    algorithms = [
        {
            'name': 'Duplicate Removal',
            'method': 'drop_duplicates(subset=["Date"], keep="first")',
            'description': 'Removes rows with duplicate dates, keeping the first occurrence'
        },
        {
            'name': 'Missing Value Handling',
            'method': 'dropna(subset=["Open", "High", "Low", "Close", "Volume"])',
            'description': 'Drops rows with any missing price or volume data'
        },
        {
            'name': 'Price Logic Validation',
            'method': 'High >= Open/Close >= Low checks',
            'description': 'Validates that prices follow logical ordering'
        },
        {
            'name': 'Volume Validation',
            'method': 'Volume >= 0 check',
            'description': 'Removes rows with negative or missing volume'
        },
        {
            'name': 'Missing Dates',
            'method': 'reindex with freq="B", ffill for prices',
            'description': 'Fills missing business days using forward fill'
        },
        {
            'name': 'Outlier Detection',
            'method': 'Z-score (threshold=3.0) or IQR method',
            'description': 'Identifies and removes price outliers based on daily returns'
        },
        {
            'name': 'Date Continuity',
            'method': 'Check for gaps > 3 business days',
            'description': 'Detects significant gaps in the date sequence'
        }
    ]
    
    for algo in algorithms:
        print(f"\n• {algo['name']}:")
        print(f"  Method: {algo['method']}")
        print(f"  Description: {algo['description']}")


def test_timezone_handling():
    print("\n" + "=" * 60)
    print("TIMEZONE HANDLING TEST")
    print("=" * 60)
    
    print("\n4. Testing timezone conversion scenarios:")
    print("-" * 30)
    
    test_dates = [
        '2020-01-01',
        '2020-06-15', 
        '2020-12-25'
    ]
    
    for date_str in test_dates:
        naive_date = pd.to_datetime(date_str)
        utc_date = naive_date.tz_localize('UTC')
        ny_date = utc_date.tz_convert('America/New_York')
        sh_date = utc_date.tz_convert('Asia/Shanghai')
        
        print(f"\nOriginal: {date_str}")
        print(f"Naive datetime: {naive_date} (tz-naive)")
        print(f"UTC: {utc_date}")
        print(f"New York: {ny_date}")
        print(f"Shanghai: {sh_date}")


def test_data_quality():
    print("\n" + "=" * 60)
    print("DATA QUALITY CHECK")
    print("=" * 60)
    
    print("\n5. Creating test data with various issues:")
    print("-" * 30)
    
    dates = pd.date_range(start='2020-01-01', periods=50, freq='B')
    
    base_price = 100.0
    prices = []
    for i in range(50):
        base_price *= (1 + np.random.uniform(-0.02, 0.02))
        prices.append(base_price)
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * 1.01 for p in prices],
        'Low': [p * 0.99 for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 50),
        'symbol': 'TEST'
    })
    
    data.loc[10, 'Date'] = pd.to_datetime('2020-01-15') + pd.Timedelta('1 days')
    data.loc[15, 'High'] = data.loc[15, 'Low'] - 1
    data.loc[20, 'Volume'] = -1000
    data.loc[25, 'Close'] = np.nan
    data.loc[30:32, :] = np.nan
    
    print(f"Test data created with {len(data)} rows")
    print(f"• Date offset error: row 10")
    print(f"• Price logic error: row 15 (High < Low)")
    print(f"• Negative volume: row 20")
    print(f"• Missing Close: row 25")
    print(f"• All NaN rows: rows 30-32")
    
    cleaner = DataCleaner()
    
    try:
        cleaned = cleaner.clean_data(data)
        print(f"\nCleaned data: {len(cleaned)} rows")
        print("\nCleaning log:")
        for log in cleaner.cleaning_log:
            print(f"  {log}")
    except Exception as e:
        print(f"\nError during cleaning: {e}")


def check_data_source_compatibility():
    print("\n" + "=" * 60)
    print("DATA SOURCE COMPATIBILITY CHECK")
    print("=" * 60)
    
    print("\n6. yfinance data characteristics:")
    print("-" * 30)
    
    print("• Default timezone: UTC (returns naive datetime)")
    print("• Date index: Local market date (not exchange timezone)")
    print("• Auto-adjust: Adjusts prices for splits and dividends")
    print("• Data frequency: Daily data by default")
    print("• Known issues:")
    print("  - Rate limiting can cause fetch failures")
    print("  - Some symbols may return empty data")
    print("  - Time zone information not included in date")
    
    print("\n7. Recommended fixes:")
    print("-" * 30)
    print("• Explicitly set timezone for date columns")
    print("• Add retry logic for fetch failures")
    print("• Validate data source reliability")
    print("• Implement fallback data sources")


if __name__ == "__main__":
    check_timezone_issues()
    analyze_data_algorithms()
    test_timezone_handling()
    test_data_quality()
    check_data_source_compatibility()
