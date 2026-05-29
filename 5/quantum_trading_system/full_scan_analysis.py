# -*- coding: utf-8 -*-
"""
全盘扫描通达信盘后数据对比分析工具
"""

import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_fetcher import DataFetcher
from core.indicators import calculate_indicators, calculate_kdj
from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor
from backtest.engine import BacktestEngine
from utils.stock_names import get_stock_name as get_stock_name_db

class FullScanAnalyzer:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.engine = BacktestEngine()
    
    def get_stock_name(self, symbol):
        if '.' in symbol:
            code = symbol.split('.')[0]
        else:
            code = symbol
        name = get_stock_name_db(code)
        if name == code:
            return symbol
        return name
    
    def analyze_stock(self, df, symbol):
        if len(df) < 60:
            return None
        
        df = df.copy()
        df = calculate_indicators(df)
        df = calculate_kdj(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        analysis = {
            'symbol': symbol,
            'name': self.get_stock_name(symbol),
            'current_price': latest['close'],
            'price_change': latest['close'] - prev['close'],
            'price_change_pct': (latest['close'] - prev['close']) / prev['close'] * 100,
            'volume': latest['volume'],
            'ma5': latest.get('ma5', 0),
            'ma20': latest.get('ma20', 0),
            'ma60': latest.get('ma60', 0),
            'rsi': latest.get('rsi', 0),
            'macd': latest.get('macd', 0),
            'macd_signal': latest.get('macd_signal', 0),
            'bb_position': latest.get('bb_position', 0),
            'kdj_k': latest.get('kdj_k', 0),
            'kdj_d': latest.get('kdj_d', 0),
            'kdj_j': latest.get('kdj_j', 0)
        }
        
        analysis['ma_status'] = self._analyze_ma(analysis)
        analysis['rsi_status'] = self._analyze_rsi(analysis)
        analysis['macd_status'] = self._analyze_macd(analysis)
        analysis['bb_status'] = self._analyze_bollinger(analysis)
        analysis['kdj_status'] = self._analyze_kdj(analysis)
        
        analysis['score'] = self._calculate_score(analysis)
        analysis['recommendation'] = self._get_recommendation(analysis['score'])
        
        return analysis
    
    def _analyze_ma(self, data):
        if data['ma5'] == 0 or data['ma20'] == 0:
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
        if data['rsi'] == 0:
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
        if data['macd'] == 0 or data['macd_signal'] == 0:
            return '数据不足'
        if data['macd'] > data['macd_signal']:
            return 'MACD金叉'
        else:
            return 'MACD死叉'
    
    def _analyze_bollinger(self, data):
        if data['bb_position'] == 0:
            return '数据不足'
        if data['bb_position'] < 0.2:
            return '接近下轨'
        elif data['bb_position'] > 0.8:
            return '接近上轨'
        else:
            return '区间中部'
    
    def _analyze_kdj(self, data):
        if data['kdj_k'] == 0 or data['kdj_d'] == 0:
            return '数据不足'
        if data['kdj_j'] < 20:
            return 'KDJ超卖'
        elif data['kdj_j'] > 80:
            return 'KDJ超买'
        elif data['kdj_k'] > data['kdj_d']:
            return 'KDJ金叉'
        else:
            return 'KDJ死叉'
    
    def _calculate_score(self, analysis):
        score = 0
        
        if analysis['ma_status'] in ['多头排列', '短期强势']:
            score += 2
        elif analysis['ma_status'] in ['空头排列', '短期弱势']:
            score -= 2
        
        if analysis['rsi_status'] == '超卖区':
            score += 1
        elif analysis['rsi_status'] == '超买区':
            score -= 1
        
        if analysis['macd_status'] == 'MACD金叉':
            score += 2
        elif analysis['macd_status'] == 'MACD死叉':
            score -= 2
        
        if analysis['bb_status'] == '接近下轨':
            score += 1
        elif analysis['bb_status'] == '接近上轨':
            score -= 1
        
        if analysis['kdj_status'] == 'KDJ超卖':
            score += 1
        elif analysis['kdj_status'] == 'KDJ超买':
            score -= 1
        
        return score
    
    def _get_recommendation(self, score):
        if score >= 5:
            return '强烈买入'
        elif score >= 3:
            return '买入'
        elif score >= 1:
            return '谨慎买入'
        elif score <= -5:
            return '强烈卖出'
        elif score <= -3:
            return '卖出'
        elif score <= -1:
            return '谨慎卖出'
        else:
            return '观望'
    
    def load_stocks_from_monitor(self):
        monitor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monitor')
        stocks_file = os.path.join(monitor_dir, 'stocks.txt')
        
        if not os.path.exists(stocks_file):
            print(f"监控文件不存在: {stocks_file}")
            return []
        
        with open(stocks_file, 'r', encoding='utf-8') as f:
            stocks = [line.strip() for line in f if line.strip()]
        
        return stocks
    
    def run_full_scan(self):
        print(f"\n{'='*80}")
        print(f"  📊 全盘扫描通达信盘后数据对比分析报告")
        print(f"     {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print(f"{'='*80}")
        
        stocks = self.load_stocks_from_monitor()
        if not stocks:
            print("\n❌ 未找到监控股票列表")
            return
        
        print(f"\n📂 发现 {len(stocks)} 只股票，开始分析...")
        
        results = []
        success_count = 0
        fail_count = 0
        
        for i, symbol in enumerate(stocks, 1):
            print(f"\r正在分析: {i}/{len(stocks)} {symbol}...", end='', flush=True)
            
            try:
                df = self.fetcher.get_stock_data(symbol)
                if df is None or len(df) < 60:
                    fail_count += 1
                    continue
                
                analysis = self.analyze_stock(df, symbol)
                if analysis:
                    results.append(analysis)
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                continue
        
        print(f"\r{' '*80}\r")
        print(f"\n✅ 分析完成: 成功 {success_count} 只, 失败 {fail_count} 只")
        
        if not results:
            print("\n❌ 没有有效分析结果")
            return
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('score', ascending=False)
        
        self.generate_report(results_df)
        self.save_report(results_df)
        
        return results_df
    
    def generate_report(self, df):
        print(f"\n{'='*80}")
        print("  🥇 强烈买入信号 (评分 >= 5)")
        print(f"{'='*80}")
        
        buy_signals = df[df['recommendation'] == '强烈买入']
        if not buy_signals.empty:
            for _, row in buy_signals.iterrows():
                print(f"\n📈 {row['name']} ({row['symbol']})")
                print(f"   收盘价: {row['current_price']:.2f} | 涨跌幅: {row['price_change_pct']:+.2f}%")
                print(f"   评分: {row['score']} | 均线: {row['ma_status']} | RSI: {row['rsi']:.1f}")
                print(f"   MACD: {row['macd_status']} | KDJ: {row['kdj_status']}")
        else:
            print("   暂无强烈买入信号")
        
        print(f"\n{'='*80}")
        print("  🔔 买入信号 (评分 3-4)")
        print(f"{'='*80}")
        
        buy_careful = df[(df['recommendation'] == '买入') | (df['recommendation'] == '谨慎买入')]
        if not buy_careful.empty:
            for _, row in buy_careful.iterrows():
                print(f"\n📊 {row['name']} ({row['symbol']})")
                print(f"   收盘价: {row['current_price']:.2f} | 涨跌幅: {row['price_change_pct']:+.2f}%")
                print(f"   评分: {row['score']} | 建议: {row['recommendation']}")
        else:
            print("   暂无买入信号")
        
        print(f"\n{'='*80}")
        print("  ⚠️ 卖出信号")
        print(f"{'='*80}")
        
        sell_signals = df[df['recommendation'].str.contains('卖出')]
        if not sell_signals.empty:
            for _, row in sell_signals.iterrows():
                print(f"\n📉 {row['name']} ({row['symbol']})")
                print(f"   收盘价: {row['current_price']:.2f} | 涨跌幅: {row['price_change_pct']:+.2f}%")
                print(f"   评分: {row['score']} | 建议: {row['recommendation']}")
        else:
            print("   暂无卖出信号")
        
        print(f"\n{'='*80}")
        print("  📊 综合统计")
        print(f"{'='*80}")
        
        rec_counts = df['recommendation'].value_counts()
        print(f"\n信号分布:")
        for rec, count in rec_counts.items():
            print(f"   {rec}: {count}只 ({count/len(df)*100:.1f}%)")
        
        avg_score = df['score'].mean()
        print(f"\n平均评分: {avg_score:.2f}")
        print(f"最高评分: {df['score'].max()} | 最低评分: {df['score'].min()}")
        
        bullish_count = len(df[df['ma_status'].isin(['多头排列', '短期强势'])])
        bearish_count = len(df[df['ma_status'].isin(['空头排列', '短期弱势'])])
        print(f"\n均线状态: 多头 {bullish_count}只 | 空头 {bearish_count}只")
        
        overbought_count = len(df[df['rsi'] > 70])
        oversold_count = len(df[df['rsi'] < 30])
        print(f"RSI状态: 超买 {overbought_count}只 | 超卖 {oversold_count}只")
    
    def save_report(self, df):
        report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_name = f"全盘扫描分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        report_path = os.path.join(report_dir, report_name)
        
        df.to_excel(report_path, index=False, encoding='utf-8')
        print(f"\n📝 报告已保存: {report_path}")
        
        md_report_name = f"全盘扫描分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        md_report_path = os.path.join(report_dir, md_report_name)
        
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 全盘扫描通达信盘后数据对比分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**分析股票数量**: {len(df)}\n\n")
            
            f.write("## 🥇 强烈买入信号\n\n")
            buy_signals = df[df['recommendation'] == '强烈买入']
            if not buy_signals.empty:
                for _, row in buy_signals.iterrows():
                    f.write(f"- **{row['name']}** ({row['symbol']}): {row['current_price']:.2f}元, 评分:{row['score']}\n")
            else:
                f.write("暂无强烈买入信号\n")
            
            f.write("\n## 🔔 买入信号\n\n")
            buy_careful = df[(df['recommendation'] == '买入') | (df['recommendation'] == '谨慎买入')]
            if not buy_careful.empty:
                for _, row in buy_careful.iterrows():
                    f.write(f"- **{row['name']}** ({row['symbol']}): {row['current_price']:.2f}元, {row['recommendation']}\n")
            else:
                f.write("暂无买入信号\n")
            
            f.write("\n## ⚠️ 卖出信号\n\n")
            sell_signals = df[df['recommendation'].str.contains('卖出')]
            if not sell_signals.empty:
                for _, row in sell_signals.iterrows():
                    f.write(f"- **{row['name']}** ({row['symbol']}): {row['current_price']:.2f}元, {row['recommendation']}\n")
            else:
                f.write("暂无卖出信号\n")
        
        print(f"📝 报告已保存: {md_report_path}")

def main():
    analyzer = FullScanAnalyzer()
    analyzer.run_full_scan()

if __name__ == "__main__":
    main()