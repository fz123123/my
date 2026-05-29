# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def calculate_indicators(df):
    df = df.copy()

    if len(df) < 60:
        return df

    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma60'] = df['close'].rolling(60).mean()

    df['ema12'] = df['close'].ewm(span=12).mean()
    df['ema26'] = df['close'].ewm(span=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    df['rsi'] = calculate_rsi(df['close'], 14)

    df['std20'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['ma20'] + 2 * df['std20']
    df['bb_lower'] = df['ma20'] - 2 * df['std20']
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-6)

    df['volume_ma20'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma20']

    df['high20'] = df['high'].rolling(20).max()
    df['low20'] = df['low'].rolling(20).min()
    df['position_20'] = (df['close'] - df['low20']) / (df['high20'] - df['low20'] + 1e-6)

    df['roc5'] = df['close'].pct_change(5)
    df['roc20'] = df['close'].pct_change(20)

    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(14).mean()

    return df


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_kdj(df, n=9, m1=3, m2=3):
    df = df.copy()
    low_list = df['low'].rolling(n).min()
    high_list = df['high'].rolling(n).max()
    rsv = (df['close'] - low_list) / (high_list - low_list + 1e-6) * 100
    df['kdj_k'] = rsv.ewm(com=m1 - 1).mean()
    df['kdj_d'] = df['kdj_k'].ewm(com=m2 - 1).mean()
    df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
    return df

