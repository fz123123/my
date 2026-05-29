import pandas as pd
import numpy as np
from datetime import datetime
from data_fetcher import DataFetcher
from data_cleaner import DataCleaner
from backtester import Backtester
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy, BollingerBandStrategy
from analyzer import PerformanceAnalyzer


def generate_summary_report(symbol: str = 'TEST', start_date: str = '2020-01-01', end_date: str = '2023-01-01'):
    print(f"Generating summary report for {symbol} ({start_date} to {end_date})...")
    
    def generate_test_data():
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n_days = len(dates)
        
        price = 150.0
        prices = []
        
        for i in range(n_days):
            if i < n_days * 0.3:
                base_return = -0.0015
            elif i < n_days * 0.6:
                base_return = 0.002
            else:
                base_return = -0.001
            
            noise = np.random.normal(0, 0.01)
            price *= (1 + base_return + noise)
            prices.append(price)
        
        prices = np.array(prices)
        data = pd.DataFrame({
            'Date': dates.astype('datetime64[ns]'),
            'Open': prices,
            'High': prices * (1 + np.random.uniform(0.001, 0.02, n_days)),
            'Low': prices * (1 - np.random.uniform(0.001, 0.02, n_days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, n_days),
            'symbol': symbol
        })
        
        return data
    
    data = generate_test_data()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_data(data)
    
    strategies = {
        'MA_Crossover': MovingAverageCrossover(short_window=20, long_window=50),
        'RSI': RSIStrategy(window=14, oversold_threshold=30, overbought_threshold=70),
        'MACD': MACDStrategy(fast_period=12, slow_period=26, signal_period=9),
        'Bollinger_Band': BollingerBandStrategy(window=20, num_std=2.0)
    }
    
    results = {}
    
    for name, strategy in strategies.items():
        backtester = Backtester(initial_capital=100000.0, commission_rate=0.001, 
                                slippage_rate=0.001, verbose=False, log_file=None)
        strategy.set_backtester(backtester)
        
        equity_curve = backtester.run_backtest(cleaned_data, strategy)
        trade_logs = backtester.get_trade_logs()
        
        analyzer = PerformanceAnalyzer(equity_curve, trade_logs)
        metrics = analyzer.calculate_metrics()
        
        results[name] = {
            'metrics': metrics,
            'equity_curve': equity_curve,
            'trade_logs': trade_logs
        }
    
    with open('backtest_summary_report.txt', 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("        QUANTITATIVE STRATEGY BACKTEST SUMMARY REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Symbol: {symbol}\n")
        f.write(f"Date Range: {start_date} to {end_date}\n")
        f.write(f"Total Trading Days: {len(cleaned_data)}\n")
        f.write(f"Initial Capital: $100,000\n")
        f.write(f"Commission Rate: 0.10%\n")
        f.write(f"Slippage Rate: 0.10%\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("1. STRATEGY PERFORMANCE SUMMARY\n")
        f.write("-" * 40 + "\n\n")
        
        for name, result in results.items():
            m = result['metrics']
            f.write(f"Strategy: {name}\n")
            f.write("-" * 20 + "\n")
            f.write(f"  Total Return:           {m.get('Total_Return', 0):.2%}\n")
            f.write(f"  Annualized Return:      {m.get('Annualized_Return', 0):.2%}\n")
            f.write(f"  Volatility:             {m.get('Volatility', 0):.2%}\n")
            f.write(f"  Sharpe Ratio:           {m.get('Sharpe_Ratio', 0):.2f}\n")
            f.write(f"  Max Drawdown:           {m.get('Max_Drawdown', 0):.2%}\n")
            f.write(f"  Calmar Ratio:           {m.get('Calmar_Ratio', 0):.2f}\n")
            f.write(f"  Total Trades:           {m.get('Total_Trades', 0):,}\n")
            f.write(f"  Win Rate:               {m.get('Win_Rate', 0):.2%}\n")
            f.write(f"  Final Equity:           ${m.get('Final_Equity', 0):,.2f}\n")
            f.write("\n")
        
        f.write("2. STRATEGY COMPARISON TABLE\n")
        f.write("-" * 40 + "\n\n")
        
        summary_data = []
        for name, result in results.items():
            m = result['metrics']
            summary_data.append({
                'Strategy': name,
                'Total Return': f"{m.get('Total_Return', 0):.2%}",
                'Annualized Return': f"{m.get('Annualized_Return', 0):.2%}",
                'Sharpe Ratio': f"{m.get('Sharpe_Ratio', 0):.2f}",
                'Max Drawdown': f"{m.get('Max_Drawdown', 0):.2%}",
                'Total Trades': f"{int(m.get('Total_Trades', 0)):,}",
                'Win Rate': f"{m.get('Win_Rate', 0):.2%}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        f.write(summary_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("3. BEST PERFORMING STRATEGY\n")
        f.write("-" * 40 + "\n\n")
        
        best_strategy = max(results.items(), key=lambda x: x[1]['metrics'].get('Total_Return', 0))
        name = best_strategy[0]
        m = best_strategy[1]['metrics']
        
        f.write(f"Top Strategy: {name}\n")
        f.write(f"Reason: Highest Total Return ({m.get('Total_Return', 0):.2%})\n")
        f.write("\nKey Metrics:\n")
        f.write(f"  - Total Return:      {m.get('Total_Return', 0):.2%}\n")
        f.write(f"  - Annualized Return: {m.get('Annualized_Return', 0):.2%}\n")
        f.write(f"  - Sharpe Ratio:      {m.get('Sharpe_Ratio', 0):.2f}\n")
        f.write(f"  - Max Drawdown:      {m.get('Max_Drawdown', 0):.2%}\n")
        f.write(f"  - Total Trades:      {m.get('Total_Trades', 0):,}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("         END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print("Report generated: backtest_summary_report.txt")
    
    return results


if __name__ == "__main__":
    generate_summary_report()
