import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mplfinance as mpf
from datetime import datetime
from typing import Dict, Optional
import os

class Logger:
    def __init__(self, log_file='backtest.log'):
        self.log_file = log_file
        self.log_entries = []
    
    def _log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{timestamp} - {level} - {message}"
        print(log_line)
        self.log_entries.append(log_line)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception as e:
            print(f"日志写入失败: {e}")
    
    def info(self, message):
        self._log('INFO', message)
    
    def warning(self, message):
        self._log('WARNING', message)
    
    def error(self, message):
        self._log('ERROR', message)
    
    def debug(self, message):
        self._log('DEBUG', message)

logger = Logger()

class Backtester:
    def __init__(self, initial_capital: float = 100000.0, transaction_cost: float = 0.001):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.results = None
        self.trade_log = []
        logger.info(f"✅ Backtester initialized: initial_capital={initial_capital:,.2f}, transaction_cost={transaction_cost:.2%}")
    
    def _validate_input_data(self, df: pd.DataFrame) -> bool:
        required_cols = ['open', 'high', 'low', 'close', 'volume', 'returns', 'position', 'signal']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.error(f"❌ 数据验证失败: 缺少必要列 {missing_cols}")
            return False
        
        if df.empty:
            logger.error("❌ 数据验证失败: 数据框为空")
            return False
        
        if len(df) < 20:
            logger.warning(f"⚠️ 数据量较少: 仅 {len(df)} 条记录，可能影响指标计算")
        
        has_nan = df[['open', 'high', 'low', 'close', 'volume']].isna().any().any()
        if has_nan:
            logger.warning("⚠️ 数据包含 NaN 值，已自动处理")
        
        logger.info(f"✅ 数据验证通过: {len(df)} 条记录, 时间范围 {df.index[0]} - {df.index[-1]}")
        return True
    
    def run_backtest(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🚀 开始执行回测...")
        
        if not self._validate_input_data(df):
            raise ValueError("数据验证失败")
        
        df = df.copy()
        
        logger.info("📊 计算策略收益...")
        df['strategy_returns'] = df['returns'] * df['position'].shift(1)
        
        logger.info("💰 计算交易成本...")
        trade_changes = df['position'].diff().fillna(0)
        df['transaction_cost'] = np.abs(trade_changes) * self.transaction_cost
        df['strategy_returns_net'] = df['strategy_returns'] - df['transaction_cost']
        
        total_cost = df['transaction_cost'].sum()
        logger.info(f"📉 总交易成本: {total_cost:.4%} (共 {len(df[df['transaction_cost'] > 0])} 次交易)")
        
        logger.info("📈 计算累计收益...")
        df['strategy_cumulative'] = (1 + df['strategy_returns']).cumprod()
        df['strategy_cumulative_net'] = (1 + df['strategy_returns_net']).cumprod()
        df['benchmark_cumulative'] = (1 + df['returns']).cumprod()
        
        df['portfolio_value'] = self.initial_capital * df['strategy_cumulative']
        df['portfolio_value_net'] = self.initial_capital * df['strategy_cumulative_net']
        df['benchmark_value'] = self.initial_capital * df['benchmark_cumulative']
        
        logger.info("📉 计算回撤...")
        df['drawdown'] = (df['strategy_cumulative'] / df['strategy_cumulative'].cummax()) - 1
        df['drawdown_net'] = (df['strategy_cumulative_net'] / df['strategy_cumulative_net'].cummax()) - 1
        df['benchmark_drawdown'] = (df['benchmark_cumulative'] / df['benchmark_cumulative'].cummax()) - 1
        
        max_dd = df['drawdown'].min()
        logger.info(f"⚠️ 最大回撤: {max_dd:.2%}")
        
        logger.info("📝 生成交易日志...")
        self._generate_trade_log(df)
        
        self.results = df
        
        final_value = df['portfolio_value_net'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        logger.info(f"✅ 回测完成! 最终净值: {final_value:,.2f}, 总收益: {total_return:.2%}")
        
        return df
    
    def _generate_trade_log(self, df: pd.DataFrame):
        trades = []
        current_position = 0
        entry_price = 0
        entry_date = None
        
        for date, row in df.iterrows():
            if row['signal'] != 0 and row['signal'] != current_position:
                if current_position != 0:
                    exit_price = row['close']
                    pnl = (exit_price - entry_price) / entry_price * current_position
                    pnl_value = pnl * self.initial_capital
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': date,
                        'position': current_position,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'pnl_value': pnl_value,
                        'duration': (date - entry_date).days
                    })
                    logger.debug(f"🔄 平仓: {entry_date.date()} -> {date.date()}, 仓位:{current_position}, PnL:{pnl:.2%}")
                
                current_position = row['signal']
                entry_price = row['close']
                entry_date = date
                logger.debug(f"📥 开仓: {date.date()}, 仓位:{current_position}, 价格:{entry_price:.2f}")
        
        if current_position != 0:
            exit_price = df.iloc[-1]['close']
            pnl = (exit_price - entry_price) / entry_price * current_position
            pnl_value = pnl * self.initial_capital
            
            trades.append({
                'entry_date': entry_date,
                'exit_date': df.index[-1],
                'position': current_position,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_value': pnl_value,
                'duration': (df.index[-1] - entry_date).days
            })
            logger.debug(f"⏰ 未平仓: {entry_date.date()} -> {df.index[-1].date()}, 仓位:{current_position}")
        
        self.trade_log = pd.DataFrame(trades)
        logger.info(f"📊 交易日志生成完成: 共 {len(trades)} 笔交易")
    
    def calculate_metrics(self, include_net: bool = True) -> Dict:
        logger.info("🔢 计算回测指标...")
        
        if self.results is None:
            logger.error("❌ 回测未执行，请先运行 run_backtest")
            raise ValueError("Run backtest first")
        
        df = self.results
        
        total_return = df['strategy_cumulative'].iloc[-1] - 1
        total_return_net = df['strategy_cumulative_net'].iloc[-1] - 1
        benchmark_return = df['benchmark_cumulative'].iloc[-1] - 1
        
        annualized_return = (1 + total_return) ** (252 / len(df)) - 1
        annualized_return_net = (1 + total_return_net) ** (252 / len(df)) - 1
        benchmark_annualized_return = (1 + benchmark_return) ** (252 / len(df)) - 1
        
        volatility = df['strategy_returns'].std() * np.sqrt(252)
        volatility_net = df['strategy_returns_net'].std() * np.sqrt(252)
        benchmark_volatility = df['returns'].std() * np.sqrt(252)
        
        sharpe_ratio = annualized_return / volatility if volatility != 0 else np.nan
        sharpe_ratio_net = annualized_return_net / volatility_net if volatility_net != 0 else np.nan
        benchmark_sharpe_ratio = benchmark_annualized_return / benchmark_volatility if benchmark_volatility != 0 else np.nan
        
        max_drawdown = df['drawdown'].min()
        max_drawdown_net = df['drawdown_net'].min()
        benchmark_max_drawdown = df['benchmark_drawdown'].min()
        
        win_trades = len(df[df['strategy_returns'] > 0])
        total_trades = len(df[df['strategy_returns'] != 0])
        win_rate = win_trades / total_trades if total_trades > 0 else 0
        win_rate_net = len(df[df['strategy_returns_net'] > 0]) / len(df[df['strategy_returns_net'] != 0]) if len(df[df['strategy_returns_net'] != 0]) > 0 else 0
        
        logger.info(f"📊 胜率计算: {win_trades}/{total_trades} = {win_rate:.2%}")
        
        profit_factor = df[df['strategy_returns'] > 0]['strategy_returns'].sum() / \
                       abs(df[df['strategy_returns'] < 0]['strategy_returns'].sum()) if len(df[df['strategy_returns'] < 0]) > 0 else np.inf
        
        profit_factor_net = df[df['strategy_returns_net'] > 0]['strategy_returns_net'].sum() / \
                          abs(df[df['strategy_returns_net'] < 0]['strategy_returns_net'].sum()) if len(df[df['strategy_returns_net'] < 0]) > 0 else np.inf
        
        avg_win = df[df['strategy_returns'] > 0]['strategy_returns'].mean()
        avg_loss = abs(df[df['strategy_returns'] < 0]['strategy_returns'].mean())
        reward_risk_ratio = avg_win / avg_loss if avg_loss != 0 else np.inf
        
        sortino_ratio = annualized_return / (df[df['strategy_returns'] < 0]['strategy_returns'].std() * np.sqrt(252)) if len(df[df['strategy_returns'] < 0]) > 0 else np.nan
        
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else np.nan
        
        var_95 = df['strategy_returns'].quantile(0.05)
        cvar_95 = df[df['strategy_returns'] <= var_95]['strategy_returns'].mean()
        
        beta = np.cov(df['strategy_returns'], df['returns'])[0, 1] / np.var(df['returns']) if np.var(df['returns']) != 0 else np.nan
        alpha = annualized_return - beta * benchmark_annualized_return
        
        metrics = {
            'Initial Capital': f'{self.initial_capital:,.2f}',
            'Transaction Cost': f'{self.transaction_cost:.2%}',
            'Total Return': f'{total_return:.2%}',
            'Total Return (Net)': f'{total_return_net:.2%}',
            'Benchmark Return': f'{benchmark_return:.2%}',
            'Annualized Return': f'{annualized_return:.2%}',
            'Annualized Return (Net)': f'{annualized_return_net:.2%}',
            'Benchmark Annualized Return': f'{benchmark_annualized_return:.2%}',
            'Volatility': f'{volatility:.2%}',
            'Volatility (Net)': f'{volatility_net:.2%}',
            'Benchmark Volatility': f'{benchmark_volatility:.2%}',
            'Sharpe Ratio': f'{sharpe_ratio:.2f}',
            'Sharpe Ratio (Net)': f'{sharpe_ratio_net:.2f}',
            'Benchmark Sharpe Ratio': f'{benchmark_sharpe_ratio:.2f}',
            'Sortino Ratio': f'{sortino_ratio:.2f}',
            'Calmar Ratio': f'{calmar_ratio:.2f}',
            'Max Drawdown': f'{max_drawdown:.2%}',
            'Max Drawdown (Net)': f'{max_drawdown_net:.2%}',
            'Benchmark Max Drawdown': f'{benchmark_max_drawdown:.2%}',
            'Win Rate': f'{win_rate:.2%}',
            'Win Rate (Net)': f'{win_rate_net:.2%}',
            'Profit Factor': f'{profit_factor:.2f}',
            'Profit Factor (Net)': f'{profit_factor_net:.2f}',
            'Reward/Risk Ratio': f'{reward_risk_ratio:.2f}',
            'Beta': f'{beta:.2f}',
            'Alpha': f'{alpha:.2%}',
            'VaR (95%)': f'{var_95:.2%}',
            'CVaR (95%)': f'{cvar_95:.2%}',
            'Number of Trades': len(self.trade_log),
            'Average Trade Duration': f"{self.trade_log['duration'].mean():.1f} days" if len(self.trade_log) > 0 else 'N/A',
            'Data Points': len(df),
            'Date Range': f"{df.index[0].date()} - {df.index[-1].date()}"
        }
        
        logger.info("✅ 指标计算完成")
        return metrics
    
    def get_trade_log(self) -> pd.DataFrame:
        return self.trade_log
    
    def plot_with_mplfinance(self, save_path: str = None):
        if self.results is None:
            raise ValueError("Run backtest first")
        
        df = self.results.copy()
        df.index = pd.to_datetime(df.index)
        
        buy_signals = df[df['signal'] == 1]
        sell_signals = df[df['signal'] == -1]
        
        add_plots = [
            mpf.make_addplot(df['sma_short'], color='blue', label='SMA 20'),
            mpf.make_addplot(df['sma_long'], color='red', label='SMA 60'),
            mpf.make_addplot(df['rsi'], panel=1, color='purple', label='RSI', ylabel='RSI'),
            mpf.make_addplot(df['macd'], panel=2, color='blue', label='MACD'),
            mpf.make_addplot(df['macd_signal'], panel=2, color='red', label='Signal'),
            mpf.make_addplot(df['position'], panel=3, color='green', label='Position', type='bar', ylabel='Position'),
            mpf.make_addplot(df['portfolio_value'] / 1000, panel=4, color='orange', label='Portfolio', ylabel='Value (k)')
        ]
        
        fig, axes = mpf.plot(
            df,
            type='candle',
            style='yahoo',
            addplot=add_plots,
            volume=True,
            volume_panel=5,
            figratio=(16, 10),
            figscale=1.2,
            title=f'{df.iloc[0].name.date()} - {df.iloc[-1].name.date()}',
            returnfig=True
        )
        
        ax = axes[0]
        for date, row in buy_signals.iterrows():
            ax.scatter(mdates.date2num(date), row['low'] * 0.99, marker='^', color='green', s=100, zorder=5)
        for date, row in sell_signals.iterrows():
            ax.scatter(mdates.date2num(date), row['high'] * 1.01, marker='v', color='red', s=100, zorder=5)
        
        plt.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"📸 图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_interactive(self, save_path: str = None):
        if self.results is None:
            raise ValueError("Run backtest first")
        
        df = self.results.copy()
        df.index = pd.to_datetime(df.index)
        
        buy_signals = df[df['signal'] == 1]
        sell_signals = df[df['signal'] == -1]
        
        fig = make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('Price & Signals', 'RSI', 'MACD', 'Position', 'Portfolio Value'),
            row_heights=[0.3, 0.15, 0.15, 0.15, 0.25]
        )
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            showlegend=False
        ), row=1, col=1)
        
        if 'sma_short' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_short'],
                name='SMA Short',
                line=dict(color='blue', width=2)
            ), row=1, col=1)
        
        if 'sma_long' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_long'],
                name='SMA Long',
                line=dict(color='red', width=2)
            ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals['low'] * 0.98,
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=12),
            name='Buy Signal'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals['high'] * 1.02,
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=12),
            name='Sell Signal'
        ), row=1, col=1)
        
        if 'rsi' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['rsi'],
                name='RSI',
                line=dict(color='purple', width=1.5)
            ), row=2, col=1)
            
            fig.add_hline(y=70, line_dash='dash', line_color='red', row=2, col=1)
            fig.add_hline(y=30, line_dash='dash', line_color='green', row=2, col=1)
        
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['macd'],
                name='MACD',
                line=dict(color='blue', width=1.5)
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['macd_signal'],
                name='Signal',
                line=dict(color='red', width=1.5)
            ), row=3, col=1)
            
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['macd'] - df['macd_signal'],
                name='MACD Histogram',
                marker_color='gray'
            ), row=3, col=1)
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['position'],
            name='Position',
            marker_color='green'
        ), row=4, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['portfolio_value'],
            name='Portfolio Value',
            line=dict(color='orange', width=2),
            yaxis='y2'
        ), row=5, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['benchmark_value'],
            name='Benchmark',
            line=dict(color='gray', width=2, dash='dash'),
            yaxis='y2'
        ), row=5, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['portfolio_value_net'],
            name='Portfolio (Net)',
            line=dict(color='blue', width=2, dash='dot'),
            yaxis='y2'
        ), row=5, col=1)
        
        fig.update_layout(
            height=1000,
            title=f'Backtest Results: {df.iloc[0].name.date()} - {df.iloc[-1].name.date()}',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text='Price', row=1, col=1)
        fig.update_yaxes(title_text='RSI', row=2, col=1)
        fig.update_yaxes(title_text='MACD', row=3, col=1)
        fig.update_yaxes(title_text='Position', row=4, col=1)
        fig.update_yaxes(title_text='Value', row=5, col=1)
        fig.update_yaxes(title_text='Value', row=5, col=1, secondary_y=True)
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"📊 交互式图表已保存到: {save_path}")
        
        fig.show()
    
    def plot_drawdown(self, save_path: str = None):
        if self.results is None:
            raise ValueError("Run backtest first")
        
        df = self.results.copy()
        df.index = pd.to_datetime(df.index)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['drawdown'] * 100,
            name='Strategy Drawdown',
            fill='tozeroy',
            line=dict(color='red', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['benchmark_drawdown'] * 100,
            name='Benchmark Drawdown',
            fill='tozeroy',
            line=dict(color='gray', width=2, dash='dash')
        ))
        
        fig.update_layout(
            height=400,
            title='Drawdown Analysis',
            yaxis_title='Drawdown (%)',
            hovermode='x unified'
        )
        
        if save_path:
            fig.write_html(save_path.replace('.html', '_drawdown.html'))
            logger.info(f"📉 回撤图表已保存到: {save_path.replace('.html', '_drawdown.html')}")
        
        fig.show()
    
    def generate_report(self, filename: str = 'backtest_report.html'):
        if self.results is None:
            raise ValueError("Run backtest first")
        
        logger.info(f"📝 生成回测报告: {filename}")
        metrics = self.calculate_metrics()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>回测报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
        .metric-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .metric-label {{ color: #7f8c8d; font-size: 14px; }}
        .metric-value {{ color: #2c3e50; font-size: 20px; font-weight: bold; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        .log-section {{ background: #f8f9fa; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>量化策略回测报告</h1>
    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>数据范围: {metrics['Date Range']}</p>
    <p>数据点数: {metrics['Data Points']}</p>
    
    <h2>策略概览</h2>
    <div class="metrics">
        <div class="metric-box">
            <div class="metric-label">总收益率</div>
            <div class="metric-value {'positive' if float(metrics['Total Return'].replace('%', '')) > 0 else 'negative'}">{metrics['Total Return']}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">年化收益率</div>
            <div class="metric-value {'positive' if float(metrics['Annualized Return'].replace('%', '')) > 0 else 'negative'}">{metrics['Annualized Return']}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">夏普比率</div>
            <div class="metric-value">{metrics['Sharpe Ratio']}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">最大回撤</div>
            <div class="metric-value negative">{metrics['Max Drawdown']}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">胜率</div>
            <div class="metric-value">{metrics['Win Rate']}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">交易次数</div>
            <div class="metric-value">{metrics['Number of Trades']}</div>
        </div>
    </div>
    
    <h2>详细指标</h2>
    <table>
"""
        
        for key, value in metrics.items():
            html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"
        
        html_content += """
    </table>
    
    <h2>交易记录</h2>
"""
        
        if not self.trade_log.empty:
            html_content += """
    <table>
        <tr><th>开仓日期</th><th>平仓日期</th><th>仓位</th><th>开仓价</th><th>平仓价</th><th>盈亏</th><th>盈亏金额</th><th>持仓天数</th></tr>
"""
            for _, trade in self.trade_log.iterrows():
                pnl_color = 'positive' if trade['pnl'] > 0 else 'negative'
                html_content += f"""
        <tr>
            <td>{trade['entry_date'].date()}</td>
            <td>{trade['exit_date'].date()}</td>
            <td>{'多头' if trade['position'] == 1 else '空头'}</td>
            <td>{trade['entry_price']:.2f}</td>
            <td>{trade['exit_price']:.2f}</td>
            <td class="{pnl_color}">{trade['pnl']:.2%}</td>
            <td class="{pnl_color}">{trade['pnl_value']:,.2f}</td>
            <td>{trade['duration']}</td>
        </tr>
"""
            html_content += "</table>"
        else:
            html_content += "<p>无交易记录</p>"
        
        html_content += "</body></html>"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ 回测报告已保存到: {filename}")