import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitor.realtime_monitor import RealtimeMonitor
from config import config

if __name__ == "__main__":
    monitor = RealtimeMonitor(strict_mode=False)
    interval = config['monitor']['refresh_interval']
    print(f"Starting real-time monitor with {interval}s refresh interval...")
    print("✅ 使用通达信本地数据进行监控")
    print("ℹ️  数据来源: 通达信 > 同花顺 > 模拟数据")
    monitor.run_monitor(interval=interval)
