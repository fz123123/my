#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from auto_monitor import AutoMonitorAlert

if __name__ == "__main__":
    monitor = AutoMonitorAlert()
    print("\n" + "="*120)
    print("启动涨停先知自动监控提醒系统...")
    print("="*120 + "\n")
    monitor.run_single_check()
