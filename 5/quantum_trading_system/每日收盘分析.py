#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日收盘数据分析与策略生成系统
功能：导入今日收盘数据 → 回测分析 → 生成明日策略 → 给出持仓建议
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross, StrategyRsi
from backtest.enhanced_engine import EnhancedBacktestEngine
from datetime import datetime, timedelta
import pandas as pd

class DailyAnalysis:
    """每日分析系统"""
    
    def __init__(self):
        self.data_engine = DataEngine()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.results = []
        
    def get_watchlist(self):
        """获取自选股列表"""
        try:
            with open('monitor/stocks.txt', 'r', encoding='utf-8') as f:
                stocks = [line.strip() for line in f 
                         if line.strip() and not line.startswith('#')]
            return stocks[:30]  # 分析前30只
        except:
            return ['000001.SZ', '600000.SH', '000002.SZ']
    
    def analyze_stock(self, symbol):
        """分析单只股票"""
        try:
            # 获取数据
            df = self.data_engine.get_stock_data(symbol)
            if df is None or len(df) < 60:
                return None
            
            # 计算指标
            df = calculate_indicators(df)
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 基本信息
            info = {
                'symbol': symbol,
                'close': latest['close'],
                'change_pct': ((latest['close'] - prev['close']) / prev['close']) * 100,
                'volume': latest.get('volume', 0),
                'ma5': latest.get('ma5', 0),
                'ma20': latest.get('ma20', 0),
                'ma60': latest.get('ma60', 0),
                'rsi': latest.get('rsi', 50),
                'macd': latest.get('macd', 0),
                'macd_signal': latest.get('macd_signal', 0),
                'atr': latest.get('atr', 0),
            }
            
            # 趋势判断
            if info['ma5'] > info['ma20'] > info['ma60']:
                info['trend'] = 'up'
                info['trend_score'] = 10
            elif info['ma5'] > info['ma20']:
                info['trend'] = 'weak_up'
                info['trend_score'] = 5
            elif info['ma5'] < info['ma20'] < info['ma60']:
                info['trend'] = 'down'
                info['trend_score'] = -10
            else:
                info['trend'] = 'sideways'
                info['trend_score'] = 0
            
            # RSI信号
            if info['rsi'] < 35:
                info['rsi_signal'] = 'oversold'
                info['rsi_score'] = 10
            elif info['rsi'] > 70:
                info['rsi_signal'] = 'overbought'
                info['rsi_score'] = -10
            else:
                info['rsi_signal'] = 'neutral'
                info['rsi_score'] = 0
            
            # MACD信号
            info['macd_signal'] = 'golden' if info['macd'] > info['macd_signal'] else 'death'
            info['macd_score'] = 5 if info['macd'] > info['macd_signal'] else -5
            
            # 回测均线策略
            ma_strategy = StrategyMaCross(5, 20)
            ma_signals = ma_strategy.generate_signals(df)
            ma_engine = EnhancedBacktestEngine(100000)
            ma_result = ma_engine.run_backtest(df, ma_signals)
            
            if ma_result:
                info['ma_return'] = ma_result.get('total_return_pct', 0)
                info['ma_sharpe'] = ma_result.get('sharpe_ratio', 0)
                info['ma_win_rate'] = ma_result.get('win_rate_pct', 0)
                info['ma_max_dd'] = ma_result.get('max_drawdown_pct', 100)
                info['ma_latest_signal'] = ma_signals.iloc[-1]['signal']
            else:
                return None
            
            # 回测RSI策略
            rsi_strategy = StrategyRsi(35, 80)
            rsi_signals = rsi_strategy.generate_signals(df)
            rsi_engine = EnhancedBacktestEngine(100000)
            rsi_result = rsi_engine.run_backtest(df, rsi_signals)
            
            if rsi_result:
                info['rsi_return'] = rsi_result.get('total_return_pct', 0)
                info['rsi_sharpe'] = rsi_result.get('sharpe_ratio', 0)
                info['rsi_win_rate'] = rsi_result.get('win_rate_pct', 0)
                info['rsi_max_dd'] = rsi_result.get('max_drawdown_pct', 100)
                info['rsi_latest_signal'] = rsi_signals.iloc[-1]['signal']
            else:
                return None
            
            # 综合评分
            info['ma_strategy_score'] = (info['ma_sharpe'] * 30 + 
                                       info['ma_return'] * 0.5 + 
                                       info['ma_win_rate'] * 0.3 -
                                       info['ma_max_dd'] * 0.3 +
                                       info['trend_score'] +
                                       info['rsi_score'] +
                                       info['macd_score'])
            
            info['rsi_strategy_score'] = (info['rsi_sharpe'] * 30 +
                                        info['rsi_return'] * 0.5 +
                                        info['rsi_win_rate'] * 0.3 -
                                        info['rsi_max_dd'] * 0.3 +
                                        info['trend_score'] +
                                        info['rsi_score'] +
                                        info['macd_score'])
            
            info['final_score'] = max(info['ma_strategy_score'], info['rsi_strategy_score'])
            info['best_strategy'] = 'MA' if info['ma_strategy_score'] >= info['rsi_strategy_score'] else 'RSI'
            info['latest_signal'] = info['ma_latest_signal'] if info['best_strategy'] == 'MA' else info['rsi_latest_signal']
            
            return info
            
        except Exception as e:
            return None
    
    def run_analysis(self):
        """运行完整分析"""
        print("="*70)
        print(f"     📊 每日收盘数据分析系统")
        print(f"     分析日期: {self.today}")
        print(f"     明日日期: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}")
        print("="*70)
        
        stocks = self.get_watchlist()
        print(f"\n📊 开始分析 {len(stocks)} 只股票...")
        
        results = []
        for i, symbol in enumerate(stocks, 1):
            print(f"\r   进度: {i}/{len(stocks)} ({i*100//len(stocks)}%) - {symbol}", end='', flush=True)
            
            result = self.analyze_stock(symbol)
            if result:
                results.append(result)
        
        print(f"\n\n✅ 分析完成！有效数据: {len(results)} 只")
        self.results = results
        return results
    
    def generate_strategy(self):
        """生成明日策略"""
        if not self.results:
            return None
        
        # 筛选优质标的
        quality_stocks = [r for r in self.results 
                         if r['final_score'] > 50 and 
                         r['trend'] in ['up', 'weak_up'] and
                         r['rsi_signal'] != 'overbought' and
                         r['ma_max_dd'] < 30]
        
        # 按综合评分排序
        sorted_stocks = sorted(quality_stocks, key=lambda x: x['final_score'], reverse=True)
        
        return sorted_stocks[:10]
    
    def generate_report(self):
        """生成完整报告"""
        print("\n" + "="*70)
        print("     📈 今日收盘数据分析报告")
        print("="*70)
        
        # 市场概况
        print("\n📊 市场概况:")
        total = len(self.results)
        up_count = sum(1 for r in self.results if r['change_pct'] > 0)
        down_count = sum(1 for r in self.results if r['change_pct'] < 0)
        
        print(f"   分析股票数: {total} 只")
        print(f"   上涨: {up_count} 只 ({up_count*100//total}%)")
        print(f"   下跌: {down_count} 只 ({down_count*100//total}%)")
        
        # 趋势分布
        trend_up = sum(1 for r in self.results if r['trend'] in ['up', 'weak_up'])
        trend_down = sum(1 for r in self.results if r['trend'] == 'down')
        trend_sideways = sum(1 for r in self.results if r['trend'] == 'sideways')
        
        print(f"\n   趋势向上: {trend_up} 只 ({trend_up*100//total}%)")
        print(f"   趋势向下: {trend_down} 只 ({trend_down*100//total}%)")
        print(f"   震荡整理: {trend_sideways} 只 ({trend_sideways*100//total}%)")
        
        # 综合判断
        if trend_up >= trend_down * 2:
            print(f"\n   🟢 市场情绪: 偏多")
        elif trend_down >= trend_up * 2:
            print(f"\n   🔴 市场情绪: 偏空")
        else:
            print(f"\n   🟡 市场情绪: 中性")
        
        # 策略建议
        print("\n" + "="*70)
        print("     🏆 明日推荐标的")
        print("="*70)
        
        top_stocks = self.generate_strategy()
        
        if top_stocks:
            print(f"\n   {'排名':<4} {'股票代码':<12} {'价格':>10} {'涨幅':>8} {'趋势':<10} {'评分':>8} {'信号':<8}")
            print("   " + "-"*70)
            
            for i, stock in enumerate(top_stocks[:5], 1):
                change_color = "🟢" if stock['change_pct'] > 0 else "🔴"
                signal = "买入" if stock['latest_signal'] == 1 else ("卖出" if stock['latest_signal'] == -1 else "观望")
                signal_color = "🟢" if stock['latest_signal'] == 1 else ("🔴" if stock['latest_signal'] == -1 else "🟡")
                
                print(f"   {i:<4} {stock['symbol']:<12} {stock['close']:>10.2f} {change_color}{stock['change_pct']:>+7.2f}% "
                      f"{'↑' if stock['trend'] in ['up', 'weak_up'] else ('↓' if stock['trend'] == 'down' else '→'):<10} "
                      f"{stock['final_score']:>8.1f} {signal_color}{signal:<8}")
            
            # 持仓建议
            print("\n" + "="*70)
            print("     💰 明日持仓建议")
            print("="*70)
            
            print(f"\n   📊 推荐标的列表:")
            for i, stock in enumerate(top_stocks[:3], 1):
                stop_loss = stock['close'] * 0.92
                take_profit = stock['close'] * 1.08
                weight = min(25 - (i-1)*5, 15)
                
                print(f"\n   🥇 第{i}位: {stock['symbol']}")
                print(f"      当前价: ¥{stock['close']:.2f}")
                print(f"      综合评分: {stock['final_score']:.1f}")
                print(f"      推荐策略: {stock['best_strategy']}")
                print(f"      建议仓位: {weight}%")
                print(f"      止损价: ¥{stop_loss:.2f}")
                print(f"      止盈价: ¥{take_profit:.2f}")
            
            # 总仓位建议
            total_weight = sum(min(25 - i*5, 15) for i in range(min(3, len(top_stocks))))
            print(f"\n   📊 总仓位建议:")
            print(f"      激进策略: {min(total_weight + 15, 50)}%")
            print(f"      稳健策略: {total_weight}%")
            print(f"      保守策略: {max(total_weight - 10, 15)}%")
            
        else:
            print("\n   ❌ 未找到符合条件的标的")
            print("   建议: 保持观望，等待更好时机")
        
        # 风险提示
        print("\n" + "="*70)
        print("     ⚠️ 风险提示")
        print("="*70)
        print("\n   1. 以上分析仅供参考，不构成投资建议")
        print("   2. 股市有风险，投资需谨慎")
        print("   3. 建议结合基本面分析综合判断")
        print("   4. 严格控制仓位和止损")
        
        print("\n" + "="*70)
        print("✅ 分析报告生成完成！")
        print("="*70)
        
        return top_stocks

def main():
    """主函数"""
    analyzer = DailyAnalysis()
    analyzer.run_analysis()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
