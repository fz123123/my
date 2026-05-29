# -*- coding: utf-8 -*-
"""
通达信数据导入与深度分析工具
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_fetcher import DataFetcher
from core.indicators import calculate_indicators, calculate_kdj
from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor, StrategyGridAdvanced
from backtest.engine import BacktestEngine
from config import config
from utils.stock_names import get_stock_name as get_stock_name_db


class StockAnalyzer:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.engine = BacktestEngine()
        
    def analyze_stock(self, df, symbol='UNKNOWN'):
        df = df.copy()
        df = calculate_indicators(df)
        df = calculate_kdj(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        analysis = {
            'symbol': symbol,
            'current_price': latest['close'],
            'price_change': latest['close'] - prev['close'],
            'price_change_pct': (latest['close'] - prev['close']) / prev['close'] * 100,
            'ma5': latest.get('ma5', np.nan),
            'ma20': latest.get('ma20', np.nan),
            'ma60': latest.get('ma60', np.nan),
            'rsi': latest.get('rsi', np.nan),
            'macd': latest.get('macd', np.nan),
            'macd_signal': latest.get('macd_signal', np.nan),
            'bb_position': latest.get('bb_position', np.nan),
            'kdj_k': latest.get('kdj_k', np.nan),
            'kdj_d': latest.get('kdj_d', np.nan),
            'kdj_j': latest.get('kdj_j', np.nan)
        }
        
        analysis['ma_status'] = self._analyze_ma(analysis)
        analysis['rsi_status'] = self._analyze_rsi(analysis)
        analysis['macd_status'] = self._analyze_macd(analysis)
        analysis['bb_status'] = self._analyze_bollinger(analysis)
        analysis['kdj_status'] = self._analyze_kdj(analysis)
        
        return analysis, df
    
    def _analyze_ma(self, data):
        if np.isnan(data['ma5']) or np.isnan(data['ma20']):
            return '数据不足'
        if data['current_price'] > data['ma5'] > data['ma20']:
            return '多头排列'
        elif data['current_price'] < data['ma5'] < data['ma20']:
            return '空头排列'
        elif data['ma5'] > data['ma20']:
            return '短期强势'
        else:
            return '短期弱势'
    
    def _analyze_rsi(self, data):
        if np.isnan(data['rsi']):
            return '数据不足'
        if data['rsi'] < 30:
            return '超卖区'
        elif data['rsi'] > 70:
            return '超买区'
        elif data['rsi'] < 50:
            return '偏弱'
        else:
            return '偏强'
    
    def _analyze_macd(self, data):
        if np.isnan(data['macd']) or np.isnan(data['macd_signal']):
            return '数据不足'
        if data['macd'] > data['macd_signal']:
            return 'MACD金叉'
        else:
            return 'MACD死叉'
    
    def _analyze_bollinger(self, data):
        if np.isnan(data['bb_position']):
            return '数据不足'
        if data['bb_position'] < 0.2:
            return '接近下轨'
        elif data['bb_position'] > 0.8:
            return '接近上轨'
        else:
            return '区间中部'
    
    def _analyze_kdj(self, data):
        if np.isnan(data['kdj_k']) or np.isnan(data['kdj_d']):
            return '数据不足'
        if data['kdj_j'] < 20:
            return 'KDJ超卖'
        elif data['kdj_j'] > 80:
            return 'KDJ超买'
        elif data['kdj_k'] > data['kdj_d']:
            return 'KDJ金叉'
        else:
            return 'KDJ死叉'
    
    def generate_signal(self, analysis):
        signals = []
        score = 0
        
        if analysis['ma_status'] in ['多头排列', '短期强势']:
            signals.append('均线看多')
            score += 2
        elif analysis['ma_status'] in ['空头排列', '短期弱势']:
            signals.append('均线看空')
            score -= 2
        
        if analysis['rsi_status'] == '超卖区':
            signals.append('RSI超卖')
            score += 1
        elif analysis['rsi_status'] == '超买区':
            signals.append('RSI超买')
            score -= 1
        
        if analysis['macd_status'] == 'MACD金叉':
            signals.append('MACD金叉')
            score += 2
        elif analysis['macd_status'] == 'MACD死叉':
            signals.append('MACD死叉')
            score -= 2
        
        if analysis['bb_status'] == '接近下轨':
            signals.append('布林带下轨支撑')
            score += 1
        elif analysis['bb_status'] == '接近上轨':
            signals.append('布林带上轨压力')
            score -= 1
        
        if analysis['kdj_status'] == 'KDJ超卖':
            signals.append('KDJ超卖')
            score += 1
        elif analysis['kdj_status'] == 'KDJ超买':
            signals.append('KDJ超买')
            score -= 1
        
        if score >= 5:
            recommendation = '强烈买入'
        elif score >= 3:
            recommendation = '买入'
        elif score >= 1:
            recommendation = '谨慎买入'
        elif score <= -5:
            recommendation = '强烈卖出'
        elif score <= -3:
            recommendation = '卖出'
        elif score <= -1:
            recommendation = '谨慎卖出'
        else:
            recommendation = '观望'
        
        return {'signals': signals, 'score': score, 'recommendation': recommendation}
    
    def backtest_strategies(self, df):
        strategies = [
            ('均线交叉', StrategyMaCross()),
            ('RSI策略', StrategyRsi()),
            ('布林带', StrategyBollinger()),
            ('多因子', StrategyMultiFactor()),
            ('网格交易', StrategyGridAdvanced())
        ]
        
        results = []
        for name, strategy in strategies:
            try:
                signals = strategy.generate_signals(df)
                result = self.engine.run_backtest(df, signals)
                if result:
                    results.append({
                        'strategy': name,
                        'total_return_pct': result['total_return_pct'],
                        'max_drawdown_pct': result['max_drawdown_pct'],
                        'sharpe_ratio': result['sharpe_ratio'],
                        'total_trades': result['total_trades'],
                        'win_rate_pct': result['win_rate_pct']
                    })
            except Exception as e:
                pass
        
        return pd.DataFrame(results)


def get_stock_name(symbol):
    if '.' in symbol:
        code = symbol.split('.')[0]
    else:
        code = symbol
    name = get_stock_name_db(code)
    if name == code:
        return symbol
    return name


def analyze_today_data():
    analyzer = StockAnalyzer()
    symbols = config['watchlist'][:5] if config['watchlist'] else ['000001.SZ']
    
    print(f"\n{'='*80}")
    print(f"  股票深度分析报告 - {datetime.now().strftime('%Y年%m月%d日')}")
    print(f"{'='*80}")
    
    for symbol in symbols:
        df = analyzer.fetcher.get_stock_data(symbol)
        if df is None or len(df) < 60:
            continue
        
        stock_name = get_stock_name(symbol)
        analysis, df = analyzer.analyze_stock(df, symbol)
        signal = analyzer.generate_signal(analysis)
        backtest_results = analyzer.backtest_strategies(df)
        
        print(f"\n{'='*60}")
        print(f"  {stock_name} ({symbol})")
        print(f"{'='*60}")
        
        print(f"\n【基本信息】")
        print(f"收盘价: {analysis['current_price']:.2f}")
        print(f"涨跌幅: {analysis['price_change_pct']:+.2f}%")
        
        print(f"\n【技术指标】")
        print(f"MA5: {analysis['ma5']:.2f} | MA20: {analysis['ma20']:.2f} | MA60: {analysis['ma60']:.2f}")
        print(f"RSI: {analysis['rsi']:.1f} | MACD: {analysis['macd']:.4f}")
        print(f"KDJ: K={analysis['kdj_k']:.1f}, D={analysis['kdj_d']:.1f}, J={analysis['kdj_j']:.1f}")
        
        print(f"\n【指标状态】")
        print(f"均线: {analysis['ma_status']} | RSI: {analysis['rsi_status']}")
        print(f"MACD: {analysis['macd_status']} | 布林带: {analysis['bb_status']} | KDJ: {analysis['kdj_status']}")
        
        print(f"\n【综合评分】: {signal['score']}")
        print(f"【信号列表】: {', '.join(signal['signals'])}")
        print(f"【投资建议】: {signal['recommendation']}")
        
        if not backtest_results.empty:
            print(f"\n【回测对比】")
            print(backtest_results[['strategy', 'total_return_pct', 'sharpe_ratio', 'win_rate_pct']].to_string(index=False))
        
        print(f"\n【明日操作建议】")
        if signal['recommendation'] in ['强烈买入', '买入']:
            print("建议: 适当加仓或买入 | 仓位: 50%-70%")
        elif signal['recommendation'] == '谨慎买入':
            print("建议: 少量试探性买入 | 仓位: 20%-30%")
        elif signal['recommendation'] in ['强烈卖出', '卖出']:
            print("建议: 减仓或清仓 | 仓位: 0%-20%")
        elif signal['recommendation'] == '谨慎卖出':
            print("建议: 适当减仓 | 仓位: 30%-50%")
        else:
            print("建议: 观望等待 | 仓位: 保持不变")


if __name__ == "__main__":
    analyze_today_data()