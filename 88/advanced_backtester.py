#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 优化版策略回测系统
ZTB Seer - Advanced Backtesting System v2.0
支持止损止盈、动态仓位管理、参数优化
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

class AdvancedBacktester:
    def __init__(self, initial_capital=100000, commission=0.0015):
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = None
        self.trades = []
        
    def generate_historical_data(self, days=250, trend='bull'):
        """生成模拟历史数据"""
        dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
        
        data = {
            'date': dates,
            'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': []
        }
        
        if trend == 'bull':
            base_return = 0.0003
            volatility = 0.015
        elif trend == 'bear':
            base_return = -0.0002
            volatility = 0.02
        else:
            base_return = 0.0001
            volatility = 0.018
            
        price = 25.0
        for i in range(days):
            daily_return = np.random.normal(base_return, volatility)
            open_price = price * (1 + np.random.normal(0, 0.005))
            close_price = price * (1 + daily_return)
            high_price = max(open_price, close_price) * (1 + abs(np.random.uniform(0, 0.015)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.uniform(0, 0.015)))
            volume = int(np.random.normal(500000, 200000))
            
            data['open'].append(round(open_price, 2))
            data['high'].append(round(high_price, 2))
            data['low'].append(round(low_price, 2))
            data['close'].append(round(close_price, 2))
            data['volume'].append(max(100000, volume))
            
            price = close_price
            
        return pd.DataFrame(data).set_index('date')
    
    def calculate_indicators(self, data):
        """计算技术指标"""
        df = data.copy()
        
        df['ma5'] = df['close'].rolling(5).mean().round(2)
        df['ma10'] = df['close'].rolling(10).mean().round(2)
        df['ma20'] = df['close'].rolling(20).mean().round(2)
        df['ma60'] = df['close'].rolling(60).mean().round(2)
        
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['dif'] = (df['ema12'] - df['ema26']).round(4)
        df['dea'] = df['dif'].ewm(span=9, adjust=False).mean().round(4)
        df['macd'] = ((df['dif'] - df['dea']) * 2).round(4)
        df['macd_hist'] = (df['macd'] > 0).astype(int)
        
        low_min = df['low'].rolling(9).min()
        high_max = df['high'].rolling(9).max()
        df['rsv'] = ((df['close'] - low_min) / (high_max - low_min) * 100).round(2)
        df['k'] = df['rsv'].ewm(com=2, adjust=False).mean().round(2)
        df['d'] = df['k'].ewm(com=2, adjust=False).mean().round(2)
        df['j'] = (3 * df['k'] - 2 * df['d']).round(2)
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = (100 - (100 / (1 + rs))).round(2)
        
        df['boll_mid'] = df['close'].rolling(20).mean()
        df['boll_std'] = df['close'].rolling(20).std()
        df['boll_upper'] = (df['boll_mid'] + 2 * df['boll_std']).round(2)
        df['boll_lower'] = (df['boll_mid'] - 2 * df['boll_std']).round(2)
        
        df['volume_ma5'] = df['volume'].rolling(5).mean()
        df['volume_ratio'] = (df['volume'] / df['volume_ma5']).round(2)
        
        return df
    
    def optimized_macd_strategy(self, df, params=None):
        """优化版MACD策略"""
        if params is None:
            params = {'fast': 12, 'slow': 26, 'signal': 9, 'threshold': 0}
            
        df['signal'] = 0
        
        for i in range(len(df)):
            if i < params['slow']:
                continue
                
            dif = df['dif'].iloc[i]
            dea = df['dea'].iloc[i]
            
            dif_prev = df['dif'].iloc[i-1]
            dea_prev = df['dea'].iloc[i-1]
            
            dif_above = dif > dea + params['threshold']
            dif_prev_below = dif_prev <= dea_prev + params['threshold']
            
            if dif_above and dif_prev_below:
                df.loc[df.index[i], 'signal'] = 1
            elif dif < dea - params['threshold'] and dif_prev >= dea_prev - params['threshold']:
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def optimized_kdj_strategy(self, df, params=None):
        """优化版KDJ策略"""
        if params is None:
            params = {'oversold': 25, 'overbought': 75, 'confirm': True}
            
        df['signal'] = 0
        
        for i in range(1, len(df)):
            k_curr = df['k'].iloc[i]
            d_curr = df['d'].iloc[i]
            j_curr = df['j'].iloc[i]
            
            k_prev = df['k'].iloc[i-1]
            d_prev = df['d'].iloc[i-1]
            
            if params['confirm']:
                gold_cross = k_prev <= d_prev and k_curr > d_curr
                oversold = j_curr < params['oversold']
                
                if gold_cross and oversold:
                    df.loc[df.index[i], 'signal'] = 1
                elif k_prev >= d_prev and k_curr < d_curr and j_curr > params['overbought']:
                    df.loc[df.index[i], 'signal'] = -1
            else:
                if k_prev <= d_prev and k_curr > d_curr:
                    df.loc[df.index[i], 'signal'] = 1
                elif k_prev >= d_prev and k_curr < d_curr:
                    df.loc[df.index[i], 'signal'] = -1
                    
        return df
    
    def optimized_ma_strategy(self, df, params=None):
        """优化版均线策略"""
        if params is None:
            params = {'fast': 5, 'slow': 20, 'confirm_ma60': True}
            
        df['signal'] = 0
        
        for i in range(1, len(df)):
            ma_fast_curr = df[f'ma{params["fast"]}'].iloc[i]
            ma_slow_curr = df[f'ma{params["slow"]}'].iloc[i]
            ma_fast_prev = df[f'ma{params["fast"]}'].iloc[i-1]
            ma_slow_prev = df[f'ma{params["slow"]}'].iloc[i-1]
            
            if pd.isna(ma_fast_curr) or pd.isna(ma_slow_curr):
                continue
                
            gold_cross = ma_fast_prev <= ma_slow_prev and ma_fast_curr > ma_slow_curr
            
            if params['confirm_ma60']:
                ma60 = df['ma60'].iloc[i]
                trend_up = pd.notna(ma60) and ma_fast_curr > ma60
                
                if gold_cross and trend_up:
                    df.loc[df.index[i], 'signal'] = 1
            else:
                if gold_cross:
                    df.loc[df.index[i], 'signal'] = 1
                    
            if ma_fast_prev >= ma_slow_prev and ma_fast_curr < ma_slow_curr:
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def optimized_rsi_strategy(self, df, params=None):
        """优化版RSI策略"""
        if params is None:
            params = {'oversold': 35, 'overbought': 65, 'confirm_volume': True}
            
        df['signal'] = 0
        
        for i in range(len(df)):
            rsi = df['rsi'].iloc[i]
            
            if pd.isna(rsi):
                continue
                
            if params['confirm_volume']:
                vol_ratio = df['volume_ratio'].iloc[i]
                strong_volume = vol_ratio > 1.5 if pd.notna(vol_ratio) else False
                
                if rsi < params['oversold'] and strong_volume:
                    df.loc[df.index[i], 'signal'] = 1
                elif rsi > params['overbought'] and strong_volume:
                    df.loc[df.index[i], 'signal'] = -1
            else:
                if rsi < params['oversold']:
                    df.loc[df.index[i], 'signal'] = 1
                elif rsi > params['overbought']:
                    df.loc[df.index[i], 'signal'] = -1
                    
        return df
    
    def bollinger_strategy(self, df, params=None):
        """布林带策略"""
        if params is None:
            params = {'position_pct': 0.5}
            
        df['signal'] = 0
        
        for i in range(len(df)):
            price = df['close'].iloc[i]
            lower = df['boll_lower'].iloc[i]
            upper = df['boll_upper'].iloc[i]
            
            if pd.isna(lower) or pd.isna(upper):
                continue
                
            position = (price - lower) / (upper - lower)
            
            if position < params['position_pct']:
                df.loc[df.index[i], 'signal'] = 1
            elif position > (1 - params['position_pct']):
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def volume_price_strategy(self, df, params=None):
        """量价配合策略"""
        if params is None:
            params = {'vol_threshold': 1.5, 'price_threshold': 0.02}
            
        df['signal'] = 0
        
        for i in range(1, len(df)):
            vol_ratio = df['volume_ratio'].iloc[i]
            price_change = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]
            
            if pd.isna(vol_ratio):
                continue
                
            if vol_ratio > params['vol_threshold'] and price_change > params['price_threshold']:
                df.loc[df.index[i], 'signal'] = 1
            elif vol_ratio > params['vol_threshold'] and price_change < -params['price_threshold']:
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def combined_strategy(self, df):
        """综合策略"""
        df['signal'] = 0
        
        df = self.optimized_macd_strategy(df)
        df['macd_signal'] = df['signal'].copy()
        
        df = self.optimized_kdj_strategy(df)
        df['kdj_signal'] = df['signal'].copy()
        
        df = self.optimized_ma_strategy(df)
        df['ma_signal'] = df['signal'].copy()
        
        df = self.optimized_rsi_strategy(df)
        df['rsi_signal'] = df['signal'].copy()
        
        for i in range(len(df)):
            signals = [
                df['macd_signal'].iloc[i],
                df['kdj_signal'].iloc[i],
                df['ma_signal'].iloc[i],
                df['rsi_signal'].iloc[i]
            ]
            
            buy_signals = sum(1 for s in signals if s == 1)
            sell_signals = sum(1 for s in signals if s == -1)
            
            if buy_signals >= 3:
                df.loc[df.index[i], 'signal'] = 1
            elif sell_signals >= 3:
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def run_backtest_with_stop_loss(self, data, strategy='combined', stop_loss=0.08, take_profit=0.15):
        """带止损止盈的回测"""
        data = self.calculate_indicators(data)
        
        if strategy == 'macd':
            data = self.optimized_macd_strategy(data)
        elif strategy == 'kdj':
            data = self.optimized_kdj_strategy(data)
        elif strategy == 'ma':
            data = self.optimized_ma_strategy(data)
        elif strategy == 'rsi':
            data = self.optimized_rsi_strategy(data)
        elif strategy == 'bollinger':
            data = self.bollinger_strategy(data)
        elif strategy == 'volume':
            data = self.volume_price_strategy(data)
        else:
            data = self.combined_strategy(data)
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        self.trades = []
        portfolio_values = []
        stop_loss_price = 0
        take_profit_price = 0
        
        for date, row in data.iterrows():
            price = row['close']
            signal = row['signal']
            
            if position > 0:
                current_loss = (price - entry_price) / entry_price
                current_profit = (price - entry_price) / entry_price
                
                if current_loss <= -stop_loss:
                    revenue = position * price * (1 - self.commission)
                    capital = revenue
                    self.trades.append({
                        'date': date, 'type': 'sell', 'price': price,
                        'shares': position, 'revenue': revenue, 'reason': '止损'
                    })
                    position = 0
                elif current_profit >= take_profit:
                    revenue = position * price * (1 - self.commission)
                    capital = revenue
                    self.trades.append({
                        'date': date, 'type': 'sell', 'price': price,
                        'shares': position, 'revenue': revenue, 'reason': '止盈'
                    })
                    position = 0
                elif signal == -1:
                    revenue = position * price * (1 - self.commission)
                    capital = revenue
                    self.trades.append({
                        'date': date, 'type': 'sell', 'price': price,
                        'shares': position, 'revenue': revenue, 'reason': '信号卖出'
                    })
                    position = 0
            else:
                if signal == 1:
                    shares = int(capital / price / 100) * 100
                    cost = shares * price * (1 + self.commission)
                    if cost <= capital and shares > 0:
                        position = shares
                        entry_price = price
                        capital -= cost
                        stop_loss_price = price * (1 - stop_loss)
                        take_profit_price = price * (1 + take_profit)
                        self.trades.append({
                            'date': date, 'type': 'buy', 'price': price,
                            'shares': shares, 'cost': cost
                        })
            
            portfolio_value = capital + position * price
            portfolio_values.append(portfolio_value)
        
        data['portfolio'] = portfolio_values
        self.results = data
        
        return self.calculate_metrics(data)
    
    def calculate_metrics(self, data):
        """计算回测指标"""
        initial_value = self.initial_capital
        final_value = data['portfolio'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value * 100
        
        days = len(data)
        years = days / 250
        if years > 0:
            annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100
        else:
            annualized_return = 0
        
        portfolio = data['portfolio'].values
        max_drawdown = 0
        peak = portfolio[0]
        for value in portfolio:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        win_trades = 0
        total_profit = 0
        buy_price = 0
        trade_count = 0
        
        for trade in self.trades:
            if trade['type'] == 'buy':
                buy_price = trade['price']
                trade_count += 1
            elif trade['type'] == 'sell' and buy_price > 0:
                profit = (trade['price'] - buy_price) * trade['shares']
                total_profit += profit
                if profit > 0:
                    win_trades += 1
                buy_price = 0
        
        total_trades = len([t for t in self.trades if t['type'] == 'sell'])
        win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        daily_returns = data['portfolio'].pct_change().dropna()
        if len(daily_returns) > 0 and daily_returns.std() != 0:
            sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(250)
        else:
            sharpe_ratio = 0
        
        return {
            'initial_capital': initial_value,
            'final_value': round(final_value, 2),
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'total_trades': total_trades,
            'avg_profit': round(avg_profit, 2),
            'sharpe_ratio': round(sharpe_ratio, 2)
        }
    
    def parameter_optimization(self, data, strategy='macd'):
        """参数优化"""
        print(f"\n🔧 正在优化 {strategy.upper()} 策略参数...")
        
        best_params = None
        best_return = float('-inf')
        all_results = []
        
        if strategy == 'macd':
            for threshold in [0, 0.01, 0.02]:
                params = {'fast': 12, 'slow': 26, 'signal': 9, 'threshold': threshold}
                for stop_loss in [0.05, 0.08, 0.10]:
                    for take_profit in [0.10, 0.15, 0.20]:
                        metrics = self.run_backtest_with_stop_loss(
                            data, strategy, stop_loss, take_profit
                        )
                        all_results.append({
                            'params': params,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            **metrics
                        })
                        
                        if metrics['total_return'] > best_return:
                            best_return = metrics['total_return']
                            best_params = (params, stop_loss, take_profit)
                            
        elif strategy == 'kdj':
            for oversold in [20, 25, 30]:
                for overbought in [70, 75, 80]:
                    params = {'oversold': oversold, 'overbought': overbought, 'confirm': True}
                    for stop_loss in [0.05, 0.08, 0.10]:
                        for take_profit in [0.10, 0.15, 0.20]:
                            metrics = self.run_backtest_with_stop_loss(
                                data, strategy, stop_loss, take_profit
                            )
                            all_results.append({
                                'params': params,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                                **metrics
                            })
                            
                            if metrics['total_return'] > best_return:
                                best_return = metrics['total_return']
                                best_params = (params, stop_loss, take_profit)
                                
        elif strategy == 'ma':
            for fast in [5, 10]:
                for slow in [20, 30]:
                    for confirm in [True, False]:
                        params = {'fast': fast, 'slow': slow, 'confirm_ma60': confirm}
                        for stop_loss in [0.05, 0.08, 0.10]:
                            for take_profit in [0.10, 0.15, 0.20]:
                                metrics = self.run_backtest_with_stop_loss(
                                    data, strategy, stop_loss, take_profit
                                )
                                all_results.append({
                                    'params': params,
                                    'stop_loss': stop_loss,
                                    'take_profit': take_profit,
                                    **metrics
                                })
                                
                                if metrics['total_return'] > best_return:
                                    best_return = metrics['total_return']
                                    best_params = (params, stop_loss, take_profit)
        
        all_results.sort(key=lambda x: -x['total_return'])
        
        return best_params, all_results[:10]
    
    def print_results(self, metrics):
        """打印回测结果"""
        print("=" * 80)
        print("⚡ 涨停先知 - 优化版回测报告 ⚡")
        print("=" * 80)
        print()
        print("📊 核心指标")
        print("-" * 50)
        print(f"初始资金:        ¥{metrics['initial_capital']:>15,}")
        print(f"最终资金:        ¥{metrics['final_value']:>15,.2f}")
        print(f"总收益率:        {metrics['total_return']:>15.2f}%")
        print(f"年化收益率:      {metrics['annualized_return']:>15.2f}%")
        print(f"最大回撤:        {metrics['max_drawdown']:>15.2f}%")
        print(f"胜率:            {metrics['win_rate']:>15.2f}%")
        print(f"交易次数:        {metrics['total_trades']:>15d}次")
        print(f"平均盈亏:        ¥{metrics['avg_profit']:>15,.2f}")
        print(f"夏普比率:        {metrics['sharpe_ratio']:>15.2f}")
        print()
        
        if self.trades:
            print("💹 交易记录")
            print("-" * 80)
            buy_count = 0
            sell_count = 0
            for i, trade in enumerate(self.trades):
                if trade['type'] == 'buy':
                    buy_count += 1
                    print(f"{buy_count}. {trade['date'].strftime('%Y-%m-%d')} 🟢 买入")
                    print(f"   价格: ¥{trade['price']:.2f} | 数量: {trade['shares']}股 | 成本: ¥{trade['cost']:.2f}")
                else:
                    sell_count += 1
                    reason = trade.get('reason', '卖出')
                    reason_icon = "🛑" if reason == '止损' else "🎯" if reason == '止盈' else "📊"
                    print(f"   {sell_count}. {trade['date'].strftime('%Y-%m-%d')} 🔴 {reason_icon} {reason}")
                    print(f"   价格: ¥{trade['price']:.2f} | 数量: {trade['shares']}股 | 收入: ¥{trade['revenue']:.2f}")
                    profit = trade['revenue'] - self.trades[buy_count*2-2]['cost']
                    profit_icon = "🟢" if profit > 0 else "🔴"
                    print(f"   盈亏: {profit_icon} ¥{profit:.2f}")
            print()
        
        if self.results is not None:
            print("📈 收益曲线")
            print("-" * 80)
            portfolio = self.results['portfolio']
            normalized = (portfolio - portfolio.min()) / (portfolio.max() - portfolio.min()) * 30
            dates = self.results.index
            step = max(1, len(dates) // 15)
            
            max_val = portfolio.max()
            min_val = portfolio.min()
            
            for i in range(0, len(dates), step):
                date_str = dates[i].strftime('%m-%d')
                bar_len = int(normalized.iloc[i])
                bar = "█" * bar_len + "░" * (30 - bar_len)
                value = f"¥{portfolio.iloc[i]:,.0f}"
                marker = "▲" if portfolio.iloc[i] >= self.initial_capital else "▼"
                print(f"{date_str} {marker} {bar} {value}")
            print()
            print(f"最高: ¥{max_val:,.2f} | 最低: ¥{min_val:,.2f} | 当前: ¥{portfolio.iloc[-1]:,.2f}")

def main():
    print("=" * 80)
    print("⚡ 涨停先知 - 优化版策略回测系统 v2.0 ⚡")
    print("=" * 80)
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 初始资金: ¥100,000")
    print("📈 回测周期: 250个交易日 (1年)")
    print("💹 手续费: 0.15%")
    print("🛡️ 止损: 8% | 🎯 止盈: 15%")
    print("=" * 80)
    print()
    
    backtester = AdvancedBacktester(initial_capital=100000, commission=0.0015)
    
    data = backtester.generate_historical_data(days=250, trend='bull')
    
    strategies = ['macd', 'kdj', 'ma', 'rsi', 'combined']
    results = {}
    
    print("🚀 正在运行多策略回测...")
    print("=" * 80)
    
    for strategy in strategies:
        metrics = backtester.run_backtest_with_stop_loss(
            data.copy(), 
            strategy=strategy,
            stop_loss=0.08,
            take_profit=0.15
        )
        results[strategy] = metrics
        
        print(f"\n📊 {strategy.upper()} 策略:")
        print(f"   总收益: {metrics['total_return']}% | 年化: {metrics['annualized_return']}%")
        print(f"   最大回撤: {metrics['max_drawdown']}% | 胜率: {metrics['win_rate']}%")
        print(f"   交易次数: {metrics['total_trades']}次 | 夏普: {metrics['sharpe_ratio']}")
    
    sorted_results = sorted(results.items(), key=lambda x: -x[1]['total_return'])
    
    print("\n" + "=" * 80)
    print("🏆 策略排名")
    print("=" * 80)
    print(f"{'策略':<10} {'总收益':<12} {'年化':<12} {'最大回撤':<12} {'胜率':<10} {'交易次数':<10} {'夏普比率':<10}")
    print("-" * 80)
    
    for name, metrics in sorted_results:
        print(f"{name.upper():<10} {metrics['total_return']:>10.2f}%   {metrics['annualized_return']:>10.2f}%   {metrics['max_drawdown']:>10.2f}%   {metrics['win_rate']:>8.2f}%   {metrics['total_trades']:>8d}   {metrics['sharpe_ratio']:>8.2f}")
    
    best_strategy = sorted_results[0][0]
    best_metrics = sorted_results[0][1]
    
    print("\n" + "=" * 80)
    print(f"🥇 最优策略: {best_strategy.upper()}")
    print("=" * 80)
    
    backtester.run_backtest_with_stop_loss(data.copy(), best_strategy, 0.08, 0.15)
    backtester.print_results(best_metrics)
    
    print("\n🔧 参数优化")
    print("=" * 80)
    
    best_params, top_results = backtester.parameter_optimization(data.copy(), 'macd')
    
    if best_params:
        print(f"\n✅ MACD策略最优参数:")
        print(f"   阈值: {best_params[0]['threshold']}")
        print(f"   止损: {best_params[1]*100}%")
        print(f"   止盈: {best_params[2]*100}%")
        
        print(f"\n🏅 TOP 3 参数组合:")
        for i, result in enumerate(top_results[:3], 1):
            print(f"\n{i}. 总收益: {result['total_return']}% | 最大回撤: {result['max_drawdown']}%")
            print(f"   止损: {result['stop_loss']*100}% | 止盈: {result['take_profit']*100}%")
    
    print("\n" + "=" * 80)
    print("✅ 优化版回测完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()