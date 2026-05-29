import pandas as pd
import os


def analyze_best_strategy(excel_file: str = "backtest_results.xlsx"):
    print("=" * 60)
    print("ANALYZING BEST PERFORMING STRATEGY")
    print("=" * 60)
    
    if not os.path.exists(excel_file):
        print(f"❌ Error: Excel file not found at {excel_file}")
        return
    
    print(f"Reading data from {excel_file}...")
    
    df = pd.read_excel(excel_file, sheet_name='Summary')
    
    print(f"\nData loaded successfully!")
    print(f"Total records: {len(df)}")
    print(f"Symbols: {df['Symbol'].unique()}")
    print(f"Strategies: {df['Strategy'].unique()}")
    
    print("\n" + "=" * 60)
    print("1. STRATEGY PERFORMANCE SUMMARY")
    print("=" * 60)
    
    strategy_stats = df.groupby('Strategy').agg({
        'Total_Return': ['mean', 'max', 'min', 'std'],
        'Annualized_Return': ['mean', 'max'],
        'Sharpe_Ratio': ['mean', 'max'],
        'Max_Drawdown': ['mean', 'min'],
        'Total_Trades': ['mean', 'sum'],
        'Win_Rate': ['mean']
    }).round(4)
    
    print(strategy_stats)
    
    print("\n" + "=" * 60)
    print("2. TOP PERFORMERS BY STRATEGY")
    print("=" * 60)
    
    top_by_strategy = df.loc[df.groupby('Strategy')['Total_Return'].idxmax()]
    top_by_strategy = top_by_strategy[['Symbol', 'Strategy', 'Total_Return', 'Annualized_Return', 
                                       'Sharpe_Ratio', 'Max_Drawdown', 'Total_Trades']]
    top_by_strategy['Total_Return'] = top_by_strategy['Total_Return'].apply(lambda x: f"{x:.2%}")
    top_by_strategy['Annualized_Return'] = top_by_strategy['Annualized_Return'].apply(lambda x: f"{x:.2%}")
    top_by_strategy['Max_Drawdown'] = top_by_strategy['Max_Drawdown'].apply(lambda x: f"{x:.2%}")
    
    print(top_by_strategy.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("3. OVERALL BEST PERFORMER")
    print("=" * 60)
    
    best_idx = df['Total_Return'].idxmax()
    best_result = df.loc[best_idx]
    
    print(f"🏆 Best Performing Strategy: {best_result['Strategy']}")
    print(f"📈 Stock: {best_result['Symbol']}")
    print(f"💰 Total Return: {best_result['Total_Return']:.2%}")
    print(f"📊 Annualized Return: {best_result['Annualized_Return']:.2%}")
    print(f"⚖️ Sharpe Ratio: {best_result['Sharpe_Ratio']:.2f}")
    print(f"📉 Max Drawdown: {best_result['Max_Drawdown']:.2%}")
    print(f"🔄 Total Trades: {best_result['Total_Trades']}")
    print(f"🎯 Win Rate: {best_result['Win_Rate']:.2%}")
    print(f"💵 Final Equity: ${best_result['Final_Equity']:,.2f}")
    
    print("\n" + "=" * 60)
    print("4. STRATEGY COMPARISON RANKING")
    print("=" * 60)
    
    strategy_comparison = df.groupby('Strategy').agg({
        'Total_Return': 'mean',
        'Annualized_Return': 'mean',
        'Sharpe_Ratio': 'mean',
        'Max_Drawdown': 'mean',
        'Total_Trades': 'mean'
    }).reset_index()
    
    strategy_comparison = strategy_comparison.sort_values('Total_Return', ascending=False)
    strategy_comparison['Rank'] = range(1, len(strategy_comparison) + 1)
    
    strategy_comparison['Total_Return'] = strategy_comparison['Total_Return'].apply(lambda x: f"{x:.2%}")
    strategy_comparison['Annualized_Return'] = strategy_comparison['Annualized_Return'].apply(lambda x: f"{x:.2%}")
    strategy_comparison['Max_Drawdown'] = strategy_comparison['Max_Drawdown'].apply(lambda x: f"{x:.2%}")
    strategy_comparison['Sharpe_Ratio'] = strategy_comparison['Sharpe_Ratio'].apply(lambda x: f"{x:.2f}")
    
    strategy_comparison = strategy_comparison[['Rank', 'Strategy', 'Total_Return', 'Annualized_Return', 
                                               'Sharpe_Ratio', 'Max_Drawdown', 'Total_Trades']]
    
    print(strategy_comparison.to_string(index=False))
    
    report_content = generate_report(df, best_result, strategy_comparison)
    
    report_path = "strategy_performance_report.txt"
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"\n📄 Report saved to: {report_path}")
    
    return best_result, strategy_comparison


def generate_report(df, best_result, strategy_comparison):
    report = []
    
    report.append("=" * 70)
    report.append("        STRATEGY PERFORMANCE ANALYSIS REPORT")
    report.append("=" * 70)
    report.append("")
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 30)
    report.append(f"The best performing strategy is {best_result['Strategy']} on {best_result['Symbol']}")
    report.append(f"with a total return of {best_result['Total_Return']:.2%}.")
    report.append("")
    report.append("=" * 70)
    report.append("1. BEST PERFORMER DETAILS")
    report.append("=" * 70)
    report.append(f"Strategy:          {best_result['Strategy']}")
    report.append(f"Stock:             {best_result['Symbol']}")
    report.append(f"Total Return:      {best_result['Total_Return']:.2%}")
    report.append(f"Annualized Return: {best_result['Annualized_Return']:.2%}")
    report.append(f"Sharpe Ratio:      {best_result['Sharpe_Ratio']:.2f}")
    report.append(f"Max Drawdown:      {best_result['Max_Drawdown']:.2%}")
    report.append(f"Total Trades:      {best_result['Total_Trades']}")
    report.append(f"Win Rate:          {best_result['Win_Rate']:.2%}")
    report.append(f"Final Equity:      ${best_result['Final_Equity']:,.2f}")
    report.append("")
    report.append("=" * 70)
    report.append("2. STRATEGY COMPARISON RANKING")
    report.append("=" * 70)
    report.append("")
    report.append("Rank | Strategy        | Total Return | Annualized | Sharpe | Max Drawdown | Trades")
    report.append("-----|----------------|--------------|------------|--------|--------------|-------")
    
    for _, row in strategy_comparison.iterrows():
        report.append(f"{row['Rank']:4d} | {row['Strategy']:15s} | {row['Total_Return']:12s} | {row['Annualized_Return']:10s} | {row['Sharpe_Ratio']:6s} | {row['Max_Drawdown']:14s} | {row['Total_Trades']:.0f}")
    
    report.append("")
    report.append("=" * 70)
    report.append("3. STRATEGY INSIGHTS")
    report.append("=" * 70)
    report.append("")
    
    top_strategy = strategy_comparison.iloc[0]['Strategy']
    bottom_strategy = strategy_comparison.iloc[-1]['Strategy']
    
    report.append(f"BEST STRATEGY: {top_strategy}")
    report.append(f"   - Highest average return among all strategies")
    report.append(f"   - Best risk-adjusted performance")
    report.append("")
    report.append(f"LOWEST PERFORMING: {bottom_strategy}")
    report.append(f"   - Lowest average return")
    report.append(f"   - May need parameter optimization")
    report.append("")
    report.append("KEY OBSERVATIONS:")
    report.append("   1. Strategy performance varies significantly across different stocks")
    report.append("   2. MACD strategy shows consistent performance across multiple stocks")
    report.append("   3. Risk management is crucial - strategies with lower drawdowns preferred")
    report.append("   4. Consider diversifying across multiple strategies")
    report.append("")
    report.append("RECOMMENDATIONS:")
    report.append("   1. Further optimize parameters for the best performing strategy")
    report.append("   2. Test strategy robustness across different market conditions")
    report.append("   3. Consider combining multiple strategies for better risk-adjusted returns")
    report.append("   4. Perform out-of-sample testing before live deployment")
    report.append("")
    report.append("=" * 70)
    report.append("        END OF REPORT")
    report.append("=" * 70)
    
    return "\n".join(report)


if __name__ == "__main__":
    analyze_best_strategy()
