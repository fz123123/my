import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
from typing import Optional


class DataFetcher:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def fetch_stock_data(self, symbol: str, start_date: str, end_date: str, 
                        auto_adjust: bool = True) -> pd.DataFrame:
        try:
            data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=auto_adjust)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            data = data.round(2)
            data['symbol'] = symbol
            data.reset_index(inplace=True)
            
            return data
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for {symbol}: {str(e)}")
    
    def fetch_multiple_stocks(self, symbols: list, start_date: str, end_date: str) -> dict:
        results = {}
        for symbol in symbols:
            try:
                data = self.fetch_stock_data(symbol, start_date, end_date)
                results[symbol] = data
            except Exception as e:
                print(f"Failed to fetch {symbol}: {e}")
        return results
    
    def save_data(self, data: pd.DataFrame, symbol: str, format: str = "csv") -> None:
        filename = f"{symbol}_{data['Date'].iloc[0].strftime('%Y%m%d')}_{data['Date'].iloc[-1].strftime('%Y%m%d')}.{format}"
        filepath = os.path.join(self.data_dir, filename)
        
        if format == "csv":
            data.to_csv(filepath, index=False)
        elif format == "parquet":
            data.to_parquet(filepath)
        else:
            raise ValueError("Unsupported format. Use 'csv' or 'parquet'")
        
        print(f"Data saved to {filepath}")
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath, parse_dates=['Date'])
        elif filepath.endswith('.parquet'):
            return pd.read_parquet(filepath)
        else:
            raise ValueError("Unsupported file format. Use '.csv' or '.parquet'")


if __name__ == "__main__":
    fetcher = DataFetcher()
    
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    data = fetcher.fetch_stock_data("AAPL", start_date, end_date)
    print(f"Fetched {len(data)} rows for AAPL")
    print(data.head())
    
    fetcher.save_data(data, "AAPL")
