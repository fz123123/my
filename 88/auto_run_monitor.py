#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import time

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

def main():
    try:
        from real_time_monitor import RealTimeMonitor

        print("="*120)
        print("启动实时盯盘系统...")
        print("="*120 + "\n")

        monitor = RealTimeMonitor()
        signals = monitor.run_monitor()

        print("\n信号收集完成！")
        print("="*120)

    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保所有依赖文件存在")
    except Exception as e:
        print(f"运行时错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
