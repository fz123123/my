#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from real_time_monitor import RealTimeMonitor

if __name__ == "__main__":
    monitor = RealTimeMonitor()
    print("\n" + "="*120)
    print("启动实时盯盘系统...")
    print("="*120 + "\n")
    signals = monitor.run_monitor()
