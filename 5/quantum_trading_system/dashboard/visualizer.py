# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Dashboard:
    def __init__(self):
        self.charts = {}
    
    def create_equity_curve(self, equity_df, title="鏉冪泭鏇茬嚎"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=equity_df.index,
            y=equity_df['equity'],
            mode='lines',
            name='鏉冪泭',
            line=dict(color='#2E86AB', width=2)
        ))
        
        if 'cash' in equity_df.columns:
            fig.add_trace(go.Scatter(
                x=equity_df.index,
                y=equity_df['cash'],
                mode='lines',
                name='鐜伴噾',
                line=dict(color='#A23B72', width=1, dash='dash')
            ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title="鏃ユ湡",
            yaxis_title="閲戦",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_drawdown_chart(self, equity_df, title="鍥炴挙鍒嗘瀽"):
        equity = equity_df['equity']
        
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown,
            mode='lines',
            name='鍥炴挙',
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.3)',
            line=dict(color='#E74C3C', width=1)
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title="鏃ユ湡",
            yaxis_title="鍥炴挙 (%)",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_price_chart(self, df, signals=None, title="浠锋牸璧板娍"):
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=(title, '鎴愪氦閲?)
        )
        
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='K绾?
            ),
            row=1, col=1
        )
        
        if 'ma5' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['ma5'],
                    mode='lines',
                    name='MA5',
                    line=dict(color='#3498DB', width=1)
                ),
                row=1, col=1
            )
        
        if 'ma20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['ma20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color='#E67E22', width=1)
                ),
                row=1, col=1
            )
        
        if signals is not None:
            buy_signals = df[signals == 1]
            sell_signals = df[signals == -1]
            
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['close'] * 1.02,
                    mode='markers',
                    name='涔板叆',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color='#27AE60',
                        line=dict(width=2, color='#2ECC71')
                    )
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['close'] * 0.98,
                    mode='markers',
                    name='鍗栧嚭',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color='#E74C3C',
                        line=dict(width=2, color='#C0392B')
                    )
                ),
                row=1, col=1
            )
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='鎴愪氦閲?,
                marker=dict(color=df['volume'], colorscale='Viridis', opacity=0.7)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            template='plotly_white',
            height=700,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def create_indicators_chart(self, df, title="鎶€鏈寚鏍?):
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.3, 0.3, 0.2, 0.2],
            subplot_titles=('RSI', 'MACD', '甯冩灄甯?, 'KDJ')
        )
        
        if 'rsi' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='#9B59B6', width=1.5)
                ),
                row=1, col=1
            )
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
        
        if 'macd' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['macd'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='#3498DB', width=1.5)
                ),
                row=2, col=1
            )
            
            if 'macd_signal' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['macd_signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color='#E74C3C', width=1)
                    ),
                    row=2, col=1
                )
            
            if 'macd_hist' in df.columns:
                colors = ['green' if val >= 0 else 'red' for val in df['macd_hist']]
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df['macd_hist'],
                        name='Histogram',
                        marker=dict(color=colors, opacity=0.6)
                    ),
                    row=2, col=1
                )
        
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bb_upper'],
                    mode='lines',
                    name='涓婅建',
                    line=dict(color='#E74C3C', width=1, dash='dash')
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bb_lower'],
                    mode='lines',
                    name='涓嬭建',
                    line=dict(color='#27AE60', width=1, dash='dash')
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['close'],
                    mode='lines',
                    name='鏀剁洏浠?,
                    line=dict(color='#2C3E50', width=1.5),
                    fill='tonexty',
                    fillcolor='rgba(200, 200, 200, 0.2)'
                ),
                row=3, col=1
            )
        
        if 'kdj_k' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['kdj_k'],
                    mode='lines',
                    name='K',
                    line=dict(color='#3498DB', width=1.5)
                ),
                row=4, col=1
            )
            
            if 'kdj_d' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['kdj_d'],
                        mode='lines',
                        name='D',
                        line=dict(color='#E74C3C', width=1)
                    ),
                    row=4, col=1
                )
            
            if 'kdj_j' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['kdj_j'],
                        mode='lines',
                        name='J',
                        line=dict(color='#27AE60', width=1)
                    ),
                    row=4, col=1
                )
        
        fig.update_layout(
            template='plotly_white',
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_performance_summary(self, result):
        metrics = {
            '鏀剁泭鐜?: f"{result['total_return_pct']:+.2f}%",
            '澶忔櫘姣旂巼': f"{result['sharpe_ratio']:.2f}",
            '鏈€澶у洖鎾?: f"{result['max_drawdown_pct']:.2f}%",
            '鑳滅巼': f"{result['win_rate_pct']:.2f}%",
            '浜ゆ槗娆℃暟': f"{result['total_trades']}"
        }
        
        fig = go.Figure(data=[
            go.Table(
                header=dict(
                    values=['<b>鎸囨爣</b>', '<b>鏁板€?/b>'],
                    fill_color='#2E86AB',
                    font=dict(color='white', size=14),
                    align='center',
                    height=40
                ),
                cells=dict(
                    values=[list(metrics.keys()), list(metrics.values())],
                    fill_color=[['#F8F9FA'] * len(metrics)],
                    font=dict(size=13),
                    align='center',
                    height=35
                )
            )
        ])
        
        fig.update_layout(
            title=dict(text="鎬ц兘鎸囨爣鎽樿", font=dict(size=18)),
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_trades_timeline(self, trades):
        if not trades or len(trades) < 2:
            return None
        
        df = pd.DataFrame(trades)
        df['date'] = pd.to_datetime(df['date'])
        
        buy_trades = df[df['type'] == 'buy']
        sell_trades = df[df['type'] == 'sell']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=buy_trades['date'],
            y=buy_trades['price'],
            mode='markers',
            name='涔板叆',
            marker=dict(
                symbol='triangle-up',
                size=15,
                color='#27AE60'
            ),
            text=[f"涔板叆<br>浠锋牸: {p}<br>鏁伴噺: {s}" 
                  for p, s in zip(buy_trades['price'], buy_trades['shares'])],
            hoverinfo='text'
        ))
        
        fig.add_trace(go.Scatter(
            x=sell_trades['date'],
            y=sell_trades['price'],
            mode='markers',
            name='鍗栧嚭',
            marker=dict(
                symbol='triangle-down',
                size=15,
                color='#E74C3C'
            ),
            text=[f"鍗栧嚭<br>浠锋牸: {p}<br>鏁伴噺: {s}" 
                  for p, s in zip(sell_trades['price'], sell_trades['shares'])],
            hoverinfo='text'
        ))
        
        fig.update_layout(
            title=dict(text="浜ゆ槗鏃堕棿绾?, font=dict(size=18)),
            xaxis_title="鏃ユ湡",
            yaxis_title="浠锋牸",
            template='plotly_white',
            height=400,
            hovermode='closest'
        )
        
        return fig
    
    def create_returns_distribution(self, equity_df):
        if len(equity_df) < 2:
            return None
        
        returns = equity_df['equity'].pct_change().dropna() * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='鏃ユ敹鐩婄巼',
            marker=dict(
                color=returns,
                colorscale='RdYlGn',
                opacity=0.7
            )
        ))
        
        fig.update_layout(
            title=dict(text="鏃ユ敹鐩婄巼鍒嗗竷", font=dict(size=18)),
            xaxis_title="鏃ユ敹鐩婄巼 (%)",
            yaxis_title="棰戞",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_monthly_returns_heatmap(self, equity_df):
        if len(equity_df) < 30:
            return None
        
        df = equity_df.copy()
        df['year'] = df.index.year
        df['month'] = df.index.month
        
        monthly_returns = df.groupby(['year', 'month'])['equity'].agg(['first', 'last'])
        monthly_returns['return'] = (monthly_returns['last'] - monthly_returns['first']) / monthly_returns['first'] * 100
        
        monthly_pivot = monthly_returns['return'].unstack(level='month')
        
        month_names = ['1鏈?, '2鏈?, '3鏈?, '4鏈?, '5鏈?, '6鏈?, 
                       '7鏈?, '8鏈?, '9鏈?, '10鏈?, '11鏈?, '12鏈?]
        
        fig = go.Figure(data=go.Heatmap(
            z=monthly_pivot.values,
            x=[month_names[i] for i in monthly_pivot.columns if 1 <= i <= 12],
            y=monthly_pivot.index,
            colorscale='RdYlGn',
            colorbar=dict(title="鏀剁泭鐜?(%)"),
            text=np.round(monthly_pivot.values, 1),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title=dict(text="鏈堝害鏀剁泭鐑姏鍥?, font=dict(size=18)),
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def generate_comprehensive_dashboard(self, backtest_result, df, signals):
        dashboard = {}
        
        if 'equity_curve' in backtest_result:
            dashboard['equity_curve'] = self.create_equity_curve(backtest_result['equity_curve'])
            dashboard['drawdown'] = self.create_drawdown_chart(backtest_result['equity_curve'])
            dashboard['returns_distribution'] = self.create_returns_distribution(backtest_result['equity_curve'])
            dashboard['monthly_heatmap'] = self.create_monthly_returns_heatmap(backtest_result['equity_curve'])
        
        dashboard['price_chart'] = self.create_price_chart(df, signals)
        dashboard['indicators'] = self.create_indicators_chart(df)
        dashboard['performance_summary'] = self.create_performance_summary(backtest_result)
        
        if 'trades' in backtest_result:
            dashboard['trades_timeline'] = self.create_trades_timeline(backtest_result['trades'])
        
        return dashboard
