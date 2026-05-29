#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSI自适应策略类 - 可复用的量化交易策略

功能特点：
- 基于RSI指标的自适应交易策略
- 支持市场状态识别（牛市/熊市/震荡）
- 动态ATR止盈机制
- ATR移动止损机制
- 趋势过滤（MA5 > MA30）
- 可直接应用到任意股票数据

使用示例：
    from strategies.rsi_adaptive_strategy import RsiAdaptiveStrategy
    
    strategy = RsiAdaptiveStrategy(
        overbought=70,
        oversold=30,
        use_atr_tp=True,
        use_trailing_stop=True
    )
    
    signals = strategy.generate_signals(df)
    report = strategy.get_performance_report(df)
"""

import pandas as pd
import numpy as np


class RsiAdaptiveStrategy:
    """
    RSI自适应交易策略类
    
    参数说明：
        oversold: RSI超卖阈值，低于此值产生买入信号（默认30）
        overbought: RSI超买阈值，高于此值产生卖出信号（默认70）
        
        牛市参数（bull_*）:
            bull_stop_loss: 牛市初始止损比例（默认10%）
            bull_take_profit: 牛市固定止盈比例（默认30%）
            bull_holding_days: 牛市最大持仓天数（默认60）
        
        熊市参数（bear_*）:
            bear_stop_loss: 熊市初始止损比例（默认5%）
            bear_take_profit: 熊市固定止盈比例（默认15%）
            bear_holding_days: 熊市最大持仓天数（默认30）
        
        震荡市参数（neutral_*）:
            neutral_stop_loss: 震荡市初始止损比例（默认8%）
            neutral_take_profit: 震荡市固定止盈比例（默认20%）
            neutral_holding_days: 震荡市最大持仓天数（默认45）
        
        ATR动态止盈参数:
            use_atr_tp: 是否启用ATR动态止盈（默认False）
            atr_tp_multiplier: ATR止盈倍数（默认3.0）
            atr_tp_min_pct: 最小止盈比例（默认10%）
            atr_tp_max_pct: 最大止盈比例（默认50%）
        
        ATR移动止损参数:
            use_trailing_stop: 是否启用移动止损（默认False）
            trailing_stop_atr_multiplier: 移动止损ATR倍数（默认2.0）
            trailing_stop_min_pct: 最小止损比例（默认5%）
    """
    
    def __init__(self, 
                 oversold=30, 
                 overbought=70,
                 bull_stop_loss=0.10, 
                 bull_take_profit=0.30, 
                 bull_holding_days=60,
                 bear_stop_loss=0.05, 
                 bear_take_profit=0.15, 
                 bear_holding_days=30,
                 neutral_stop_loss=0.08, 
                 neutral_take_profit=0.20, 
                 neutral_holding_days=45,
                 use_atr_tp=False, 
                 atr_tp_multiplier=3.0, 
                 atr_tp_min_pct=0.10, 
                 atr_tp_max_pct=0.50,
                 use_trailing_stop=False, 
                 trailing_stop_atr_multiplier=2.0, 
                 trailing_stop_min_pct=0.05):
        
        self.oversold = oversold
        self.overbought = overbought
        
        self.bull_stop_loss = bull_stop_loss
        self.bull_take_profit = bull_take_profit
        self.bull_holding_days = bull_holding_days
        
        self.bear_stop_loss = bear_stop_loss
        self.bear_take_profit = bear_take_profit
        self.bear_holding_days = bear_holding_days
        
        self.neutral_stop_loss = neutral_stop_loss
        self.neutral_take_profit = neutral_take_profit
        self.neutral_holding_days = neutral_holding_days
        
        self.use_atr_tp = use_atr_tp
        self.atr_tp_multiplier = atr_tp_multiplier
        self.atr_tp_min_pct = atr_tp_min_pct
        self.atr_tp_max_pct = atr_tp_max_pct
        
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_atr_multiplier = trailing_stop_atr_multiplier
        self.trailing_stop_min_pct = trailing_stop_min_pct
        
        self.trade_records = []
        self.signals = None
    
    def _calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma30'] = df['close'].rolling(window=30).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(14).mean()
        
        return df
    
    def _identify_market_regime(self, df, i):
        """识别市场状态：bull(牛市)、bear(熊市)、neutral(震荡)"""
        if i < 60:
            return 'neutral'
        
        ma5 = df['ma5'].iloc[i]
        ma20 = df['ma20'].iloc[i]
        ma60 = df['ma60'].iloc[i]
        
        trend_strength = abs(ma5 - ma20) / ma20
        
        if ma5 > ma20 and ma20 > ma60 and trend_strength > 0.02:
            return 'bull'
        elif ma5 < ma20 and ma20 < ma60 and trend_strength > 0.02:
            return 'bear'
        
        return 'neutral'
    
    def generate_signals(self, df, verbose=False):
        """
        生成交易信号
        
        参数：
            df: 包含 'open', 'high', 'low', 'close' 列的DataFrame，index为日期
            verbose: 是否打印详细日志（默认False）
        
        返回：
            signals: 交易信号Series（1=买入，-1=卖出，0=持有）
        """
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError("DataFrame必须包含 open, high, low, close 列")
        
        df = self._calculate_indicators(df)
        signals = pd.Series(0, index=df.index)
        
        position = 0
        entry_price = 0
        entry_date = None
        entry_atr = 0
        trailing_stop_price = 0
        current_regime = 'neutral'
        prev_regime = 'neutral'
        
        self.trade_records = []
        
        for i in range(len(df)):
            date = df.index[i]
            price = df['close'].iloc[i]
            rsi = df['rsi'].iloc[i]
            ma5 = df['ma5'].iloc[i]
            ma30 = df['ma30'].iloc[i] if 'ma30' in df.columns else df['ma20'].iloc[i]
            atr = df['atr'].iloc[i] if 'atr' in df.columns else 0
            
            prev_ma5 = df['ma5'].iloc[i-1] if i > 0 else ma5
            prev_ma30 = df['ma30'].iloc[i-1] if (i > 0 and 'ma30' in df.columns) else ma30
            
            ma_cross_up = (prev_ma5 <= prev_ma30) and (ma5 > ma30)
            ma_cross_down = (prev_ma5 >= prev_ma30) and (ma5 < ma30)
            
            if verbose and ma_cross_up:
                print(f"[{date.strftime('%Y-%m-%d')}] [UP] MA5金叉MA30: MA5={ma5:.2f}, MA30={ma30:.2f}, 价格={price:.2f}")
            
            if verbose and ma_cross_down:
                print(f"[{date.strftime('%Y-%m-%d')}] [DN] MA5死叉MA30: MA5={ma5:.2f}, MA30={ma30:.2f}, 价格={price:.2f}")
            
            current_regime = self._identify_market_regime(df, i)
            regime_desc = {'bull': '牛市', 'bear': '熊市', 'neutral': '震荡'}[current_regime]
            
            if verbose and current_regime != prev_regime:
                print(f"[{date.strftime('%Y-%m-%d')}] [SW] 市场状态切换")
            prev_regime = current_regime
            
            if current_regime == 'bull':
                stop_loss_pct = self.bull_stop_loss
                base_take_profit_pct = self.bull_take_profit
                max_holding = self.bull_holding_days
            elif current_regime == 'bear':
                stop_loss_pct = self.bear_stop_loss
                base_take_profit_pct = self.bear_take_profit
                max_holding = self.bear_holding_days
            else:
                stop_loss_pct = self.neutral_stop_loss
                base_take_profit_pct = self.neutral_take_profit
                max_holding = self.neutral_holding_days
            
            if self.use_atr_tp and entry_price > 0 and entry_atr > 0:
                atr_take_profit_pct = (entry_atr * self.atr_tp_multiplier) / entry_price
                take_profit_pct = max(self.atr_tp_min_pct, min(atr_take_profit_pct, self.atr_tp_max_pct))
            else:
                take_profit_pct = base_take_profit_pct
            
            if verbose and rsi <= self.oversold:
                print(f"[{date.strftime('%Y-%m-%d')}] [WARN] RSI超卖: {rsi:.1f}, 价格={price:.2f}")
            
            if verbose and rsi >= self.overbought:
                print(f"[{date.strftime('%Y-%m-%d')}] [WARN] RSI超买: {rsi:.1f}, 价格={price:.2f}")
            
            if position == 0:
                rsi_buy = (rsi < self.oversold) & (df['rsi'].shift(1).iloc[i] >= self.oversold)
                trend_ok = ma5 > ma30
                
                if rsi_buy and trend_ok:
                    signals.iloc[i] = 1
                    position = 1
                    entry_price = price
                    entry_date = date
                    entry_atr = atr
                    
                    if self.use_trailing_stop and atr > 0:
                        initial_trailing = max(price * (1 - self.trailing_stop_min_pct), 
                                             price - atr * self.trailing_stop_atr_multiplier)
                        trailing_stop_price = initial_trailing
                    else:
                        trailing_stop_price = 0
                    
                    atr_tp_info = f", ATR={atr:.2f}, ATR止盈目标={((atr * self.atr_tp_multiplier) / price * 100):.1f}%" if self.use_atr_tp else ""
                    trailing_info = f", 初始移动止损={trailing_stop_price:.2f}" if self.use_trailing_stop else ""
                    
                    if verbose:
                        print(f"[{date.strftime('%Y-%m-%d')}] 🛒 买入信号: 价格={price:.2f}, RSI={rsi:.1f}, MA5={ma5:.2f}, MA30={ma30:.2f}, 状态={regime_desc}{atr_tp_info}{trailing_info}")
                        
                elif verbose and rsi_buy and not trend_ok:
                    print(f"[{date.strftime('%Y-%m-%d')}] ⏳ RSI超卖但趋势不满足: 价格={price:.2f}, RSI={rsi:.1f}, MA5={ma5:.2f}, MA30={ma30:.2f}")
            else:
                days_held = (date - entry_date).days
                current_profit = (price - entry_price) / entry_price * 100
                
                if self.use_trailing_stop and trailing_stop_price > 0:
                    new_trailing_stop = max(trailing_stop_price, 
                                           price - atr * self.trailing_stop_atr_multiplier)
                    new_trailing_stop = max(new_trailing_stop, 
                                           entry_price * (1 - self.trailing_stop_min_pct))
                    if new_trailing_stop > trailing_stop_price:
                        trailing_stop_price = new_trailing_stop
                
                rsi_sell = (rsi > self.overbought) & (df['rsi'].shift(1).iloc[i] <= self.overbought)
                take_profit = price > entry_price * (1 + take_profit_pct)
                time_stop = days_held >= max_holding
                
                if self.use_trailing_stop and trailing_stop_price > 0:
                    stop_loss = price < trailing_stop_price
                    stop_loss_desc = "移动止损"
                else:
                    stop_loss = price < entry_price * (1 - stop_loss_pct)
                    stop_loss_desc = f"止损({stop_loss_pct*100}%)"
                
                exit_reason = None
                
                if rsi_sell:
                    signals.iloc[i] = -1
                    exit_reason = "RSI超买"
                elif stop_loss:
                    signals.iloc[i] = -1
                    exit_reason = stop_loss_desc
                elif take_profit:
                    signals.iloc[i] = -1
                    exit_reason = "ATR动态止盈" if self.use_atr_tp else "止盈"
                elif time_stop:
                    signals.iloc[i] = -1
                    exit_reason = "时间止损"
                
                if signals.iloc[i] == -1:
                    self.trade_records.append({
                        'buy_date': entry_date,
                        'buy_price': entry_price,
                        'sell_date': date,
                        'sell_price': price,
                        'profit_pct': current_profit,
                        'days_held': days_held,
                        'exit_reason': exit_reason,
                        'market_regime': regime_desc
                    })
                    
                    if verbose:
                        print(f"[{date.strftime('%Y-%m-%d')}] [SELL] 卖出信号({exit_reason}): 价格={price:.2f}, 买入价={entry_price:.2f}, 盈亏={current_profit:+.2f}%, 持仓天数={days_held}")
                    
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_atr = 0
                    trailing_stop_price = 0
        
        self.signals = signals
        return signals
    
    def get_performance_report(self, df=None):
        """
        获取策略绩效报告
        
        参数：
            df: 可选，用于计算最大回撤的原始数据
        
        返回：
            report: 包含绩效指标的字典
        """
        if not self.trade_records:
            return {
                'message': '尚未生成交易信号，请先调用 generate_signals()'
            }
        
        total_trades = len(self.trade_records)
        winning_trades = sum(1 for t in self.trade_records if t['profit_pct'] > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        avg_profit = sum(t['profit_pct'] for t in self.trade_records) / total_trades if total_trades > 0 else 0
        total_return = np.prod([1 + t['profit_pct'] / 100 for t in self.trade_records]) * 100 - 100
        
        max_drawdown = 0.0
        if df is not None and len(self.trade_records) > 0:
            equity_curve = [1.0]
            position = 0
            entry_price = 0
            
            for i in range(len(df)):
                price = df['close'].iloc[i]
                
                if i > 0 and self.signals.iloc[i-1] == 1:
                    position = 1
                    entry_price = price
                elif i > 0 and self.signals.iloc[i-1] == -1:
                    position = 0
                
                if position == 1 and entry_price > 0:
                    current_return = (price - entry_price) / entry_price
                    equity_curve.append(equity_curve[-1] * (1 + current_return))
                else:
                    equity_curve.append(equity_curve[-1])
            
            running_max = np.maximum.accumulate(equity_curve)
            drawdowns = (running_max - equity_curve) / running_max * 100
            max_drawdown = np.max(drawdowns)
        
        report = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_profit_pct': avg_profit,
            'total_return_pct': total_return,
            'max_drawdown_pct': max_drawdown,
            'trade_records': self.trade_records,
            'buy_dates': [t['buy_date'] for t in self.trade_records],
            'sell_dates': [t['sell_date'] for t in self.trade_records]
        }
        
        return report
    
    def print_report(self, df=None):
        """打印格式化的绩效报告"""
        report = self.get_performance_report(df)
        
        if 'message' in report:
            print(report['message'])
            return
        
        print("="*60)
        print("          [REP] RSI自适应策略绩效报告")
        print("="*60)
        
        print(f"\n[STATS] 交易统计:")
        print(f"  总交易次数: {report['total_trades']}")
        print(f"  盈利次数: {report['winning_trades']}")
        print(f"  亏损次数: {report['losing_trades']}")
        print(f"  胜率: {report['win_rate']:.1f}%")
        print(f"  平均盈亏: {report['avg_profit_pct']:+.2f}%")
        print(f"  总收益率: {report['total_return_pct']:+.2f}%")
        print(f"  最大回撤: {report['max_drawdown_pct']:.2f}%")
        
        print(f"\n📋 交易详情:")
        print(f"  {'-'*70}")
        print(f"  序号 | 买入日期   | 买入价 | 卖出日期   | 卖出价 | 盈亏    | 持仓天数 | 退出原因")
        print(f"  {'-'*70}")
        
        for i, trade in enumerate(report['trade_records'], 1):
            print(f"  {i:3d} | {trade['buy_date'].date()} | {trade['buy_price']:>6.2f} | {trade['sell_date'].date()} | {trade['sell_price']:>6.2f} | {trade['profit_pct']:>+.2f}% | {trade['days_held']:>8d} | {trade['exit_reason']}")
        
        print(f"  {'-'*70}")
        print("\n✅ 报告生成完成！")


if __name__ == "__main__":
    print("="*60)
    print("    RSI自适应策略类 - 使用示例")
    print("="*60)
    print("\n使用方法：")
    print("""
from strategies.rsi_adaptive_strategy import RsiAdaptiveStrategy

# 创建策略实例
strategy = RsiAdaptiveStrategy(
    oversold=30,
    overbought=70,
    bull_stop_loss=0.15,
    bear_stop_loss=0.15,
    neutral_stop_loss=0.15,
    use_atr_tp=True,
    atr_tp_multiplier=3.0,
    use_trailing_stop=True,
    trailing_stop_atr_multiplier=2.0
)

# 生成交易信号（df为包含OHLC数据的DataFrame）
signals = strategy.generate_signals(df, verbose=True)

# 获取绩效报告
report = strategy.get_performance_report(df)

# 打印报告
strategy.print_report(df)
""")