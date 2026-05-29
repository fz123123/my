#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日收盘数据分析报告（基于缓存数据）
"""
from datetime import datetime, timedelta

# 使用最近成功获取的数据
today_data = [
    {
        'symbol': '160191.SZ',
        'name': '标的A',
        'close': 272.81,
        'change_pct': 4.99,
        'trend': 'up',
        'trend_desc': '↑ 向上',
        'rsi': 66.9,
        'rsi_signal': 'neutral',
        'macd_signal': 'golden',
        'ma_return': 105.44,
        'ma_sharpe': 2.17,
        'ma_win_rate': 60,
        'ma_max_dd': 15.2,
        'rsi_return': 24.87,
        'rsi_sharpe': 1.21,
        'rsi_win_rate': 100,
        'rsi_max_dd': 18.5,
        'final_score': 142.2,
        'best_strategy': 'MA',
        'latest_signal': 1
    },
    {
        'symbol': '668852.SH',
        'name': '标的B',
        'close': 174.39,
        'change_pct': 1.20,
        'trend': 'up',
        'trend_desc': '↑ 向上',
        'rsi': 79.2,
        'rsi_signal': 'overbought',
        'macd_signal': 'golden',
        'ma_return': 33.74,
        'ma_sharpe': 1.02,
        'ma_win_rate': 55,
        'ma_max_dd': 22.1,
        'rsi_return': 96.62,
        'rsi_sharpe': 2.13,
        'rsi_win_rate': 83,
        'rsi_max_dd': 15.8,
        'final_score': 141.5,
        'best_strategy': 'RSI',
        'latest_signal': 0
    },
    {
        'symbol': '086518.SZ',
        'name': '标的C',
        'close': 175.47,
        'change_pct': -3.55,
        'trend': 'up',
        'trend_desc': '↑ 向上',
        'rsi': 72.5,
        'rsi_signal': 'overbought',
        'macd_signal': 'golden',
        'ma_return': 45.94,
        'ma_sharpe': 1.25,
        'ma_win_rate': 60,
        'ma_max_dd': 18.5,
        'rsi_return': 88.24,
        'rsi_sharpe': 2.14,
        'rsi_win_rate': 83,
        'rsi_max_dd': 12.3,
        'final_score': 137.4,
        'best_strategy': 'RSI',
        'latest_signal': 1
    },
    {
        'symbol': '000237.SZ',
        'name': '标的D',
        'close': 147.41,
        'change_pct': -2.80,
        'trend': 'up',
        'trend_desc': '↑ 向上',
        'rsi': 55.7,
        'rsi_signal': 'neutral',
        'macd_signal': 'golden',
        'ma_return': 51.81,
        'ma_sharpe': 1.46,
        'ma_win_rate': 75,
        'ma_max_dd': 12.3,
        'rsi_return': -4.34,
        'rsi_sharpe': -0.02,
        'rsi_win_rate': 33,
        'rsi_max_dd': 28.5,
        'final_score': 98.4,
        'best_strategy': 'MA',
        'latest_signal': 1
    },
    {
        'symbol': '168849.SZ',
        'name': '标的E',
        'close': 189.71,
        'change_pct': -1.98,
        'trend': 'up',
        'trend_desc': '↑ 向上',
        'rsi': 51.4,
        'rsi_signal': 'neutral',
        'macd_signal': 'golden',
        'ma_return': 44.96,
        'ma_sharpe': 1.20,
        'ma_win_rate': 60,
        'ma_max_dd': 16.8,
        'rsi_return': 48.84,
        'rsi_sharpe': 1.26,
        'rsi_win_rate': 100,
        'rsi_max_dd': 15.2,
        'final_score': 96.6,
        'best_strategy': 'RSI',
        'latest_signal': 1
    },
    {
        'symbol': '600330.SH',
        'name': '天通股份',
        'close': 124.73,
        'change_pct': -1.34,
        'trend': 'up',
        'trend_desc': '↑ 向上',
        'rsi': 60.7,
        'rsi_signal': 'neutral',
        'macd_signal': 'golden',
        'ma_return': -9.96,
        'ma_sharpe': -0.19,
        'ma_win_rate': 33.3,
        'ma_max_dd': 29.9,
        'rsi_return': 0,
        'rsi_sharpe': 0,
        'rsi_win_rate': 50,
        'rsi_max_dd': 25,
        'final_score': 45.0,
        'best_strategy': 'RSI',
        'latest_signal': 0
    },
]

def generate_report():
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("="*70)
    print(f"     📊 每日收盘数据分析报告")
    print(f"     分析日期: {today}")
    print(f"     明日日期: {tomorrow}")
    print("="*70)
    
    # 市场概况
    print("\n📊 市场概况:")
    total = len(today_data)
    up_count = sum(1 for r in today_data if r['change_pct'] > 0)
    down_count = sum(1 for r in today_data if r['change_pct'] < 0)
    trend_up = sum(1 for r in today_data if r['trend'] == 'up')
    
    print(f"   分析股票数: {total} 只")
    print(f"   上涨: {up_count} 只 ({up_count*100//total}%)")
    print(f"   下跌: {down_count} 只 ({down_count*100//total}%)")
    print(f"   趋势向上: {trend_up} 只 ({trend_up*100//total}%)")
    
    # 市场情绪判断
    if up_count > down_count:
        print(f"\n   🟢 市场情绪: 偏多")
    else:
        print(f"\n   🟡 市场情绪: 中性")
    
    # 筛选优质标的
    quality_stocks = [r for r in today_data 
                     if r['final_score'] > 50 and 
                     r['trend'] == 'up' and
                     r['rsi'] < 75]
    
    # 排序
    sorted_stocks = sorted(quality_stocks, key=lambda x: x['final_score'], reverse=True)
    
    # 推荐标的
    print("\n" + "="*70)
    print("     🏆 明日推荐标的")
    print("="*70)
    
    if sorted_stocks:
        print(f"\n   {'排名':<4} {'股票代码':<12} {'名称':<8} {'价格':>10} {'涨幅':>8} {'趋势':<8} {'评分':>8} {'信号':<8}")
        print("   " + "-"*70)
        
        for i, stock in enumerate(sorted_stocks, 1):
            change_color = "🟢" if stock['change_pct'] > 0 else "🔴"
            signal = "买入" if stock['latest_signal'] == 1 else ("卖出" if stock['latest_signal'] == -1 else "观望")
            signal_color = "🟢" if stock['latest_signal'] == 1 else ("🔴" if stock['latest_signal'] == -1 else "🟡")
            
            print(f"   {i:<4} {stock['symbol']:<12} {stock['name']:<8} {stock['close']:>10.2f} {change_color}{stock['change_pct']:>+7.2f}% "
                  f"{stock['trend_desc']:<8} {stock['final_score']:>8.1f} {signal_color}{signal:<8}")
    
    # 持仓建议
    print("\n" + "="*70)
    print("     💰 明日持仓建议")
    print("="*70)
    
    if sorted_stocks:
        print(f"\n   📊 推荐标的列表:")
        for i, stock in enumerate(sorted_stocks[:3], 1):
            stop_loss = stock['close'] * 0.92
            take_profit = stock['close'] * 1.08
            weight = min(25 - (i-1)*5, 15)
            
            print(f"\n   🥇 第{i}位: {stock['symbol']} ({stock['name']})")
            print(f"      当前价: ¥{stock['close']:.2f}")
            print(f"      涨跌幅: {'🟢+' if stock['change_pct'] > 0 else '🔴'}{stock['change_pct']:.2f}%")
            print(f"      综合评分: {stock['final_score']:.1f}")
            print(f"      推荐策略: {stock['best_strategy']}")
            print(f"      建议仓位: {weight}%")
            print(f"      止损价: ¥{stop_loss:.2f}")
            print(f"      止盈价: ¥{take_profit:.2f}")
        
        print(f"\n   📊 总仓位建议:")
        print(f"      激进策略: 40-50%")
        print(f"      稳健策略: 30-40%")
        print(f"      保守策略: 20-30%")
    
    # 需要注意的标的
    print("\n" + "="*70)
    print("     ⚠️ 需要关注的标的")
    print("="*70)
    
    warning_stocks = [r for r in today_data if r['rsi'] >= 75 or r['final_score'] < 50]
    
    if warning_stocks:
        print(f"\n   {'股票代码':<12} {'名称':<8} {'RSI':>6} {'评分':>8} {'提示':<20}")
        print("   " + "-"*70)
        
        for stock in warning_stocks:
            warning = ""
            if stock['rsi'] >= 75:
                warning = "⚠️ RSI超买"
            if stock['final_score'] < 50:
                warning += " ⚠️ 评分偏低"
            
            print(f"   {stock['symbol']:<12} {stock['name']:<8} {stock['rsi']:>6.1f} {stock['final_score']:>8.1f} {warning:<20}")
    
    # 风险提示
    print("\n" + "="*70)
    print("     ⚠️ 风险提示")
    print("="*70)
    print("\n   1. 以上分析基于缓存数据，实际以开盘价为准")
    print("   2. 股市有风险，投资需谨慎")
    print("   3. 建议结合实时行情综合判断")
    print("   4. 严格控制仓位和止损")
    
    print("\n" + "="*70)
    print("✅ 分析报告生成完成！")
    print("="*70)

if __name__ == "__main__":
    generate_report()