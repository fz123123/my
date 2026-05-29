#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞价后智能选股系统（立即运行版）
功能：扫描全部股票，回测对比，选出今日最佳标的
无需用户确认，直接运行
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross, StrategyRsi
from backtest.enhanced_engine import EnhancedBacktestEngine
import pandas as pd
from datetime import datetime
import time

class StockScanner:
    def __init__(self):
        self.data_engine = DataEngine()
        self.results = []
    
    def get_watchlist(self):
        try:
            with open('monitor/stocks.txt', 'r', encoding='utf-8') as f:
                stocks = [line.strip() for line in f 
                         if line.strip() and not line.startswith('#')]
            return stocks[:50]  # 快速扫描前50只
        except:
            return ['000001.SZ', '000002.SZ', '600000.SH']
    
    def scan_stock(self, symbol):
        try:
            df = self.data_engine.get_stock_data(symbol)
            if df is None or len(df) < 60:
                return None
            
            df = calculate_indicators(df)
            latest = df.iloc[-1]
            
            info = {
                'symbol': symbol,
                'close': latest['close'],
                'change_pct': ((latest['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close']) * 100,
                'ma5': latest.get('ma5', 0),
                'ma20': latest.get('ma20', 0),
                'rsi': latest.get('rsi', 50),
            }
            
            info['trend'] = 'up' if info['ma5'] > info['ma20'] else ('down' if info['ma5'] < info['ma20'] else 'sideways')
            info['rsi_signal'] = 'oversold' if info['rsi'] < 35 else ('overbought' if info['rsi'] > 70 else 'neutral')
            
            # 均线策略回测
            ma_strategy = StrategyMaCross(5, 20)
            ma_signals = ma_strategy.generate_signals(df)
            ma_engine = EnhancedBacktestEngine(100000)
            ma_result = ma_engine.run_backtest(df, ma_signals)
            
            if not ma_result:
                return None
            
            info['ma_return'] = ma_result['total_return_pct']
            info['ma_sharpe'] = ma_result['sharpe_ratio']
            info['ma_win_rate'] = ma_result['win_rate_pct']
            info['ma_max_dd'] = ma_result['max_drawdown_pct']
            
            # RSI策略回测
            rsi_strategy = StrategyRsi(35, 80)
            rsi_signals = rsi_strategy.generate_signals(df)
            rsi_engine = EnhancedBacktestEngine(100000)
            rsi_result = rsi_engine.run_backtest(df, rsi_signals)
            
            if not rsi_result:
                return None
            
            info['rsi_return'] = rsi_result['total_return_pct']
            info['rsi_sharpe'] = rsi_result['sharpe_ratio']
            info['rsi_win_rate'] = rsi_result['win_rate_pct']
            info['rsi_max_dd'] = rsi_result['max_drawdown_pct']
            
            # 评分
            info['ma_score'] = info['ma_sharpe'] * 30 + info['ma_return'] * 0.5 + info['ma_win_rate'] * 0.3 - info['ma_max_dd'] * 0.3
            info['rsi_score'] = info['rsi_sharpe'] * 30 + info['rsi_return'] * 0.5 + info['rsi_win_rate'] * 0.3 - info['rsi_max_dd'] * 0.3
            
            trend_bonus = 10 if info['trend'] == 'up' else (-10 if info['trend'] == 'down' else 0)
            info['ma_score'] += trend_bonus
            info['rsi_score'] += trend_bonus
            
            if info['rsi_signal'] == 'oversold' and info['trend'] == 'up':
                info['rsi_score'] += 15
            
            info['final_score'] = max(info['ma_score'], info['rsi_score'])
            info['best_strategy'] = 'MA' if info['ma_score'] >= info['rsi_score'] else 'RSI'
            
            return info
        except:
            return None
    
    def scan_all(self):
        stocks = self.get_watchlist()
        results = []
        
        print(f"\n📊 开始扫描 {len(stocks)} 只股票...")
        
        for i, symbol in enumerate(stocks, 1):
            print(f"\r   扫描进度: {i}/{len(stocks)} ({i*100//len(stocks)}%) - {symbol}", end='', flush=True)
            
            result = self.scan_stock(symbol)
            if result:
                results.append(result)
            
            time.sleep(0.05)
        
        print(f"\n\n   ✅ 扫描完成！有效数据: {len(results)} 只")
        self.results = results
        return results

def main():
    print("="*70)
    print(f"     ⏰ 竞价后智能选股系统")
    print(f"     当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    print("\n🔄 初始化扫描器...")
    scanner = StockScanner()
    
    print("\n🚀 开始扫描股票...")
    results = scanner.scan_all()
    
    if not results:
        print("\n❌ 扫描失败，未获取到有效数据")
        return
    
    # 筛选优质股票
    quality = [r for r in results 
               if r['final_score'] > 0 and r['trend'] == 'up' and r['ma_max_dd'] < 30]
    
    if not quality:
        print("\n❌ 未找到符合条件的股票")
        return
    
    # 排名
    ranked = sorted(quality, key=lambda x: x['final_score'], reverse=True)
    top_stocks = ranked[:5]
    
    # 输出结果
    print("\n" + "="*70)
    print("     🏆 今日最佳标的 TOP 5")
    print("="*70)
    
    for i, stock in enumerate(top_stocks, 1):
        print(f"\n   {'='*70}")
        print(f"   🥇 第{i}名: {stock['symbol']}")
        print(f"   {'='*70}")
        
        print(f"\n   📊 基本信息:")
        print(f"      当前价格: ¥{stock['close']:.2f}")
        print(f"      涨跌幅: {stock['change_pct']:+.2f}%")
        print(f"      趋势: {'↑ 向上' if stock['trend'] == 'up' else '↓ 向下'}")
        print(f"      RSI: {stock['rsi']:.1f}")
        
        print(f"\n   📈 均线策略: 收益率 {stock['ma_return']:+.2f}% | 夏普 {stock['ma_sharpe']:.2f} | 胜率 {stock['ma_win_rate']:.0f}%")
        print(f"   📉 RSI策略: 收益率 {stock['rsi_return']:+.2f}% | 夏普 {stock['rsi_sharpe']:.2f} | 胜率 {stock['rsi_win_rate']:.0f}%")
        
        print(f"\n   🎯 综合评分: {stock['final_score']:.1f} | 推荐策略: {stock['best_strategy']}")
        
        stop_loss = stock['close'] * 0.92
        print(f"   🛡️ 止损价: ¥{stop_loss:.2f}")
    
    print("\n\n" + "="*70)
    print("     💰 操作建议")
    print("="*70)
    
    if top_stocks:
        print(f"\n   🏆 首选标的: {top_stocks[0]['symbol']}")
        print(f"      建议仓位: 20%")
        
        if len(top_stocks) > 1:
            print(f"   📈 次选标的: {top_stocks[1]['symbol']}")
            print(f"      建议仓位: 10%")
        
        print(f"\n   📊 总仓位建议: 30-40%")
    
    print("\n" + "="*70)
    print("✅ 选股完成！")
    print("="*70)

if __name__ == "__main__":
    main()