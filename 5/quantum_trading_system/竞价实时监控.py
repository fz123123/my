#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集合竞价实时监控（持续刷新版）
监控时间: 9:15 - 9:25，每分钟自动刷新
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from datetime import datetime
import time

def clear_screen():
    """清屏"""
    os.system('cls')

def get_realtime_auction_data(symbol, data_engine):
    """获取竞价数据"""
    try:
        df = data_engine.get_stock_data(symbol)
        if df is None or len(df) < 2:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        yesterday_close = prev['close']
        current_price = latest['close']
        change_pct = ((current_price - yesterday_close) / yesterday_close) * 100
        
        return {
            'symbol': symbol,
            'yesterday_close': yesterday_close,
            'current_price': current_price,
            'change_pct': change_pct,
            'rsi': latest.get('rsi', 50),
            'volume': latest.get('volume', 0),
            'ma5': latest.get('ma5', 0),
            'ma20': latest.get('ma20', 0),
        }
    except:
        return None

def analyze_opportunity(data):
    """分析机会"""
    if not data:
        return "数据获取失败", "neutral", []
    
    change = data['change_pct']
    rsi = data['rsi']
    
    # 判断竞价强度
    if change > 5:
        intensity = "非常强势"
        color = "🔴"
        actions = ["⚠️ 高开过大，警惕高开低走", "建议：观望为主，等待回调"]
    elif change > 2:
        intensity = "强势"
        color = "🟢"
        actions = ["💡 竞价强势，上涨概率大", "建议：可适度关注，等待回调买入"]
    elif change > 0:
        intensity = "温和上涨"
        color = "🟢"
        actions = ["💡 竞价温和上涨", "建议：关注开盘后走势，可考虑买入"]
    elif change > -2:
        intensity = "小幅低开"
        color = "🟡"
        actions = ["💡 小幅低开，正常波动", "建议：观望为主，等待企稳信号"]
    elif change > -5:
        intensity = "偏弱"
        color = "🟠"
        if rsi < 35:
            actions = ["💡 低开且RSI超卖", "建议：可关注超跌反弹机会"]
        else:
            actions = ["⚠️ 竞价偏弱", "建议：观望为主，等待确认"]
    else:
        intensity = "大幅低开"
        color = "🔴"
        actions = ["⚠️ 大幅低开，风险较大", "建议：坚决规避，不要盲目抄底"]
    
    # RSI建议
    rsi_advice = []
    if rsi > 70:
        rsi_advice.append(f"⚠️ RSI={rsi:.0f}偏高，追涨风险大")
    elif rsi < 30:
        rsi_advice.append(f"💡 RSI={rsi:.0f}超卖，可能有反弹")
    
    return intensity, color, actions + rsi_advice

def monitor_loop():
    """持续监控循环"""
    print("="*70)
    print("     量子量化系统 - 集合竞价持续监控")
    print("     监控标的: 重点关注股票")
    print("="*70)
    
    # 初始化
    print("\n🔄 初始化数据引擎...")
    data_engine = DataEngine()
    print("   ✅ 初始化完成")
    
    # 监控标的
    stocks = [
        ('000224.SZ', '首选标的', 20),
        ('000242.SZ', '次选标的', 10),
        ('160058.SZ', '关注标的', 10),
        ('160369.SZ', '关注标的', 10),
    ]
    
    refresh_count = 0
    
    try:
        while True:
            clear_screen()
            current_time = datetime.now()
            
            print("="*70)
            print(f"     集合竞价实时监控 - 第{refresh_count+1}次刷新")
            print(f"     时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            
            # 检查是否在竞价时间
            hour = current_time.hour
            minute = current_time.minute
            
            if hour == 9 and 15 <= minute <= 25:
                print("\n🟢 现在是集合竞价时间（9:15-9:25）")
                print("   正在获取实时竞价数据...\n")
            elif hour < 9 or (hour == 9 and minute < 15):
                print(f"\n⏰ 现在是 {hour}:{minute:02d}，竞价还未开始")
                print("   竞价时间: 9:15-9:25")
                print("   建议: 等待竞价开始后再操作\n")
            elif hour == 9 and minute > 25:
                print(f"\n⏰ 竞价时间已过（9:25）")
                print("   现在是9:30前过渡期，观察开盘价\n")
            else:
                print(f"\n⏰ 当前时间 {hour}:{minute:02d}，不在竞价时间")
                print("   竞价时间: 9:15-9:25\n")
            
            # 获取并显示所有标的竞价数据
            results = []
            
            print("📊 竞价数据:")
            print(f"\n   {'股票代码':<12} {'昨收':>10} {'当前':>10} {'涨幅':>8} {'RSI':>6} {'竞价状态':<15}")
            print("   " + "-"*70)
            
            for symbol, note, weight in stocks:
                data = get_realtime_auction_data(symbol, data_engine)
                
                if data:
                    intensity, color, actions = analyze_opportunity(data)
                    
                    print(f"   {symbol:<12} {data['yesterday_close']:>10.2f} "
                          f"{data['current_price']:>10.2f} {data['change_pct']:>+7.2f}% "
                          f"{data['rsi']:>6.1f} {color}{intensity}")
                    
                    results.append({
                        'symbol': symbol,
                        'note': note,
                        'weight': weight,
                        'data': data,
                        'intensity': intensity,
                        'color': color,
                        'actions': actions
                    })
                else:
                    print(f"   {symbol:<12} {'N/A':>10}")
            
            # 给出综合建议
            if results:
                print("\n\n" + "="*70)
                print("     💡 综合竞价建议")
                print("="*70)
                
                # 找出最佳标的
                best = None
                best_score = -999
                
                for r in results:
                    score = 0
                    change = r['data']['change_pct']
                    rsi = r['data']['rsi']
                    
                    # 竞价溢价评分
                    if 0 <= change <= 2:
                        score += 30
                    elif -1 <= change < 0:
                        score += 20
                    elif change > 2:
                        score += 10
                    else:
                        score += 0
                    
                    # RSI评分
                    if 40 <= rsi <= 60:
                        score += 30
                    elif 30 <= rsi < 40 or 60 < rsi <= 70:
                        score += 15
                    else:
                        score += 0
                    
                    if score > best_score:
                        best_score = score
                        best = r
                        best['score'] = score
                
                if best:
                    print(f"\n   🏆 竞价最佳标的: {best['symbol']}")
                    print(f"      竞价涨幅: {best['data']['change_pct']:+.2f}%")
                    print(f"      RSI: {best['data']['rsi']:.1f}")
                    print(f"      综合评分: {best['score']}")
                    print(f"\n   操作建议:")
                    for action in best['actions']:
                        print(f"      {action}")
                
                # 给出仓位建议
                print(f"\n   📊 仓位建议:")
                
                good_count = sum(1 for r in results if r['data']['change_pct'] > -2 and 30 <= r['data']['rsi'] <= 70)
                
                if good_count >= 3:
                    print("      🟢 市场竞价良好，可积极关注")
                    print("      建议仓位: 40-50%")
                elif good_count >= 2:
                    print("      🟡 市场竞价一般，谨慎操作")
                    print("      建议仓位: 30-40%")
                else:
                    print("      🔴 市场竞价较差，建议观望")
                    print("      建议仓位: 20-30%")
            
            print("\n\n" + "="*70)
            print("     ⏰ 时间节点提醒")
            print("="*70)
            
            print(f"\n   当前时间: {hour}:{minute:02d}")
            
            if hour == 9 and minute < 15:
                remaining = 15 - minute
                print(f"   ⏰ 竞价开始还有 {remaining} 分钟")
                print("   建议: 做好准备，关注竞价数据变化")
            elif hour == 9 and 15 <= minute <= 25:
                remaining = 25 - minute
                print(f"   🟢 竞价进行中，剩余 {remaining} 分钟")
                print("   建议: 持续关注，等待最佳买入时机")
            elif hour == 9 and minute >= 25:
                print("   ⏰ 竞价即将结束")
                print("   建议: 做出最终决策，等待开盘")
            else:
                print("   ⏰ 竞价时间已过")
                print("   建议: 进入开盘观察阶段")
            
            print("\n" + "="*70)
            print("     ⏱️ 操作时间表")
            print("="*70)
            
            print("\n   9:15-9:25  集合竞价阶段 ← 当前")
            print("   9:25-9:30  竞价结束，等待开盘")
            print("   9:30-9:35  开盘后前5分钟观察期")
            print("   9:35-10:00 最佳操作时段")
            print("   10:00后    不建议新开仓位")
            
            print("\n   按 Ctrl+C 退出监控")
            print("="*70)
            
            refresh_count += 1
            
            # 每60秒刷新一次
            print(f"\n   ⏱️ 将在60秒后自动刷新 ({refresh_count}/∞)...")
            time.sleep(60)  # 等待60秒
            
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("     监控已停止")
        print("="*70)
        print(f"\n   共刷新 {refresh_count} 次")
        print("   最后更新时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        if results:
            print("\n   📊 最终竞价总结:")
            for r in results:
                print(f"      {r['symbol']}: {r['color']}{r['intensity']}")
        
        print("\n💡 提示: 竞价结束后，关注开盘后走势再决定操作")
        print("="*70)

if __name__ == "__main__":
    monitor_loop()
