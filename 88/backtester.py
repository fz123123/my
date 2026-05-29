#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 策略回测系统
ZTB Seer - Backtesting System
支持多种技术指标策略回测
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

class Backtester:
    def __init__(self, initial_capital=100000, commission=0.0015):
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = None
        
    def generate_historical_data(self, days=120):
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
        
        price = 25.0
        for i in range(days):
            change = np.random.normal(0, 0.02)
            open_price = price * (1 + np.random.normal(0, 0.005))
            close_price = price * (1 + change)
            high_price = max(open_price, close_price) * (1 + np.random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - np.random.uniform(0, 0.01))
            volume = int(np.random.normal(500000, 200000))
            
            data['open'].append(round(open_price, 2))
            data['high'].append(round(high_price, 2))
            data['low'].append(round(low_price, 2))
            data['close'].append(round(close_price, 2))
            data['volume'].append(volume)
            
            price = close_price
            
        return pd.DataFrame(data).set_index('date')
    
    def calculate_indicators(self, data):
        """计算技术指标"""
        df = data.copy()
        
        # 均线
        df['ma5'] = df['close'].rolling(5).mean().round(2)
        df['ma10'] = df['close'].rolling(10).mean().round(2)
        df['ma20'] = df['close'].rolling(20).mean().round(2)
        
        # MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['dif'] = (df['ema12'] - df['ema26']).round(4)
        df['dea'] = df['dif'].ewm(span=9, adjust=False).mean().round(4)
        df['macd'] = ((df['dif'] - df['dea']) * 2).round(4)
        
        # KDJ
        low_min = df['low'].rolling(9).min()
        high_max = df['high'].rolling(9).max()
        df['rsv'] = ((df['close'] - low_min) / (high_max - low_min) * 100).round(2)
        df['k'] = df['rsv'].ewm(com=2, adjust=False).mean().round(2)
        df['d'] = df['k'].ewm(com=2, adjust=False).mean().round(2)
        df['j'] = (3 * df['k'] - 2 * df['d']).round(2)
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = (100 - (100 / (1 + rs))).round(2)
        
        # 布林带
        df['boll_mid'] = df['close'].rolling(20).mean().round(2)
        df['boll_std'] = df['close'].rolling(20).std()
        df['boll_upper'] = (df['boll_mid'] + 2 * df['boll_std']).round(2)
        df['boll_lower'] = (df['boll_mid'] - 2 * df['boll_std']).round(2)
        
        return df
    
    def strategy_macd_gold(self, df):
        """MACD金叉策略"""
        signals = []
        for i in range(len(df)):
            if i < 1:
                signals.append(0)
                continue
            
            prev_dif = df['dif'].iloc[i-1]
            prev_dea = df['dea'].iloc[i-1]
            curr_dif = df['dif'].iloc[i]
            curr_dea = df['dea'].iloc[i]
            
            # MACD金叉：DIF上穿DEA
            if prev_dif <= prev_dea and curr_dif > curr_dea and curr_dif > 0:
                signals.append(1)
            # MACD死叉：DIF下穿DEA
            elif prev_dif >= prev_dea and curr_dif < curr_dea and curr_dif < 0:
                signals.append(-1)
            else:
                signals.append(0)
                
        df['signal_macd'] = signals
        return df
    
    def strategy_kdj(self, df):
        """KDJ策略"""
        signals = []
        for i in range(len(df)):
            if i < 1:
                signals.append(0)
                continue
            
            k_prev = df['k'].iloc[i-1]
            d_prev = df['d'].iloc[i-1]
            k_curr = df['k'].iloc[i]
            d_curr = df['d'].iloc[i]
            
            # KDJ金叉且K<20（超卖）
            if k_prev <= d_prev and k_curr > d_curr and k_curr < 30:
                signals.append(1)
            # KDJ死叉且K>80（超买）
            elif k_prev >= d_prev and k_curr < d_curr and k_curr > 70:
                signals.append(-1)
            else:
                signals.append(0)
                
        df['signal_kdj'] = signals
        return df
    
    def strategy_ma_crossover(self, df):
        """均线交叉策略"""
        signals = []
        for i in range(len(df)):
            if i < 1:
                signals.append(0)
                continue
            
            ma5_prev = df['ma5'].iloc[i-1]
            ma10_prev = df['ma10'].iloc[i-1]
            ma5_curr = df['ma5'].iloc[i]
            ma10_curr = df['ma10'].iloc[i]
            
            # 金叉：MA5上穿MA10
            if ma5_prev <= ma10_prev and ma5_curr > ma10_curr:
                signals.append(1)
            # 死叉：MA5下穿MA10
            elif ma5_prev >= ma10_prev and ma5_curr < ma10_curr:
                signals.append(-1)
            else:
                signals.append(0)
                
        df['signal_ma'] = signals
        return df
    
    def strategy_rsi(self, df):
        """RSI策略"""
        signals = []
        for i in range(len(df)):
            rsi = df['rsi'].iloc[i]
            
            if rsi < 30:
                signals.append(1)
            elif rsi > 70:
                signals.append(-1)
            else:
                signals.append(0)
                
        df['signal_rsi'] = signals
        return df
    
    def strategy_combined(self, df):
        """组合策略"""
        df = self.strategy_macd_gold(df)
        df = self.strategy_kdj(df)
        df = self.strategy_ma_crossover(df)
        df = self.strategy_rsi(df)
        
        # 综合信号：至少2个策略发出买入/卖出信号
        df['signal'] = 0
        for i in range(len(df)):
            buy_count = sum([
                df['signal_macd'].iloc[i] == 1,
                df['signal_kdj'].iloc[i] == 1,
                df['signal_ma'].iloc[i] == 1,
                df['signal_rsi'].iloc[i] == 1
            ])
            sell_count = sum([
                df['signal_macd'].iloc[i] == -1,
                df['signal_kdj'].iloc[i] == -1,
                df['signal_ma'].iloc[i] == -1,
                df['signal_rsi'].iloc[i] == -1
            ])
            
            if buy_count >= 2:
                df.loc[df.index[i], 'signal'] = 1
            elif sell_count >= 2:
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def run_backtest(self, strategy='combined', days=120):
        """运行回测"""
        # 生成历史数据
        data = self.generate_historical_data(days)
        data = self.calculate_indicators(data)
        
        # 应用策略
        if strategy == 'macd':
            data = self.strategy_macd_gold(data)
            data['signal'] = data['signal_macd']
        elif strategy == 'kdj':
            data = self.strategy_kdj(data)
            data['signal'] = data['signal_kdj']
        elif strategy == 'ma':
            data = self.strategy_ma_crossover(data)
            data['signal'] = data['signal_ma']
        elif strategy == 'rsi':
            data = self.strategy_rsi(data)
            data['signal'] = data['signal_rsi']
        else:
            data = self.strategy_combined(data)
            
        # 执行交易
        capital = self.initial_capital
        position = 0
        trades = []
        portfolio_value = []
        
        for date, row in data.iterrows():
            price = row['close']
            
            # 买入信号
            if row['signal'] == 1 and position == 0:
                shares = int(capital / price / 100) * 100
                cost = shares * price * (1 + self.commission)
                if cost <= capital:
                    position = shares
                    capital -= cost
                    trades.append({
                        'date': date,
                        'type': 'buy',
                        'price': price,
                        'shares': shares,
                        'cost': cost
                    })
            
            # 卖出信号
            elif row['signal'] == -1 and position > 0:
                revenue = position * price * (1 - self.commission)
                capital += revenue
                trades.append({
                    'date': date,
                    'type': 'sell',
                    'price': price,
                    'shares': position,
                    'revenue': revenue
                })
                position = 0
            
            # 计算账户价值
            portfolio_value.append(capital + position * price)
            
        data['portfolio'] = portfolio_value
        self.results = data
        self.trades = trades
        
        return self.calculate_metrics(data, trades)
    
    def calculate_metrics(self, data, trades):
        """计算回测指标"""
        initial_value = self.initial_capital
        final_value = data['portfolio'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value * 100
        
        # 年化收益率
        days = len(data)
        annualized_return = ((1 + total_return / 100) ** (365 / days) - 1) * 100
        
        # 最大回撤
        portfolio = data['portfolio'].values
        max_drawdown = 0
        peak = portfolio[0]
        for value in portfolio:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 胜率
        win_trades = 0
        lose_trades = 0
        total_profit = 0
        
        for i in range(0, len(trades), 2):
            if i + 1 < len(trades):
                buy_price = trades[i]['price']
                sell_price = trades[i+1]['price']
                profit = (sell_price - buy_price) * trades[i]['shares']
                total_profit += profit
                if profit > 0:
                    win_trades += 1
                else:
                    lose_trades += 1
        
        win_rate = win_trades / (win_trades + lose_trades) * 100 if (win_trades + lose_trades) > 0 else 0
        
        # 平均盈亏
        avg_profit = total_profit / (win_trades + lose_trades) if (win_trades + lose_trades) > 0 else 0
        
        # 夏普比率（简化版）
        daily_returns = data['portfolio'].pct_change().dropna()
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        
        return {
            'initial_capital': initial_value,
            'final_value': round(final_value, 2),
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'total_trades': len(trades) // 2,
            'avg_profit': round(avg_profit, 2),
            'sharpe_ratio': round(sharpe_ratio, 2)
        }
    
    def print_results(self, metrics):
        """打印回测结果"""
        print("=" * 80)
        print("⚡ 涨停先知 - 策略回测报告 ⚡")
        print("=" * 80)
        print()
        print("📊 回测结果汇总")
        print("-" * 40)
        print(f"初始资金: ¥{metrics['initial_capital']:,}")
        print(f"最终资金: ¥{metrics['final_value']:,}")
        print(f"总收益率: {metrics['total_return']}%")
        print(f"年化收益率: {metrics['annualized_return']}%")
        print(f"最大回撤: {metrics['max_drawdown']}%")
        print(f"胜率: {metrics['win_rate']}%")
        print(f"交易次数: {metrics['total_trades']}次")
        print(f"平均盈亏: ¥{metrics['avg_profit']:,}")
        print(f"夏普比率: {metrics['sharpe_ratio']}")
        print()
        
        print("📈 收益曲线统计")
        print("-" * 40)
        portfolio = self.results['portfolio']
        print(f"最高市值: ¥{portfolio.max():,.2f}")
        print(f"最低市值: ¥{portfolio.min():,.2f}")
        print(f"平均市值: ¥{portfolio.mean():,.2f}")
        print()
        
        print("💹 交易记录")
        print("-" * 40)
        for i, trade in enumerate(self.trades):
            trade_type = "买入" if trade['type'] == 'buy' else "卖出"
            print(f"{i+1}. {trade['date'].strftime('%Y-%m-%d')} {trade_type}")
            print(f"     价格: ¥{trade['price']:.2f}")
            print(f"     数量: {trade['shares']}股")
            if trade['type'] == 'buy':
                print(f"     成本: ¥{trade['cost']:.2f}")
            else:
                print(f"     收入: ¥{trade['revenue']:.2f}")
        print()
        
        print("=" * 80)
        
        # 简单的收益曲线ASCII图
        print("📉 收益曲线")
        print("-" * 40)
        portfolio = self.results['portfolio']
        normalized = (portfolio - portfolio.min()) / (portfolio.max() - portfolio.min()) * 20
        dates = self.results.index
        step = max(1, len(dates) // 30)
        
        for i in range(0, len(dates), step):
            date_str = dates[i].strftime('%m-%d')
            bar = "█" * int(normalized.iloc[i])
            value = f"¥{portfolio.iloc[i]:,.0f}"
            print(f"{date_str}: {bar} {value}")
    
    def compare_strategies(self):
        """比较不同策略"""
        strategies = ['macd', 'kdj', 'ma', 'rsi', 'combined']
        results = {}
        
        print("=" * 80)
        print("⚡ 策略对比分析 ⚡")
        print("=" * 80)
        print()
        
        for strategy in strategies:
            metrics = self.run_backtest(strategy)
            results[strategy] = metrics
            print(f"📊 {strategy.upper()} 策略:")
            print(f"   总收益: {metrics['total_return']}% | 年化: {metrics['annualized_return']}%")
            print(f"   最大回撤: {metrics['max_drawdown']}% | 胜率: {metrics['win_rate']}%")
            print(f"   交易次数: {metrics['total_trades']}次 | 夏普: {metrics['sharpe_ratio']}")
            print()
        
        # 找出最优策略
        best_return = max(results.items(), key=lambda x: x[1]['total_return'])
        best_risk = min(results.items(), key=lambda x: x[1]['max_drawdown'])
        
        print("🏆 策略排名")
        print("-" * 40)
        sorted_by_return = sorted(results.items(), key=lambda x: -x[1]['total_return'])
        for i, (name, metrics) in enumerate(sorted_by_return, 1):
            print(f"{i}. {name.upper()}: {metrics['total_return']}%")
        
        print()
        print(f"🥇 最高收益策略: {best_return[0].upper()} ({best_return[1]['total_return']}%)")
        print(f"🥈 最小回撤策略: {best_risk[0].upper()} ({best_risk[1]['max_drawdown']}%)")
        print()
        print("=" * 80)
        
        return results

if __name__ == "__main__":
    backtester = Backtester(initial_capital=100000)
    
    print("请选择回测模式:")
    print("1. 单一策略回测")
    print("2. 多策略对比")
    choice = input("请输入选择 (1/2): ")
    
    if choice == '1':
        print("\n请选择策略:")
        print("1. MACD金叉策略")
        print("2. KDJ策略")
        print("3. 均线交叉策略")
        print("4. RSI策略")
        print("5. 组合策略")
        strategy_choice = input("请输入选择 (1-5): ")
        
        strategy_map = {'1': 'macd', '2': 'kdj', '3': 'ma', '4': 'rsi', '5': 'combined'}
        strategy = strategy_map.get(strategy_choice, 'combined')
        
        print(f"\n正在运行 {strategy.upper()} 策略回测...")
        metrics = backtester.run_backtest(strategy)
        backtester.print_results(metrics)
        
    elif choice == '2':
        backtester.compare_strategies()
        
    else:
        print("无效选择")