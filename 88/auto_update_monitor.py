#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停雷达 - 自动更新监控系统
ZTB Seer - Auto Update Monitor System
"""

import sys
import time
import os
from datetime import datetime, timedelta
import subprocess

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

class AutoUpdateMonitor:
    def __init__(self):
        self.project_dir = 'C:\\Users\\Administrator\\Documents\\trae_projects\\88'
        self.signal_file = os.path.join(self.project_dir, 'signals_today.txt')
        self.check_interval = 1800  # 30分钟检查一次
        self.market_open_time = datetime.strptime("09:30", "%H:%M")
        self.market_close_time = datetime.strptime("15:00", "%H:%M")
        
    def is_trading_time(self):
        """检查是否在交易时间"""
        now = datetime.now()
        current_time = now.time()
        
        morning_open = datetime.strptime("09:30", "%H:%M").time()
        morning_close = datetime.strptime("11:30", "%H:%M").time()
        afternoon_open = datetime.strptime("13:00", "%H:%M").time()
        afternoon_close = datetime.strptime("15:00", "%H:%M").time()
        
        is_morning = morning_open <= current_time <= morning_close
        is_afternoon = afternoon_open <= current_time <= afternoon_close
        
        return is_morning or is_afternoon
    
    def run_signal_check(self):
        """运行信号检查"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'='*80}")
        print(f"[{timestamp}] Running signal check...")
        print(f"{'='*80}")
        
        try:
            result = subprocess.run(
                ['python', 'one_click_check.py'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                print("Signal check completed successfully!")
                return True
            else:
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error running signal check: {e}")
            return False
    
    def send_notification(self, title, message):
        """发送Windows通知"""
        try:
            subprocess.run([
                'powershell', '-Command',
                f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null; '
                f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            ])
        except:
            pass
    
    def check_for_new_signals(self):
        """检查是否有新信号"""
        if not os.path.exists(self.signal_file):
            return None
            
        try:
            with open(self.signal_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if '[NEW!]' in content:
                return content
            return None
        except:
            return None
    
    def run_continuous_monitor(self):
        """持续监控模式"""
        print("\n" + "="*80)
        print("ZTB SEER - AUTO UPDATE MONITOR")
        print("="*80)
        print(f"Project Dir: {self.project_dir}")
        print(f"Check Interval: {self.check_interval//60} minutes")
        print(f"Signal File: {self.signal_file}")
        print("="*80)
        print("\nMonitor started! Press Ctrl+C to stop.")
        print("\nTrading Hours: 09:30-11:30, 13:00-15:00")
        print("Auto-check during trading hours only.")
        print("\n" + "="*80 + "\n")
        
        check_count = 0
        
        while True:
            try:
                now = datetime.now()
                current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                
                if self.is_trading_time():
                    check_count += 1
                    print(f"\n[{current_time_str}] Check #{check_count} - Trading Time")
                    
                    success = self.run_signal_check()
                    
                    if success:
                        new_signals = self.check_for_new_signals()
                        if new_signals:
                            print("\n" + "!"*80)
                            print("NEW SIGNALS DETECTED!")
                            print("!"*80)
                            self.send_notification(
                                "涨停雷达 - 新信号提醒",
                                "检测到新的买卖信号！请查看 signals_today.txt"
                            )
                else:
                    print(f"[{current_time_str}] Not trading time, waiting...")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n\nMonitor stopped by user.")
                break
            except Exception as e:
                print(f"\nError: {e}")
                time.sleep(60)
    
    def run_once(self):
        """单次运行模式"""
        print("\n" + "="*80)
        print("ZTB SEER - ONE-TIME CHECK")
        print("="*80)
        
        success = self.run_signal_check()
        
        if success:
            new_signals = self.check_for_new_signals()
            if new_signals:
                print("\n" + "!"*80)
                print("NEW SIGNALS DETECTED!")
                print("!"*80)
            else:
                print("\nNo new signals detected.")
        
        return success

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ZTB Seer Auto Update Monitor')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in minutes')
    
    args = parser.parse_args()
    
    monitor = AutoUpdateMonitor()
    
    if args.interval:
        monitor.check_interval = args.interval * 60
    
    if args.once:
        monitor.run_once()
    else:
        monitor.run_continuous_monitor()

if __name__ == '__main__':
    main()
