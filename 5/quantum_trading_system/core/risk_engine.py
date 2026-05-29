# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


class RiskEngine:
    def __init__(self, 
                 stop_loss_pct=None,
                 take_profit_pct=None,
                 max_position_ratio=None,
                 max_daily_loss_pct=None,
                 max_single_trade_pct=None):
        
        self.stop_loss_pct = stop_loss_pct or config['risk_control']['stop_loss_default']
        self.take_profit_pct = take_profit_pct or config['risk_control']['take_profit_default']
        self.max_position_ratio = max_position_ratio or config['trading']['max_position_ratio']
        self.max_daily_loss_pct = max_daily_loss_pct or config['risk_control']['max_drawdown']
        self.max_single_trade_pct = max_single_trade_pct or 0.05
        
        self.daily_start_capital = None
        self.daily_loss = 0
        self.trading_halt = False
        
    def reset_daily(self, current_capital):
        self.daily_start_capital = current_capital
        self.daily_loss = 0
        self.trading_halt = False
        
    def check_position_limits(self, position_value, current_capital):
        position_ratio = position_value / current_capital if current_capital > 0 else 0
        
        if position_ratio > self.max_position_ratio:
            return {
                'allowed': False,
                'reason': 'position_limit',
                'message': f'持仓比例 {position_ratio:.2%} 超过限制 {self.max_position_ratio:.2%}',
                'max_shares': int((current_capital * self.max_position_ratio) / position_value * 100) // 100 * 100 if position_value > 0 else 0
            }
        
        return {'allowed': True}
    
    def check_stop_loss(self, buy_price, current_price, position_value, total_cost):
        unrealized_pnl = position_value - total_cost
        unrealized_pnl_pct = unrealized_pnl / total_cost if total_cost > 0 else 0
        
        if unrealized_pnl_pct <= -self.stop_loss_pct:
            return {
                'triggered': True,
                'reason': 'stop_loss',
                'message': f'止损触发:亏损{unrealized_pnl_pct:.2%}',
                'action': 'SELL'
            }
        
        return {'triggered': False}
    
    def check_take_profit(self, buy_price, current_price, position_value, total_cost):
        unrealized_pnl = position_value - total_cost
        unrealized_pnl_pct = unrealized_pnl / total_cost if total_cost > 0 else 0
        
        if unrealized_pnl_pct >= self.take_profit_pct:
            return {
                'triggered': True,
                'reason': 'take_profit',
                'message': f'止盈触发:盈利{unrealized_pnl_pct:.2%}',
                'action': 'SELL'
            }
        
        return {'triggered': False}
    
    def check_trailing_stop(self, buy_price, current_price, highest_price_since_buy, trailing_pct=0.03):
        if highest_price_since_buy is None:
            return {'triggered': False}
        
        current_return = (current_price - buy_price) / buy_price if buy_price > 0 else 0
        peak_return = (highest_price_since_buy - buy_price) / buy_price if buy_price > 0 else 0
        
        trailing_trigger = peak_return - current_return
        
        if trailing_trigger >= trailing_pct and peak_return > 0.02:
            return {
                'triggered': True,
                'reason': 'trailing_stop',
                'message': f'移动止损:回撤{trailing_trigger:.2%}',
                'action': 'SELL'
            }
        
        return {'triggered': False}
    
    def check_daily_loss_limit(self, current_capital):
        if self.daily_start_capital is None:
            self.daily_start_capital = current_capital
            return {'triggered': False}
        
        daily_pnl = current_capital - self.daily_start_capital
        daily_pnl_pct = daily_pnl / self.daily_start_capital if self.daily_start_capital > 0 else 0
        
        if daily_pnl_pct <= -self.max_daily_loss_pct:
            self.trading_halt = True
            return {
                'triggered': True,
                'reason': 'daily_loss_limit',
                'message': f'日亏损限制已触发:{daily_pnl_pct:.2%}',
                'action': 'HALT'
            }
        
        return {'triggered': False}
    
    def check_single_trade_limit(self, trade_value, current_capital):
        trade_ratio = trade_value / current_capital if current_capital > 0 else 0
        
        if trade_ratio > self.max_single_trade_pct:
            return {
                'allowed': False,
                'reason': 'single_trade_limit',
                'message': f'单笔交易 {trade_ratio:.2%} 超过限制 {self.max_single_trade_pct:.2%}',
                'max_trade_value': current_capital * self.max_single_trade_pct
            }
        
        return {'allowed': True}
    
    def calculate_position_size(self, capital, price, risk_pct=None):
        if risk_pct is None:
            risk_pct = self.max_position_ratio
        
        max_investment = capital * risk_pct
        max_shares = int(max_investment / price / 100) * 100
        
        return {
            'max_investment': max_investment,
            'max_shares': max_shares,
            'max_value': max_shares * price
        }
    
    def calculate_stop_loss_price(self, buy_price, method='fixed', atr=None, multiplier=2):
        if method == 'fixed':
            return buy_price * (1 - self.stop_loss_pct)
        elif method == 'atr' and atr is not None:
            return buy_price - (atr * multiplier)
        else:
            return buy_price * (1 - self.stop_loss_pct)
    
    def calculate_take_profit_price(self, buy_price, method='fixed', atr=None, multiplier=3):
        if method == 'fixed':
            return buy_price * (1 + self.take_profit_pct)
        elif method == 'atr' and atr is not None:
            return buy_price + (atr * multiplier)
        else:
            return buy_price * (1 + self.take_profit_pct)
    
    def get_risk_metrics(self, position_value, total_cost, current_capital, peak_capital):
        if total_cost == 0:
            return None
        
        unrealized_pnl = position_value - total_cost
        unrealized_pnl_pct = unrealized_pnl / total_cost
        total_return = (current_capital - peak_capital) / peak_capital if peak_capital > 0 else 0
        
        return {
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'position_ratio': position_value / current_capital if current_capital > 0 else 0,
            'total_return_pct': total_return,
            'stop_loss_distance_pct': (position_value / total_cost - 1 - (-self.stop_loss_pct)) if position_value > 0 else 0,
            'take_profit_distance_pct': (self.take_profit_pct - (position_value / total_cost - 1)) if position_value > 0 else 0,
            'risk_reward_ratio': self.take_profit_pct / self.stop_loss_pct if self.stop_loss_pct > 0 else 0
        }
    
    def is_trading_allowed(self):
        if self.trading_halt:
            return {
                'allowed': False,
                'reason': 'trading_halted',
                'message': '交易暂停:日亏损限制已触发'
            }
        return {'allowed': True}
    
    def should_buy(self, current_capital, proposed_trade_value):
        check_halt = self.is_trading_allowed()
        if not check_halt['allowed']:
            return check_halt
        
        check_trade = self.check_single_trade_limit(proposed_trade_value, current_capital)
        if not check_trade['allowed']:
            return check_trade
        
        return {'allowed': True}
    
    def should_sell(self, buy_price, current_price, position_value, total_cost, 
                   highest_price_since_buy=None, atr=None):
        checks = [
            self.check_stop_loss(buy_price, current_price, position_value, total_cost),
            self.check_take_profit(buy_price, current_price, position_value, total_cost)
        ]
        
        if highest_price_since_buy is not None:
            checks.append(
                self.check_trailing_stop(buy_price, current_price, highest_price_since_buy)
            )
        
        for check in checks:
            if check.get('triggered'):
                return check
        
        return {'triggered': False}
    
    def update_config(self, **kwargs):
        if 'stop_loss_pct' in kwargs:
            self.stop_loss_pct = kwargs['stop_loss_pct']
        if 'take_profit_pct' in kwargs:
            self.take_profit_pct = kwargs['take_profit_pct']
        if 'max_position_ratio' in kwargs:
            self.max_position_ratio = kwargs['max_position_ratio']
        if 'max_daily_loss_pct' in kwargs:
            self.max_daily_loss_pct = kwargs['max_daily_loss_pct']
        if 'max_single_trade_pct' in kwargs:
            self.max_single_trade_pct = kwargs['max_single_trade_pct']
    
    def get_config_summary(self):
        return {
            'stop_loss_pct': f"{self.stop_loss_pct:.1%}",
            'take_profit_pct': f"{self.take_profit_pct:.1%}",
            'max_position_ratio': f"{self.max_position_ratio:.1%}",
            'max_daily_loss_pct': f"{self.max_daily_loss_pct:.1%}",
            'max_single_trade_pct': f"{self.max_single_trade_pct:.1%}",
            'trading_halted': self.trading_halt
        }