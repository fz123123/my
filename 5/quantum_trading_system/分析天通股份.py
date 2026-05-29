#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天通股份 (600330.SH) 专项分析
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross, StrategyRsi
from backtest.enhanced_engine import EnhancedBacktestEngine
from datetime import datetime

def analyze_stock(symbol, stock_name):
    """分析指定股票"""
    print("="*70)
    print(f"     📊 {stock_name} ({symbol}) 专项分析")
    print(f"     分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 获取数据
    data_engine = DataEngine()
    print("\n🔄 获取股票数据...")
    
    df = data_engine.get_stock_data(symbol)
    
    if df is None or len(df) < 60:
        print(f"\n❌ 无法获取 {stock_name} 的数据")
        return
    
    # 计算指标
    df = calculate_indicators(df)
    
    # 获取最新数据
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['close']
    current_price = latest['close']
    change_pct = ((current_price - prev_close) / prev_close) * 100
    
    print(f"\n✅ 数据获取成功")
    print(f"   数据周期: {len(df)} 条")
    print(f"   时间范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
    
    # 基本信息
    print("\n" + "="*70)
    print("     📈 基本信息")
    print("="*70)
    
    print(f"\n   📊 价格信息:")
    print(f"      当前价格: ¥{current_price:.2f}")
    print(f"      涨跌幅: {'🟢' if change_pct > 0 else '🔴'}{change_pct:+.2f}%")
    print(f"      成交量: {latest.get('volume', 0):,} 股")
    
    # 技术指标
    ma5 = latest.get('ma5', 0)
    ma20 = latest.get('ma20', 0)
    ma60 = latest.get('ma60', 0)
    rsi = latest.get('rsi', 50)
    macd = latest.get('macd', 0)
    macd_signal = latest.get('macd_signal', 0)
    atr = latest.get('atr', 0)
    
    print(f"\n   📈 均线系统:")
    print(f"      MA5: ¥{ma5:.2f}")
    print(f"      MA20: ¥{ma20:.2f}")
    print(f"      MA60: ¥{ma60:.2f}")
    
    # 判断趋势
    if ma5 > ma20 > ma60:
        trend_status = "🟢 多头排列"
        trend = "up"
    elif ma5 < ma20 < ma60:
        trend_status = "🔴 空头排列"
        trend = "down"
    else:
        trend_status = "🟡 震荡整理"
        trend = "sideways"
    
    print(f"      趋势状态: {trend_status}")
    
    print(f"\n   📊 技术指标:")
    print(f"      RSI(14): {rsi:.1f}")
    print(f"      MACD: {macd:.2f}")
    print(f"      MACD Signal: {macd_signal:.2f}")
    print(f"      ATR: {atr:.2f}")
    
    # RSI状态
    if rsi < 30:
        rsi_status = "🟢 超卖区域，可能反弹"
    elif rsi > 70:
        rsi_status = "🔴 超买区域，注意回调"
    else:
        rsi_status = "🟡 正常区间"
    
    print(f"      RSI状态: {rsi_status}")
    
    # MACD状态
    if macd > macd_signal:
        macd_status = "🟢 MACD金叉，多头信号"
    else:
        macd_status = "🔴 MACD死叉，空头信号"
    
    print(f"      MACD状态: {macd_status}")
    
    # 回测分析
    print("\n" + "="*70)
    print("     🎯 策略回测分析")
    print("="*70)
    
    # 均线策略
    ma_strategy = StrategyMaCross(short_period=5, long_period=20)
    ma_signals = ma_strategy.generate_signals(df)
    ma_engine = EnhancedBacktestEngine(initial_capital=100000)
    ma_result = ma_engine.run_backtest(df, ma_signals)
    
    if ma_result:
        print(f"\n   📈 均线交叉策略 (MA5/MA20):")
        print(f"      收益率: {ma_result['total_return_pct']:+.2f}%")
        print(f"      夏普比率: {ma_result['sharpe_ratio']:.2f}")
        print(f"      胜率: {ma_result['win_rate_pct']:.1f}%")
        print(f"      最大回撤: {ma_result['max_drawdown_pct']:.1f}%")
        print(f"      交易次数: {ma_result['trade_count']} 次")
        
        current_ma_signal = "🟢 买入" if ma_signals.iloc[-1]['signal'] == 1 else ("🔴 卖出" if ma_signals.iloc[-1]['signal'] == -1 else "🟡 观望")
        print(f"      当前信号: {current_ma_signal}")
    
    # RSI策略
    rsi_strategy = StrategyRsi(oversold=35, overbought=80)
    rsi_signals = rsi_strategy.generate_signals(df)
    rsi_engine = EnhancedBacktestEngine(initial_capital=100000)
    rsi_result = rsi_engine.run_backtest(df, rsi_signals)
    
    if rsi_result:
        print(f"\n   📉 RSI策略 (35/80):")
        print(f"      收益率: {rsi_result['total_return_pct']:+.2f}%")
        print(f"      夏普比率: {rsi_result['sharpe_ratio']:.2f}")
        print(f"      胜率: {rsi_result['win_rate_pct']:.1f}%")
        print(f"      最大回撤: {rsi_result['max_drawdown_pct']:.1f}%")
        print(f"      交易次数: {rsi_result['trade_count']} 次")
        
        current_rsi_signal = "🟢 买入" if rsi_signals.iloc[-1]['signal'] == 1 else ("🔴 卖出" if rsi_signals.iloc[-1]['signal'] == -1 else "🟡 观望")
        print(f"      当前信号: {current_rsi_signal}")
    
    # 综合评分
    print("\n" + "="*70)
    print("     ⭐ 综合评分")
    print("="*70)
    
    if ma_result and rsi_result:
        ma_score = ma_result['sharpe_ratio'] * 30 + ma_result['total_return_pct'] * 0.5 + ma_result['win_rate_pct'] * 0.3 - ma_result['max_drawdown_pct'] * 0.3
        rsi_score = rsi_result['sharpe_ratio'] * 30 + rsi_result['total_return_pct'] * 0.5 + rsi_result['win_rate_pct'] * 0.3 - rsi_result['max_drawdown_pct'] * 0.3
        
        trend_bonus = 10 if trend == 'up' else (-10 if trend == 'down' else 0)
        ma_score += trend_bonus
        rsi_score += trend_bonus
        
        final_score = max(ma_score, rsi_score)
        best_strategy = 'MA均线策略' if ma_score >= rsi_score else 'RSI策略'
        
        print(f"\n   📊 评分详情:")
        print(f"      均线策略评分: {ma_score:.1f}")
        print(f"      RSI策略评分: {rsi_score:.1f}")
        print(f"      最终综合评分: {final_score:.1f}")
        print(f"      推荐策略: {best_strategy}")
    
    # 操作建议
    print("\n" + "="*70)
    print("     💡 操作建议")
    print("="*70)
    
    print(f"\n   📊 当前状态:")
    print(f"      趋势: {trend_status}")
    print(f"      RSI: {rsi_status}")
    print(f"      MACD: {macd_status}")
    
    print(f"\n   🛡️ 风险参数:")
    stop_loss = current_price * 0.92
    take_profit = current_price * 1.08
    print(f"      建议止损价: ¥{stop_loss:.2f} (下跌8%)")
    print(f"      建议止盈价: ¥{take_profit:.2f} (上涨8%)")
    
    print(f"\n   🎯 综合建议:")
    
    if ma_result and rsi_result:
        if final_score >= 80:
            print(f"      ⭐⭐⭐ 强烈关注，可考虑买入")
            print(f"      建议仓位: 15-20%")
        elif final_score >= 50:
            print(f"      ⭐⭐ 可关注，等待更好时机")
            print(f"      建议仓位: 5-10%")
        else:
            print(f"      ⭐ 暂不建议，继续观察")
            print(f"      建议仓位: 0%")
    
    print("\n   ⚠️ 风险提示:")
    print(f"      1. 以上分析仅供参考，不构成投资建议")
    print(f"      2. 股市有风险，投资需谨慎")
    print(f"      3. 建议结合基本面分析综合判断")
    
    print("\n" + "="*70)
    print("✅ 分析完成！")
    print("="*70)

if __name__ == "__main__":
    # 天通股份 600330.SH
    analyze_stock("600330.SH", "天通股份")
