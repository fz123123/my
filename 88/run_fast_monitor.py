#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUNBUFFERED'] = '1'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from luoman_alert import LuomanAlertSystem

if __name__ == "__main__":
    print("\n" + "="*120)
    print("🦅 启动实时数据盯盘系统 - 快速连续监控模式")
    print("="*120 + "\n")
    
    alert_system = LuomanAlertSystem()
    
    print("📊 监控配置:")
    print("   • 股票: 罗曼股份(SH605289)")
    print("   • 监控间隔: 60秒 (每分钟检查一次)")
    print("   • 数据源: 新浪财经 (实时数据)")
    print("\n🚨 预警触发条件:")
    print("   • 上涨预警: ¥160, ¥170, ¥180, ¥200, ¥220")
    print("   • 回调预警: ¥150, ¥145, ¥140, ¥130, ¥120")
    print("   • 涨跌幅: ±5%, ±10%")
    print("\n⏰ 开始时间: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("💡 提示: 按 Ctrl+C 停止监控\n")
    print("="*120)
    print("开始实时监控...\n")
    
    try:
        alert_system.run_continuous_monitor(interval_seconds=60)
    except KeyboardInterrupt:
        print("\n\n👋 实时盯盘已停止")
        print("再见！祝您投资顺利！\n")
