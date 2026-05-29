import time
import datetime
import os
import json
from datetime import datetime, timedelta

class TomorrowWatchdog:
    def __init__(self):
        self.stocks_to_watch = [
            {"code": "111003.SH", "name": "科创50ETF", "last_price": 14272.00, "rsi": 34.2},
            {"code": "501092.SH", "name": "银华日利", "last_price": 13.00, "rsi": 31.2},
            {"code": "600531.SH", "name": "豫光金铅", "last_price": 13.84, "rsi": 34.2},
            {"code": "600979.SH", "name": "广安爱众", "last_price": 4.72, "rsi": 35.0},
            {"code": "603016.SH", "name": "新宏泰", "last_price": 49.43, "rsi": 33.5},
            {"code": "603183.SH", "name": "建研院", "last_price": 4.60, "rsi": 34.5},
            {"code": "603906.SH", "name": "龙蟠科技", "last_price": 27.83, "rsi": 35.7, "signal": "buy"},
            {"code": "688106.SH", "name": "金宏气体", "last_price": 32.50, "rsi": 34.3},
            {"code": "000570.SZ", "name": "苏常柴A", "last_price": 6.21, "rsi": 31.9},
            {"code": "002029.SZ", "name": "七匹狼", "last_price": 10.22, "rsi": 34.3},
            {"code": "002120.SZ", "name": "韵达股份", "last_price": 7.40, "rsi": 13.9, "alert": "oversold"},
            {"code": "002216.SZ", "name": "三全食品", "last_price": 13.69, "rsi": 26.3, "alert": "oversold"},
            {"code": "002242.SZ", "name": "九阳股份", "last_price": 10.34, "rsi": 32.8},
            {"code": "002620.SZ", "name": "瑞和股份", "last_price": 8.87, "rsi": 31.4},
            {"code": "160513.SZ", "name": "鼎信转债", "last_price": 22.22, "rsi": 34.0},
            {"code": "166107.SZ", "name": "国投瑞银", "last_price": 15.76, "rsi": 40.6, "signal": "buy"},
            {"code": "300015.SZ", "name": "爱尔眼科", "last_price": 9.47, "rsi": 24.9, "alert": "oversold"},
            {"code": "300521.SZ", "name": "爱司凯", "last_price": 26.87, "rsi": 31.1},
            {"code": "300957.SZ", "name": "贝泰妮", "last_price": 39.00, "rsi": 26.6, "alert": "oversold"},
            {"code": "301003.SZ", "name": "壶化股份", "last_price": 55.88, "rsi": 40.6},
            {"code": "301027.SZ", "name": "华蓝集团", "last_price": 23.96, "rsi": 32.8},
            {"code": "301116.SZ", "name": "益客食品", "last_price": 10.35, "rsi": 31.0},
            {"code": "301608.SZ", "name": "山石转债", "last_price": 66.65, "rsi": 26.3, "alert": "oversold"},
        ]
        
        self.log_file = f"明日盯盘_{datetime.now().strftime('%Y%m%d')}.log"
        self.refresh_interval_trading = 120
        self.refresh_interval_non_trading = 300
        
        os.makedirs("watchdog_logs", exist_ok=True)
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_line = f"{timestamp} [{level}] {message}\n"
        print(log_line.strip())
        
        with open(os.path.join("watchdog_logs", self.log_file), "a", encoding="utf-8") as f:
            f.write(log_line)
    
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
                self.log("✅ 市场已开盘！开始实时监控")
                break
    
    def analyze_stock(self, stock):
        signals = []
        rsi = stock.get("rsi", 50)
        
        if rsi < 30:
            signals.append(f"⚠️ RSI超卖 ({rsi})")
        elif rsi > 70:
            signals.append(f"⚠️ RSI超买 ({rsi})")
        
        if stock.get("signal") == "buy":
            signals.append("🟢 买入信号")
        
        if stock.get("alert") == "oversold":
            signals.append("🔔 超卖关注")
        
        return signals
    
    def scan_market(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        is_trading = self.is_trading_time()
        
        self.log(f"🔍 开始扫描 [{current_time}] - {'交易时间' if is_trading else '非交易时间'}")
        
        buy_signals = []
        alert_stocks = []
        
        for stock in self.stocks_to_watch:
            signals = self.analyze_stock(stock)
            
            if stock.get("signal") == "buy":
                buy_signals.append(stock)
            elif stock.get("alert") == "oversold":
                alert_stocks.append(stock)
            
            if signals:
                signal_str = " | ".join(signals)
                self.log(f"📈 {stock['name']} ({stock['code']}): {stock['last_price']:.2f} - {signal_str}")
        
        if buy_signals:
            self.log("="*60)
            self.log("🚨🚨🚨 买入信号触发！🚨🚨🚨")
            self.log("="*60)
            for stock in buy_signals:
                self.log(f"🟢 {stock['name']} ({stock['code']})")
                self.log(f"   价格: {stock['last_price']:.2f} | RSI: {stock['rsi']}")
            self.log("="*60)
        
        if alert_stocks:
            self.log("🔔 超卖关注列表:")
            for stock in alert_stocks:
                self.log(f"   ⚠️ {stock['name']}: RSI={stock['rsi']}, 价格={stock['last_price']:.2f}")
        
        return buy_signals, alert_stocks
    
    def run(self):
        self.log("="*60)
        self.log("🦅 明日自动盯盘系统启动")
        self.log("="*60)
        self.log(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"🎯 监控股票数量: {len(self.stocks_to_watch)} 只")
        self.log(f"📝 日志文件: watchdog_logs/{self.log_file}")
        self.log("="*60)
        
        self.wait_for_market_open()
        
        try:
            while True:
                buy_signals, alert_stocks = self.scan_market()
                
                is_trading = self.is_trading_time()
                interval = self.refresh_interval_trading if is_trading else self.refresh_interval_non_trading
                interval_text = "2分钟" if is_trading else "5分钟"
                
                self.log(f"⏳ {interval_text}后再次扫描...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log("🛑 用户手动停止盯盘")
        except Exception as e:
            self.log(f"❌ 系统异常: {str(e)}", level="ERROR")
        
        self.log("✅ 盯盘结束")

if __name__ == "__main__":
    watchdog = TomorrowWatchdog()
    watchdog.run()