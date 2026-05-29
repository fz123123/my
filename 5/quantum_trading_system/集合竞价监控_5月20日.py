#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集合竞价实时监控 - 5月20日
监控时间: 9:15 - 9:25
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
import pandas as pd
from datetime import datetime
import time

def get_premarket_data(symbol, data_engine):
    """获取集合竞价数据"""
    try:
        # 获取最新数据作为竞价参考
        df = data_engine.get_stock_data(symbol)
        if df is None or len(df) < 2:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 计算竞价相关指标
        change_pct = ((latest['close'] - prev['close']) / prev['close']) * 100
        
        # 模拟竞价数据（实际需要交易所数据接口）
        # 这里基于昨日收盘价和当前行情估算
        yesterday_close = prev['close']
        current_estimate = latest['close']
        
        # 竞价涨幅估算（根据当前价格相对昨日收盘的变化）
        auction_premium = ((current_estimate - yesterday_close) / yesterday_close) * 100
        
        return {
            'symbol': symbol,
            'yesterday_close': yesterday_close,
            'current_estimate': current_estimate,
            'auction_premium': auction_premium,
            'volume': latest.get('volume', 0),
            'ma5': latest.get('ma5', 0),
            'ma20': latest.get('ma20', 0),
            'rsi': latest.get('rsi', 50),
        }
    except Exception as e:
        return None

def analyze_auction_opportunity(data, current_time):
    """分析竞价机会"""
    if not data:
        return None
    
    analysis = {
        'symbol': data['symbol'],
        'time': current_time,
        'yesterday_close': data['yesterday_close'],
        'auction_premium': data['auction_premium'],
        'rsi': data['rsi'],
    }
    
    # 判断竞价强度
    if abs(data['auction_premium']) < 0.5:
        analysis['intensity'] = 'normal'
        analysis['intensity_text'] = '竞价平稳'
    elif data['auction_premium'] > 2:
        analysis['intensity'] = 'strong_up'
        analysis['intensity_text'] = '竞价强势'
    elif data['auction_premium'] > 5:
        analysis['intensity'] = 'very_strong_up'
        analysis['intensity_text'] = '竞价非常强势，小心高开低走'
    elif data['auction_premium'] < -2:
        analysis['intensity'] = 'weak'
        analysis['intensity_text'] = '竞价偏弱'
    elif data['auction_premium'] < -5:
        analysis['intensity'] = 'very_weak'
        analysis['intensity_text'] = '竞价大幅低开，关注是否超跌'
    else:
        analysis['intensity'] = 'normal'
        analysis['intensity_text'] = '竞价正常'
    
    # 生成操作建议
    suggestions = []
    
    # 竞价强势判断
    if data['auction_premium'] > 3:
        suggestions.append({
            'type': 'warning',
            'text': '⚠️ 高开幅度过大，建议观望'
        })
        suggestions.append({
            'type': 'action',
            'text': '建议: 等待回调后再买入，避免追高'
        })
    elif data['auction_premium'] > 1:
        suggestions.append({
            'type': 'info',
            'text': '💡 竞价温和上涨，可适度关注'
        })
        if data['rsi'] < 65:
            suggestions.append({
                'type': 'action',
                'text': '建议: 若开盘后回调到均线附近可买入'
            })
    
    # 竞价弱势判断
    if data['auction_premium'] < -3:
        suggestions.append({
            'type': 'warning',
            'text': '⚠️ 大幅低开，警惕惯性下跌'
        })
        suggestions.append({
            'type': 'action',
            'text': '建议: 观望为主，等待企稳信号'
        })
    elif data['auction_premium'] < -1:
        suggestions.append({
            'type': 'info',
            'text': '💡 小幅低开，关注是否超跌反弹'
        })
        if data['rsi'] < 35:
            suggestions.append({
                'type': 'action',
                'text': '建议: RSI超卖，可关注反弹机会'
            })
    
    # 竞价平稳判断
    if abs(data['auction_premium']) < 0.5:
        suggestions.append({
            'type': 'info',
            'text': '💡 竞价平稳，等待开盘明确方向'
        })
        suggestions.append({
            'type': 'action',
            'text': '建议: 观察开盘后10分钟走势再决定'
        })
    
    # RSI判断
    if data['rsi'] > 70:
        suggestions.append({
            'type': 'warning',
            'text': f'⚠️ RSI={data["rsi"]:.0f}偏高，追涨需谨慎'
        })
    elif data['rsi'] < 30:
        suggestions.append({
            'type': 'info',
            'text': f'💡 RSI={data["rsi"]:.0f}超卖，可能存在反弹机会'
        })
    
    analysis['suggestions'] = suggestions
    
    # 评分
    score = 50
    
    # 竞价溢价评分
    if -1 <= data['auction_premium'] <= 2:
        score += 30
    elif -2 <= data['auction_premium'] < -1 or 2 < data['auction_premium'] <= 4:
        score += 15
    else:
        score -= 20
    
    # RSI评分
    if 40 <= data['rsi'] <= 60:
        score += 20
    elif 30 <= data['rsi'] < 40 or 60 < data['rsi'] <= 70:
        score += 10
    else:
        score -= 10
    
    analysis['score'] = score
    
    return analysis

def monitor_auction():
    """监控集合竞价"""
    print("="*70)
    print("     量子量化系统 - 集合竞价实时监控")
    print("     监控时间: 9:15 - 9:25")
    print("="*70)
    
    # 初始化数据引擎
    print("\n🔄 初始化数据引擎...")
    data_engine = DataEngine()
    print("   ✅ 初始化完成")
    
    # 重点监控标的
    monitor_stocks = [
        ('000224.SZ', '首选标的'),
        ('000242.SZ', '次选标的'),
        ('160058.SZ', '关注标的'),
        ('160369.SZ', '关注标的'),
    ]
    
    current_time = datetime.now()
    print(f"\n⏰ 当前时间: {current_time.strftime('%H:%M:%S')}")
    print(f"📅 日期: {current_time.strftime('%Y-%m-%d')}")
    
    # 判断是否在竞价时间内
    hour = current_time.hour
    minute = current_time.minute
    
    if 9 <= hour < 9.5:  # 9:00-9:30之间
        print("\n🟢 当前处于竞价/开盘时段")
        
        # 获取竞价数据
        print("\n" + "="*70)
        print("     竞价数据分析")
        print("="*70)
        
        auction_results = []
        
        for symbol, note in monitor_stocks:
            print(f"\n   分析 {symbol} ({note})...")
            
            data = get_premarket_data(symbol, data_engine)
            
            if data:
                analysis = analyze_auction_opportunity(data, current_time)
                auction_results.append(analysis)
                
                print(f"      昨日收盘: {data['yesterday_close']:.2f}")
                print(f"      当前估算: {data['current_estimate']:.2f}")
                print(f"      竞价涨幅: {data['auction_premium']:+.2f}%")
                print(f"      RSI: {data['rsi']:.1f}")
                print(f"      竞价状态: {analysis['intensity_text']}")
                print(f"      综合评分: {analysis['score']}")
                
                if analysis['suggestions']:
                    print(f"      操作建议:")
                    for suggestion in analysis['suggestions']:
                        print(f"         {suggestion['text']}")
            else:
                print(f"      ⚠️ 数据获取失败")
        
        # 生成最终建议
        print("\n\n" + "="*70)
        print("     竞价阶段最终建议")
        print("="*70)
        
        # 按评分排序
        auction_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n   📊 竞价机会排名:")
        for i, result in enumerate(auction_results, 1):
            print(f"\n   {i}. {result['symbol']}")
            print(f"      竞价涨幅: {result['auction_premium']:+.2f}%")
            print(f"      竞价状态: {result['intensity_text']}")
            print(f"      综合评分: {result['score']}")
            
            # 找出操作建议
            action_suggestions = [s for s in result['suggestions'] if s['type'] == 'action']
            if action_suggestions:
                print(f"      操作建议:")
                for suggestion in action_suggestions:
                    print(f"         {suggestion['text']}")
        
        # 给出整体建议
        print("\n\n" + "="*70)
        print("     💡 竞价阶段整体建议")
        print("="*70)
        
        best = auction_results[0] if auction_results else None
        
        if best:
            if best['score'] >= 80:
                print(f"\n   🟢 竞价机会较好")
                print(f"   首选标的: {best['symbol']}")
                print(f"   竞价涨幅: {best['auction_premium']:+.2f}%")
                print(f"   建议: 可在开盘后积极关注")
            elif best['score'] >= 60:
                print(f"\n   🟡 竞价机会一般")
                print(f"   首选标的: {best['symbol']}")
                print(f"   竞价涨幅: {best['auction_premium']:+.2f}%")
                print(f"   建议: 观望为主，等待回调")
            else:
                print(f"\n   🔴 竞价机会不佳")
                print(f"   建议: 今日谨慎操作，控制仓位")
        
        print("\n\n" + "="*70)
        print("     ⏰ 后续操作时间表")
        print("="*70)
        
        print(f"\n   9:30 开盘 - 观察开盘价是否延续竞价趋势")
        print(f"   9:30-9:35 观察前5分钟走势")
        print(f"   9:35-10:00 关键决策时段")
        print(f"   10:00-11:00 最佳操作时段")
        print(f"   11:00后 不建议新开仓位")
        
    else:
        print("\n⏰ 当前不在竞价时间（9:15-9:25）")
        print(f"   当前时间: {current_time.strftime('%H:%M:%S')}")
        print("\n💡 竞价监控将在9:15自动启动")
        
        # 即使不在竞价时间，也可以给出前一天收盘后的分析
        print("\n" + "="*70)
        print("     昨日收盘分析（仅供参考）")
        print("="*70)
        
        for symbol, note in monitor_stocks[:2]:
            print(f"\n   {symbol} ({note}):")
            data = get_premarket_data(symbol, data_engine)
            if data:
                print(f"      收盘价: {data['yesterday_close']:.2f}")
                print(f"      RSI: {data['rsi']:.1f}")
                
                if data['rsi'] < 35:
                    print(f"      状态: RSI超卖，关注反弹机会")
                elif data['rsi'] > 65:
                    print(f"      状态: RSI偏高，注意回调风险")
                else:
                    print(f"      状态: RSI适中，等待方向明确")
    
    print("\n" + "="*70)
    print("✅ 竞价监控完成！")
    print("="*70)
    print("\n💡 提示:")
    print("   1. 集合竞价仅供参考，实际操作需结合开盘后走势")
    print("   2. 高开低走和低开高走是常见现象")
    print("   3. 建议等待开盘后趋势明确再操作")
    print("   4. 严格控制仓位和止损")

if __name__ == "__main__":
    monitor_auction()
