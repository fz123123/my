import pandas as pd
import numpy as np
from data_cleaner import DataCleaner
from backtester import Backtester
from strategies import MovingAverageCrossover


def generate_simple_data():
    dates = pd.date_range(start='2020-01-01', periods=200, freq='B')
    
    prices = np.array([100.0 + i * 0.5 for i in range(100)] + 
                      [150.0 - (i-100) * 0.3 for i in range(100, 200)])
    
    data = pd.DataFrame({
        'Date': dates.astype('datetime64[ns]'),
        'Open': prices,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Close': prices,
        'Volume': 1000000,
        'symbol': 'TEST'
    })
    
    return data


data = generate_simple_data()
print(f"Data shape: {data.shape}")
print(f"Price range: {data['Close'].min():.2f} - {data['Close'].max():.2f}")

cleaner = DataCleaner()
cleaned_data = cleaner.clean_data(data)

backtester = Backtester(initial_capital=100000.0, commission_rate=0.0, slippage_rate=0.0)
strategy = MovingAverageCrossover(short_window=20, long_window=50)
strategy.set_backtester(backtester)

for i in range(len(cleaned_data)):
    current_data = cleaned_data.iloc[:i+1]
    backtester.current_date = current_data['Date'].iloc[-1]
    
    if len(current_data) >= 50:
        short_ma = current_data['Close'].rolling(window=20).mean().iloc[-1]
        long_ma = current_data['Close'].rolling(window=50).mean().iloc[-1]
        print(f"Day {i}: Close={current_data['Close'].iloc[-1]:.2f}, "
              f"Short MA={short_ma:.2f}, Long MA={long_ma:.2f}")
    
    strategy.on_data(current_data)

equity_curve = pd.DataFrame(backtester.equity_curve)
trade_logs = backtester.get_trade_logs()

print(f"\nNumber of trades: {len(trade_logs)}")
print(f"Final equity: ${equity_curve['Equity'].iloc[-1]:.2f}")

if not trade_logs.empty:
    print("\nTrade Logs:")
    print(trade_logs)
