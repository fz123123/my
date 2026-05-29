#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from 鹰眼压金_回测版 import EagleEyeSystem

if __name__ == "__main__":
    system = EagleEyeSystem()
    system.print_banner()
    print("\n🚀 正在启动实时盯盘功能...")
    print("\n📈 实时行情监控")
    print("请访问 http://localhost:5174 查看涨停先知系统")
    print("\n或者运行: python real_time_monitor.py")
