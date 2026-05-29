#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦅 鹰眼压金 - 夜盘监控系统
监控期货夜盘交易情况
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
from datetime import datetime
import random

def display_night_market():
    """显示夜盘市场监控"""
    
    print("\n" + "="*80)
    print("    🌙 鹰眼压金 - 夜盘交易监控系统")
    print(f"    当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 夜盘交易时间
    print(f"\n⏰ 夜盘交易时间:")
    print(f"   上期所/郑商所/大商所: 21:00 - 01:00")
    print(f"   中金所股指期货: 21:00 - 02:30")
    print(f"   能源中心: 21:00 - 02:30")
    
    # 当前交易状态
    current_hour = datetime.now().hour
    if 21 <= current_hour or current_hour < 3:
        print(f"\n🟢 当前状态: 夜盘交易进行中")
    else:
        print(f"\n🔴 当前状态: 夜盘交易未开始/已结束")
    
    # 模拟夜盘数据
    futures = [
        {'name': '螺纹钢', 'code': 'RB', 'price': 3856, 'change': 23, 'change_pct': 0.60, 'volume': 125600},
        {'name': '铁矿石', 'code': 'I', 'price': 923, 'change': -8, 'change_pct': -0.86, 'volume': 89200},
        {'name': '焦煤', 'code': 'JM', 'price': 1856, 'change': 45, 'change_pct': 2.48, 'volume': 45600},
        {'name': '焦炭', 'code': 'J', 'price': 2458, 'change': 32, 'change_pct': 1.32, 'volume': 32400},
        {'name': 'PTA', 'code': 'TA', 'price': 5680, 'change': -15, 'change_pct': -0.26, 'volume': 156800},
        {'name': '甲醇', 'code': 'MA', 'price': 2890, 'change': 18, 'change_pct': 0.63, 'volume': 98500},
        {'name': '玻璃', 'code': 'FG', 'price': 1568, 'change': -23, 'change_pct': -1.45, 'volume': 67200},
        {'name': '沪铜', 'code': 'CU', 'price': 72580, 'change': 120, 'change_pct': 0.17, 'volume': 23400},
        {'name': '沪铝', 'code': 'AL', 'price': 19850, 'change': -50, 'change_pct': -0.25, 'volume': 34500},
        {'name': '原油', 'code': 'SC', 'price': 523.6, 'change': 8.2, 'change_pct': 1.59, 'volume': 78900},
        {'name': '黄金', 'code': 'AU', 'price': 4285.6, 'change': 15.3, 'change_pct': 0.36, 'volume': 12300},
        {'name': '白银', 'code': 'AG', 'price': 5426, 'change': -8, 'change_pct': -0.15, 'volume': 23400}
    ]
    
    print(f"\n📊 夜盘行情 (模拟实时数据):")
    print("-"*80)
    print(f"{'品种':<8} {'代码':<6} {'最新价':>10} {'涨跌':>10} {'涨跌幅':>10} {'成交量':>12}")
    print("-"*80)
    
    up_count = 0
    down_count = 0
    
    for future in futures:
        color = "🟢" if future['change'] >= 0 else "🔴"
        sign = "+" if future['change'] >= 0 else ""
        
        print(f"{future['name']:<8} {future['code']:<6} {future['price']:>10.2f} {color} {sign}{future['change']:>8.2f} {sign}{future['change_pct']:>9.2f}%  {future['volume']:>12,}")
        
        if future['change'] > 0:
            up_count += 1
        elif future['change'] < 0:
            down_count += 1
    
    print("-"*80)
    
    # 统计
    print(f"\n📈 夜盘涨跌统计:")
    print(f"   🟢 上涨: {up_count} 个")
    print(f"   🔴 下跌: {down_count} 个")
    print(f"   ➡️ 持平: {len(futures) - up_count - down_count} 个")
    
    # 热点品种
    print(f"\n🔥 夜盘热点:")
    print(f"   • 焦煤 (JM): +2.48% - 领涨")
    print(f"   • 原油 (SC): +1.59% - 能源走强")
    print(f"   • 玻璃 (FG): -1.45% - 领跌")
    
    # 操作建议
    print(f"\n💡 夜盘操作建议:")
    print(f"   1. 关注焦煤、原油等能源品种")
    print(f"   2. 注意夜盘波动可能较大")
    print(f"   3. 设置合理止损")
    print(f"   4. 避免持仓过夜风险")
    
    print("\n" + "="*80)
    print("⚠️ 风险提示: 以上数据仅供参考，不构成投资建议")
    print("="*80)

if __name__ == "__main__":
    display_night_market()
