import pandas as pd
import numpy as np
from data_cleaner import DataCleaner
from backtester import Backtester
from strategies import MovingAverageCrossover


def generate_test_data():
    dates = pd.date_range(start='2020-01-01', periods=250, freq='B')
    
    prices = []
    price = 150.0
    
    for i in range(80):
        price -= 0.5
        prices.append(price)
    
    for i in range(120):
        price += 0.4
        prices.append(price)
    
    for i in range(50):
        price -= 0.3
        prices.append(price)
    
    prices = np.array(prices)
    
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


data = generate_test_data()
print(f"Data shape: {data.shape}")
print(f"Price range: {data['Close'].min():.2f} - {data['Close'].max():.2f}")

cleaner = DataCleaner()
cleaned_data = cleaner.clean_data(data)

backtester = Backtester(initial_capital=100000.0, commission_rate=0.0, slippage_rate=0.0)
strategy = MovingAverageCrossover(short_window=20, long_window=50)
strategy.set_backtester(backtester)

print("\nRunning backtest with MA crossover strategy...")
equity_df = backtester.run_backtest(cleaned_data, strategy)

print("\nDetected signals during backtest:")
print("Day | Close | Short MA | Long MA | Signal")
print("----|-------|----------|---------|-------")
for i in range(len(cleaned_data)):
    if len(cleaned_data.iloc[:i+1]) >= 50:
        current_data = cleaned_data.iloc[:i+1]
        short_ma = current_data['Close'].rolling(window=20).mean().iloc[-1]
        long_ma = current_data['Close'].rolling(window=50).mean().iloc[-1]
        
        prev_short_ma = current_data['Close'].rolling(window=20).mean().iloc[-2]
        prev_long_ma = current_data['Close'].rolling(window=50).mean().iloc[-2]
        
        signal = ""
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            signal = "BUY"
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            signal = "SELL"
        
        if signal:
            print(f"{i:4d} | {current_data['Close'].iloc[-1]:6.2f} | {short_ma:8.2f} | {long_ma:7.2f} | {signal}")
trade_logs = backtester.get_trade_logs()

print(f"\nNumber of trades: {len(trade_logs)}")
print(f"Initial equity: ${equity_df['Equity'].iloc[0]:.2f}")
print(f"Final equity: ${equity_df['Equity'].iloc[-1]:.2f}")
print(f"Total return: {(equity_df['Equity'].iloc[-1] / equity_df['Equity'].iloc[0] - 1):.2%}")

if not trade_logs.empty:
    print("\nTrade Logs:")
    print(trade_logs[['date', 'direction', 'quantity', 'fill_price']])
