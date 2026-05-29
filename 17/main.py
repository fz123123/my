from data_fetcher import DataFetcher
from data_cleaner import DataCleaner
from backtester import Backtester
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy, BollingerBandStrategy
from analyzer import PerformanceAnalyzer
from datetime import datetime, timedelta
import pandas as pd


def run_backtest(strategy_name: str, symbol: str, start_date: str, end_date: str):
    print(f"Starting backtest for {strategy_name} on {symbol}...")
    
    fetcher = DataFetcher()
    cleaner = DataCleaner()
    
    raw_data = fetcher.fetch_stock_data(symbol, start_date, end_date)
    print(f"Fetched {len(raw_data)} rows of raw data")
    
    cleaned_data = cleaner.clean_data(raw_data)
    print(f"Cleaned to {len(cleaned_data)} rows")
    
    print("\nCleaning Report:")
    print(cleaner.get_cleaning_report())
    
    backtester = Backtester(initial_capital=100000.0, commission_rate=0.001, slippage_rate=0.001)
    
    if strategy_name == 'ma_crossover':
        strategy = MovingAverageCrossover(short_window=50, long_window=200)
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
    
    print("\n" + "=" * 50)
    print(f"BACKTEST RESULTS: {strategy_name.upper()} Strategy")
    print("=" * 50)
    analyzer.print_summary()
    
    analyzer.plot_equity_curve(save_path=f'{strategy_name}_equity.png')
    analyzer.plot_drawdown(save_path=f'{strategy_name}_drawdown.png')
    analyzer.plot_returns_distribution(save_path=f'{strategy_name}_returns.png')
    
    analyzer.generate_report(file_path=f'{strategy_name}_report.txt')
    
    return analyzer.metrics


def compare_strategies(symbol: str, start_date: str, end_date: str):
    strategies = ['ma_crossover', 'rsi', 'macd', 'bollinger']
    results = {}
    
    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Testing {strategy.upper()} strategy")
        print('='*60)
        
        try:
            metrics = run_backtest(strategy, symbol, start_date, end_date)
            results[strategy] = metrics
        except Exception as e:
            print(f"Error running {strategy}: {e}")
            results[strategy] = None
    
    if results:
        summary_df = pd.DataFrame.from_dict(results, orient='index')
        summary_df = summary_df[['Total_Return', 'Annualized_Return', 'Max_Drawdown', 
                                'Sharpe_Ratio', 'Total_Trades', 'Win_Rate']]
        
        print("\n" + "="*60)
        print("STRATEGY COMPARISON SUMMARY")
        print("="*60)
        print(summary_df.round(4))
        
        summary_df.to_csv('strategy_comparison.csv')
        print("\nComparison saved to strategy_comparison.csv")


if __name__ == "__main__":
    symbol = "AAPL"
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Running backtest for {symbol} from {start_date} to {end_date}")
    
    compare_strategies(symbol, start_date, end_date)
