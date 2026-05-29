import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_simulated_yfinance_data(n_days: int = 100, start_price: float = 100.0):
    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='B')
    prices = []
    base_price = start_price
    
    for i in range(n_days):
        base_price *= (1 + np.random.uniform(-0.02, 0.02))
        prices.append(base_price)
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * (1.005 + np.random.random() * 0.005) for p in prices],
        'Low': [p * (0.99 - np.random.random() * 0.005) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(5000000, 20000000, n_days),
        'symbol': 'TEST_STOCK'
    })
    
    return data.round(2)


def generate_simulated_trading_software_data(base_data: pd.DataFrame):
    simulated = base_data.copy()
    
    simulated['Close'] = simulated['Close'] * (1 + np.random.normal(0, 0.003, len(simulated)))
    simulated['Open'] = simulated['Close'] * (0.998 + np.random.random(len(simulated)) * 0.004)
    simulated['High'] = simulated[['Open', 'Close']].max(axis=1) * (1 + np.random.random(len(simulated)) * 0.003)
    simulated['Low'] = simulated[['Open', 'Close']].min(axis=1) * (1 - np.random.random(len(simulated)) * 0.003)
    simulated['Volume'] = (simulated['Volume'] * 1.03 * (0.97 + np.random.random(len(simulated)) * 0.06)).astype(int)
    
    simulated['Open'] = simulated['Open'].round(2)
    simulated['High'] = simulated['High'].round(2)
    simulated['Low'] = simulated['Low'].round(2)
    simulated['Close'] = simulated['Close'].round(2)
    
    return simulated


def compare_data_sources(yf_data: pd.DataFrame, manual_data: pd.DataFrame, symbol: str = "TEST"):
    print("=" * 70)
    print(f"DATA COMPARISON ANALYSIS FOR {symbol}")
    print("=" * 70)
    
    print(f"\n1. yfinance Data")
    print("-" * 50)
    print(f"   Rows: {len(yf_data)}")
    print(f"   Date range: {yf_data['Date'].min().date()} to {yf_data['Date'].max().date()}")
    
    print(f"\n2. Trading Software Data")
    print("-" * 50)
    print(f"   Rows: {len(manual_data)}")
    print(f"   Date range: {manual_data['Date'].min().date()} to {manual_data['Date'].max().date()}")
    
    print(f"\n3. Data Comparison Report")
    print("-" * 50)
    
    comparison_df = pd.DataFrame({
        'Metric': [
            'Total Rows',
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
            len(yf_data),
            f"{yf_data['Volume'].mean():,.0f}",
            f"{yf_data['Volume'].max():,.0f}",
            f"{yf_data['Volume'].min():,.0f}",
            f"${yf_data['Close'].mean():.2f}",
            f"${yf_data['Close'].max():.2f}",
            f"${yf_data['Close'].min():.2f}",
            f"{(yf_data['Close'].iloc[-1] / yf_data['Close'].iloc[0] - 1) * 100:.2f}%",
            f"{yf_data['Close'].pct_change().std() * 100:.2f}%"
        ],
        'Trading Software': [
            len(manual_data),
            f"{manual_data['Volume'].mean():,.0f}",
            f"{manual_data['Volume'].max():,.0f}",
            f"{manual_data['Volume'].min():,.0f}",
            f"${manual_data['Close'].mean():.2f}",
            f"${manual_data['Close'].max():.2f}",
            f"${manual_data['Close'].min():.2f}",
            f"{(manual_data['Close'].iloc[-1] / manual_data['Close'].iloc[0] - 1) * 100:.2f}%",
            f"{manual_data['Close'].pct_change().std() * 100:.2f}%"
        ],
        'Difference': [
            f"{len(yf_data) - len(manual_data)}",
            f"{((yf_data['Volume'].mean() - manual_data['Volume'].mean()) / manual_data['Volume'].mean() * 100):.1f}%",
            f"{((yf_data['Volume'].max() - manual_data['Volume'].max()) / manual_data['Volume'].max() * 100):.1f}%",
            f"{((yf_data['Volume'].min() - manual_data['Volume'].min()) / manual_data['Volume'].min() * 100):.1f}%",
            f"${yf_data['Close'].mean() - manual_data['Close'].mean():.2f}",
            f"${yf_data['Close'].max() - manual_data['Close'].max():.2f}",
            f"${yf_data['Close'].min() - manual_data['Close'].min():.2f}",
            f"{((yf_data['Close'].iloc[-1] / yf_data['Close'].iloc[0] - 1) - (manual_data['Close'].iloc[-1] / manual_data['Close'].iloc[0] - 1)) * 100:.2f}%",
            f"{(yf_data['Close'].pct_change().std() - manual_data['Close'].pct_change().std()) * 100:.2f}%"
        ]
    })
    
    print(comparison_df.to_string(index=False))
    
    print(f"\n4. Daily Price Comparison")
    print("-" * 50)
    
    merged = pd.merge(yf_data[['Date', 'Close', 'Volume']], 
                     manual_data[['Date', 'Close', 'Volume']], 
                     on='Date', suffixes=('_yf', '_sw'))
    
    merged['price_diff'] = merged['Close_yf'] - merged['Close_sw']
    merged['price_diff_pct'] = (merged['Close_yf'] - merged['Close_sw']) / merged['Close_sw'] * 100
    merged['volume_diff_pct'] = (merged['Volume_yf'] - merged['Volume_sw']) / merged['Volume_sw'] * 100
    
    max_price_diff = merged['price_diff_pct'].abs().max()
    max_vol_diff = merged['volume_diff_pct'].abs().max()
    
    print(f"   Total matching days: {len(merged)}")
    print(f"   Max price difference: {max_price_diff:.2f}%")
    print(f"   Max volume difference: {max_vol_diff:.2f}%")
    
    significant_diffs = merged[merged['price_diff_pct'].abs() > 0.5]
    if len(significant_diffs) > 0:
        print(f"\n   Significant price differences (>0.5%):")
        print("   Date       yfinance    Software   Diff (%)")
        print("   ---------- ---------- ---------- --------")
        for _, row in significant_diffs.head(5).iterrows():
            print(f"   {row['Date'].date()}  ${row['Close_yf']:.2f}    ${row['Close_sw']:.2f}    {row['price_diff_pct']:.2f}%")
    
    print(f"\n5. Common Data Differences Explained")
    print("-" * 50)
    print("   • Timezone differences")
    print("   • Price adjustment (split/dividend)")
    print("   • Data source timing differences")
    print("   • Volume calculation methods")
    print("   • Market data feed delays")
    print("   • Data aggregation methods")
    
    return comparison_df


def analyze_volume_spikes(data: pd.DataFrame, threshold: float = 2.0):
    print("\n" + "=" * 70)
    print("VOLUME SPIKE ANALYSIS")
    print("=" * 70)
    
    data = data.copy().sort_values('Date')
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
            price_change = row['price_change'] if not np.isnan(row['price_change']) else 0
            print(f"{row['Date'].date()}  {row['Volume']:,.0f}  {row['volume_ma']:,.0f}  {row['volume_zscore']:.2f}     {price_change:.2%}")
    
    return spikes


def main():
    print("=" * 70)
    print("DATA COMPARISON DEMO")
    print("=" * 70)
    print("Comparing simulated yfinance data with trading software data")
    print("=" * 70)
    
    print("\nStep 1: Generate simulated data")
    print("-" * 50)
    yf_data = generate_simulated_yfinance_data(n_days=100)
    trading_data = generate_simulated_trading_software_data(yf_data)
    print("✓ Generated 100 days of simulated data")
    
    print("\nStep 2: Run data comparison")
    print("-" * 50)
    compare_data_sources(yf_data, trading_data, "TEST_STOCK")
    
    print("\nStep 3: Analyze volume spikes")
    print("-" * 50)
    analyze_volume_spikes(trading_data)
    
    print("\n" + "=" * 70)
    print("INSTRUCTIONS FOR REAL DATA COMPARISON")
    print("=" * 70)
    print("1. Open your trading software (东方财富/同花顺)")
    print("2. Find the stock you want to compare")
    print("3. Export historical data to CSV format")
    print("4. Ensure columns are: Date, Open, High, Low, Close, Volume")
    print("5. Save as 'trading_software_data.csv'")
    print("6. Run: python data_comparison_tool.py")
    print("7. Select option 2 and enter your stock symbol and date range")
    print("=" * 70)


if __name__ == "__main__":
    main()
