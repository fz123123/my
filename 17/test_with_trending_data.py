import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_cleaner import DataCleaner
from backtester import Backtester
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy, BollingerBandStrategy
from analyzer import PerformanceAnalyzer


def generate_trending_data(start_date: str, end_date: str, symbol: str = 'TEST') -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    n_days = len(dates)
    
    price = 100.0
    prices = []
    
    for i in range(n_days):
        base_return = 0.001
        
        if i < n_days * 0.3:
            base_return = 0.002
        elif i < n_days * 0.6:
            base_return = -0.0015
        else:
            base_return = 0.0015
        
        noise = np.random.normal(0, 0.01)
        price *= (1 + base_return + noise)
        prices.append(price)
    
    prices = np.array(prices)
    high = prices * (1 + np.random.uniform(0.001, 0.02, n_days))
    low = prices * (1 - np.random.uniform(0.001, 0.02, n_days))
    open_price = prices * (1 + np.random.uniform(-0.003, 0.003, n_days))
    volume = np.random.randint(1000000, 10000000, n_days)
    
    data = pd.DataFrame({
        'Date': dates.astype('datetime64[ns]'),
        'Open': open_price.round(2),
        'High': high.round(2),
        'Low': low.round(2),
        'Close': prices.round(2),
        'Volume': volume,
        'symbol': symbol
    })
    
    return data


def run_backtest(strategy_name: str, data: pd.DataFrame):
    print(f"Running {strategy_name} strategy...")
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_data(data)
    print(f"Data: {len(data)} -> {len(cleaned_data)} rows")
    
    backtester = Backtester(initial_capital=100000.0, commission_rate=0.001, slippage_rate=0.001)
    
    if strategy_name == 'ma_crossover':
        strategy = MovingAverageCrossover(short_window=20, long_window=50)
    elif strategy_name == 'rsi':
        strategy = RSIStrategy(window=14, oversold_threshold=30, overbought_threshold=70)
    elif strategy_name == 'macd':
        strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    elif strategy_name == 'bollinger':
        strategy = BollingerBandStrategy(window=20, num_std=2.0)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    strategy.set_backtester(backtester)
    
    equity_curve = backtester.run_backtest(cleaned_data, strategy)
    trade_logs = backtester.get_trade_logs()
    
    analyzer = PerformanceAnalyzer(equity_curve, trade_logs)
    analyzer.calculate_metrics()
    
    print(f"\n{strategy_name.upper()} RESULTS:")
    analyzer.print_summary()
    
    analyzer.generate_report(file_path=f'{strategy_name}_report.txt')
    
    return analyzer.metrics


if __name__ == "__main__":
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    
    print(f"Generating trending data from {start_date} to {end_date}...")
    data = generate_trending_data(start_date, end_date)
    print(f"Generated {len(data)} rows of trending data")
    print(f"Initial price: ${data['Close'].iloc[0]:.2f}")
    print(f"Final price: ${data['Close'].iloc[-1]:.2f}")
    
    strategies = ['ma_crossover', 'rsi', 'macd', 'bollinger']
    results = {}
    
    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Testing {strategy.upper()} strategy")
        print('='*60)
        
        try:
            metrics = run_backtest(strategy, data.copy())
            results[strategy] = metrics
        except Exception as e:
            print(f"Error running {strategy}: {e}")
            results[strategy] = None
    
    if results and any(results.values()):
        valid_results = {k: v for k, v in results.items() if v is not None}
        summary_df = pd.DataFrame.from_dict(valid_results, orient='index')
        summary_df = summary_df[['Total_Return', 'Annualized_Return', 'Max_Drawdown', 
                                'Sharpe_Ratio', 'Total_Trades', 'Win_Rate']]
        
        print("\n" + "="*60)
        print("STRATEGY COMPARISON SUMMARY")
        print("="*60)
        print(summary_df.round(4))
        
        summary_df.to_csv('strategy_comparison.csv')
        print("\nComparison saved to strategy_comparison.csv")
