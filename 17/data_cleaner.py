import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pytz


class DataCleaner:
    def __init__(self):
        self.cleaning_log = []
    
    def _log(self, message: str, severity: str = "INFO") -> None:
        self.cleaning_log.append(f"[{severity}] {message}")
    
    def validate_data_structure(self, data: pd.DataFrame) -> Tuple[bool, str]:
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            return False, f"Missing required columns: {missing_cols}"
        
        if not pd.api.types.is_datetime64_any_dtype(data['Date']):
            try:
                data['Date'] = pd.to_datetime(data['Date'])
                self._log("Converted Date column to datetime type", "INFO")
            except Exception as e:
                return False, f"Date column cannot be converted to datetime: {str(e)}"
        
        return True, "Data structure is valid"
    
    def remove_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(data)
        data = data.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
        removed_count = initial_count - len(data)
        
        if removed_count > 0:
            self._log(f"Removed {removed_count} rows with missing values", "WARNING")
        
        return data
    
    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(data)
        data = data.drop_duplicates(subset=['Date'], keep='first')
        removed_count = initial_count - len(data)
        
        if removed_count > 0:
            self._log(f"Removed {removed_count} duplicate rows", "WARNING")
        
        return data
    
    def validate_price_logic(self, data: pd.DataFrame) -> pd.DataFrame:
        invalid_mask = (
            (data['High'] < data['Low']) |
            (data['Open'] < data['Low']) |
            (data['Open'] > data['High']) |
            (data['Close'] < data['Low']) |
            (data['Close'] > data['High'])
        )
        
        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            self._log(f"Found {invalid_count} rows with invalid price logic", "ERROR")
            data = data[~invalid_mask]
        
        return data
    
    def validate_volume(self, data: pd.DataFrame) -> pd.DataFrame:
        invalid_mask = (data['Volume'] < 0) | (data['Volume'].isna())
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            self._log(f"Found {invalid_count} rows with invalid volume", "ERROR")
            data = data[~invalid_mask]
        
        return data
    
    def fill_missing_dates(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data = data.set_index('Date')
        
        expected_dates = pd.date_range(start=data.index.min(), end=data.index.max(), freq='B')
        data = data.reindex(expected_dates)
        
        data['symbol'] = data['symbol'].ffill()
        
        data[['Open', 'High', 'Low', 'Close']] = data[['Open', 'High', 'Low', 'Close']].ffill()
        data['Volume'] = data['Volume'].fillna(0)
        
        missing_count = data['Open'].isna().sum()
        if missing_count > 0:
            self._log(f"Filled {missing_count} missing trading days", "INFO")
        
        data = data.dropna(subset=['Open'])
        data = data.reset_index().rename(columns={'index': 'Date'})
        
        return data
    
    def detect_outliers(self, data: pd.DataFrame, method: str = 'zscore', threshold: float = 3.0) -> pd.DataFrame:
        data = data.copy()
        
        if len(data) < 10:
            return data
        
        if method == 'zscore':
            pct_change = data['Close'].pct_change().dropna()
            if len(pct_change) < 2:
                return data
            
            std = pct_change.std()
            if std == 0:
                return data
            
            z_scores = np.abs((pct_change - pct_change.mean()) / std)
            outliers = z_scores > threshold
        elif method == 'iqr':
            pct_change = data['Close'].pct_change().dropna()
            if len(pct_change) < 2:
                return data
            
            q1, q3 = pct_change.quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = (pct_change < (q1 - 1.5 * iqr)) | (pct_change > (q3 + 1.5 * iqr))
        else:
            raise ValueError("Method must be 'zscore' or 'iqr'")
        
        outlier_dates = pct_change[outliers].index
        if len(outlier_dates) > 0:
            self._log(f"Detected {len(outlier_dates)} outliers using {method} method", "WARNING")
            data = data[~data['Date'].isin(outlier_dates)]
        
        return data
    
    def validate_date_continuity(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy().sort_values('Date')
        data['date_diff'] = data['Date'].diff().dt.days
        
        gaps = data[data['date_diff'] > 3]
        if len(gaps) > 0:
            self._log(f"Found {len(gaps)} date gaps larger than 3 days", "INFO")
            for _, row in gaps.iterrows():
                self._log(f"Gap detected: {row['Date'] - timedelta(days=row['date_diff'])} to {row['Date']}", "INFO")
        
        data = data.drop('date_diff', axis=1)
        return data
    
    def set_timezone(self, data: pd.DataFrame, timezone: str = 'America/New_York') -> pd.DataFrame:
        data = data.copy()
        
        if data['Date'].dt.tz is None:
            try:
                data['Date'] = data['Date'].dt.tz_localize('UTC').dt.tz_convert(timezone)
                self._log(f"Set timezone to {timezone}", "INFO")
            except Exception as e:
                self._log(f"Failed to set timezone: {str(e)}", "WARNING")
        
        return data
    
    def clean_data(self, data: pd.DataFrame, fill_missing: bool = True, 
                  remove_outliers: bool = True, outlier_method: str = 'zscore',
                  set_tz: bool = False, timezone: str = 'America/New_York') -> pd.DataFrame:
        self.cleaning_log = []
        
        is_valid, message = self.validate_data_structure(data)
        if not is_valid:
            raise ValueError(f"Data validation failed: {message}")
        
        self._log("Starting data cleaning process...")
        
        data = self.remove_duplicates(data)
        data = self.remove_missing_values(data)
        data = self.validate_price_logic(data)
        data = self.validate_volume(data)
        
        if fill_missing:
            data = self.fill_missing_dates(data)
        
        if remove_outliers:
            data = self.detect_outliers(data, method=outlier_method)
        
        data = self.validate_date_continuity(data)
        
        if set_tz:
            data = self.set_timezone(data, timezone)
        
        data = data.sort_values('Date').reset_index(drop=True)
        
        self._log(f"Cleaning completed. Final row count: {len(data)}")
        
        return data
    
    def get_cleaning_report(self) -> str:
        return "\n".join(self.cleaning_log)


if __name__ == "__main__":
    from data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    cleaner = DataCleaner()
    
    print("Testing with simulated data...")
    dates = pd.date_range(start='2020-01-01', periods=50, freq='B')
    prices = np.array([100.0 + i * 0.5 + np.random.normal(0, 1) for i in range(50)])
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 50),
        'symbol': 'TEST'
    })
    
    data.loc[10, 'High'] = data.loc[10, 'Low'] - 1
    data.loc[20, 'Volume'] = -1000
    data.loc[25, 'Close'] = np.nan
    
    print(f"Original data: {len(data)} rows")
    
    cleaned_data = cleaner.clean_data(data)
    print(f"Cleaned data: {len(cleaned_data)} rows")
    
    print("\nCleaning Report:")
    print(cleaner.get_cleaning_report())