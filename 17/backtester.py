import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class Order:
    order_id: str
    timestamp: datetime
    symbol: str
    order_type: str
    direction: str
    quantity: float
    price: float
    status: str = "pending"
    filled_price: float = 0.0
    filled_quantity: float = 0.0
    commission: float = 0.0


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float = 0.0
    
    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        if self.quantity == 0:
            return 0.0
        return (self.current_price - self.avg_cost) * self.quantity


class Backtester:
    def __init__(self, initial_capital: float = 100000.0, commission_rate: float = 0.001, 
                 slippage_rate: float = 0.001, margin_rate: float = 1.0, verbose: bool = True,
                 log_file: str = 'backtest.log'):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.margin_rate = margin_rate
        self.verbose = verbose
        self.log_file = log_file
        
        self._setup_logging()
        
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trade_logs: List[Dict[str, Any]] = []
        
        self.equity_curve = []
        self.current_date = None
        self.order_id_counter = 0
        self.current_day = 0
        self.total_days = 0
        
        self.logger.info(f"========== Backtester initialized ==========")
        self.logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        self.logger.info(f"Commission Rate: {commission_rate*100:.2f}%")
        self.logger.info(f"Slippage Rate: {slippage_rate*100:.2f}%")
        self.logger.info(f"=============================================")
    
    def _setup_logging(self):
        self.logger = logging.getLogger('backtester')
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file, mode='w')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if self.verbose else logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _generate_order_id(self) -> str:
        self.order_id_counter += 1
        return f"ORD_{self.current_date.strftime('%Y%m%d')}_{self.order_id_counter}"
    
    def _calculate_slippage(self, price: float, direction: str) -> float:
        slippage = price * self.slippage_rate
        if direction == 'buy':
            return price + slippage
        else:
            return price - slippage
    
    def _calculate_commission(self, price: float, quantity: float) -> float:
        return price * quantity * self.commission_rate
    
    def submit_order(self, symbol: str, order_type: str, direction: str, 
                    quantity: float, price: float = 0.0) -> str:
        if direction not in ['buy', 'sell']:
            raise ValueError("Direction must be 'buy' or 'sell'")
        
        if order_type == 'market':
            order_price = 0.0
        elif order_type == 'limit':
            order_price = price
        else:
            raise ValueError("Order type must be 'market' or 'limit'")
        
        order = Order(
            order_id=self._generate_order_id(),
            timestamp=self.current_date,
            symbol=symbol,
            order_type=order_type,
            direction=direction,
            quantity=quantity,
            price=order_price
        )
        
        self.orders.append(order)
        
        self.logger.info(f"[{self.current_date.date()}] Order submitted: {order.direction.upper()} {order.quantity} shares of {order.symbol} "
                       f"(Type: {order.order_type}, ID: {order.order_id})")
        
        return order.order_id
    
    def buy(self, symbol: str, quantity: float, order_type: str = 'market', price: float = 0.0) -> str:
        return self.submit_order(symbol, order_type, 'buy', quantity, price)
    
    def sell(self, symbol: str, quantity: float, order_type: str = 'market', price: float = 0.0) -> str:
        return self.submit_order(symbol, order_type, 'sell', quantity, price)
    
    def _fill_order(self, order: Order, current_price: float) -> bool:
        if order.status != 'pending':
            return False
        
        if order.order_type == 'market':
            fill_price = self._calculate_slippage(current_price, order.direction)
            self.logger.debug(f"[{self.current_date.date()}] Market order fill price calculated: ${fill_price:.2f} (slippage: {self.slippage_rate*100:.2f}%)")
        elif order.order_type == 'limit':
            if order.direction == 'buy' and current_price <= order.price:
                fill_price = order.price
                self.logger.debug(f"[{self.current_date.date()}] Limit buy order filled at ${fill_price:.2f}")
            elif order.direction == 'sell' and current_price >= order.price:
                fill_price = order.price
                self.logger.debug(f"[{self.current_date.date()}] Limit sell order filled at ${fill_price:.2f}")
            else:
                self.logger.debug(f"[{self.current_date.date()}] Limit order not filled (current: ${current_price:.2f}, limit: ${order.price:.2f})")
                return False
        else:
            return False
        
        commission = self._calculate_commission(fill_price, order.quantity)
        total_cost = fill_price * order.quantity + commission
        
        self.logger.debug(f"[{self.current_date.date()}] Order {order.order_id}: commission = ${commission:.2f}, total cost = ${total_cost:.2f}")
        
        if order.direction == 'buy':
            if self.cash < total_cost:
                self.logger.warning(f"[{self.current_date.date()}] Insufficient cash for buy order! "
                                 f"Required: ${total_cost:.2f}, Available: ${self.cash:.2f}")
                return False
            
            self.cash -= total_cost
            
            if order.symbol in self.positions:
                position = self.positions[order.symbol]
                total_quantity = position.quantity + order.quantity
                position.avg_cost = (position.avg_cost * position.quantity + fill_price * order.quantity) / total_quantity
                position.quantity = total_quantity
                self.logger.debug(f"[{self.current_date.date()}] Position updated: {order.symbol} now has {position.quantity} shares at avg cost ${position.avg_cost:.2f}")
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_cost=fill_price
                )
                self.logger.debug(f"[{self.current_date.date()}] New position opened: {order.symbol} - {order.quantity} shares at ${fill_price:.2f}")
        else:
            if order.symbol not in self.positions or self.positions[order.symbol].quantity < order.quantity:
                self.logger.warning(f"[{self.current_date.date()}] Insufficient shares for sell order! "
                                 f"Required: {order.quantity}, Available: {self.positions.get(order.symbol, Position('',0,0)).quantity}")
                return False
            
            position = self.positions[order.symbol]
            position.quantity -= order.quantity
            
            proceeds = fill_price * order.quantity - commission
            self.cash += proceeds
            
            self.logger.debug(f"[{self.current_date.date()}] Sell proceeds: ${proceeds:.2f} (commission: ${commission:.2f})")
            
            if position.quantity <= 0:
                del self.positions[order.symbol]
                self.logger.debug(f"[{self.current_date.date()}] Position closed: {order.symbol}")
        
        order.status = 'filled'
        order.filled_price = fill_price
        order.filled_quantity = order.quantity
        order.commission = commission
        
        self.trade_logs.append({
            'date': self.current_date,
            'order_id': order.order_id,
            'symbol': order.symbol,
            'direction': order.direction,
            'quantity': order.quantity,
            'fill_price': fill_price,
            'commission': commission,
            'cash_after': self.cash
        })
        
        self.logger.info(f"[{self.current_date.date()}] ORDER FILLED: {order.direction.upper()} {order.quantity} {order.symbol} @ ${fill_price:.2f} "
                       f"| Commission: ${commission:.2f} | Cash: ${self.cash:.2f}")
        
        return True
    
    def _update_positions(self, data: pd.DataFrame) -> None:
        for symbol, position in self.positions.items():
            row = data[data['symbol'] == symbol]
            if not row.empty:
                old_price = position.current_price
                position.current_price = row['Close'].iloc[0]
                if old_price != 0:
                    pnl_change = (position.current_price - old_price) * position.quantity
                    self.logger.debug(f"[{self.current_date.date()}] Position {symbol}: price updated ${old_price:.2f} -> ${position.current_price:.2f}, "
                                   f"Unrealized PnL: ${position.unrealized_pnl:.2f}")
    
    def _calculate_total_equity(self) -> float:
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    def run_backtest(self, data: pd.DataFrame, strategy=None) -> pd.DataFrame:
        self.cash = self.initial_capital
        self.positions = {}
        self.orders = []
        self.trade_logs = []
        self.equity_curve = []
        self.order_id_counter = 0
        
        data = data.sort_values('Date')
        self.total_days = len(data)
        
        self.logger.info(f"========== Starting Backtest ==========")
        self.logger.info(f"Date range: {data['Date'].iloc[0].date()} to {data['Date'].iloc[-1].date()}")
        self.logger.info(f"Total trading days: {self.total_days}")
        self.logger.info(f"Strategy: {strategy.__class__.__name__ if strategy else 'None'}")
        self.logger.info("========================================")
        
        for self.current_day, (_, row) in enumerate(data.iterrows()):
            self.current_date = row['Date']
            
            self.logger.debug(f"\n[{self.current_date.date()}] Day {self.current_day + 1}/{self.total_days}")
            self.logger.debug(f"[{self.current_date.date()}] Current price: ${row['Close']:.2f}")
            self.logger.debug(f"[{self.current_date.date()}] Current cash: ${self.cash:.2f}")
            
            if strategy is not None:
                current_data = data.iloc[:self.current_day+1]
                self.logger.debug(f"[{self.current_date.date()}] Calling strategy.on_data() with {len(current_data)} bars")
                strategy.on_data(current_data)
            
            pending_orders = [o for o in self.orders if o.status == 'pending']
            self.logger.debug(f"[{self.current_date.date()}] Pending orders: {len(pending_orders)}")
            
            for order in pending_orders:
                self._fill_order(order, row['Close'])
            
            self._update_positions(pd.DataFrame([row]))
            
            equity = self._calculate_total_equity()
            positions_value = equity - self.cash
            
            self.equity_curve.append({
                'Date': self.current_date,
                'Equity': equity,
                'Cash': self.cash,
                'Positions_Value': positions_value,
                'Num_Positions': len(self.positions)
            })
            
            if (self.current_day + 1) % 50 == 0 or self.current_day == self.total_days - 1:
                self.logger.info(f"[{self.current_date.date()}] Progress: {self.current_day + 1}/{self.total_days} days | "
                               f"Equity: ${equity:.2f} | Cash: ${self.cash:.2f} | "
                               f"Positions: {len(self.positions)} | Total Value: ${positions_value:.2f}")
        
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['Return'] = equity_df['Equity'].pct_change().fillna(0)
        equity_df['Cumulative_Return'] = (1 + equity_df['Return']).cumprod() - 1
        
        total_return = equity_df['Cumulative_Return'].iloc[-1]
        final_equity = equity_df['Equity'].iloc[-1]
        
        self.logger.info(f"\n========== Backtest Completed ==========")
        self.logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"Final Equity: ${final_equity:,.2f}")
        self.logger.info(f"Total Return: {total_return*100:.2f}%")
        self.logger.info(f"Total Trades: {len(self.trade_logs)}")
        self.logger.info(f"========================================\n")
        
        return equity_df
    
    def get_trade_logs(self) -> pd.DataFrame:
        return pd.DataFrame(self.trade_logs)
    
    def get_summary(self) -> Dict[str, float]:
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        total_return = equity_df['Cumulative_Return'].iloc[-1]
        daily_returns = equity_df['Return']
        
        annualized_return = (1 + total_return) ** (252 / len(equity_df)) - 1
        volatility = daily_returns.std() * np.sqrt(252)
        
        if volatility > 0:
            sharpe_ratio = annualized_return / volatility
        else:
            sharpe_ratio = 0.0
        
        max_drawdown = 0.0
        peak = equity_df['Equity'].iloc[0]
        for equity in equity_df['Equity']:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        winning_trades = [t for t in self.trade_logs if t['direction'] == 'buy']
        losing_trades = [t for t in self.trade_logs if t['direction'] == 'sell']
        win_rate = len(winning_trades) / len(self.trade_logs) if self.trade_logs else 0.0
        
        return {
            'Initial_Capital': self.initial_capital,
            'Final_Equity': equity_df['Equity'].iloc[-1],
            'Total_Return': total_return,
            'Annualized_Return': annualized_return,
            'Volatility': volatility,
            'Sharpe_Ratio': sharpe_ratio,
            'Max_Drawdown': max_drawdown,
            'Win_Rate': win_rate,
            'Total_Trades': len(self.trade_logs)
        }
