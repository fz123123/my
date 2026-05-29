#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 明日策略选股系统
导入通达信今日收盘数据，回测分析，选出明日上车股票
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester

class TomorrowStrategy:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.backtester = Backtester()
        
    def get_today_data(self):
        """获取今日收盘数据"""
        print("\n📡 正在获取通达信今日收盘数据...")
        
        try:
            # 获取上海市场股票
            sh_stocks = self.tdx_reader.get_available_stocks('sh')
            # 获取深圳市场股票
            sz_stocks = self.tdx_reader.get_available_stocks('sz')
            
            all_stocks = sh_stocks + sz_stocks
            print(f"✅ 发现 {len(all_stocks)} 只股票")
            
            return all_stocks
            
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return []
    
    def analyze_stock(self, stock):
        """分析单只股票"""
        try:
            df = self.tdx_reader.read_stock_data(stock['market'], stock['code'], years=1)
            
            if df.empty or len(df) < 60:
                return None
                
            # 计算技术指标
            df = self.backtester.calculate_indicators(df)
            
            # 获取最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 计算评分
            score = 0
            signals = []
            
            # 均线多头排列
            if latest['ma5'] > latest['ma10'] > latest['ma20']:
                score += 20
                signals.append('均线多头')
            
            # MACD金叉
            if prev['dif'] <= prev['dea'] and latest['dif'] > latest['dea']:
                score += 25
                signals.append('MACD金叉')
            elif latest['dif'] > latest['dea']:
                score += 10
                signals.append('MACD多头')
            
            # KDJ金叉
            if prev['k'] <= prev['d'] and latest['k'] > latest['d']:
                score += 20
                signals.append('KDJ金叉')
            elif latest['k'] > latest['d'] and latest['k'] < 80:
                score += 10
                signals.append('KDJ多头')
            
            # RSI处于低位
            if latest['rsi'] < 50 and latest['rsi'] > 30:
                score += 15
                signals.append('RSI低位')
            elif latest['rsi'] <= 30:
                score += 20
                signals.append('RSI超卖')
            
            # 价格在布林带下轨附近
            if latest['close'] <= latest['boll_lower'] * 1.02:
                score += 15
                signals.append('布林带下轨')
            
            # 成交量放大
            vol_avg = df['volume'].rolling(20).mean().iloc[-1]
            if latest['volume'] > vol_avg * 1.5:
                score += 10
                signals.append('放量')
            
            # 涨幅适中
            change = (latest['close'] - prev['close']) / prev['close'] * 100
            if 2 <= change <= 5:
                score += 10
                signals.append('温和上涨')
            elif change > 5:
                score += 5
                signals.append('强势上涨')
            
            # 排除涨停股票
            if change >= 9.8:
                signals.append('涨停')
                score -= 20
                
            # 排除跌停股票
            if change <= -9.8:
                signals.append('跌停')
                return None
            
            return {
                'code': f"{stock['market'].upper()}{stock['code']}",
                'name': stock['name'],
                'price': latest['close'],
                'change': change,
                'score': score,
                'signals': signals,
                'ma5': latest['ma5'],
                'ma10': latest['ma10'],
                'ma20': latest['ma20'],
                'macd': latest['macd'],
                'dif': latest['dif'],
                'dea': latest['dea'],
                'k': latest['k'],
                'd': latest['d'],
                'j': latest['j'],
                'rsi': latest['rsi'],
                'volume': latest['volume']
            }
            
        except Exception as e:
            return None
    
    def run_strategy(self):
        """运行选股策略"""
        print("\n" + "="*120)
        print("🦅 涨停先知 - 明日策略选股系统")
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)
        
        stocks = self.get_today_data()
        
        if not stocks:
            print("\n❌ 无法获取股票数据")
            return
        
        print(f"\n🔍 开始分析 {len(stocks)} 只股票...")
        
        results = []
        count = 0
        total = len(stocks)
        
        for stock in stocks:
            count += 1
            if count % 50 == 0:
                print(f"   进度: {count}/{total} ({count/total*100:.1f}%)")
                
            result = self.analyze_stock(stock)
            if result:
                results.append(result)
        
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n✅ 分析完成! 发现 {len(results)} 只符合条件的股票")
        
        # 输出结果
        self.print_results(results)
        
        return results
    
    def print_results(self, results):
        """输出选股结果"""
        print("\n" + "="*120)
        print("🏆 明日上车股票推荐")
        print("="*120)
        
        # 只显示前20只
        top_stocks = results[:20]
        
        if not top_stocks:
            print("\n❌ 没有找到符合条件的股票")
            return
        
        # 打印表格
        print("\n" + "="*120)
        print(f"{'排名':<4} {'代码':<10} {'名称':<10} {'价格':<8} {'涨幅':<8} {'评分':<6} {'信号'}")
        print("-"*120)
        
        for i, stock in enumerate(top_stocks, 1):
            signals_str = ",".join(stock['signals'][:4])
            print(f"{i:<4} {stock['code']:<10} {stock['name']:<10} ¥{stock['price']:<7.2f} {stock['change']:>+.2f}%    {stock['score']:<6} {signals_str}")
        
        print("-"*120)
        
        # 详细分析
        print("\n📊 详细分析:")
        
        for i, stock in enumerate(top_stocks[:5], 1):
            print(f"\n{i}. {stock['name']} ({stock['code']})")
            print(f"   价格: ¥{stock['price']:.2f}")
            print(f"   涨幅: {stock['change']:+.2f}%")
            print(f"   评分: {stock['score']}/100")
            print(f"   技术信号: {', '.join(stock['signals'])}")
            print(f"   均线: MA5={stock['ma5']:.2f}, MA10={stock['ma10']:.2f}, MA20={stock['ma20']:.2f}")
            print(f"   MACD: DIF={stock['dif']:.4f}, DEA={stock['dea']:.4f}, MACD={stock['macd']:.4f}")
            print(f"   KDJ: K={stock['k']:.2f}, D={stock['d']:.2f}, J={stock['j']:.2f}")
            print(f"   RSI: {stock['rsi']:.2f}")
        
        # 策略建议
        print("\n" + "="*120)
        print("💡 明日策略建议")
        print("="*120)
        
        high_score = [s for s in results if s['score'] >= 70]
        medium_score = [s for s in results if 50 <= s['score'] < 70]
        
        print(f"\n📈 强烈关注 ({len(high_score)}只):")
        for stock in high_score[:5]:
            print(f"   • {stock['name']} ({stock['code']}) - 评分: {stock['score']}")
        
        print(f"\n⚡ 适度关注 ({len(medium_score)}只):")
        for stock in medium_score[:5]:
            print(f"   • {stock['name']} ({stock['code']}) - 评分: {stock['score']}")
        
        print("\n🎯 操作建议:")
        print("   1. 优先关注评分70以上的股票")
        print("   2. 结合开盘价和成交量确认入场时机")
        print("   3. 设置合理止损位（建议5%-8%）")
        print("   4. 控制仓位，不要满仓操作")
        
        print("\n" + "="*120)
        print("⚠️ 风险提示: 以上分析仅供参考，不构成投资建议")
        print("="*120)
        
        # 保存结果到文件
        self.save_results(results)
    
    def save_results(self, results):
        """保存选股结果"""
        try:
            df = pd.DataFrame(results)
            filename = f"选股结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, encoding='utf-8-sig', index=False)
            print(f"\n✅ 选股结果已保存到: {filename}")
        except Exception as e:
            print(f"\n❌ 保存失败: {e}")

if __name__ == "__main__":
    strategy = TomorrowStrategy()
    results = strategy.run_strategy()
