import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_fetcher import DataFetcher
from data_cleaner import DataCleaner
import os


def clean_full_stock_data(symbols: list, start_date: str, end_date: str, output_dir: str = "cleaned_data"):
    print("=" * 60)
    print("FULL DATA CLEANING PROCESS")
    print("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    fetcher = DataFetcher()
    cleaner = DataCleaner()
    
    all_reports = []
    
    for symbol in symbols:
        print(f"\n{'='*40}")
        print(f"Processing {symbol}")
        print(f"{'='*40}")
        
        try:
            print(f"Step 1: Fetching data for {symbol}...")
            raw_data = fetcher.fetch_stock_data(symbol, start_date, end_date)
            print(f"   Raw data: {len(raw_data)} rows")
            
            print(f"Step 2: Cleaning data...")
            cleaned_data = cleaner.clean_data(raw_data, fill_missing=True, remove_outliers=True)
            print(f"   Cleaned data: {len(cleaned_data)} rows")
            
            print(f"Step 3: Saving cleaned data...")
            filename = f"{symbol}_{start_date.replace('-','')}_{end_date.replace('-','')}_cleaned.csv"
            filepath = os.path.join(output_dir, filename)
            cleaned_data.to_csv(filepath, index=False)
            print(f"   Saved to: {filepath}")
            
            print(f"Step 4: Generating cleaning report...")
            report = {
                'symbol': symbol,
                'raw_rows': len(raw_data),
                'cleaned_rows': len(cleaned_data),
                'removed_rows': len(raw_data) - len(cleaned_data),
                'cleaning_log': cleaner.get_cleaning_report()
            }
            all_reports.append(report)
            
            print(f"\nCleaning Report for {symbol}:")
            print("-" * 30)
            print(cleaner.get_cleaning_report())
            
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            all_reports.append({
                'symbol': symbol,
                'error': str(e)
            })
    
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)
    
    summary_df = pd.DataFrame([{
        'Symbol': r['symbol'],
        'Raw Rows': r.get('raw_rows', 'N/A'),
        'Cleaned Rows': r.get('cleaned_rows', 'N/A'),
        'Removed': r.get('removed_rows', 'N/A'),
        'Status': 'Error' if 'error' in r else 'Success'
    } for r in all_reports])
    
    print(summary_df.to_string(index=False))
    
    report_path = os.path.join(output_dir, 'cleaning_summary_report.txt')
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("        DATA CLEANING SUMMARY REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Date Range: {start_date} to {end_date}\n")
        f.write(f"Symbols Processed: {len(symbols)}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("1. SUMMARY TABLE\n")
        f.write("-" * 30 + "\n")
        f.write(summary_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("2. DETAILED CLEANING LOGS\n")
        f.write("-" * 30 + "\n\n")
        
        for report in all_reports:
            if 'error' in report:
                f.write(f"Symbol: {report['symbol']}\n")
                f.write(f"Status: ERROR - {report['error']}\n")
            else:
                f.write(f"Symbol: {report['symbol']}\n")
                f.write(f"Raw Rows: {report['raw_rows']}\n")
                f.write(f"Cleaned Rows: {report['cleaned_rows']}\n")
                f.write(f"Removed Rows: {report['removed_rows']}\n")
                f.write("Cleaning Log:\n")
                f.write("-" * 20 + "\n")
                f.write(report['cleaning_log'])
                f.write("\n")
            
            f.write("\n" + "-" * 50 + "\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("         END OF REPORT\n")
        f.write("=" * 70 + "\n")
    
    print(f"\nSummary report saved to: {report_path}")
    print(f"Cleaned data files saved to: {output_dir}/")
    
    return all_reports


def generate_large_test_dataset(n_symbols: int = 10, n_days: int = 500):
    print(f"Generating {n_symbols} test symbols with {n_days} days each...")
    
    all_data = []
    
    base_date = datetime(2020, 1, 1)
    dates = pd.date_range(start=base_date, periods=n_days, freq='B')
    
    for i in range(n_symbols):
        symbol = f"STOCK_{i+1:03d}"
        
        price = 50 + np.random.uniform(0, 50)
        prices = []
        
        for j in range(n_days):
            base_return = np.random.uniform(-0.005, 0.005)
            noise = np.random.normal(0, 0.01)
            price *= (1 + base_return + noise)
            prices.append(price)
        
        prices = np.array(prices)
        
        if np.random.random() < 0.1:
            prices[np.random.randint(0, n_days)] *= 2
        
        data = pd.DataFrame({
            'Date': dates.astype('datetime64[ns]'),
            'Open': prices,
            'High': prices * (1 + np.random.uniform(0.001, 0.02)),
            'Low': prices * (1 - np.random.uniform(0.001, 0.02)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, n_days),
            'symbol': symbol
        })
        
        if np.random.random() < 0.2:
            data.loc[np.random.randint(0, n_days), ['Open', 'High', 'Low', 'Close']] = np.nan
        
        if np.random.random() < 0.15:
            idx = np.random.randint(0, n_days)
            data.loc[idx, 'High'] = data.loc[idx, 'Low'] - 1
        
        all_data.append(data)
    
    print(f"Generated {len(all_data)} datasets")
    return all_data


if __name__ == "__main__":
    print("Option 1: Use simulated large dataset")
    print("Option 2: Use real Yahoo Finance data")
    
    test_mode = True
    
    if test_mode:
        print("\nUsing simulated test dataset...")
        datasets = generate_large_test_dataset(n_symbols=5, n_days=365)
        
        output_dir = "cleaned_data"
        os.makedirs(output_dir, exist_ok=True)
        
        cleaner = DataCleaner()
        all_reports = []
        
        for data in datasets:
            symbol = data['symbol'].iloc[0]
            print(f"\nProcessing {symbol}...")
            print(f"Raw rows: {len(data)}")
            
            cleaned = cleaner.clean_data(data)
            print(f"Cleaned rows: {len(cleaned)}")
            
            filename = f"{symbol}_cleaned.csv"
            cleaned.to_csv(os.path.join(output_dir, filename), index=False)
            
            all_reports.append({
                'symbol': symbol,
                'raw': len(data),
                'cleaned': len(cleaned),
                'log': cleaner.get_cleaning_report()
            })
        
        print("\n" + "="*60)
        print("CLEANING SUMMARY")
        print("="*60)
        for r in all_reports:
            print(f"{r['symbol']}: {r['raw']} -> {r['cleaned']} rows")
        
        print(f"\nCleaned data saved to: {output_dir}/")
    
    else:
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        start_date = "2020-01-01"
        end_date = "2023-01-01"
        
        clean_full_stock_data(symbols, start_date, end_date)
