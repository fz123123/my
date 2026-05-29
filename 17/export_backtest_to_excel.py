import pandas as pd
import os
from backtester import Backtester
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy, BollingerBandStrategy
from analyzer import PerformanceAnalyzer


def export_backtest_to_excel(data_dir: str = "cleaned_data", output_file: str = "backtest_results.xlsx"):
    print("=" * 60)
    print("EXPORTING BACKTEST RESULTS TO EXCEL")
    print("=" * 60)
    
    cleaned_files = [f for f in os.listdir(data_dir) if f.endswith('_cleaned.csv')]
    
    if not cleaned_files:
        print(f"No cleaned data files found in {data_dir}")
        return
    
    print(f"Found {len(cleaned_files)} cleaned data files")
    
    all_results = {}
    all_equity_curves = {}
    all_trade_logs = {}
    
    for filename in cleaned_files:
        symbol = filename.replace('_cleaned.csv', '')
        filepath = os.path.join(data_dir, filename)
        
        print(f"\nProcessing {symbol}...")
        
        try:
            data = pd.read_csv(filepath, parse_dates=['Date'])
            
            strategies = {
                'MA_Crossover': MovingAverageCrossover(short_window=20, long_window=50),
                'RSI': RSIStrategy(window=14, oversold_threshold=30, overbought_threshold=70),
                'MACD': MACDStrategy(fast_period=12, slow_period=26, signal_period=9),
                'Bollinger_Band': BollingerBandStrategy(window=20, num_std=2.0)
            }
            
            symbol_results = {}
            symbol_equity_curves = {}
            symbol_trade_logs = {}
            
            for strategy_name, strategy in strategies.items():
                backtester = Backtester(initial_capital=100000.0, commission_rate=0.001, 
                                        slippage_rate=0.001, verbose=False, log_file=None)
                strategy.set_backtester(backtester)
                
                equity_curve = backtester.run_backtest(data, strategy)
                trade_logs = backtester.get_trade_logs()
                
                analyzer = PerformanceAnalyzer(equity_curve, trade_logs)
                metrics = analyzer.calculate_metrics()
                
                symbol_results[strategy_name] = metrics
                symbol_equity_curves[strategy_name] = equity_curve
                symbol_trade_logs[strategy_name] = trade_logs
            
            all_results[symbol] = symbol_results
            all_equity_curves[symbol] = symbol_equity_curves
            all_trade_logs[symbol] = symbol_trade_logs
            
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
    
    print("\nGenerating Excel report...")
    
    summary_data = []
    for symbol, strategies in all_results.items():
        for strategy_name, metrics in strategies.items():
            summary_data.append({
                'Symbol': symbol,
                'Strategy': strategy_name,
                'Total_Return': metrics.get('Total_Return', 0),
                'Annualized_Return': metrics.get('Annualized_Return', 0),
                'Volatility': metrics.get('Volatility', 0),
                'Sharpe_Ratio': metrics.get('Sharpe_Ratio', 0),
                'Sortino_Ratio': metrics.get('Sortino_Ratio', 0),
                'Max_Drawdown': metrics.get('Max_Drawdown', 0),
                'Calmar_Ratio': metrics.get('Calmar_Ratio', 0),
                'Win_Rate': metrics.get('Win_Rate', 0),
                'Profit_Factor': metrics.get('Profit_Factor', 0),
                'Total_Trades': metrics.get('Total_Trades', 0),
                'Final_Equity': metrics.get('Final_Equity', 0)
            })
    
    summary_df = pd.DataFrame(summary_data)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        summary_formatted = summary_df.copy()
        summary_formatted['Total_Return'] = summary_formatted['Total_Return'].apply(lambda x: f"{x:.2%}")
        summary_formatted['Annualized_Return'] = summary_formatted['Annualized_Return'].apply(lambda x: f"{x:.2%}")
        summary_formatted['Volatility'] = summary_formatted['Volatility'].apply(lambda x: f"{x:.2%}")
        summary_formatted['Max_Drawdown'] = summary_formatted['Max_Drawdown'].apply(lambda x: f"{x:.2%}")
        summary_formatted['Win_Rate'] = summary_formatted['Win_Rate'].apply(lambda x: f"{x:.2%}")
        summary_formatted['Final_Equity'] = summary_formatted['Final_Equity'].apply(lambda x: f"${x:,.2f}")
        summary_formatted.to_excel(writer, sheet_name='Summary_Formatted', index=False)
        
        for symbol, strategies in all_equity_curves.items():
            for strategy_name, equity_curve in strategies.items():
                sheet_name = f"{symbol}_{strategy_name}"[:31]
                equity_curve.to_excel(writer, sheet_name=sheet_name, index=False)
        
        for symbol, strategies in all_trade_logs.items():
            for strategy_name, trade_logs in strategies.items():
                if not trade_logs.empty:
                    sheet_name = f"{symbol}_{strategy_name}_Trades"[:31]
                    trade_logs.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\nExcel file saved to: {output_file}")
    print(f"\nExcel file structure:")
    print("-" * 40)
    print("1. Summary - Raw numerical results")
    print("2. Summary_Formatted - Human-readable formatted results")
    print("3. {Symbol}_{Strategy} - Equity curves for each strategy")
    print("4. {Symbol}_{Strategy}_Trades - Trade logs (if any)")
    
    return output_file


if __name__ == "__main__":
    export_backtest_to_excel()
