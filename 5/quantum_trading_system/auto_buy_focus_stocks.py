import time
import datetime
import os
import json
from datetime import datetime, timedelta

class AutoBuyFocusStocks:
    def __init__(self):
        self.focus_stocks = [
            {"code": "000625.SZ", "name": "长安汽车", "target_rsi_below": 30, "target_price_below_ma5": True},
            {"code": "000858.SZ", "name": "五粮液", "target_rsi_below": 30, "target_price_below_ma5": True},
            {"code": "600519.SH", "name": "贵州茅台", "target_rsi_below": 30, "target_price_below_ma5": True},
        ]
        
        self.signal_file_path = "backups/saves/"
        self.trade_log_path = "backups/trades/"
        self.config = {
            'initial_capital': 100000.0,
            'max_position_per_stock': 0.33,
            'stop_loss_pct': 0.08,
            'take_profit_pct': 0.15,
            'order_delay': 1.0,
            'check_interval': 60,
        }
        
        self.portfolio = {}
        self.cash = self.config['initial_capital']
        self.bought_stocks = []
        
        os.makedirs(self.trade_log_path, exist_ok=True)
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_line = f"{timestamp} [{level}] {message}\n"
        print(log_line.strip())
        
        log_file = os.path.join(self.trade_log_path, f"auto_buy_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    def get_latest_signal_file(self):
        files = [f for f in os.listdir(self.signal_file_path) if f.startswith('monitor_signals')]
        if not files:
            return None
        files.sort(reverse=True)
        return os.path.join(self.signal_file_path, files[0])
    
    def load_signal_data(self):
        signal_file = self.get_latest_signal_file()
        if not signal_file:
            self.log("❌ 未找到信号文件", "ERROR")
            return None
        
        try:
            with open(signal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            self.log(f"❌ 加载信号文件失败: {e}", "ERROR")
            return None
    
    def is_trading_time(self):
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)
        lunch_start = now.replace(hour=11, minute=30, second=0, microsecond=0)
        lunch_end = now.replace(hour=13, minute=0, second=0, microsecond=0)
        
        if now.weekday() >= 5:
            return False
        
        if market_open <= now < lunch_start:
            return True
        if lunch_end <= now <= market_close:
            return True
        return False
    
    def wait_for_market_open(self):
        self.log("⏳ 等待市场开盘...")
        while True:
            now = datetime.now()
            
            if now.weekday() >= 5:
                self.log("📅 周末休息，等待下一个交易日")
                time.sleep(3600)
                continue
            
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            current_time = now.strftime("%H:%M:%S")
            
            if now < market_open:
                wait_seconds = (market_open - now).total_seconds()
                self.log(f"⏰ 当前时间: {current_time}, 距离开盘还有 {int(wait_seconds/60)} 分钟 {int(wait_seconds%60)} 秒")
                time.sleep(60)
            else:
                self.log("✅ 市场已开盘！开始监控重点股票")
                break
    
    def check_buy_condition(self, stock_data, focus_info):
        code = stock_data.get('symbol', '')
        if code != focus_info['code']:
            return False, "代码不匹配"
        
        rsi = stock_data.get('rsi', 50)
        price = stock_data.get('price', 0)
        ma5 = stock_data.get('ma5', 0)
        
        conditions = []
        
        if rsi < focus_info['target_rsi_below']:
            conditions.append(f"RSI({rsi:.1f}) < {focus_info['target_rsi_below']}")
        else:
            return False, f"RSI({rsi:.1f}) >= {focus_info['target_rsi_below']}"
        
        if focus_info['target_price_below_ma5'] and ma5 > 0:
            if price < ma5:
                conditions.append(f"价格({price:.2f}) < MA5({ma5:.2f})")
            else:
                return False, f"价格({price:.2f}) >= MA5({ma5:.2f})"
        
        return True, "; ".join(conditions)
    
    def execute_buy(self, stock_data, focus_info):
        code = focus_info['code']
        name = focus_info['name']
        price = stock_data.get('price', 0)
        
        if code in self.bought_stocks:
            self.log(f"⏳ [{name}] 今日已买入，跳过")
            return False
        
        max_investment = self.cash * self.config['max_position_per_stock']
        shares = int(max_investment / price)
        
        if shares <= 0 or price <= 0:
            self.log(f"❌ [{name}] 无法买入: 价格={price:.2f}, 可用资金={self.cash:.2f}")
            return False
        
        cost = shares * price
        
        if cost > self.cash:
            self.log(f"❌ [{name}] 资金不足: 需要 {cost:.2f}, 可用 {self.cash:.2f}")
            return False
        
        self.cash -= cost
        self.bought_stocks.append(code)
        
        self.portfolio[code] = {
            'name': name,
            'shares': shares,
            'avg_cost': price,
            'current_price': price,
            'stop_loss': price * (1 - self.config['stop_loss_pct']),
            'take_profit': price * (1 + self.config['take_profit_pct']),
            'buy_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.log(f"💰 [{name}] 买入成功!")
        self.log(f"   代码: {code}")
        self.log(f"   价格: {price:.2f}")
        self.log(f"   数量: {shares}股")
        self.log(f"   花费: {cost:.2f}元")
        self.log(f"   止损: {self.portfolio[code]['stop_loss']:.2f}")
        self.log(f"   止盈: {self.portfolio[code]['take_profit']:.2f}")
        
        self.log_trade(code, name, 'buy', shares, price, cost)
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
        self.log("="*60)
        self.log("🦅 重点股票自动买入系统")
        self.log("="*60)
        self.log(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"🎯 监控股票: {', '.join([s['name'] for s in self.focus_stocks])}")
        self.log(f"💰 初始资金: {self.config['initial_capital']:.2f}元")
        self.log(f"📝 日志目录: {self.trade_log_path}")
        self.log("="*60)
        
        self.wait_for_market_open()
        
        try:
            while True:
                signal_data = self.load_signal_data()
                if not signal_data:
                    time.sleep(self.config['check_interval'])
                    continue
                
                self.log(f"\n🔍 开始扫描 [{datetime.now().strftime('%H:%M:%S')}]")
                
                for focus_info in self.focus_stocks:
                    found_stock = None
                    for item in signal_data:
                        if item.get('symbol') == focus_info['code']:
                            found_stock = item
                            break
                    
                    if not found_stock:
                        self.log(f"❌ 未找到 [{focus_info['name']}] 的数据")
                        continue
                    
                    price = found_stock.get('price', 0)
                    rsi = found_stock.get('rsi', 50)
                    ma5 = found_stock.get('ma5', 0)
                    
                    self.log(f"📈 [{focus_info['name']}]: 价格={price:.2f}, RSI={rsi:.1f}, MA5={ma5:.2f}")
                    
                    meets_condition, reason = self.check_buy_condition(found_stock, focus_info)
                    
                    if meets_condition:
                        self.log(f"✅ 满足买入条件: {reason}")
                        self.execute_buy(found_stock, focus_info)
                    else:
                        self.log(f"⏳ 未满足条件: {reason}")
                
                if len(self.bought_stocks) >= len(self.focus_stocks):
                    self.log("\n🎉 所有关注股票已买入完成！")
                    break
                
                is_trading = self.is_trading_time()
                interval = self.config['check_interval'] if is_trading else 300
                interval_text = "1分钟" if is_trading else "5分钟"
                
                self.log(f"\n⏳ {interval_text}后再次扫描...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log("🛑 用户手动停止")
        except Exception as e:
            self.log(f"❌ 系统异常: {str(e)}", level="ERROR")
        
        self.log("\n📊 最终账户状态:")
        self.log(f"   可用资金: {self.cash:.2f}")
        self.log(f"   持仓价值: {self.get_portfolio_value():.2f}")
        self.log(f"   总资产: {self.cash + self.get_portfolio_value():.2f}")
        self.log(f"   已买入股票: {len(self.bought_stocks)} 只")
        
        if self.portfolio:
            self.log("\n   持仓详情:")
            for code, pos in self.portfolio.items():
                self.log(f"     {pos['name']}: {pos['shares']}股 @ {pos['avg_cost']:.2f}")
        
        self.log("\n✅ 自动买入任务完成")

if __name__ == "__main__":
    trader = AutoBuyFocusStocks()
    trader.run()