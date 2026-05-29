import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from data_fetcher import DataFetcher
from data_cleaner import DataCleaner


def compare_data_sources(symbol: str, start_date: str, end_date: str, manual_data: pd.DataFrame = None):
    print("=" * 70)
    print(f"DATA COMPARISON ANALYSIS FOR {symbol}")
    print("=" * 70)
    
    fetcher = DataFetcher()
    cleaner = DataCleaner()
    
    print(f"\n1. Fetching data from yfinance...")
    print("-" * 50)
    
    try:
        yf_data = fetcher.fetch_stock_data(symbol, start_date, end_date)
        yf_cleaned = cleaner.clean_data(yf_data)
        print(f"   ✓ Successfully fetched {len(yf_cleaned)} rows")
        print(f"   Date range: {yf_cleaned['Date'].min().date()} to {yf_cleaned['Date'].max().date()}")
    except Exception as e:
        print(f"   ✗ Failed to fetch yfinance data: {e}")
        return
    
    if manual_data is not None:
        print(f"\n2. Processing manual data (from trading software)...")
        print("-" * 50)
        try:
            manual_cleaned = cleaner.clean_data(manual_data)
            print(f"   ✓ Successfully processed {len(manual_cleaned)} rows")
            print(f"   Date range: {manual_cleaned['Date'].min().date()} to {manual_cleaned['Date'].max().date()}")
        except Exception as e:
            print(f"   ✗ Failed to process manual data: {e}")
            manual_cleaned = None
    else:
        manual_cleaned = None
    
    print(f"\n3. Data Comparison Report")
    print("-" * 50)
    
    comparison_df = pd.DataFrame({
        'Metric': [
            'Total Rows',
            'Date Range Start',
            'Date Range End',
            'Avg Daily Volume',
            'Max Volume',
            'Min Volume',
            'Avg Close Price',
            'Max Close Price',
            'Min Close Price',
            'Total Return',
            'Volatility (Daily)'
        ],
        'yfinance': [
            len(yf_cleaned),
            yf_cleaned['Date'].min().date(),
            yf_cleaned['Date'].max().date(),
            f"{yf_cleaned['Volume'].mean():,.0f}",
            f"{yf_cleaned['Volume'].max():,.0f}",
            f"{yf_cleaned['Volume'].min():,.0f}",
            f"${yf_cleaned['Close'].mean():.2f}",
            f"${yf_cleaned['Close'].max():.2f}",
            f"${yf_cleaned['Close'].min():.2f}",
            f"{(yf_cleaned['Close'].iloc[-1] / yf_cleaned['Close'].iloc[0] - 1) * 100:.2f}%",
            f"{yf_cleaned['Close'].pct_change().std() * 100:.2f}%"
        ]
    })
    
    if manual_cleaned is not None and not manual_cleaned.empty:
        comparison_df['Manual'] = [
            len(manual_cleaned),
            manual_cleaned['Date'].min().date(),
            manual_cleaned['Date'].max().date(),
            f"{manual_cleaned['Volume'].mean():,.0f}",
            f"{manual_cleaned['Volume'].max():,.0f}",
            f"{manual_cleaned['Volume'].min():,.0f}",
            f"${manual_cleaned['Close'].mean():.2f}",
            f"${manual_cleaned['Close'].max():.2f}",
            f"${manual_cleaned['Close'].min():.2f}",
            f"{(manual_cleaned['Close'].iloc[-1] / manual_cleaned['Close'].iloc[0] - 1) * 100:.2f}%",
            f"{manual_cleaned['Close'].pct_change().std() * 100:.2f}%"
        ]
        
        comparison_df['Difference'] = [
            f"{len(yf_cleaned) - len(manual_cleaned)}",
            '-',
            '-',
            f"{((yf_cleaned['Volume'].mean() - manual_cleaned['Volume'].mean()) / manual_cleaned['Volume'].mean() * 100):.1f}%",
            f"{((yf_cleaned['Volume'].max() - manual_cleaned['Volume'].max()) / manual_cleaned['Volume'].max() * 100):.1f}%",
            f"{((yf_cleaned['Volume'].min() - manual_cleaned['Volume'].min()) / manual_cleaned['Volume'].min() * 100):.1f}%",
            f"${yf_cleaned['Close'].mean() - manual_cleaned['Close'].mean():.2f}",
            f"${yf_cleaned['Close'].max() - manual_cleaned['Close'].max():.2f}",
            f"${yf_cleaned['Close'].min() - manual_cleaned['Close'].min():.2f}",
            f"{((yf_cleaned['Close'].iloc[-1] / yf_cleaned['Close'].iloc[0] - 1) - (manual_cleaned['Close'].iloc[-1] / manual_cleaned['Close'].iloc[0] - 1)) * 100:.2f}%",
            f"{(yf_cleaned['Close'].pct_change().std() - manual_cleaned['Close'].pct_change().std()) * 100:.2f}%"
        ]
    
    print(comparison_df.to_string(index=False))
    
    if manual_cleaned is not None and not manual_cleaned.empty:
        print(f"\n4. Daily Price Comparison")
        print("-" * 50)
        
        merged = pd.merge(yf_cleaned[['Date', 'Close', 'Volume']], 
                         manual_cleaned[['Date', 'Close', 'Volume']], 
                         on='Date', suffixes=('_yf', '_manual'))
        
        merged['price_diff'] = merged['Close_yf'] - merged['Close_manual']
        merged['price_diff_pct'] = (merged['Close_yf'] - merged['Close_manual']) / merged['Close_manual'] * 100
        merged['volume_diff_pct'] = (merged['Volume_yf'] - merged['Volume_manual']) / merged['Volume_manual'] * 100
        
        max_price_diff = merged['price_diff_pct'].abs().max()
        max_vol_diff = merged['volume_diff_pct'].abs().max()
        
        print(f"   Total matching days: {len(merged)}")
        print(f"   Max price difference: {max_price_diff:.2f}%")
        print(f"   Max volume difference: {max_vol_diff:.2f}%")
        
        significant_diffs = merged[merged['price_diff_pct'].abs() > 1]
        if len(significant_diffs) > 0:
            print(f"\n   Significant price differences (>1%):")
            print("   Date       yfinance    Manual     Diff (%)")
            print("   ---------- ---------- ---------- --------")
            for _, row in significant_diffs.iterrows():
                print(f"   {row['Date'].date()}  ${row['Close_yf']:.2f}    ${row['Close_manual']:.2f}    {row['price_diff_pct']:.2f}%")
    
    print(f"\n5. Common Data Differences Explained")
    print("-" * 50)
    print("   • Timezone differences")
    print("   • Price adjustment (split/dividend)")
    print("   • Data source timing differences")
    print("   • Volume calculation methods")
    print("   • Market data feed delays")
    print("   • Data aggregation methods")
    
    return comparison_df


def create_manual_data_template(output_file: str = "data_comparison_template.csv"):
    template = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=10, freq='B'),
        'Open': [100.0] * 10,
        'High': [101.0] * 10,
        'Low': [99.0] * 10,
        'Close': [100.0] * 10,
        'Volume': [1000000] * 10,
        'symbol': ['AAPL'] * 10
    })
    
    template.to_csv(output_file, index=False)
    print(f"Template saved to: {output_file}")
    print("Please fill in the data from your trading software (东方财富/同花顺)")
    print("Columns: Date, Open, High, Low, Close, Volume, symbol")


def analyze_volume_spikes(data: pd.DataFrame, threshold: float = 2.0):
    print("\n" + "=" * 70)
    print("VOLUME SPIKE ANALYSIS")
    print("=" * 70)
    
    data = data.copy().sort_values('Date')
    data['volume_pct_change'] = data['Volume'].pct_change()
    data['volume_ma'] = data['Volume'].rolling(20).mean()
    data['volume_std'] = data['Volume'].rolling(20).std()
    data['volume_zscore'] = (data['Volume'] - data['volume_ma']) / data['volume_std']
    data['price_change'] = data['Close'].pct_change()
    
    spikes = data[data['volume_zscore'].abs() > threshold]
    
    print(f"Analyzing {len(data)} trading days")
    print(f"Found {len(spikes)} volume spikes (> {threshold}σ from 20-day average)")
    
    if len(spikes) > 0:
        print("\nSpike Details:")
        print("Date       Volume      Avg Volume  Z-Score  Price Change")
        print("---------- ----------  ----------  -------- -------------")
        
        for _, row in spikes.iterrows():
            price_change = row['price_change']
            print(f"{row['Date'].date()}  {row['Volume']:,.0f}  {row['volume_ma']:,.0f}  {row['volume_zscore']:.2f}     {price_change:.2%}")
    
    return spikes


if __name__ == "__main__":
    print("=" * 70)
    print("DATA COMPARISON TOOL")
    print("=" * 70)
    print("1. Create a template file for manual data entry")
    print("2. Run comparison analysis")
    print("=" * 70)
    
    choice = input("Enter your choice (1/2): ").strip()
    
    if choice == '1':
        create_manual_data_template()
    elif choice == '2':
        symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        
        manual_file = input("Enter manual data file path (leave empty to skip): ").strip()
        
        manual_data = None
        if manual_file and os.path.exists(manual_file):
            manual_data = pd.read_csv(manual_file, parse_dates=['Date'])
        
        compare_data_sources(symbol, start_date, end_date, manual_data)
    else:
        print("Invalid choice")
