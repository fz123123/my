#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from luoman_alert import LuomanAlertSystem

if __name__ == "__main__":
    print("\n" + "="*120)
    print("启动实时数据盯盘系统 - 连续监控模式")
    print("="*120 + "\n")
    
    alert_system = LuomanAlertSystem()
    
    print("监控设置:")
    print("  • 股票: 罗曼股份(SH605289)")
    print("  • 监控间隔: 60秒")
    print("  • 数据源: 新浪财经")
    print("\n按 Ctrl+C 停止监控\n")
    
    alert_system.run_continuous_monitor(interval_seconds=60)
