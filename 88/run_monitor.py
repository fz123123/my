#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from real_time_monitor import RealTimeMonitor

if __name__ == "__main__":
    monitor = RealTimeMonitor()
    print("\n🚀 启动实时盯盘系统...")
    signals = monitor.run_monitor()
