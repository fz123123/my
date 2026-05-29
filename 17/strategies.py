import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Strategy(ABC):
    def __init__(self):
        self.backtester = None
        self.params = {}
    
    def set_backtester(self, backtester):
        self.backtester = backtester
    
    def set_params(self, params: Dict[str, Any]):
        self.params.update(params)
    
    @abstractmethod
    def on_data(self, data: pd.DataFrame) -> None:
        pass
    
    def get_position_size(self, price: float, risk_per_trade: float = 0.01) -> int:
        if self.backtester is None:
            return 0
        
        risk_amount = self.backtester.cash * risk_per_trade
        position_size = int(risk_amount / price)
        
        return max(position_size, 1)


class MovingAverageCrossover(Strategy):
    def __init__(self, short_window: int = 50, long_window: int = 200):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.signal_df = None
    
    def on_data(self, data: pd.DataFrame) -> None:
        if len(data) < self.long_window:
            return
        
        self.signal_df = data.copy()
        self.signal_df['short_ma'] = self.signal_df['Close'].rolling(window=self.short_window).mean()
        self.signal_df['long_ma'] = self.signal_df['Close'].rolling(window=self.long_window).mean()
        
        latest_data = self.signal_df.iloc[-1]
        prev_data = self.signal_df.iloc[-2]
        
        symbol = data['symbol'].iloc[0]
        
        if prev_data['short_ma'] <= prev_data['long_ma'] and latest_data['short_ma'] > latest_data['long_ma']:
            if symbol in self.backtester.positions:
                return
            
            price = latest_data['Close']
            quantity = self.get_position_size(price)
            
            if quantity > 0 and self.backtester.cash >= price * quantity:
                self.backtester.buy(symbol, quantity)
        
        elif prev_data['short_ma'] >= prev_data['long_ma'] and latest_data['short_ma'] < latest_data['long_ma']:
            if symbol not in self.backtester.positions:
                return
            
            quantity = self.backtester.positions[symbol].quantity
            if quantity > 0:
                self.backtester.sell(symbol, quantity)


class RSIStrategy(Strategy):
    def __init__(self, window: int = 14, oversold_threshold: int = 30, overbought_threshold: int = 70):
        super().__init__()
        self.window = window
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
    
    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        avg_gains = gains.rolling(window=self.window).mean()
        avg_losses = losses.rolling(window=self.window).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def on_data(self, data: pd.DataFrame) -> None:
        if len(data) < self.window + 1:
            return
        
        rsi = self._calculate_rsi(data['Close'])
        latest_rsi = rsi.iloc[-1]
        symbol = data['symbol'].iloc[0]
        price = data['Close'].iloc[-1]
        
        if latest_rsi < self.oversold_threshold:
            if symbol not in self.backtester.positions:
                quantity = self.get_position_size(price)
                if quantity > 0 and self.backtester.cash >= price * quantity:
                    self.backtester.buy(symbol, quantity)
        
        elif latest_rsi > self.overbought_threshold:
            if symbol in self.backtester.positions:
                quantity = self.backtester.positions[symbol].quantity
                if quantity > 0:
                    self.backtester.sell(symbol, quantity)


class MACDStrategy(Strategy):
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def _calculate_macd(self, prices: pd.Series) -> pd.DataFrame:
        ema_fast = prices.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow_period, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd - signal
        
        return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': histogram})
    
    def on_data(self, data: pd.DataFrame) -> None:
        if len(data) < self.slow_period + self.signal_period:
            return
        
        macd_df = self._calculate_macd(data['Close'])
        
        latest_macd = macd_df.iloc[-1]
        prev_macd = macd_df.iloc[-2]
        
        symbol = data['symbol'].iloc[0]
        price = data['Close'].iloc[-1]
        
        if prev_macd['MACD'] <= prev_macd['Signal'] and latest_macd['MACD'] > latest_macd['Signal']:
            if symbol not in self.backtester.positions:
                quantity = self.get_position_size(price)
                if quantity > 0 and self.backtester.cash >= price * quantity:
                    self.backtester.buy(symbol, quantity)
        
        elif prev_macd['MACD'] >= prev_macd['Signal'] and latest_macd['MACD'] < latest_macd['Signal']:
            if symbol in self.backtester.positions:
                quantity = self.backtester.positions[symbol].quantity
                if quantity > 0:
                    self.backtester.sell(symbol, quantity)


class BollingerBandStrategy(Strategy):
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__()
        self.window = window
        self.num_std = num_std
    
    def on_data(self, data: pd.DataFrame) -> None:
        if len(data) < self.window:
            return
        
        rolling_mean = data['Close'].rolling(window=self.window).mean()
        rolling_std = data['Close'].rolling(window=self.window).std()
        
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        
        latest_close = data['Close'].iloc[-1]
        latest_lower = lower_band.iloc[-1]
        latest_upper = upper_band.iloc[-1]
        
        prev_close = data['Close'].iloc[-2]
        prev_lower = lower_band.iloc[-2]
        prev_upper = upper_band.iloc[-2]
        
        symbol = data['symbol'].iloc[0]
        price = latest_close
        
        if prev_close >= prev_lower and latest_close < latest_lower:
            if symbol not in self.backtester.positions:
                quantity = self.get_position_size(price)
                if quantity > 0 and self.backtester.cash >= price * quantity:
                    self.backtester.buy(symbol, quantity)
        
        elif prev_close <= prev_upper and latest_close > latest_upper:
            if symbol in self.backtester.positions:
                quantity = self.backtester.positions[symbol].quantity
                if quantity > 0:
                    self.backtester.sell(symbol, quantity)


class DualMovingAverageStrategy(Strategy):
    def __init__(self, short_window: int = 20, medium_window: int = 50):
        super().__init__()
        self.short_window = short_window
        self.medium_window = medium_window
    
    def on_data(self, data: pd.DataFrame) -> None:
        if len(data) < self.medium_window:
            return
        
        short_ma = data['Close'].rolling(window=self.short_window).mean()
        medium_ma = data['Close'].rolling(window=self.medium_window).mean()
        
        latest_short = short_ma.iloc[-1]
        latest_medium = medium_ma.iloc[-1]
        prev_short = short_ma.iloc[-2]
        prev_medium = medium_ma.iloc[-2]
        
        symbol = data['symbol'].iloc[0]
        price = data['Close'].iloc[-1]
        
        if prev_short <= prev_medium and latest_short > latest_medium:
            if symbol not in self.backtester.positions:
                quantity = self.get_position_size(price)
                if quantity > 0 and self.backtester.cash >= price * quantity:
                    self.backtester.buy(symbol, quantity)
        
        elif prev_short >= prev_medium and latest_short < latest_medium:
            if symbol in self.backtester.positions:
                quantity = self.backtester.positions[symbol].quantity
                if quantity > 0:
                    self.backtester.sell(symbol, quantity)
