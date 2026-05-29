#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集合竞价实时监控（增强版 - 带价格跳水报警）
监控时间: 9:15 - 9:25
报警条件: 价格突然跳水超过阈值
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from datetime import datetime
import time
import winsound  # Windows声音报警
import threading

class PriceAlarm:
    """价格报警类"""
    
    def __init__(self):
        self.alarms = []
        self.last_alarm_time = {}
        self.alarm_cooldown = 300  # 同一标的5分钟内不重复报警
    
    def check_price_drop(self, symbol, current_price, yesterday_close, threshold=2.0):
        """检查价格跳水"""
        drop_percent = ((yesterday_close - current_price) / yesterday_close) * 100
        
        if drop_percent >= threshold:
            # 检查是否在冷却期内
            current_time = time.time()
            last_alarm = self.last_alarm_time.get(symbol, 0)
            
            if current_time - last_alarm > self.alarm_cooldown:
                alarm = {
                    'symbol': symbol,
                    'yesterday_close': yesterday_close,
                    'current_price': current_price,
                    'drop_percent': drop_percent,
                    'threshold': threshold,
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'severity': self._get_severity(drop_percent)
                }
                
                self.alarms.append(alarm)
                self.last_alarm_time[symbol] = current_time
                
                return alarm
        
        return None
    
    def _get_severity(self, drop_percent):
        """判断严重程度"""
        if drop_percent >= 5:
            return "🔴 严重"
        elif drop_percent >= 3:
            return "🟠 警告"
        else:
            return "🟡 注意"
    
    def play_alarm_sound(self):
        """播放报警声音"""
        try:
            # 播放系统报警声音
            winsound.MessageBeep(winsound.MB_ICONWARNING)
        except:
            pass
    
    def trigger_alarm(self, alarm):
        """触发报警"""
        self.play_alarm_sound()
        return alarm

class EnhancedAuctionMonitor:
    """增强版竞价监控"""
    
    def __init__(self):
        self.data_engine = DataEngine()
        self.alarm = PriceAlarm()
        self.price_history = {}  # 价格历史记录
        self.baseline_prices = {}  # 基线价格（昨日收盘）
        
        # 监控标的
        self.stocks = [
            ('000224.SZ', '首选标的', 20),
            ('000242.SZ', '次选标的', 10),
            ('160058.SZ', '关注标的', 10),
            ('160369.SZ', '关注标的', 10),
        ]
        
        # 报警阈值配置
        self.alarm_thresholds = {
            'critical': 5.0,  # 下跌超过5% - 严重报警
            'warning': 3.0,   # 下跌超过3% - 警告
            'notice': 2.0,    # 下跌超过2% - 注意
        }
    
    def get_realtime_data(self, symbol):
        """获取实时数据"""
        try:
            df = self.data_engine.get_stock_data(symbol)
            if df is None or len(df) < 2:
                return None
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            yesterday_close = prev['close']
            current_price = latest['close']
            
            return {
                'symbol': symbol,
                'yesterday_close': yesterday_close,
                'current_price': current_price,
                'change_pct': ((current_price - yesterday_close) / yesterday_close) * 100,
                'drop_pct': ((yesterday_close - current_price) / yesterday_close) * 100,
                'rsi': latest.get('rsi', 50),
                'volume': latest.get('volume', 0),
                'ma5': latest.get('ma5', 0),
                'ma20': latest.get('ma20', 0),
            }
        except:
            return None
    
    def check_alarms(self, data):
        """检查所有报警条件"""
        if not data:
            return []
        
        alarms = []
        
        # 检查多个阈值
        for threshold_name, threshold_value in self.alarm_thresholds.items():
            alarm = self.alarm.check_price_drop(
                data['symbol'],
                data['current_price'],
                data['yesterday_close'],
                threshold_value
            )
            
            if alarm:
                alarms.append(alarm)
        
        return alarms
    
    def display_alarms(self, alarms):
        """显示报警信息"""
        if not alarms:
            return
        
        print("\n" + "="*70)
        print("     🚨🚨🚨 价格跳水报警 🚨🚨🚨")
        print("="*70)
        
        for alarm in alarms:
            print(f"\n   {alarm['severity']}")
            print(f"   标的: {alarm['symbol']}")
            print(f"   报警时间: {alarm['time']}")
            print(f"   昨收价格: ¥{alarm['yesterday_close']:.2f}")
            print(f"   当前价格: ¥{alarm['current_price']:.2f}")
            print(f"   跳水幅度: {alarm['drop_percent']:.2f}%")
            
            # 触发声音报警
            self.alarm.trigger_alarm(alarm)
        
        print("\n" + "="*70)
        print("     ⚠️ 紧急操作建议")
        print("="*70)
        
        for alarm in alarms:
            if alarm['drop_percent'] >= 5:
                print(f"\n   {alarm['symbol']}:")
                print(f"   🔴 严重跳水！立即止损，不要抱有幻想")
                print(f"   🔴 建议：开盘即卖出，控制亏损")
            elif alarm['drop_percent'] >= 3:
                print(f"\n   {alarm['symbol']}:")
                print(f"   🟠 大幅跳水！密切关注，做好止损准备")
                print(f"   🟠 建议：设置止损单，跌破重要支撑立即离场")
            else:
                print(f"\n   {alarm['symbol']}:")
                print(f"   🟡 小幅跳水：继续观察，等待企稳信号")
        
        print("\n" + "="*70)
    
    def run(self):
        """运行监控"""
        os.system('cls')
        
        print("="*70)
        print("     量子量化系统 - 集合竞价实时监控（增强版）")
        print("     🚨 带有价格跳水自动报警功能 🚨")
        print("="*70)
        
        print("\n🔄 初始化数据引擎...")
        print("   ✅ 初始化完成")
        
        print("\n📊 报警阈值设置:")
        print(f"   🔴 严重报警: 下跌 ≥ {self.alarm_thresholds['critical']}%")
        print(f"   🟠 警告报警: 下跌 ≥ {self.alarm_thresholds['warning']}%")
        print(f"   🟡 注意报警: 下跌 ≥ {self.alarm_thresholds['notice']}%")
        
        print("\n⏰ 监控标的:")
        for symbol, note, weight in self.stocks:
            print(f"   - {symbol} ({note})")
        
        refresh_count = 0
        
        try:
            while True:
                os.system('cls')
                current_time = datetime.now()
                
                print("="*70)
                print(f"     集合竞价实时监控（增强版） - 第{refresh_count+1}次刷新")
                print(f"     时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"     🚨 报警功能: 开启")
                print("="*70)
                
                # 获取并显示所有数据
                results = []
                all_alarms = []
                
                print("\n📊 竞价数据:")
                print(f"\n   {'股票代码':<12} {'昨收':>10} {'当前':>10} {'涨幅':>8} {'跳水':>8} {'RSI':>6} {'状态':<15}")
                print("   " + "-"*70)
                
                for symbol, note, weight in self.stocks:
                    data = self.get_realtime_data(symbol)
                    
                    if data:
                        # 检查报警
                        alarms = self.check_alarms(data)
                        all_alarms.extend(alarms)
                        
                        # 判断状态
                        change = data['change_pct']
                        if change > 3:
                            status = "🟢竞价强势"
                        elif change > 0:
                            status = "🟢竞价上涨"
                        elif change > -2:
                            status = "🟡竞价平稳"
                        else:
                            status = "🔴竞价走弱"
                        
                        # 高亮跳水幅度
                        drop = data['drop_pct']
                        if drop >= 5:
                            drop_str = f"🔴{drop:+.2f}%"
                        elif drop >= 3:
                            drop_str = f"🟠{drop:+.2f}%"
                        elif drop >= 2:
                            drop_str = f"🟡{drop:+.2f}%"
                        else:
                            drop_str = f"{drop:+.2f}%"
                        
                        print(f"   {symbol:<12} {data['yesterday_close']:>10.2f} "
                              f"{data['current_price']:>10.2f} {data['change_pct']:>+7.2f}% "
                              f"{drop_str:>8} {data['rsi']:>6.1f} {status}")
                        
                        results.append(data)
                
                # 显示报警信息
                if all_alarms:
                    self.display_alarms(all_alarms)
                
                # 综合建议
                if results:
                    print("\n\n" + "="*70)
                    print("     💡 综合竞价建议")
                    print("="*70)
                    
                    # 计算平均涨幅
                    avg_change = sum(r['change_pct'] for r in results) / len(results)
                    
                    print(f"\n   平均竞价涨幅: {avg_change:+.2f}%")
                    
                    if avg_change > 2:
                        print("   🟢 市场竞价强势")
                        print("   建议仓位: 40-50%")
                    elif avg_change > 0:
                        print("   🟡 市场竞价偏暖")
                        print("   建议仓位: 30-40%")
                    else:
                        print("   🔴 市场竞价偏弱")
                        print("   建议仓位: 20-30%")
                
                print("\n\n" + "="*70)
                print("     ⏰ 时间节点提醒")
                print("="*70)
                
                hour = current_time.hour
                minute = current_time.minute
                
                if hour == 9 and 15 <= minute <= 25:
                    remaining = 25 - minute
                    print(f"\n   🟢 竞价进行中，剩余 {remaining} 分钟")
                    print("   建议: 密切关注，随时准备报警")
                elif hour == 9 and minute < 15:
                    remaining = 15 - minute
                    print(f"\n   ⏰ 竞价开始还有 {remaining} 分钟")
                else:
                    print(f"\n   ⏰ 当前时间: {hour}:{minute:02d}")
                
                print("\n   9:15-9:25  竞价阶段 ← 当前重点监控")
                print("   9:30       开盘")
                print("   9:30-10:00 最佳操作时段")
                
                print("\n   按 Ctrl+C 退出监控")
                print("="*70)
                
                refresh_count += 1
                
                # 竞价期间每30秒刷新一次，非竞价期间每60秒刷新
                if hour == 9 and 15 <= minute <= 25:
                    sleep_time = 30  # 竞价期间更频繁
                else:
                    sleep_time = 60
                
                print(f"\n   ⏱️ 将在 {sleep_time} 秒后自动刷新 ({refresh_count}/∞)...")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("     监控已停止")
            print("="*70)
            print(f"\n   共刷新 {refresh_count} 次")
            
            if all_alarms:
                print("\n   📊 报警记录:")
                for alarm in all_alarms:
                    print(f"      {alarm['time']} {alarm['symbol']}: {alarm['drop_percent']:+.2f}%")

if __name__ == "__main__":
    monitor = EnhancedAuctionMonitor()
    monitor.run()
