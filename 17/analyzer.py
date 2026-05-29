import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, Any, Optional


class PerformanceAnalyzer:
    def __init__(self, equity_curve: pd.DataFrame, trade_logs: pd.DataFrame = None):
        self.equity_curve = equity_curve
        self.trade_logs = trade_logs
        self.metrics = {}
    
    def calculate_metrics(self) -> Dict[str, float]:
        if self.equity_curve.empty:
            return {}
        
        equity = self.equity_curve['Equity']
        returns = equity.pct_change().fillna(0)
        
        total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
        
        num_days = len(self.equity_curve)
        annualized_return = (1 + total_return) ** (252 / num_days) - 1
        
        volatility = returns.std() * np.sqrt(252)
        
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0.0
        
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
        
        sortino_ratio = self._calculate_sortino_ratio(returns)
        
        win_days = returns[returns > 0].count()
        total_days = len(returns)
        win_rate = win_days / total_days if total_days > 0 else 0.0
        
        avg_win = returns[returns > 0].mean()
        avg_loss = returns[returns < 0].mean()
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0.0
        
        self.metrics = {
            'Total_Return': total_return,
            'Annualized_Return': annualized_return,
            'Volatility': volatility,
            'Sharpe_Ratio': sharpe_ratio,
            'Sortino_Ratio': sortino_ratio,
            'Max_Drawdown': max_drawdown,
            'Calmar_Ratio': calmar_ratio,
            'Win_Rate': win_rate,
            'Profit_Factor': profit_factor,
            'Avg_Daily_Return': returns.mean(),
            'Std_Daily_Return': returns.std(),
            'Best_Day': returns.max(),
            'Worst_Day': returns.min(),
            'Final_Equity': equity.iloc[-1]
        }
        
        if self.trade_logs is not None and not self.trade_logs.empty:
            self._calculate_trade_metrics()
        
        return self.metrics
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        
        annualized_return = (1 + returns.sum()) ** (252 / len(returns)) - 1
        
        return annualized_return / downside_std if downside_std > 0 else 0.0
    
    def _calculate_trade_metrics(self) -> None:
        if self.trade_logs is None or self.trade_logs.empty:
            return
        
        trades = self.trade_logs.copy()
        trades['pnl'] = trades.apply(lambda row: 
            (row['fill_price'] - self._get_entry_price(row)) * row['quantity'] 
            if row['direction'] == 'sell' else 0, axis=1
        )
        
        total_pnl = trades['pnl'].sum()
        avg_trade_pnl = trades['pnl'].mean() if len(trades) > 0 else 0.0
        
        winning_trades = trades[trades['pnl'] > 0]
        losing_trades = trades[trades['pnl'] <= 0]
        
        win_rate = len(winning_trades) / len(trades) if len(trades) > 0 else 0.0
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0.0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0.0
        
        profit_factor = avg_win / abs(avg_loss) if avg_loss != 0 else 0.0
        
        self.metrics.update({
            'Total_Trades': len(trades),
            'Total_PnL': total_pnl,
            'Avg_Trade_PnL': avg_trade_pnl,
            'Trade_Win_Rate': win_rate,
            'Avg_Win': avg_win,
            'Avg_Loss': avg_loss,
            'Trade_Profit_Factor': profit_factor
        })
    
    def _get_entry_price(self, trade_row: pd.Series) -> float:
        if self.trade_logs is None:
            return 0.0
        
        entry_trades = self.trade_logs[
            (self.trade_logs['symbol'] == trade_row['symbol']) &
            (self.trade_logs['direction'] == 'buy') &
            (self.trade_logs['date'] < trade_row['date'])
        ]
        
        if entry_trades.empty:
            return 0.0
        
        return entry_trades.iloc[-1]['fill_price']
    
    def plot_equity_curve(self, save_path: str = None) -> None:
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve['Date'], self.equity_curve['Equity'], label='Equity', color='blue')
        plt.plot(self.equity_curve['Date'], self.equity_curve['Cash'], label='Cash', color='green')
        plt.plot(self.equity_curve['Date'], self.equity_curve['Positions_Value'], label='Positions', color='orange')
        
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Value ($)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        plt.show()
    
    def plot_drawdown(self, save_path: str = None) -> None:
        equity = self.equity_curve['Equity']
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        
        plt.figure(figsize=(12, 6))
        plt.fill_between(self.equity_curve['Date'], drawdown, 0, alpha=0.3, color='red')
        plt.plot(self.equity_curve['Date'], drawdown, label='Drawdown', color='red')
        
        plt.title('Drawdown')
        plt.xlabel('Date')
        plt.ylabel('Drawdown (%)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        plt.show()
    
    def plot_returns_distribution(self, save_path: str = None) -> None:
        returns = self.equity_curve['Return']
        
        plt.figure(figsize=(12, 6))
        sns.histplot(returns, kde=True, bins=50, color='blue')
        
        plt.title('Daily Returns Distribution')
        plt.xlabel('Daily Return')
        plt.ylabel('Frequency')
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        plt.show()
    
    def print_summary(self) -> None:
        if not self.metrics:
            self.calculate_metrics()
        
        print("=" * 50)
        print("PERFORMANCE ANALYSIS SUMMARY")
        print("=" * 50)
        
        print("\n[Return Metrics]")
        print(f"Total Return:          {self.metrics.get('Total_Return', 0):.2%}")
        print(f"Annualized Return:     {self.metrics.get('Annualized_Return', 0):.2%}")
        print(f"Average Daily Return:  {self.metrics.get('Avg_Daily_Return', 0):.2%}")
        print(f"Best Day:              {self.metrics.get('Best_Day', 0):.2%}")
        print(f"Worst Day:             {self.metrics.get('Worst_Day', 0):.2%}")
        
        print("\n[Risk Metrics]")
        print(f"Volatility:            {self.metrics.get('Volatility', 0):.2%}")
        print(f"Max Drawdown:          {self.metrics.get('Max_Drawdown', 0):.2%}")
        
        print("\n[Risk-Adjusted Returns]")
        print(f"Sharpe Ratio:          {self.metrics.get('Sharpe_Ratio', 0):.2f}")
        print(f"Sortino Ratio:         {self.metrics.get('Sortino_Ratio', 0):.2f}")
        print(f"Calmar Ratio:          {self.metrics.get('Calmar_Ratio', 0):.2f}")
        
        print("\n[Trade Metrics]")
        print(f"Total Trades:          {self.metrics.get('Total_Trades', 0):,}")
        print(f"Win Rate:              {self.metrics.get('Win_Rate', 0):.2%}")
        print(f"Profit Factor:         {self.metrics.get('Profit_Factor', 0):.2f}")
        
        if 'Total_PnL' in self.metrics:
            print(f"Total PnL:             ${self.metrics.get('Total_PnL', 0):,.2f}")
            print(f"Average Trade PnL:     ${self.metrics.get('Avg_Trade_PnL', 0):,.2f}")
        
        print("=" * 50)
    
    def generate_report(self, file_path: str = 'backtest_report.txt') -> None:
        if not self.metrics:
            self.calculate_metrics()
        
        with open(file_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("QUANTITATIVE STRATEGY BACKTEST REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            
            f.write("1. RETURN METRICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Return:          {self.metrics.get('Total_Return', 0):.2%}\n")
            f.write(f"Annualized Return:     {self.metrics.get('Annualized_Return', 0):.2%}\n")
            f.write(f"Average Daily Return:  {self.metrics.get('Avg_Daily_Return', 0):.4f}\n")
            f.write(f"Best Day:              {self.metrics.get('Best_Day', 0):.2%}\n")
            f.write(f"Worst Day:             {self.metrics.get('Worst_Day', 0):.2%}\n")
            f.write("\n")
            
            f.write("2. RISK METRICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Volatility (Annualized):  {self.metrics.get('Volatility', 0):.2%}\n")
            f.write(f"Standard Deviation:       {self.metrics.get('Std_Daily_Return', 0):.4f}\n")
            f.write(f"Maximum Drawdown:         {self.metrics.get('Max_Drawdown', 0):.2%}\n")
            f.write("\n")
            
            f.write("3. RISK-ADJUSTED RETURN METRICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Sharpe Ratio:          {self.metrics.get('Sharpe_Ratio', 0):.2f}\n")
            f.write(f"Sortino Ratio:         {self.metrics.get('Sortino_Ratio', 0):.2f}\n")
            f.write(f"Calmar Ratio:          {self.metrics.get('Calmar_Ratio', 0):.2f}\n")
            f.write("\n")
            
            f.write("4. TRADE STATISTICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Number of Trades:   {self.metrics.get('Total_Trades', 0):,}\n")
            f.write(f"Win Rate:                 {self.metrics.get('Win_Rate', 0):.2%}\n")
            f.write(f"Profit Factor:            {self.metrics.get('Profit_Factor', 0):.2f}\n")
            
            if 'Total_PnL' in self.metrics:
                f.write(f"Total PnL:                ${self.metrics.get('Total_PnL', 0):,.2f}\n")
                f.write(f"Average Trade PnL:        ${self.metrics.get('Avg_Trade_PnL', 0):,.2f}\n")
                f.write(f"Average Win:              ${self.metrics.get('Avg_Win', 0):,.2f}\n")
                f.write(f"Average Loss:             ${self.metrics.get('Avg_Loss', 0):,.2f}\n")
            
            f.write("\n")
            f.write("=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")
        
        print(f"Report saved to {file_path}")
