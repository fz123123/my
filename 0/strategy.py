import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List

class Strategy:
    def __init__(self, strategy_type: str = 'combined'):
        self.name = "龙量化策略"
        self.strategy_type = strategy_type
        self.parameters = {
            'sma_short': 20,
            'sma_long': 60,
            'rsi_window': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_window': 20,
            'atr_window': 14,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.05,
            'min_volume_ratio': 1.2,
            'min_hold_days': 5
        }
    
    def set_parameters(self, params: Dict):
        self.parameters.update(params)
    
    def generate_signals_sma_crossover(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        short_window = self.parameters['sma_short']
        long_window = self.parameters['sma_long']
        
        df['sma_short'] = df['close'].rolling(short_window).mean()
        df['sma_long'] = df['close'].rolling(long_window).mean()
        
        golden_cross = (df['sma_short'].shift(1) <= df['sma_long'].shift(1)) & (df['sma_short'] > df['sma_long'])
        death_cross = (df['sma_short'].shift(1) >= df['sma_long'].shift(1)) & (df['sma_short'] < df['sma_long'])
        
        df.loc[golden_cross, 'signal'] = 1
        df.loc[death_cross, 'signal'] = -1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        return df
    
    def generate_signals_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        window = self.parameters['rsi_window']
        overbought = self.parameters['rsi_overbought']
        oversold = self.parameters['rsi_oversold']
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df.loc[df['rsi'] < oversold, 'signal'] = 1
        df.loc[df['rsi'] > overbought, 'signal'] = -1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        return df
    
    def generate_signals_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        fast = self.parameters['macd_fast']
        slow = self.parameters['macd_slow']
        signal_period = self.parameters['macd_signal']
        
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        golden_cross = (df['macd'].shift(1) <= df['macd_signal'].shift(1)) & (df['macd'] > df['macd_signal'])
        death_cross = (df['macd'].shift(1) >= df['macd_signal'].shift(1)) & (df['macd'] < df['macd_signal'])
        
        df.loc[golden_cross, 'signal'] = 1
        df.loc[death_cross, 'signal'] = -1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        return df
    
    def generate_signals_bollinger(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        window = self.parameters['bb_window']
        
        df['bb_mid'] = df['close'].rolling(window).mean()
        df['bb_std'] = df['close'].rolling(window).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
        
        df.loc[df['close'] <= df['bb_lower'], 'signal'] = 1
        df.loc[df['close'] >= df['bb_upper'], 'signal'] = -1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        return df
    
    def generate_signals_combined(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        short_window = self.parameters['sma_short']
        long_window = self.parameters['sma_long']
        rsi_overbought = self.parameters['rsi_overbought']
        rsi_oversold = self.parameters['rsi_oversold']
        min_volume_ratio = self.parameters['min_volume_ratio']
        min_hold_days = self.parameters['min_hold_days']
        
        df['sma_short'] = df['close'].rolling(short_window).mean()
        df['sma_long'] = df['close'].rolling(long_window).mean()
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
        
        long_condition = (
            (df['sma_short'] > df['sma_long']) &
            (df['rsi'] < rsi_overbought) &
            (df['macd'] > df['macd_signal']) &
            (df['close'] >= df['bb_lower']) &
            (df['volume_ratio'] > min_volume_ratio)
        )
        
        short_condition = (
            (df['sma_short'] < df['sma_long']) &
            (df['rsi'] > rsi_oversold) &
            (df['macd'] < df['macd_signal']) &
            (df['close'] <= df['bb_upper'])
        )
        
        df.loc[long_condition, 'signal'] = 1
        df.loc[short_condition, 'signal'] = -1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        
        df['position_change'] = (df['position'] != df['position'].shift()).astype(int)
        df['position_group'] = df['position_change'].cumsum()
        df['days_in_position'] = df.groupby('position_group').cumcount()
        
        exit_long = (df['rsi'] > rsi_overbought) | (df['close'] >= df['bb_upper'])
        exit_short = (df['rsi'] < rsi_oversold) | (df['close'] <= df['bb_lower'])
        
        exit_long = exit_long & (df['days_in_position'] >= min_hold_days)
        exit_short = exit_short & (df['days_in_position'] >= min_hold_days)
        
        df.loc[exit_long & (df['position'] == 1), 'signal'] = -1
        df.loc[exit_short & (df['position'] == -1), 'signal'] = 1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        
        df['position_change'] = (df['position'] != df['position'].shift()).astype(int)
        df['position_group'] = df['position_change'].cumsum()
        df['days_in_position'] = df.groupby('position_group').cumcount()
        
        return df
    
    def generate_signals_trend_following(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean()
        df['atr'] = self._calculate_atr(df['high'], df['low'], df['close'], 14)
        
        trend_up = (df['sma_50'] > df['sma_200']) & (df['close'] > df['sma_50'])
        trend_down = (df['sma_50'] < df['sma_200']) & (df['close'] < df['sma_50'])
        
        df.loc[trend_up & (df['position'] != 1), 'signal'] = 1
        df.loc[trend_down & (df['position'] != -1), 'signal'] = -1
        
        trailing_stop_long = df['close'] - df['atr'] * 2
        trailing_stop_short = df['close'] + df['atr'] * 2
        
        df['trailing_stop'] = np.where(df['position'] == 1, trailing_stop_long, 
                                      np.where(df['position'] == -1, trailing_stop_short, np.nan))
        df['trailing_stop'] = df['trailing_stop'].ffill()
        
        df.loc[(df['position'] == 1) & (df['close'] <= df['trailing_stop']), 'signal'] = -1
        df.loc[(df['position'] == -1) & (df['close'] >= df['trailing_stop']), 'signal'] = 1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        return df
    
    def generate_signals_mean_reversion(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        window = 20
        df['sma'] = df['close'].rolling(window).mean()
        df['std'] = df['close'].rolling(window).std()
        df['z_score'] = (df['close'] - df['sma']) / df['std']
        
        enter_long = df['z_score'] < -1.5
        enter_short = df['z_score'] > 1.5
        exit_long = df['z_score'] > 0
        exit_short = df['z_score'] < 0
        
        df.loc[enter_long & (df['position'] != 1), 'signal'] = 1
        df.loc[enter_short & (df['position'] != -1), 'signal'] = -1
        df.loc[exit_long & (df['position'] == 1), 'signal'] = -1
        df.loc[exit_short & (df['position'] == -1), 'signal'] = 1
        
        df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        return df
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        return atr
    
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        strategies = {
            'sma_crossover': self.generate_signals_sma_crossover,
            'rsi': self.generate_signals_rsi,
            'macd': self.generate_signals_macd,
            'bollinger': self.generate_signals_bollinger,
            'combined': self.generate_signals_combined,
            'trend_following': self.generate_signals_trend_following,
            'mean_reversion': self.generate_signals_mean_reversion
        }
        
        if self.strategy_type in strategies:
            df = strategies[self.strategy_type](df)
        else:
            df = self.generate_signals_combined(df)
        
        df['returns'] = df['close'].pct_change()
        
        return df.dropna()
    
    def optimize_parameters(self, df: pd.DataFrame, param_grid: Dict, metric: str = 'sharpe_ratio') -> Dict:
        best_params = {}
        best_score = -np.inf
        
        from itertools import product
        
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        
        for params in product(*values):
            param_dict = dict(zip(keys, params))
            self.set_parameters(param_dict)
            
            result = self.execute(df)
            score = self._calculate_metric(result, metric)
            
            if score > best_score:
                best_score = score
                best_params = param_dict
        
        self.set_parameters(best_params)
        return best_params
    
    def _calculate_metric(self, df: pd.DataFrame, metric: str) -> float:
        total_return = df['returns'].sum()
        volatility = df['returns'].std()
        sharpe_ratio = total_return / volatility if volatility != 0 else 0
        
        metrics = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'volatility': -volatility,
            'win_rate': len(df[df['returns'] > 0]) / len(df)
        }
        
        return metrics.get(metric, sharpe_ratio)