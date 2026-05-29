#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取5月19日最新市场数据并给出策略方向
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyRsi, StrategyMaCross
import pandas as pd
from datetime import datetime

def get_watchlist():
    """读取自选股列表"""
    try:
        with open('monitor/stocks.txt', 'r', encoding='utf-8') as f:
            stocks = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return stocks
    except:
        return ['000001.SZ', '000002.SZ', '600000.SH']

def analyze_stock(symbol, data_engine):
    """分析单只股票"""
    try:
        df = data_engine.get_stock_data(symbol)
        if df is None or len(df) < 30:
            return None
        
        df = calculate_indicators(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        analysis = {
            'symbol': symbol,
            'close': latest['close'],
            'change_pct': ((latest['close'] - prev['close']) / prev['close']) * 100,
            'volume_ratio': latest.get('volume_ratio', 1),
            'ma5': latest['ma5'],
            'ma20': latest['ma20'],
            'rsi': latest['rsi'],
            'macd': latest.get('macd', 0),
            'signal': latest.get('signal', 0),
            'boll_upper': latest.get('boll_upper', 0),
            'boll_lower': latest.get('boll_lower', 0),
            'atr': latest.get('atr', 0),
        }
        
        if analysis['ma5'] > analysis['ma20']:
            analysis['trend'] = 'up'
        elif analysis['ma5'] < analysis['ma20']:
            analysis['trend'] = 'down'
        else:
            analysis['trend'] = 'sideways'
        
        if analysis['rsi'] < 35:
            analysis['rsi_signal'] = 'oversold'
        elif analysis['rsi'] > 80:
            analysis['rsi_signal'] = 'overbought'
        else:
            analysis['rsi_signal'] = 'neutral'
        
        if analysis['close'] < analysis['boll_lower']:
            analysis['boll_signal'] = 'below_lower'
        elif analysis['close'] > analysis['boll_upper']:
            analysis['boll_signal'] = 'above_upper'
        else:
            analysis['boll_signal'] = 'normal'
        
        return analysis
    
    except Exception as e:
        print(f"   ❌ {symbol}: {e}")
        return None

def generate_strategy(analysis):
    """生成策略建议"""
    if analysis is None:
        return None
    
    strategies = []
    
    # RSI策略评估
    if analysis['rsi_signal'] == 'oversold' and analysis['trend'] == 'up':
        strategies.append({
            'type': 'RSI超跌反弹',
            'signal': 'BUY',
            'confidence': 'HIGH',
            'reason': f"RSI={analysis['rsi']:.1f}超卖且趋势向上"
        })
    elif analysis['rsi_signal'] == 'overbought' and analysis['trend'] == 'down':
        strategies.append({
            'type': 'RSI超买回调',
            'signal': 'SELL',
            'confidence': 'HIGH',
            'reason': f"RSI={analysis['rsi']:.1f}超买且趋势向下"
        })
    
    # 趋势策略评估
    if analysis['trend'] == 'up' and analysis['rsi'] < 70:
        strategies.append({
            'type': '均线多头排列',
            'signal': 'BUY',
            'confidence': 'MEDIUM',
            'reason': f"MA5>MA20多头排列，RSI={analysis['rsi']:.1f}未超买"
        })
    elif analysis['trend'] == 'down' and analysis['rsi'] > 30:
        strategies.append({
            'type': '均线空头排列',
            'signal': 'SELL',
            'confidence': 'MEDIUM',
            'reason': f"MA5<MA20空头排列，RSI={analysis['rsi']:.1f}未超卖"
        })
    
    # 布林带策略
    if analysis['boll_signal'] == 'below_lower':
        strategies.append({
            'type': '布林带下轨反弹',
            'signal': 'BUY',
            'confidence': 'MEDIUM',
            'reason': "价格触及布林带下轨，可能反弹"
        })
    elif analysis['boll_signal'] == 'above_upper':
        strategies.append({
            'type': '布林带上轨回调',
            'signal': 'SELL',
            'confidence': 'MEDIUM',
            'reason': "价格触及布林带上轨，可能回调"
        })
    
    if not strategies:
        strategies.append({
            'type': '观望',
            'signal': 'HOLD',
            'confidence': 'LOW',
            'reason': "无明确信号，建议等待"
        })
    
    return strategies

def main():
    print("="*70)
    print("     量子量化系统 - 5月19日市场分析")
    print(f"     分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    print("\n📥 获取自选股列表...")
    watchlist = get_watchlist()
    print(f"   ✅ 找到 {len(watchlist)} 只自选股")
    
    print("\n🔄 初始化数据引擎...")
    data_engine = DataEngine()
    print("   ✅ 初始化完成")
    
    print("\n" + "="*70)
    print("     正在分析自选股数据...")
    print("="*70)
    
    results = []
    
    for i, symbol in enumerate(watchlist[:20], 1):
        print(f"\n   [{i}/{min(20, len(watchlist))}] 分析 {symbol}...")
        analysis = analyze_stock(symbol, data_engine)
        
        if analysis:
            strategies = generate_strategy(analysis)
            analysis['strategies'] = strategies
            results.append(analysis)
            
            print(f"       价格: {analysis['close']:.2f} ({analysis['change_pct']:+.2f}%)")
            print(f"       趋势: {analysis['trend']} | RSI: {analysis['rsi']:.1f}")
            
            if strategies:
                best = strategies[0]
                print(f"       信号: {best['signal']} ({best['type']})")
        else:
            print(f"       ⚠️ 数据获取失败")
    
    print("\n" + "="*70)
    print("     📊 市场分析报告")
    print("="*70)
    
    buy_signals = [r for r in results if any(s['signal'] == 'BUY' for s in r['strategies'])]
    sell_signals = [r for r in results if any(s['signal'] == 'SELL' for s in r['strategies'])]
    hold_signals = [r for r in results if any(s['signal'] == 'HOLD' for s in r['strategies'])]
    
    print(f"\n📈 信号统计:")
    print(f"   买入信号: {len(buy_signals)} 只")
    print(f"   卖出信号: {len(sell_signals)} 个")
    print(f"   观望信号: {len(hold_signals)} 个")
    
    print(f"\n\n" + "="*70)
    print("     🎯 策略方向建议")
    print("="*70)
    
    if buy_signals:
        print("\n✅ **建议关注（买入信号）**\n")
        
        buy_signals.sort(key=lambda x: x['rsi'])
        
        for i, stock in enumerate(buy_signals[:5], 1):
            print(f"   {i}. **{stock['symbol']}**")
            print(f"      价格: {stock['close']:.2f} ({stock['change_pct']:+.2f}%)")
            print(f"      趋势: {stock['trend']} | RSI: {stock['rsi']:.1f}")
            
            for strategy in stock['strategies']:
                if strategy['signal'] == 'BUY':
                    print(f"      ✅ {strategy['type']}")
                    print(f"         置信度: {strategy['confidence']}")
                    print(f"         原因: {strategy['reason']}")
                    break
            print()
    
    if sell_signals:
        print("\n⚠️ **注意风险（卖出信号）**\n")
        
        for i, stock in enumerate(sell_signals[:3], 1):
            print(f"   {i}. **{stock['symbol']}**")
            print(f"      价格: {stock['close']:.2f} ({stock['change_pct']:+.2f}%)")
            print(f"      趋势: {stock['trend']} | RSI: {stock['rsi']:.1f}")
            
            for strategy in stock['strategies']:
                if strategy['signal'] == 'SELL':
                    print(f"      ⚠️ {strategy['type']}")
                    print(f"         原因: {strategy['reason']}")
                    break
            print()
    
    print("\n" + "="*70)
    print("     💡 操作建议")
    print("="*70)
    
    if len(buy_signals) > len(sell_signals):
        print("\n🟢 **市场偏多**")
        print("   建议关注买入信号个股，控制仓位")
        print("   建议仓位: 40-60%")
    elif len(sell_signals) > len(buy_signals):
        print("\n🔴 **市场偏空**")
        print("   建议减仓或观望")
        print("   建议仓位: 20-40%")
    else:
        print("\n🟡 **市场中性**")
        print("   建议谨慎操作，等待明确信号")
        print("   建议仓位: 30-50%")
    
    print("\n" + "="*70)
    print("     详细分析结果")
    print("="*70)
    
    print(f"\n   {'股票代码':<12} {'价格':>10} {'涨跌幅':>8} {'趋势':>8} {'RSI':>6} {'信号':<15}")
    print("   " + "-"*70)
    
    for stock in sorted(results, key=lambda x: x['change_pct'], reverse=True):
        main_signal = "无信号"
        for s in stock['strategies']:
            if s['signal'] != 'HOLD':
                main_signal = f"{s['signal']}-{s['type'][:10]}"
                break
        
        print(f"   {stock['symbol']:<12} {stock['close']:>10.2f} {stock['change_pct']:>+7.2f}% "
              f"{stock['trend']:>8} {stock['rsi']:>6.1f} {main_signal:<15}")
    
    print("\n" + "="*70)
    print("✅ 分析完成！")
    print("="*70)
    print("\n💡 提示: 以上建议仅供参考，不构成投资建议")
    print("   请结合市场整体情况和个人风险承受能力决策")

if __name__ == "__main__":
    main()
