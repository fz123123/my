#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞价后智能选股系统
功能：扫描全部股票，回测对比，选出今日最佳标的
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
    """股票扫描器"""
    
    def __init__(self):
        self.data_engine = DataEngine()
        self.results = []
        self.scanned_count = 0
        self.failed_count = 0
    
    def get_watchlist(self):
        """获取自选股列表"""
        try:
            with open('monitor/stocks.txt', 'r', encoding='utf-8') as f:
                stocks = [line.strip() for line in f 
                         if line.strip() and not line.startswith('#')]
            return stocks
        except:
            print("   ⚠️ 无法读取自选股列表，使用默认列表")
            return ['000001.SZ', '600000.SH', '600519.SH']
    
    def scan_stock(self, symbol):
        """扫描单只股票"""
        try:
            # 获取数据
            df = self.data_engine.get_stock_data(symbol)
            if df is None or len(df) < 60:
                return None
            
            # 计算指标
            df = calculate_indicators(df)
            
            latest = df.iloc[-1]
            prev = df.iloc[-1]
            
            # 基本信息
            info = {
                'symbol': symbol,
                'close': latest['close'],
                'change_pct': ((latest['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close']) * 100,
                'volume': latest.get('volume', 0),
                'ma5': latest.get('ma5', 0),
                'ma20': latest.get('ma20', 0),
                'rsi': latest.get('rsi', 50),
                'atr': latest.get('atr', 0),
            }
            
            # 判断趋势
            if info['ma5'] > info['ma20']:
                info['trend'] = 'up'
            elif info['ma5'] < info['ma20']:
                info['trend'] = 'down'
            else:
                info['trend'] = 'sideways'
            
            # RSI信号
            if info['rsi'] < 35:
                info['rsi_signal'] = 'oversold'
            elif info['rsi'] > 70:
                info['rsi_signal'] = 'overbought'
            else:
                info['rsi_signal'] = 'neutral'
            
            # 回测均线策略
            ma_strategy = StrategyMaCross(short_period=5, long_period=20)
            ma_signals = ma_strategy.generate_signals(df)
            
            ma_engine = EnhancedBacktestEngine(initial_capital=100000)
            ma_result = ma_engine.run_backtest(df, ma_signals)
            
            if ma_result:
                info['ma_return'] = ma_result['total_return_pct']
                info['ma_sharpe'] = ma_result['sharpe_ratio']
                info['ma_win_rate'] = ma_result['win_rate_pct']
                info['ma_max_dd'] = ma_result['max_drawdown_pct']
            else:
                return None
            
            # 回测RSI策略
            rsi_strategy = StrategyRsi(oversold=35, overbought=80)
            rsi_signals = rsi_strategy.generate_signals(df)
            
            rsi_engine = EnhancedBacktestEngine(initial_capital=100000)
            rsi_result = rsi_engine.run_backtest(df, rsi_signals)
            
            if rsi_result:
                info['rsi_return'] = rsi_result['total_return_pct']
                info['rsi_sharpe'] = rsi_result['sharpe_ratio']
                info['rsi_win_rate'] = rsi_result['win_rate_pct']
                info['rsi_max_dd'] = rsi_result['max_drawdown_pct']
            else:
                return None
            
            # 计算综合评分
            info['ma_score'] = (info['ma_sharpe'] * 30 + 
                              info['ma_return'] * 0.5 + 
                              info['ma_win_rate'] * 0.3 -
                              info['ma_max_dd'] * 0.3)
            
            info['rsi_score'] = (info['rsi_sharpe'] * 30 + 
                               info['rsi_return'] * 0.5 + 
                               info['rsi_win_rate'] * 0.3 -
                               info['rsi_max_dd'] * 0.3)
            
            # 趋势加成
            trend_bonus = 10 if info['trend'] == 'up' else (-10 if info['trend'] == 'down' else 0)
            info['ma_score'] += trend_bonus
            info['rsi_score'] += trend_bonus
            
            # RSI加成
            if info['rsi_signal'] == 'oversold' and info['trend'] == 'up':
                info['rsi_score'] += 15  # 超跌反弹加分
            
            # 最终评分（取两个策略中较好的）
            info['final_score'] = max(info['ma_score'], info['rsi_score'])
            info['best_strategy'] = 'MA' if info['ma_score'] >= info['rsi_score'] else 'RSI'
            
            return info
            
        except Exception as e:
            return None
    
    def scan_all(self, limit=None):
        """扫描所有股票"""
        print("\n" + "="*70)
        print("     竞价后智能选股系统")
        print("     扫描全部股票，回测对比，选出最佳标的")
        print("="*70)
        
        stocks = self.get_watchlist()
        total = len(stocks)
        
        if limit:
            stocks = stocks[:limit]
            total = limit
        
        print(f"\n📊 开始扫描 {total} 只股票...")
        print(f"   开始时间: {datetime.now().strftime('%H:%M:%S')}")
        
        results = []
        
        for i, symbol in enumerate(stocks, 1):
            print(f"\r   扫描进度: {i}/{total} ({i*100//total}%) - {symbol}", end='', flush=True)
            
            result = self.scan_stock(symbol)
            
            if result:
                results.append(result)
                self.scanned_count += 1
            else:
                self.failed_count += 1
            
            # 每50只股票显示进度
            if i % 50 == 0:
                print(f"\n   ✅ 已扫描: {i}/{total} - 有效: {len(results)}")
            
            # 避免请求过快
            time.sleep(0.1)
        
        print(f"\n\n   ✅ 扫描完成！")
        print(f"   总计扫描: {total} 只")
        print(f"   有效数据: {len(results)} 只")
        print(f"   失败数量: {self.failed_count} 只")
        
        self.results = results
        return results

class StockSelector:
    """股票选择器"""
    
    def __init__(self, results):
        self.results = results
    
    def filter_quality_stocks(self):
        """筛选优质股票"""
        quality = []
        
        for r in self.results:
            # 基本筛选条件
            if r['final_score'] < 0:
                continue
            if r['close'] < 1 or r['close'] > 1000:  # 过滤价格异常
                continue
            if r['trend'] != 'up':  # 只选趋势向上的
                continue
            if r['ma_max_dd'] > 30:  # 最大回撤不能太大
                continue
            
            quality.append(r)
        
        return quality
    
    def rank_stocks(self, stocks):
        """排名股票"""
        # 按多个指标综合排名
        ranked = sorted(stocks, key=lambda x: (
            x['final_score'],           # 综合评分
            x['rsi_win_rate'],          # 胜率
            -x['rsi_max_dd'],           # 最大回撤（越小越好）
            x['rsi_sharpe'],            # 夏普比率
            x['change_pct']             # 涨幅
        ), reverse=True)
        
        return ranked
    
    def select_top_stocks(self, n=5):
        """选出TOP N股票"""
        quality = self.filter_quality_stocks()
        ranked = self.rank_stocks(quality)
        return ranked[:n]
    
    def generate_report(self, top_stocks):
        """生成选股报告"""
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
            print(f"      RSI: {stock['rsi']:.1f} ({stock['rsi_signal']})")
            
            print(f"\n   📈 均线策略表现:")
            print(f"      收益率: {stock['ma_return']:+.2f}%")
            print(f"      夏普比率: {stock['ma_sharpe']:.2f}")
            print(f"      胜率: {stock['ma_win_rate']:.1f}%")
            print(f"      最大回撤: {stock['ma_max_dd']:.1f}%")
            
            print(f"\n   📉 RSI策略表现:")
            print(f"      收益率: {stock['rsi_return']:+.2f}%")
            print(f"      夏普比率: {stock['rsi_sharpe']:.2f}")
            print(f"      胜率: {stock['rsi_win_rate']:.1f}%")
            print(f"      最大回撤: {stock['rsi_max_dd']:.1f}%")
            
            print(f"\n   🎯 综合评分:")
            print(f"      最终评分: {stock['final_score']:.2f}")
            print(f"      推荐策略: {stock['best_strategy']}")
            
            # 操作建议
            print(f"\n   💡 操作建议:")
            
            if stock['best_strategy'] == 'MA':
                print(f"      策略: 均线交叉策略 MA(5/20)")
                print(f"      买入信号: MA5上穿MA20时买入")
                print(f"      卖出信号: MA5下穿MA20时卖出")
            else:
                print(f"      策略: RSI策略 RSI(35/80)")
                if stock['rsi_signal'] == 'oversold':
                    print(f"      当前信号: RSI超卖，可关注买入机会")
                elif stock['rsi_signal'] == 'overbought':
                    print(f"      当前信号: RSI超买，注意回调风险")
                else:
                    print(f"      当前信号: RSI适中，可关注")
            
            # 风险提示
            print(f"\n   ⚠️ 风险提示:")
            print(f"      最大回撤风险: {stock['ma_max_dd'] if stock['best_strategy']=='MA' else stock['rsi_max_dd']:.1f}%")
            if stock['ma_max_dd'] > 20 or stock['rsi_max_dd'] > 20:
                print(f"      ⚠️ 回撤较大，建议设置止损")
            
            # 止损建议
            stop_loss = stock['close'] * 0.92
            print(f"\n   🛡️ 止损建议:")
            print(f"      止损价: ¥{stop_loss:.2f} (下跌8%)")
        
        return top_stocks

def main():
    """主函数"""
    print("\n" + "="*70)
    print("     ⏰ 竞价后智能选股系统")
    print(f"     当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 检查是否在竞价时间后
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    
    if hour == 9 and minute < 30:
        print(f"\n⚠️ 当前时间: {hour}:{minute:02d}")
        print("   竞价还未结束（9:30）")
        print("   建议在9:30竞价结束后运行此脚本")
        
        response = input("\n   是否继续运行？(y/n): ")
        if response.lower() != 'y':
            print("\n   已取消")
            return
    
    # 开始扫描
    print("\n🔄 初始化扫描器...")
    scanner = StockScanner()
    
    print("\n💡 提示: 扫描全部自选股可能需要5-10分钟")
    print("   是否继续？(y/n): ")
    
    # 直接开始扫描
    print("\n   开始扫描...")
    
    # 扫描前100只股票作为演示
    results = scanner.scan_all(limit=100)
    
    if not results:
        print("\n❌ 扫描失败，未获取到有效数据")
        return
    
    # 选择最佳标的
    print("\n🔄 分析选股...")
    selector = StockSelector(results)
    
    # 选出TOP 5
    top_stocks = selector.select_top_stocks(n=5)
    
    # 生成报告
    selector.generate_report(top_stocks)
    
    # 综合建议
    print("\n\n" + "="*70)
    print("     💰 今日操作综合建议")
    print("="*70)
    
    if top_stocks:
        print(f"\n   🏆 今日首选标的: {top_stocks[0]['symbol']}")
        print(f"      评分: {top_stocks[0]['final_score']:.2f}")
        print(f"      推荐策略: {top_stocks[0]['best_strategy']}")
        print(f"      建议仓位: 20%")
        
        if len(top_stocks) > 1:
            print(f"\n   📈 次选标的: {top_stocks[1]['symbol']}")
            print(f"      评分: {top_stocks[1]['final_score']:.2f}")
            print(f"      建议仓位: 10%")
        
        print(f"\n   📊 总仓位建议:")
        print(f"      激进策略: 40-50%")
        print(f"      稳健策略: 30-40%")
        print(f"      保守策略: 20-30%")
    
    print("\n\n" + "="*70)
    print("✅ 选股完成！")
    print("="*70)
    print("\n💡 提示:")
    print("   1. 以上建议仅供参考，不构成投资建议")
    print("   2. 建议结合市场整体情况综合判断")
    print("   3. 严格控制仓位和止损")
    print("   4. 股市有风险，投资需谨慎")

if __name__ == "__main__":
    main()
