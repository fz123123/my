# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


class BacktestEngine:
    def __init__(self, initial_capital=None):
        if initial_capital is None:
            initial_capital = config['trading']['initial_capital']
        self.initial_capital = initial_capital
        self.fee_rate = config['trading']['fee_rate']
        self.slippage = config['trading']['slippage']

    def run_backtest(self, df, signals):
        df = df.copy()
        df['signal'] = signals

        df = df.dropna(subset=['signal'])

        if len(df) == 0:
            return None

        cash = self.initial_capital
        position = 0
        trades = []
        equity_curve = []

        for i, (idx, row) in enumerate(df.iterrows()):
            current_price = row['close']

            if row['signal'] == 1 and position == 0:
                buy_price = current_price * (1 + self.slippage)
                shares = int(cash / buy_price / 100) * 100
                if shares > 0:
                    cost = shares * buy_price
                    fee = cost * self.fee_rate
                    cash -= (cost + fee)
                    position = shares
                    trades.append({
                        'date': idx,
                        'type': 'buy',
                        'price': buy_price,
                        'shares': shares,
                        'value': cost
                    })

            elif row['signal'] == -1 and position > 0:
                sell_price = current_price * (1 - self.slippage)
                revenue = position * sell_price
                fee = revenue * self.fee_rate
                cash += (revenue - fee)
                trades.append({
                    'date': idx,
                    'type': 'sell',
                    'price': sell_price,
                    'shares': position,
                    'value': revenue
                })
                position = 0

            current_equity = cash + position * current_price
            equity_curve.append({
                'date': idx,
                'equity': current_equity,
                'cash': cash,
                'position': position
            })

        if position > 0:
            sell_price = df.iloc[-1]['close'] * (1 - self.slippage)
            revenue = position * sell_price
            fee = revenue * self.fee_rate
            cash += (revenue - fee)
            trades.append({
                'date': df.index[-1],
                'type': 'sell',
                'price': sell_price,
                'shares': position,
                'value': revenue
            })

        equity_df = pd.DataFrame(equity_curve).set_index('date')
        final_equity = cash

        total_return = (final_equity - self.initial_capital) / self.initial_capital

        if len(equity_df) > 1:
            returns = equity_df['equity'].pct_change().dropna()
            if len(returns) > 0:
                sharpe_ratio = np.sqrt(252) * returns.mean() / (returns.std() + 1e-6)
            else:
                sharpe_ratio = 0

            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (running_max - cumulative) / running_max
            max_drawdown = drawdown.max()
        else:
            sharpe_ratio = 0
            max_drawdown = 0

        win_trades = 0
        total_trades = len(trades) // 2
        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy = trades[i]
                sell = trades[i + 1]
                if sell['price'] > buy['price']:
                    win_trades += 1

        win_rate = win_trades / max(total_trades, 1)

        return {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'final_equity': final_equity,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'trades': trades,
            'equity_curve': equity_df
        }

