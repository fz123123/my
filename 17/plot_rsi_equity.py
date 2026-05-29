import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from data_cleaner import DataCleaner
from backtester import Backtester
from strategies import RSIStrategy
from analyzer import PerformanceAnalyzer


def generate_rsi_equity_curve():
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    
    print(f"Generating RSI strategy equity curve from {start_date} to {end_date}...")
    
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
        'symbol': 'TEST'
    })
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_data(data)
    
    backtester = Backtester(initial_capital=100000.0, commission_rate=0.001, 
                            slippage_rate=0.001, verbose=False, log_file=None)
    strategy = RSIStrategy(window=14, oversold_threshold=30, overbought_threshold=70)
    strategy.set_backtester(backtester)
    
    equity_curve = backtester.run_backtest(cleaned_data, strategy)
    trade_logs = backtester.get_trade_logs()
    
    analyzer = PerformanceAnalyzer(equity_curve, trade_logs)
    metrics = analyzer.calculate_metrics()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    ax1.plot(equity_curve['Date'], equity_curve['Equity'], label='Total Equity', color='blue', linewidth=2)
    ax1.plot(equity_curve['Date'], equity_curve['Cash'], label='Cash', color='green', linewidth=1.5, linestyle='--')
    ax1.plot(equity_curve['Date'], equity_curve['Positions_Value'], label='Positions', color='orange', linewidth=1.5, linestyle='-.')
    
    for _, trade in trade_logs.iterrows():
        date = trade['date']
        if trade['direction'] == 'buy':
            ax1.scatter(date, equity_curve[equity_curve['Date'] == date]['Equity'].values[0], 
                       color='green', marker='^', s=100, label='Buy' if 'Buy' not in ax1.legend().get_texts() else "")
        else:
            ax1.scatter(date, equity_curve[equity_curve['Date'] == date]['Equity'].values[0], 
                       color='red', marker='v', s=100, label='Sell' if 'Sell' not in ax1.legend().get_texts() else "")
    
    ax1.set_title('RSI Strategy Equity Curve', fontsize=16, pad=20)
    ax1.set_ylabel('Value ($)', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('#f8f9fa')
    
    equity = equity_curve['Equity']
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    
    ax2.fill_between(equity_curve['Date'], drawdown, 0, where=drawdown < 0, 
                    color='red', alpha=0.3, label='Drawdown')
    ax2.plot(equity_curve['Date'], drawdown, color='red', linewidth=1)
    
    ax2.set_title('Drawdown', fontsize=14)
    ax2.set_ylabel('Drawdown (%)', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('#f8f9fa')
    
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_minor_locator(mdates.MonthLocator())
    
    plt.tight_layout()
    
    summary_text = f"""Strategy: RSI (14-period)
Initial Capital: $100,000
Final Equity: ${metrics.get('Final_Equity', 0):,.2f}
Total Return: {metrics.get('Total_Return', 0):.2%}
Annualized Return: {metrics.get('Annualized_Return', 0):.2%}
Sharpe Ratio: {metrics.get('Sharpe_Ratio', 0):.2f}
Max Drawdown: {metrics.get('Max_Drawdown', 0):.2%}
Total Trades: {metrics.get('Total_Trades', 0):,}"""
    
    fig.text(0.98, 0.95, summary_text, fontsize=10, 
             ha='right', va='top', bbox=dict(facecolor='white', alpha=0.9))
    
    plt.savefig('rsi_equity_curve.png', dpi=300, bbox_inches='tight')
    print("Equity curve saved to: rsi_equity_curve.png")
    
    print("\nRSI Strategy Performance Summary:")
    print("-" * 40)
    print(f"Initial Capital:  ${100000:,}")
    print(f"Final Equity:     ${metrics.get('Final_Equity', 0):,.2f}")
    print(f"Total Return:     {metrics.get('Total_Return', 0):.2%}")
    print(f"Annualized Return:{metrics.get('Annualized_Return', 0):.2%}")
    print(f"Sharpe Ratio:     {metrics.get('Sharpe_Ratio', 0):.2f}")
    print(f"Max Drawdown:     {metrics.get('Max_Drawdown', 0):.2%}")
    print(f"Total Trades:     {metrics.get('Total_Trades', 0):,}")
    print(f"Win Rate:         {metrics.get('Win_Rate', 0):.2%}")


if __name__ == "__main__":
    generate_rsi_equity_curve()
