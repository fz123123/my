# -*- coding: utf-8 -*-
"""
Quantum Trading System - 一键智能启动
自动启动所有量化系统功能
"""

import os
import sys
import time

def print_logo():
    logo = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        QUANTUM TRADING SYSTEM v3.0                                ║
║          全功能量化交易系统 - 一键智能启动                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(logo)

def run_analysis():
    """运行深度分析"""
    print("\n� 正在运行深度分析...")
    try:
        import analysis_tdx
        analysis_tdx.analyze_today_data()
        print("\n✅ 深度分析完成")
    except Exception as e:
        print(f"❌ 深度分析失败: {e}")

def start_monitor():
    """启动实时监控"""
    print("\n� 启动实时监控...")
    try:
        from monitor.realtime_monitor import RealtimeMonitor
        from config import config
        
        monitor = RealtimeMonitor(strict_mode=False)
        interval = config['monitor']['refresh_interval']
        print(f"✅ 实时监控已启动，刷新间隔: {interval}秒")
        monitor.run_monitor(interval=interval)
    except Exception as e:
        print(f"❌ 实时监控启动失败: {e}")

def main():
    print_logo()
    
    print("\n� 正在启动量化交易系统...")
    print("="*60)
    
    # 先运行深度分析
    run_analysis()
    
    # 然后启动实时监控
    start_monitor()

if __name__ == "__main__":
    main()