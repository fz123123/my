import pandas as pd
import os
from backtester import Backtester
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy, BollingerBandStrategy
from analyzer import PerformanceAnalyzer


def run_backtest_with_cleaned_data(data_dir: str = "cleaned_data"):
    print("=" * 60)
    print("BACKTEST WITH CLEANED DATA")
    print("=" * 60)
    
    cleaned_files = [f for f in os.listdir(data_dir) if f.endswith('_cleaned.csv')]
    
    if not cleaned_files:
        print(f"No cleaned data files found in {data_dir}")
        return
    
    print(f"Found {len(cleaned_files)} cleaned data files")
    print(f"Files: {cleaned_files}")
    
    all_results = {}
    
    for filename in cleaned_files:
        symbol = filename.replace('_cleaned.csv', '')
        filepath = os.path.join(data_dir, filename)
        
        print(f"\n{'='*40}")
        print(f"Processing {symbol}")
        print(f"{'='*40}")
        
        try:
            print(f"Step 1: Loading cleaned data...")
            data = pd.read_csv(filepath, parse_dates=['Date'])
            print(f"   Data loaded: {len(data)} rows")
            print(f"   Date range: {data['Date'].min().date()} to {data['Date'].max().date()}")
            
            strategies = {
                'MA_Crossover': MovingAverageCrossover(short_window=20, long_window=50),
                'RSI': RSIStrategy(window=14, oversold_threshold=30, overbought_threshold=70),
                'MACD': MACDStrategy(fast_period=12, slow_period=26, signal_period=9),
                'Bollinger_Band': BollingerBandStrategy(window=20, num_std=2.0)
            }
            
            symbol_results = {}
            
            for strategy_name, strategy in strategies.items():
                print(f"\n   Running {strategy_name} strategy...")
                
                backtester = Backtester(initial_capital=100000.0, commission_rate=0.001, 
                                        slippage_rate=0.001, verbose=False, log_file=None)
                strategy.set_backtester(backtester)
                
                equity_curve = backtester.run_backtest(data, strategy)
                trade_logs = backtester.get_trade_logs()
                
                analyzer = PerformanceAnalyzer(equity_curve, trade_logs)
                metrics = analyzer.calculate_metrics()
                
                symbol_results[strategy_name] = {
                    'metrics': metrics,
                    'equity_curve': equity_curve,
                    'trade_logs': trade_logs
                }
                
                print(f"      Total Return: {metrics.get('Total_Return', 0):.2%}")
                print(f"      Sharpe Ratio: {metrics.get('Sharpe_Ratio', 0):.2f}")
                print(f"      Max Drawdown: {metrics.get('Max_Drawdown', 0):.2%}")
                print(f"      Total Trades: {metrics.get('Total_Trades', 0)}")
            
            all_results[symbol] = symbol_results
        
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
    
    print("\n" + "=" * 60)
    print("BACKTEST SUMMARY REPORT")
    print("=" * 60)
    
    summary_data = []
    for symbol, strategies in all_results.items():
        for strategy_name, result in strategies.items():
            m = result['metrics']
            summary_data.append({
                'Symbol': symbol,
                'Strategy': strategy_name,
                'Total Return': f"{m.get('Total_Return', 0):.2%}",
                'Annualized Return': f"{m.get('Annualized_Return', 0):.2%}",
                'Sharpe Ratio': f"{m.get('Sharpe_Ratio', 0):.2f}",
                'Max Drawdown': f"{m.get('Max_Drawdown', 0):.2%}",
                'Total Trades': int(m.get('Total_Trades', 0))
            })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    report_path = os.path.join(data_dir, 'backtest_summary_report.txt')
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("        BACKTEST SUMMARY REPORT (Cleaned Data)\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated on: {pd.Timestamp.now()}\n")
        f.write(f"Number of Symbols: {len(all_results)}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("1. STRATEGY PERFORMANCE SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(summary_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("2. BEST PERFORMING STRATEGIES\n")
        f.write("-" * 30 + "\n\n")
        
        for symbol, strategies in all_results.items():
            best_strategy = max(strategies.items(), key=lambda x: x[1]['metrics'].get('Total_Return', 0))
            name = best_strategy[0]
            m = best_strategy[1]['metrics']
            
            f.write(f"Symbol: {symbol}\n")
            f.write(f"Best Strategy: {name}\n")
            f.write(f"Total Return: {m.get('Total_Return', 0):.2%}\n")
            f.write(f"Annualized Return: {m.get('Annualized_Return', 0):.2%}\n")
            f.write(f"Sharpe Ratio: {m.get('Sharpe_Ratio', 0):.2f}\n")
            f.write(f"Max Drawdown: {m.get('Max_Drawdown', 0):.2%}\n")
            f.write(f"Total Trades: {m.get('Total_Trades', 0)}\n")
            f.write("\n" + "-" * 50 + "\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("         END OF REPORT\n")
        f.write("=" * 70 + "\n")
    
    print(f"\nReport saved to: {report_path}")
    
    return all_results


if __name__ == "__main__":
    run_backtest_with_cleaned_data()
