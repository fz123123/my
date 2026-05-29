import pandas as pd
import numpy as np
import datetime

class DataProcessor:
    def __init__(self):
        pass
    
    def fetch_real_time_data(self, ticker='AAPL', period='1d', interval='1m'):
        try:
            import yfinance as yf
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(period=period, interval=interval)
            
            if data.empty:
                print(f"警告: 无法获取 {ticker} 的实时数据，使用模拟数据")
                return self.generate_simulated_real_time_data(ticker)
            
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            data = data.round(2)
            
            print(f"成功获取 {ticker} 实时数据: {len(data)} 条记录")
            print(f"最新时间: {data.index[-1]}")
            print(f"最新收盘价: ${data['close'].iloc[-1]:.2f}")
            
            return data
            
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            print("使用模拟实时数据")
            return self.generate_simulated_real_time_data(ticker)
    
    def generate_simulated_real_time_data(self, ticker='AAPL'):
        now = datetime.datetime.now()
        dates = pd.date_range(start=now - datetime.timedelta(days=1), periods=390, freq='1T')
        
        base_price = {'AAPL': 178.50, 'GOOGL': 141.20, 'MSFT': 378.90, 'NVDA': 875.50}.get(ticker, 150.0)
        
        time_of_day = dates.hour * 60 + dates.minute
        morning_vol = np.sin(time_of_day / 60 * np.pi / 4) * 2
        afternoon_vol = np.sin((time_of_day - 300) / 60 * np.pi / 3) * 1.5 if time_of_day > 300 else 0
        
        prices = base_price + morning_vol + afternoon_vol + np.random.randn(len(dates)) * 0.3
        
        df = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(len(dates)) * 0.8,
            'low': prices - np.random.rand(len(dates)) * 0.8,
            'close': prices,
            'volume': np.random.randint(50000, 500000, len(dates))
        }, index=dates)
        
        df = df.between_time('09:30', '16:00')
        
        print(f"生成模拟实时数据: {ticker}")
        print(f"最新时间: {df.index[-1]}")
        print(f"最新收盘价: ${df['close'].iloc[-1]:.2f}")
        
        return df
    
    def fetch_daily_history(self, ticker='AAPL', start_date=None, end_date=None):
        try:
            import yfinance as yf
            
            if end_date is None:
                end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            if start_date is None:
                start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
            
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                print(f"警告: 无法获取 {ticker} 历史数据，使用模拟数据")
                return self.generate_simulated_daily_data(ticker, start_date, end_date)
            
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            data = data.round(2)
            
            print(f"成功获取 {ticker} 历史数据: {len(data)} 条记录")
            print(f"时间范围: {data.index[0].date()} - {data.index[-1].date()}")
            print(f"最新收盘价: ${data['close'].iloc[-1]:.2f}")
            
            return data
            
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            print("使用模拟历史数据")
            return self.generate_simulated_daily_data(ticker, start_date, end_date)
    
    def generate_simulated_daily_data(self, ticker='AAPL', start_date=None, end_date=None):
        if end_date is None:
            end_date = datetime.datetime.now()
        else:
            end_date = pd.to_datetime(end_date)
        
        if start_date is None:
            start_date = end_date - datetime.timedelta(days=365)
        else:
            start_date = pd.to_datetime(start_date)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        base_price = {'AAPL': 120.0, 'GOOGL': 100.0, 'MSFT': 280.0, 'NVDA': 400.0}.get(ticker, 100.0)
        days = len(dates)
        trend = np.linspace(0, 80, days)
        seasonality = np.sin(np.linspace(0, 8 * np.pi, days)) * 5
        noise = np.random.randn(days) * 2
        
        prices = base_price + trend + seasonality + noise
        
        df = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(days) * 4,
            'low': prices - np.random.rand(days) * 4,
            'close': prices,
            'volume': np.random.randint(1000000, 15000000, days)
        }, index=dates)
        
        df = df.round(2)
        
        print(f"生成模拟历史数据: {ticker}")
        print(f"时间范围: {df.index[0].date()} - {df.index[-1].date()}")
        print(f"最新收盘价: ${df['close'].iloc[-1]:.2f}")
        
        return df
    
    def preprocess_data(self, df):
        df = df.copy()
        
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean()
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
        
        df['atr'] = df[['high', 'low', 'close']].apply(
            lambda x: max(x['high'] - x['low'], 
                         abs(x['high'] - x['close'].shift()), 
                         abs(x['low'] - x['close'].shift())), axis=1
        ).rolling(14).mean()
        
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        df['daily_range'] = df['high'] - df['low']
        df['close_change'] = df['close'] - df['open']
        
        df = df.dropna()
        
        return df