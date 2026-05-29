# -*- coding: utf-8 -*-
"""
基础策略模块
包含常用的量化交易策略：
- 均线交叉策略
- RSI策略（基础、增强、自适应版本）
- 布林带策略
- 多因子策略
- 网格交易策略
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.indicators import calculate_indicators, calculate_kdj


class StrategyMaCross:
    """
    均线交叉策略
    当短期均线上穿长期均线时买入，下穿时卖出
    优化参数: MA(6,13)
    """
    def __init__(self, short_period=6, long_period=13):
        """
        初始化策略
        
        参数:
            short_period: 短期均线周期，默认5日
            long_period: 长期均线周期，默认20日
        """
        self.short_period = short_period
        self.long_period = long_period

    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列，1=买入，-1=卖出，0=无操作
        """
        df = df.copy()
        df = calculate_indicators(df)

        signals = pd.Series(0, index=df.index)

        short_col = f'ma{self.short_period}'
        long_col = f'ma{self.long_period}'

        if short_col not in df.columns:
            df[short_col] = df['close'].rolling(self.short_period).mean()
        if long_col not in df.columns:
            df[long_col] = df['close'].rolling(self.long_period).mean()

        buy_condition = (df[short_col] > df[long_col]) & (df[short_col].shift(1) <= df[long_col].shift(1))
        sell_condition = (df[short_col] < df[long_col]) & (df[short_col].shift(1) >= df[long_col].shift(1))

        signals[buy_condition] = 1
        signals[sell_condition] = -1

        return signals


class StrategyRsi:
    """
    基础RSI策略
    RSI超卖时买入，超买时卖出
    """
    def __init__(self, oversold=30, overbought=70):
        """
        初始化策略
        
        参数:
            oversold: 超卖阈值，默认30
            overbought: 超买阈值，默认70
        """
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列，1=买入，-1=卖出，0=无操作
        """
        df = df.copy()
        df = calculate_indicators(df)

        signals = pd.Series(0, index=df.index)

        # RSI从超卖区回升，买入信号
        buy_condition = (df['rsi'] < self.oversold) & (df['rsi'].shift(1) >= self.oversold)
        # RSI从超买区回落，卖出信号
        sell_condition = (df['rsi'] > self.overbought) & (df['rsi'].shift(1) <= self.overbought)

        signals[buy_condition] = 1
        signals[sell_condition] = -1

        return signals


class StrategyRsiEnhanced:
    """
    增强版RSI策略
    包含止损、止盈、时间止损、趋势过滤
    """
    def __init__(self, oversold=30, overbought=70, stop_loss_pct=0.08, take_profit_pct=0.20, 
                 max_holding_days=60, use_trend_filter=True, trend_period=20):
        """
        初始化策略
        
        参数:
            oversold: 超卖阈值
            overbought: 超买阈值
            stop_loss_pct: 止损比例
            take_profit_pct: 止盈比例
            max_holding_days: 最大持仓天数
            use_trend_filter: 是否使用趋势过滤
            trend_period: 趋势均线周期
        """
        self.oversold = oversold
        self.overbought = overbought
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_holding_days = max_holding_days
        self.use_trend_filter = use_trend_filter
        self.trend_period = trend_period

    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列，1=买入，-1=卖出，0=无操作
        """
        df = df.copy()
        df = calculate_indicators(df)

        signals = pd.Series(0, index=df.index)
        
        position = 0  # 持仓状态，0=空仓，1=持仓
        entry_price = 0  # 买入价格
        entry_date = None  # 买入日期
        
        for i in range(len(df)):
            date = df.index[i]
            price = df['close'].iloc[i]
            rsi = df['rsi'].iloc[i]
            ma5 = df['ma5'].iloc[i]
            ma20 = df['ma20'].iloc[i]
            
            if position == 0:
                # 空仓状态：寻找买入机会
                rsi_buy = (rsi < self.oversold) & (df['rsi'].shift(1).iloc[i] >= self.oversold)
                
                if self.use_trend_filter:
                    trend_ok = ma5 > ma20  # 趋势过滤：MA5在MA20上方
                else:
                    trend_ok = True
                
                if rsi_buy and trend_ok:
                    signals.iloc[i] = 1
                    position = 1
                    entry_price = price
                    entry_date = date
            else:
                # 持仓状态：检查卖出条件
                days_held = (date - entry_date).days
                
                rsi_sell = (rsi > self.overbought) & (df['rsi'].shift(1).iloc[i] <= self.overbought)
                stop_loss = price < entry_price * (1 - self.stop_loss_pct)  # 止损
                take_profit = price > entry_price * (1 + self.take_profit_pct)  # 止盈
                time_stop = days_held >= self.max_holding_days  # 时间止损
                
                if rsi_sell or stop_loss or take_profit or time_stop:
                    signals.iloc[i] = -1
                    position = 0
                    entry_price = 0
                    entry_date = None

        return signals


class StrategyRsiAdaptive:
    """
    自适应RSI策略
    根据市场状态（牛市/熊市/震荡）动态调整参数
    包含ATR止盈和移动止损
    """
    def __init__(self, oversold=30, overbought=70, 
                 bull_stop_loss=0.10, bull_take_profit=0.30, bull_holding_days=60,
                 bear_stop_loss=0.05, bear_take_profit=0.15, bear_holding_days=30,
                 neutral_stop_loss=0.08, neutral_take_profit=0.20, neutral_holding_days=45,
                 use_atr_tp=False, atr_tp_multiplier=3.0, atr_tp_min_pct=0.10, atr_tp_max_pct=0.50,
                 use_trailing_stop=False, trailing_stop_atr_multiplier=2.0, trailing_stop_min_pct=0.05):
        """
        初始化策略
        
        参数:
            oversold, overbought: RSI超卖超买阈值
            bull_stop_loss, bull_take_profit, bull_holding_days: 牛市参数
            bear_stop_loss, bear_take_profit, bear_holding_days: 熊市参数
            neutral_stop_loss, neutral_take_profit, neutral_holding_days: 震荡参数
            use_atr_tp: 是否使用ATR动态止盈
            atr_tp_multiplier: ATR止盈倍数
            use_trailing_stop: 是否使用移动止损
            trailing_stop_atr_multiplier: 移动止损ATR倍数
        """
        self.oversold = oversold
        self.overbought = overbought
        
        # 牛市参数
        self.bull_stop_loss = bull_stop_loss
        self.bull_take_profit = bull_take_profit
        self.bull_holding_days = bull_holding_days
        
        # 熊市参数
        self.bear_stop_loss = bear_stop_loss
        self.bear_take_profit = bear_take_profit
        self.bear_holding_days = bear_holding_days
        
        # 震荡参数
        self.neutral_stop_loss = neutral_stop_loss
        self.neutral_take_profit = neutral_take_profit
        self.neutral_holding_days = neutral_holding_days
        
        # ATR止盈参数
        self.use_atr_tp = use_atr_tp
        self.atr_tp_multiplier = atr_tp_multiplier
        self.atr_tp_min_pct = atr_tp_min_pct
        self.atr_tp_max_pct = atr_tp_max_pct
        
        # 移动止损参数
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_atr_multiplier = trailing_stop_atr_multiplier
        self.trailing_stop_min_pct = trailing_stop_min_pct

    def _identify_market_regime(self, df, i):
        """
        识别市场状态（牛市/熊市/震荡）
        
        参数:
            df: 数据
            i: 当前位置
            
        返回:
            'bull' | 'bear' | 'neutral'
        """
        if i < 60:
            return 'neutral'
        
        ma5 = df['ma5'].iloc[i]
        ma20 = df['ma20'].iloc[i]
        ma60 = df['ma60'].iloc[i]
        
        trend_strength = abs(ma5 - ma20) / ma20
        
        if ma5 > ma20 and ma20 > ma60 and trend_strength > 0.02:
            return 'bull'  # 牛市
        elif ma5 < ma20 and ma20 < ma60 and trend_strength > 0.02:
            return 'bear'  # 熊市
        
        return 'neutral'  # 震荡

    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列
        """
        df = df.copy()
        df = calculate_indicators(df)

        signals = pd.Series(0, index=df.index)
        
        position = 0
        entry_price = 0
        entry_date = None
        entry_atr = 0
        trailing_stop_price = 0
        current_regime = 'neutral'
        prev_regime = 'neutral'
        
        for i in range(len(df)):
            date = df.index[i]
            price = df['close'].iloc[i]
            rsi = df['rsi'].iloc[i]
            ma5 = df['ma5'].iloc[i]
            ma20 = df['ma20'].iloc[i]
            ma30 = df['ma30'].iloc[i] if 'ma30' in df.columns else ma20
            atr = df['atr'].iloc[i] if 'atr' in df.columns else 0
            
            # 均线交叉检测
            prev_ma5 = df['ma5'].iloc[i-1] if i > 0 else ma5
            prev_ma30 = df['ma30'].iloc[i-1] if (i > 0 and 'ma30' in df.columns) else ma30
            
            ma_cross_up = (prev_ma5 <= prev_ma30) and (ma5 > ma30)
            ma_cross_down = (prev_ma5 >= prev_ma30) and (ma5 < ma30)
            
            if ma_cross_up:
                print(f"[{date.strftime('%Y-%m-%d')}] [UP] MA5金叉MA30: MA5={ma5:.2f}, MA30={ma30:.2f}, 价格={price:.2f}")
            
            if ma_cross_down:
                print(f"[{date.strftime('%Y-%m-%d')}] [DN] MA5死叉MA30: MA5={ma5:.2f}, MA30={ma30:.2f}, 价格={price:.2f}")
            
            # 识别市场状态
            current_regime = self._identify_market_regime(df, i)
            regime_desc = {'bull': '牛市', 'bear': '熊市', 'neutral': '震荡'}[current_regime]
            
            if current_regime != prev_regime:
                print(f"[{date.strftime('%Y-%m-%d')}] [SW] 市场状态切换")
            prev_regime = current_regime
            
            # 根据市场状态选择参数
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
            
            # ATR动态止盈
            if self.use_atr_tp and entry_price > 0 and entry_atr > 0:
                atr_take_profit_pct = (entry_atr * self.atr_tp_multiplier) / entry_price
                take_profit_pct = max(self.atr_tp_min_pct, min(atr_take_profit_pct, self.atr_tp_max_pct))
            else:
                take_profit_pct = base_take_profit_pct
            
            if rsi <= self.oversold:
                print(f"[{date.strftime('%Y-%m-%d')}] [WARN] RSI超卖: {rsi:.1f}, 价格={price:.2f}")
            
            if rsi >= self.overbought:
                print(f"[{date.strftime('%Y-%m-%d')}] [WARN] RSI超买: {rsi:.1f}, 价格={price:.2f}")
            
            if position == 0:
                # 空仓：寻找买入机会
                rsi_buy = (rsi < self.oversold) & (df['rsi'].shift(1).iloc[i] >= self.oversold)
                trend_ok = ma5 > ma30
                
                if rsi_buy and trend_ok:
                    signals.iloc[i] = 1
                    position = 1
                    entry_price = price
                    entry_date = date
                    entry_atr = atr
                    # 初始化移动止损
                    if self.use_trailing_stop and atr > 0:
                        initial_trailing = max(price * (1 - self.trailing_stop_min_pct), price - atr * self.trailing_stop_atr_multiplier)
                        trailing_stop_price = initial_trailing
                    else:
                        trailing_stop_price = 0
                    atr_tp_info = f", ATR={atr:.2f}, ATR止盈目标={((atr * self.atr_tp_multiplier) / price * 100):.1f}%" if self.use_atr_tp else ""
                    trailing_info = f", 初始移动止损={trailing_stop_price:.2f}" if self.use_trailing_stop else ""
                    print(f"[{date.strftime('%Y-%m-%d')}] 🛒 买入信号: 价格={price:.2f}, RSI={rsi:.1f}, MA5={ma5:.2f}, MA30={ma30:.2f}, 状态={regime_desc}{atr_tp_info}{trailing_info}")
                elif rsi_buy and not trend_ok:
                    print(f"[{date.strftime('%Y-%m-%d')}] ⏳ RSI超卖但趋势不满足: 价格={price:.2f}, RSI={rsi:.1f}, MA5={ma5:.2f}, MA30={ma30:.2f}")
            else:
                # 持仓：检查卖出条件
                days_held = (date - entry_date).days
                current_profit = (price - entry_price) / entry_price * 100
                
                # 更新移动止损
                if self.use_trailing_stop and trailing_stop_price > 0:
                    new_trailing_stop = max(trailing_stop_price, price - atr * self.trailing_stop_atr_multiplier)
                    new_trailing_stop = max(new_trailing_stop, entry_price * (1 - self.trailing_stop_min_pct))
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
                
                if rsi_sell:
                    signals.iloc[i] = -1
                    print(f"[{date.strftime('%Y-%m-%d')}] [SELL] 卖出信号(RSI超买): 价格={price:.2f}, 买入价={entry_price:.2f}, 盈亏={current_profit:+.2f}%, 持仓天数={days_held}")
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_atr = 0
                    trailing_stop_price = 0
                elif stop_loss:
                    signals.iloc[i] = -1
                    print(f"[{date.strftime('%Y-%m-%d')}] 🛑 卖出信号({stop_loss_desc}): 价格={price:.2f}, 买入价={entry_price:.2f}, 盈亏={current_profit:+.2f}%, 止损价={trailing_stop_price:.2f}" if self.use_trailing_stop else f"[{date.strftime('%Y-%m-%d')}] 🛑 卖出信号({stop_loss_desc}): 价格={price:.2f}, 买入价={entry_price:.2f}, 盈亏={current_profit:+.2f}%")
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_atr = 0
                    trailing_stop_price = 0
                elif take_profit:
                    signals.iloc[i] = -1
                    tp_type = "ATR动态止盈" if self.use_atr_tp else "止盈"
                    print(f"[{date.strftime('%Y-%m-%d')}] 🎯 卖出信号({tp_type}): 价格={price:.2f}, 买入价={entry_price:.2f}, 盈亏={current_profit:+.2f}%, 止盈比例={take_profit_pct*100:.1f}%")
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_atr = 0
                    trailing_stop_price = 0
                elif time_stop:
                    signals.iloc[i] = -1
                    print(f"[{date.strftime('%Y-%m-%d')}] ⏰ 卖出信号(时间止损): 价格={price:.2f}, 买入价={entry_price:.2f}, 盈亏={current_profit:+.2f}%, 持仓天数={days_held}")
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_atr = 0
                    trailing_stop_price = 0

        return signals


class StrategyBollinger:
    """
    布林带策略
    价格跌破下轨买入，突破上轨卖出
    """
    def __init__(self):
        """初始化策略"""
        pass

    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列
        """
        df = df.copy()
        df = calculate_indicators(df)

        signals = pd.Series(0, index=df.index)

        # 跌破下轨买入
        buy_condition = (df['close'] < df['bb_lower']) & (df['close'].shift(1) >= df['bb_lower'].shift(1))
        # 突破上轨卖出
        sell_condition = (df['close'] > df['bb_upper']) & (df['close'].shift(1) <= df['bb_upper'].shift(1))

        signals[buy_condition] = 1
        signals[sell_condition] = -1

        return signals


class StrategyMultiFactor:
    """
    多因子策略
    结合均线、RSI、布林带、KDJ多个因子
    """
    def __init__(self):
        """初始化策略"""
        pass

    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列
        """
        df = df.copy()
        df = calculate_indicators(df)
        df = calculate_kdj(df)

        signals = pd.Series(0, index=df.index)

        # 买入因子
        ma_up = df['ma5'] > df['ma20']  # 均线多头
        rsi_ok = df['rsi'] < 50  # RSI不超买
        bb_low = df['bb_position'] < 0.2  # 布林带低位
        kdj_up = df['kdj_k'] > df['kdj_d']  # KDJ金叉

        # 卖出因子
        ma_down = df['ma5'] < df['ma20']  # 均线空头
        rsi_high = df['rsi'] > 70  # RSI超买
        bb_high = df['bb_position'] > 0.8  # 布林带高位
        kdj_down = df['kdj_k'] < df['kdj_d']  # KDJ死叉

        buy_condition = ma_up & rsi_ok & (bb_low | kdj_up)
        sell_condition = ma_down & rsi_high & (bb_high | kdj_down)

        signals[buy_condition] = 1
        signals[sell_condition] = -1

        return signals


class StrategyGrid:
    """
    基础网格交易策略
    在价格区间内设置网格，触及网格线时交易
    """
    def __init__(self, grid_levels=5, grid_range_pct=0.10, auto_adjust=True):
        """
        初始化策略
        
        参数:
            grid_levels: 网格层级数
            grid_range_pct: 网格区间比例
            auto_adjust: 是否自动调整网格
        """
        self.grid_levels = grid_levels
        self.grid_range_pct = grid_range_pct
        self.auto_adjust = auto_adjust
        self.grid_lines = []
        self.last_price = None
        
    def calculate_grid_lines(self, df):
        """
        计算网格线位置
        
        参数:
            df: 价格数据
            
        返回:
            grid_lines: 网格价格数组
        """
        if len(df) < 30:
            return []
        
        # 基于最近30天高低点计算网格
        recent_high = df['high'].rolling(30).max().iloc[-1]
        recent_low = df['low'].rolling(30).min().iloc[-1]
        
        grid_range = recent_high - recent_low
        if grid_range == 0:
            grid_range = recent_high * self.grid_range_pct
        
        grid_step = grid_range / self.grid_levels
        
        grid_lines = []
        for i in range(self.grid_levels + 1):
            price = recent_low + i * grid_step
            grid_lines.append(price)
        
        return grid_lines
    
    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列
        """
        df = df.copy()
        
        self.grid_lines = self.calculate_grid_lines(df)
        signals = pd.Series(0, index=df.index)
        
        if not self.grid_lines or len(self.grid_lines) < 2:
            return signals
        
        for i in range(1, len(df)):
            current_price = df['close'].iloc[i]
            prev_price = df['close'].iloc[i-1]
            
            # 检查是否穿越网格线
            for j in range(len(self.grid_lines)-1):
                lower_line = self.grid_lines[j]
                upper_line = self.grid_lines[j+1]
                
                if prev_price <= lower_line and current_price > lower_line:
                    # 上穿下网格线，买入
                    signals.iloc[i] = 1
                    break
                elif prev_price >= upper_line and current_price < upper_line:
                    # 下穿上网格线，卖出
                    signals.iloc[i] = -1
                    break
        
        return signals
    
    def get_grid_info(self):
        """获取网格信息"""
        return {
            'levels': self.grid_levels,
            'range_pct': self.grid_range_pct,
            'grid_lines': self.grid_lines,
            'auto_adjust': self.auto_adjust
        }


class StrategyGridAdvanced:
    """
    进阶网格交易策略
    包含成交量过滤、RSI过滤、动态调整网格
    """
    def __init__(self, grid_levels=5, grid_range_pct=0.10, 
                 volume_filter=False, rsi_filter=False, 
                 dynamic_adjust=True, take_profit_pct=0.02):
        """
        初始化策略
        
        参数:
            grid_levels: 网格层级数
            grid_range_pct: 网格区间比例
            volume_filter: 是否使用成交量过滤
            rsi_filter: 是否使用RSI过滤
            dynamic_adjust: 是否动态调整
            take_profit_pct: 止盈比例
        """
        self.grid_levels = grid_levels
        self.grid_range_pct = grid_range_pct
        self.volume_filter = volume_filter
        self.rsi_filter = rsi_filter
        self.dynamic_adjust = dynamic_adjust
        self.take_profit_pct = take_profit_pct
        self.grid_lines = []
        self.position = 0
        self.buy_price = 0
        
    def calculate_grid_lines(self, df):
        """
        计算网格线（考虑波动率）
        
        参数:
            df: 价格数据
            
        返回:
            grid_lines: 网格价格数组
        """
        if len(df) < 60:
            return []
        
        # 计算波动率
        volatility = df['close'].rolling(60).std() / df['close'].rolling(60).mean()
        volatility = volatility.iloc[-1]
        
        # 基于最近60天高低点计算网格
        recent_high = df['high'].rolling(60).max().iloc[-1]
        recent_low = df['low'].rolling(60).min().iloc[-1]
        
        grid_range = recent_high - recent_low
        if grid_range == 0:
            grid_range = recent_high * self.grid_range_pct * (1 + volatility)
        
        grid_step = grid_range / self.grid_levels
        
        grid_lines = []
        for i in range(self.grid_levels + 1):
            price = recent_low + i * grid_step
            grid_lines.append(price)
        
        return grid_lines
    
    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列
        """
        df = df.copy()
        df = calculate_indicators(df)
        
        self.grid_lines = self.calculate_grid_lines(df)
        signals = pd.Series(0, index=df.index)
        
        if not self.grid_lines or len(self.grid_lines) < 2:
            return signals
        
        for i in range(1, len(df)):
            current_price = df['close'].iloc[i]
            prev_price = df['close'].iloc[i-1]
            
            # 成交量过滤
            volume_ok = True
            if self.volume_filter:
                volume_avg = df['volume'].rolling(20).mean().iloc[i]
                volume_ok = df['volume'].iloc[i] >= volume_avg * 0.5
            
            # RSI过滤
            rsi_ok = True
            if self.rsi_filter:
                rsi = df['rsi'].iloc[i]
                rsi_ok = 20 < rsi < 80
            
            if not volume_ok or not rsi_ok:
                continue
            
            # 检查网格穿越
            for j in range(len(self.grid_lines)-1):
                lower_line = self.grid_lines[j]
                upper_line = self.grid_lines[j+1]
                mid_line = (lower_line + upper_line) / 2
                
                if prev_price <= lower_line and current_price > lower_line:
                    if self.position <= 0:
                        signals.iloc[i] = 1
                        self.position = 1
                        self.buy_price = current_price
                    break
                elif prev_price >= upper_line and current_price < upper_line:
                    if self.position >= 0:
                        signals.iloc[i] = -1
                        self.position = -1
                    break
                elif self.position > 0 and self.buy_price > 0:
                    # 止盈
                    profit = (current_price - self.buy_price) / self.buy_price
                    if profit >= self.take_profit_pct:
                        signals.iloc[i] = -1
                        self.position = 0
        
        return signals
    
    def get_grid_info(self):
        """获取网格信息"""
        return {
            'levels': self.grid_levels,
            'range_pct': self.grid_range_pct,
            'grid_lines': self.grid_lines,
            'volume_filter': self.volume_filter,
            'rsi_filter': self.rsi_filter,
            'dynamic_adjust': self.dynamic_adjust,
            'take_profit_pct': self.take_profit_pct
        }


class StrategyGridScalping:
    """
    网格高频交易策略
    适用于短期频繁交易
    """
    def __init__(self, tick_size=0.01, profit_target=0.002, loss_limit=0.005, min_volume=100):
        """
        初始化策略
        
        参数:
            tick_size: 报价单位
            profit_target: 盈利目标比例
            loss_limit: 止损比例
            min_volume: 最小成交量
        """
        self.tick_size = tick_size
        self.profit_target = profit_target
        self.loss_limit = loss_limit
        self.min_volume = min_volume
        self.position = 0
        self.entry_price = 0
        
    def generate_signals(self, df):
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            signals: 信号序列
        """
        df = df.copy()
        signals = pd.Series(0, index=df.index)
        
        for i in range(1, len(df)):
            current_price = df['close'].iloc[i]
            volume = df['volume'].iloc[i]
            
            if volume < self.min_volume:
                continue
            
            if self.position == 0:
                # 空仓买入
                signals.iloc[i] = 1
                self.position = 1
                self.entry_price = current_price
            elif self.position == 1:
                # 持仓检查止盈止损
                pnl = (current_price - self.entry_price) / self.entry_price
                
                if pnl >= self.profit_target:
                    signals.iloc[i] = -1
                    self.position = 0
                elif pnl <= -self.loss_limit:
                    signals.iloc[i] = -1
                    self.position = 0
        
        return signals
