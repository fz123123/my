import json
import time
import datetime
import os
import sys
from datetime import datetime, timedelta

class AutoTrader:
    def __init__(self):
        self.signal_file_path = "backups/saves/"
        self.trade_log_path = "backups/trades/"
        self.config = {
            'initial_capital': 100000.0,
            'max_position_per_stock': 0.2,
            'stop_loss_pct': 0.08,
            'take_profit_pct': 0.15,
            'order_delay': 1.0
        }
        self.portfolio = {}
        self.cash = self.config['initial_capital']
        self.today_signals = []
        
        os.makedirs(self.trade_log_path, exist_ok=True)
    
    def get_latest_signal_file(self):
        files = [f for f in os.listdir(self.signal_file_path) if f.startswith('monitor_signals')]
        if not files:
            return None
        files.sort(reverse=True)
        return os.path.join(self.signal_file_path, files[0])
    
    def load_today_signals(self):
        signal_file = self.get_latest_signal_file()
        if not signal_file:
            print("❌ 未找到信号文件")
            return False
        
        try:
            with open(signal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.today_signals = data.get('signals', [])
                print(f"✅ 成功加载 {len(self.today_signals)} 条信号")
                return True
        except Exception as e:
            print(f"❌ 加载信号文件失败: {e}")
            return False
    
    def is_trading_time(self):
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)
        
        if now.weekday() >= 5:
            return False
        
        return market_open <= now <= market_close
    
    def wait_for_market_open(self):
        print("⏳ 等待市场开盘...")
        while True:
            now = datetime.now()
            
            if now.weekday() >= 5:
                print(f"📅 今天是周末，等待下一个交易日...")
                time.sleep(3600)
                continue
            
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            
            if now < market_open:
                wait_seconds = (market_open - now).total_seconds()
                print(f"⏰ 当前时间: {now.strftime('%H:%M:%S')}")
                print(f"📈 距离开盘还有 {int(wait_seconds / 60)} 分钟 {int(wait_seconds % 60)} 秒")
                time.sleep(60)
            else:
                print("✅ 市场已开盘！")
                break
    
    def execute_trade(self, signal):
        stock_code = signal['code']
        stock_name = signal['name']
        signal_type = signal['signal']
        price = signal.get('price', 0)
        action = 'buy' if signal_type == 'buy' else 'sell'
        
        if action == 'buy':
            max_investment = self.cash * self.config['max_position_per_stock']
            shares = int(max_investment / price)
            
            if shares <= 0 or price <= 0:
                print(f"❌ [{stock_name}] 无法买入: 价格={price}, 可用资金={self.cash:.2f}")
                return False
            
            cost = shares * price
            
            if cost > self.cash:
                print(f"❌ [{stock_name}] 资金不足: 需要 {cost:.2f}, 可用 {self.cash:.2f}")
                return False
            
            self.cash -= cost
            
            if stock_code in self.portfolio:
                self.portfolio[stock_code]['shares'] += shares
                self.portfolio[stock_code]['avg_cost'] = (
                    self.portfolio[stock_code]['avg_cost'] * (self.portfolio[stock_code]['shares'] - shares) + cost
                ) / self.portfolio[stock_code]['shares']
            else:
                self.portfolio[stock_code] = {
                    'name': stock_name,
                    'shares': shares,
                    'avg_cost': price,
                    'current_price': price,
                    'stop_loss': price * (1 - self.config['stop_loss_pct']),
                    'take_profit': price * (1 + self.config['take_profit_pct'])
                }
            
            print(f"💰 [{stock_name}] 买入成功: {shares}股 @ {price:.2f}, 花费 {cost:.2f}")
            self.log_trade(stock_code, stock_name, 'buy', shares, price, cost)
            
        elif action == 'sell':
            if stock_code not in self.portfolio or self.portfolio[stock_code]['shares'] <= 0:
                print(f"❌ [{stock_name}] 持仓不足，无法卖出")
                return False
            
            shares = self.portfolio[stock_code]['shares']
            revenue = shares * price
            profit = (price - self.portfolio[stock_code]['avg_cost']) * shares
            
            self.cash += revenue
            print(f"📤 [{stock_name}] 卖出成功: {shares}股 @ {price:.2f}, 收入 {revenue:.2f}, 盈利 {profit:.2f}")
            self.log_trade(stock_code, stock_name, 'sell', shares, price, revenue)
            
            del self.portfolio[stock_code]
        
        time.sleep(self.config['order_delay'])
        return True
    
    def log_trade(self, code, name, action, shares, price, amount):
        log_entry = {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'code': code,
            'name': name,
            'action': action,
            'shares': shares,
            'price': price,
            'amount': amount,
            'cash_after': self.cash,
            'portfolio_value': self.get_portfolio_value()
        }
        
        log_file = os.path.join(self.trade_log_path, f"trades_{datetime.now().strftime('%Y%m%d')}.json")
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_portfolio_value(self):
        return sum(p['shares'] * p['current_price'] for p in self.portfolio.values())
    
    def run(self):
        print("🚀 自动交易系统启动")
        print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.wait_for_market_open()
        
        if not self.load_today_signals():
            print("❌ 无法加载信号，退出")
            return
        
        print("\n📊 今日信号列表:")
        for i, signal in enumerate(self.today_signals, 1):
            action = "🟢 买入" if signal['signal'] == 'buy' else "🔴 卖出"
            print(f"  {i}. [{signal['name']}] {action} @ {signal.get('price', 0):.2f}")
        
        print("\n💹 执行交易:")
        buy_signals = [s for s in self.today_signals if s['signal'] == 'buy']
        sell_signals = [s for s in self.today_signals if s['signal'] == 'sell']
        
        for signal in sell_signals:
            self.execute_trade(signal)
        
        for signal in buy_signals:
            self.execute_trade(signal)
        
        print("\n📈 交易完成后的账户状态:")
        print(f"   可用资金: {self.cash:.2f}")
        print(f"   持仓价值: {self.get_portfolio_value():.2f}")
        print(f"   总资产: {self.cash + self.get_portfolio_value():.2f}")
        print(f"   持仓股票: {len(self.portfolio)} 只")
        
        if self.portfolio:
            print("\n   持仓详情:")
            for code, pos in self.portfolio.items():
                print(f"     {pos['name']}: {pos['shares']}股 @ {pos['avg_cost']:.2f}")
        
        print("\n✅ 自动交易执行完成")

if __name__ == "__main__":
    trader = AutoTrader()
    trader.run()