import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_cleaner import DataCleaner


def validate_data_format():
    print("=" * 60)
    print("DATA FORMAT VALIDATION")
    print("=" * 60)
    
    dates = pd.date_range(start='2020-01-01', periods=50, freq='B')
    
    prices = np.array([100.0 + i * 0.5 + np.random.normal(0, 1) for i in range(50)])
    
    test_data = pd.DataFrame({
        'Date': dates.astype('datetime64[ns]'),
        'Open': prices,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 50),
        'symbol': 'TEST'
    })
    
    print("Test Data Structure:")
    print("-" * 40)
    print(f"Columns: {list(test_data.columns)}")
    print(f"Rows: {len(test_data)}")
    print(f"Date dtype: {test_data['Date'].dtype}")
    print(f"Price dtypes: Open={test_data['Open'].dtype}, High={test_data['High'].dtype}, Low={test_data['Low'].dtype}, Close={test_data['Close'].dtype}")
    print(f"Volume dtype: {test_data['Volume'].dtype}")
    print("\nSample data:")
    print(test_data.head())
    
    return test_data


def test_cleaning_pipeline():
    print("\n" + "=" * 60)
    print("DATA CLEANING PIPELINE TEST")
    print("=" * 60)
    
    dates = pd.date_range(start='2020-01-01', periods=100, freq='B')
    prices = np.array([100.0 + i * 0.3 + np.random.normal(0, 1.5) for i in range(100)])
    
    data = pd.DataFrame({
        'Date': dates.astype('datetime64[ns]'),
        'Open': prices,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 100),
        'symbol': 'TEST'
    })
    
    data.loc[10, 'High'] = 90
    data.loc[10, 'Low'] = 95
    data.loc[20, 'Volume'] = -1000
    data.loc[30, 'Close'] = np.nan
    data.loc[40:42, :] = np.nan
    data.loc[50, 'Date'] = data.loc[49, 'Date']
    
    print("Test data with intentional errors:")
    print("-" * 40)
    print(f"Initial rows: {len(data)}")
    print(f"Rows with invalid price logic (High < Low): 1 (row 10)")
    print(f"Rows with negative volume: 1 (row 20)")
    print(f"Rows with missing Close price: 1 (row 30)")
    print(f"Rows with all NaN: 3 (rows 40-42)")
    print(f"Duplicate dates: 1 (row 50)")
    
    cleaner = DataCleaner()
    
    try:
        cleaned_data = cleaner.clean_data(data)
        
        print("\nCleaning Results:")
        print("-" * 40)
        print(f"Final rows: {len(cleaned_data)}")
        print(f"Rows removed: {len(data) - len(cleaned_data)}")
        
        print("\nCleaning Log:")
        print("-" * 40)
        for log in cleaner.cleaning_log:
            print(log)
        
        print("\nValidation checks after cleaning:")
        print("-" * 40)
        
        invalid_price = ((cleaned_data['High'] < cleaned_data['Low']) |
                        (cleaned_data['Open'] < cleaned_data['Low']) |
                        (cleaned_data['Open'] > cleaned_data['High']) |
                        (cleaned_data['Close'] < cleaned_data['Low']) |
                        (cleaned_data['Close'] > cleaned_data['High'])).sum()
        print(f"Invalid price logic rows: {invalid_price}")
        
        invalid_volume = (cleaned_data['Volume'] < 0).sum()
        print(f"Negative volume rows: {invalid_volume}")
        
        missing_values = cleaned_data[['Open', 'High', 'Low', 'Close', 'Volume']].isna().sum().sum()
        print(f"Missing values: {missing_values}")
        
        duplicate_dates = cleaned_data.duplicated(subset=['Date']).sum()
        print(f"Duplicate dates: {duplicate_dates}")
        
        date_gaps = cleaned_data['Date'].diff().dt.days.max()
        print(f"Max date gap (business days): {date_gaps}")
        
        print("\n✅ All validation checks passed!")
        
    except Exception as e:
        print(f"\n❌ Error during cleaning: {e}")


def test_edge_cases():
    print("\n" + "=" * 60)
    print("EDGE CASE TESTS")
    print("=" * 60)
    
    cleaner = DataCleaner()
    
    print("\n1. Empty DataFrame test:")
    try:
        empty_data = pd.DataFrame()
        cleaner.clean_data(empty_data)
        print("❌ Should have raised error for missing columns")
    except ValueError as e:
        print(f"✅ Correctly raised error: {e}")
    
    print("\n2. Missing required columns test:")
    try:
        bad_data = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=10, freq='B'),
            'Open': [100] * 10,
            'Close': [100] * 10
        })
        cleaner.clean_data(bad_data)
        print("❌ Should have raised error for missing columns")
    except ValueError as e:
        print(f"✅ Correctly raised error: {e}")
    
    print("\n3. Non-datetime Date column test:")
    try:
        bad_data = pd.DataFrame({
            'Date': ['2020-01-01', '2020-01-02'],
            'Open': [100, 101],
            'High': [101, 102],
            'Low': [99, 100],
            'Close': [100, 101],
            'Volume': [1000, 2000],
            'symbol': ['TEST', 'TEST']
        })
        cleaner.clean_data(bad_data)
        print("❌ Should have raised error for non-datetime Date")
    except ValueError as e:
        print(f"✅ Correctly raised error: {e}")


if __name__ == "__main__":
    validate_data_format()
    test_cleaning_pipeline()
    test_edge_cases()
