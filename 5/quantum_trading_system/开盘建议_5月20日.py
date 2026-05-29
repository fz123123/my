#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5月20日开盘建议 - 实时市场分析
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyRsi
import pandas as pd
from datetime import datetime
import time

def get_realtime_quote(symbol, data_engine):
    """获取实时行情"""
    try:
        df = data_engine.get_stock_data(symbol)
        if df is None or len(df) < 5:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        return {
            'symbol': symbol,
            'close': latest['close'],
            'prev_close': prev['close'],
            'change_pct': ((latest['close'] - prev['close']) / prev['close']) * 100,
            'volume': latest.get('volume', 0),
            'ma5': latest.get('ma5', 0),
            'ma20': latest.get('ma20', 0),
            'rsi': latest.get('rsi', 50),
        }
    except Exception as e:
        return None

def analyze_market_sentiment(data_engine):
    """分析市场情绪"""
    key_stocks = [
        ('000001.SZ', '平安银行'),
        ('600000.SH', '浦发银行'),
        ('600519.SH', '贵州茅台'),
        ('000002.SZ', '万科A'),
        ('601318.SH', '中国平安'),
    ]
    
    results = []
    
    for symbol, name in key_stocks:
        try:
            df = data_engine.get_stock_data(symbol)
            if df is not None and len(df) >= 5:
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                change = ((latest['close'] - prev['close']) / prev['close']) * 100
                
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'price': latest['close'],
                    'change': change
                })
        except:
            continue
    
    return results

def generate_open_recommendations(data_engine):
    """生成开盘推荐"""
    candidates = [
        '160058.SZ',  # RSI适中，超跌反弹
        '000224.SZ',  # RSI接近超卖
        '160369.SZ',  # 稳健选择
        '000242.SZ',  # 涨幅较大
        '160350.SZ',  # 趋势向上
    ]
    
    recommendations = []
    
    for symbol in candidates:
        analysis = get_realtime_quote(symbol, data_engine)
        if analysis:
            score = 0
            reasons = []
            
            # RSI评分
            if 40 <= analysis['rsi'] <= 60:
                score += 30
                reasons.append(f"RSI适中({analysis['rsi']:.1f})")
            elif analysis['rsi'] < 40:
                score += 25
                reasons.append(f"RSI偏低({analysis['rsi']:.1f})，有反弹空间")
            elif analysis['rsi'] > 70:
                score -= 20
                reasons.append(f"RSI偏高({analysis['rsi']:.1f})，注意风险")
            
            # 涨跌评分
            if analysis['change_pct'] < -2:
                score += 25
                reasons.append(f"超跌({analysis['change_pct']:+.1f}%)，反弹概率大")
            elif -2 <= analysis['change_pct'] < 0:
                score += 20
                reasons.append(f"小幅下跌({analysis['change_pct']:+.1f}%)，可关注")
            elif 0 <= analysis['change_pct'] < 2:
                score += 15
                reasons.append(f"小幅上涨({analysis['change_pct']:+.1f}%)，趋势良好")
            elif analysis['change_pct'] >= 2:
                score += 10
                reasons.append(f"涨幅较大({analysis['change_pct']:+.1f}%)")
            
            # 均线评分
            if analysis['ma5'] > analysis['ma20']:
                score += 20
                reasons.append("均线多头排列")
            elif analysis['ma5'] < analysis['ma20']:
                score -= 20
                reasons.append("均线空头排列")
            
            # 绝对价格评分
            if analysis['close'] < 100:
                score += 10
                reasons.append("价格较低，安全边际高")
            
            recommendations.append({
                'symbol': symbol,
                'price': analysis['close'],
                'change': analysis['change_pct'],
                'rsi': analysis['rsi'],
                'score': score,
                'reasons': reasons
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def main():
    print("="*70)
    print("     量子量化系统 - 5月20日 开盘建议")
    print(f"     生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    print("\n🔄 初始化数据引擎...")
    data_engine = DataEngine()
    print("   ✅ 初始化完成")
    
    print("\n" + "="*70)
    print("     📊 市场情绪分析")
    print("="*70)
    
    print("\n   关键股票表现:")
    sentiment = analyze_market_sentiment(data_engine)
    
    if sentiment:
        up_count = sum(1 for s in sentiment if s['change'] > 0)
        down_count = len(sentiment) - up_count
        
        for stock in sentiment:
            trend = "🔴" if stock['change'] < 0 else "🟢"
            print(f"   {trend} {stock['name']:<8} {stock['price']:>8.2f} ({stock['change']:>+6.2f}%)")
        
        print(f"\n   市场情绪: {up_count}只上涨 / {down_count}只下跌")
        
        if up_count > down_count:
            print("   情绪判断: 🟢 市场偏暖")
        elif down_count > up_count:
            print("   情绪判断: 🔴 市场偏弱")
        else:
            print("   情绪判断: 🟡 市场中性")
    
    print("\n" + "="*70)
    print("     🎯 开盘推荐标的")
    print("="*70)
    
    print("\n   正在分析候选标的...")
    recommendations = generate_open_recommendations(data_engine)
    
    if recommendations:
        print("\n   综合评分排名:")
        print(f"   {'排名':<4} {'股票代码':<12} {'价格':>10} {'涨跌幅':>8} {'RSI':>6} {'评分':>6} {'评价':<15}")
        print("   " + "-"*70)
        
        for i, rec in enumerate(recommendations[:5], 1):
            if rec['score'] >= 70:
                eval_text = "⭐⭐⭐强烈推荐"
            elif rec['score'] >= 55:
                eval_text = "⭐⭐推荐买入"
            else:
                eval_text = "⭐可关注"
            
            print(f"   {i:<4} {rec['symbol']:<12} {rec['price']:>10.2f} {rec['change']:>+7.2f}% "
                  f"{rec['rsi']:>6.1f} {rec['score']:>5} {eval_text:<15}")
        
        print("\n\n   " + "="*70)
        print("     重点标的详细分析")
        print("   " + "="*70)
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"\n   {'='*70}")
            print(f"   {i}. {rec['symbol']} - 综合评分: {rec['score']}")
            print(f"   {'='*70}")
            
            print(f"\n   📊 基本信息:")
            print(f"      当前价格: {rec['price']:.2f}")
            print(f"      涨跌幅: {rec['change']:+.2f}%")
            print(f"      RSI: {rec['rsi']:.1f}")
            
            print(f"\n   📝 推荐理由:")
            for reason in rec['reasons']:
                print(f"      ✅ {reason}")
            
            # 操作建议
            if rec['score'] >= 70:
                action = "强烈建议开盘关注"
                action_level = "🟢"
            elif rec['score'] >= 55:
                action = "建议开盘买入"
                action_level = "🟡"
            else:
                action = "可轻仓试探"
                action_level = "⚠️"
            
            print(f"\n   💡 操作建议:")
            print(f"      {action_level} {action}")
            
            # 风险提示
            print(f"\n   ⚠️ 风险提示:")
            if rec['change'] < -3:
                print(f"      - 跌幅较大，警惕惯性下跌")
            if rec['rsi'] < 35:
                print(f"      - RSI超卖，可能继续下探")
            if rec['rsi'] > 65:
                print(f"      - RSI偏高，追涨需谨慎")
            
            print(f"\n   🎯 参考价位:")
            buy_price = rec['price'] * 0.995  # 开盘价下浮0.5%
            stop_loss = rec['price'] * 0.92   # 8%止损
            target1 = rec['price'] * 1.08      # 第一目标8%
            target2 = rec['price'] * 1.15      # 第二目标15%
            
            print(f"      建议买入价: {buy_price:.2f} 以下")
            print(f"      止损价: {stop_loss:.2f} (下跌8%)")
            print(f"      第一目标: {target1:.2f} (上涨8%)")
            print(f"      第二目标: {target2:.2f} (上涨15%)")
    
    print("\n\n" + "="*70)
    print("     💰 开盘操作策略")
    print("="*70)
    
    if recommendations:
        best = recommendations[0]
        
        print(f"\n   🏆 首选标的: {best['symbol']}")
        print(f"      建议理由: {best['reasons'][0] if best['reasons'] else '综合评分最高'}")
        print(f"      建议仓位: 20%")
        print(f"      建议价格: 开盘后{best['price']*0.995:.2f}以下可买入")
        
        if len(recommendations) > 1:
            second = recommendations[1]
            print(f"\n   📈 次选标的: {second['symbol']}")
            print(f"      建议理由: {second['reasons'][0] if second['reasons'] else '综合评分次高'}")
            print(f"      建议仓位: 10%")
    
    print(f"\n   📊 总仓位建议:")
    print(f"      激进策略: 40-50%")
    print(f"      稳健策略: 30-40%")
    print(f"      保守策略: 20-30%")
    
    print(f"\n   ⏰ 开盘操作时间表:")
    print(f"      9:15-9:25  竞价阶段，观察开盘价")
    print(f"      9:25-9:30  决定是否操作")
    print(f"      9:30-10:00 观察开盘走势，不急于操作")
    print(f"      10:00-11:00 最佳买入时段")
    print(f"      14:30后    不新开仓位")
    
    print("\n" + "="*70)
    print("     ⚠️ 风险控制提醒")
    print("="*70)
    
    print(f"\n   🛡️ 必须遵守的规则:")
    print(f"      1. 单笔止损不超过8%")
    print(f"      2. 总仓位不超过50%")
    print(f"      3. 避免追涨杀跌")
    print(f"      4. 趋势破坏坚决离场")
    
    print(f"\n   🚨 立即止损情况:")
    print(f"      - 开盘下跌超过5%")
    print(f"      - 跌破重要支撑位")
    print(f"      - 放量下跌")
    
    print("\n" + "="*70)
    print("✅ 5月20日开盘建议生成完成！")
    print("="*70)
    print("\n💡 免责声明: 以上建议仅供参考，不构成投资建议")
    print("   股市有风险，投资需谨慎！")

if __name__ == "__main__":
    main()
