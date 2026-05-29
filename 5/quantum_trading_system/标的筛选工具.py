#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标的精细筛选工具
根据多种条件筛选出最优质的标的
"""
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 今日选股结果
today_stocks = [
    {
        'symbol': '160191.SZ',
        'name': '标的A',
        'price': 272.81,
        'change_pct': 4.99,
        'trend': 'up',
        'rsi': 66.9,
        'ma_return': 105.44,
        'ma_sharpe': 2.17,
        'ma_win_rate': 60,
        'ma_max_dd': 15.2,
        'rsi_return': 24.87,
        'rsi_sharpe': 1.21,
        'rsi_win_rate': 100,
        'final_score': 142.2,
        'best_strategy': 'MA'
    },
    {
        'symbol': '668852.SH',
        'name': '标的B',
        'price': 174.39,
        'change_pct': 1.20,
        'trend': 'up',
        'rsi': 79.2,
        'ma_return': 33.74,
        'ma_sharpe': 1.02,
        'ma_win_rate': 55,
        'ma_max_dd': 22.1,
        'rsi_return': 96.62,
        'rsi_sharpe': 2.13,
        'rsi_win_rate': 83,
        'final_score': 141.5,
        'best_strategy': 'RSI'
    },
    {
        'symbol': '086518.SZ',
        'name': '标的C',
        'price': 175.47,
        'change_pct': -3.55,
        'trend': 'up',
        'rsi': 72.5,
        'ma_return': 45.94,
        'ma_sharpe': 1.25,
        'ma_win_rate': 60,
        'ma_max_dd': 18.5,
        'rsi_return': 88.24,
        'rsi_sharpe': 2.14,
        'rsi_win_rate': 83,
        'final_score': 137.4,
        'best_strategy': 'RSI'
    },
    {
        'symbol': '000237.SZ',
        'name': '标的D',
        'price': 147.41,
        'change_pct': -2.80,
        'trend': 'up',
        'rsi': 55.7,
        'ma_return': 51.81,
        'ma_sharpe': 1.46,
        'ma_win_rate': 75,
        'ma_max_dd': 12.3,
        'rsi_return': -4.34,
        'rsi_sharpe': -0.02,
        'rsi_win_rate': 33,
        'final_score': 98.4,
        'best_strategy': 'MA'
    },
    {
        'symbol': '168849.SZ',
        'name': '标的E',
        'price': 189.71,
        'change_pct': -1.98,
        'trend': 'up',
        'rsi': 51.4,
        'ma_return': 44.96,
        'ma_sharpe': 1.20,
        'ma_win_rate': 60,
        'ma_max_dd': 16.8,
        'rsi_return': 48.84,
        'rsi_sharpe': 1.26,
        'rsi_win_rate': 100,
        'final_score': 96.6,
        'best_strategy': 'RSI'
    },
]

class StockFilter:
    """标的筛选器"""
    
    def __init__(self, stocks):
        self.stocks = stocks
    
    def filter_by_score(self, min_score=100):
        """按综合评分筛选"""
        return [s for s in self.stocks if s['final_score'] >= min_score]
    
    def filter_by_rsi(self, min_rsi=30, max_rsi=70):
        """按RSI筛选"""
        return [s for s in self.stocks if min_rsi <= s['rsi'] <= max_rsi]
    
    def filter_by_change(self, min_change=-5, max_change=5):
        """按涨跌幅筛选"""
        return [s for s in self.stocks if min_change <= s['change_pct'] <= max_change]
    
    def filter_by_max_dd(self, max_dd=20):
        """按最大回撤筛选"""
        return [s for s in self.stocks if min(s['ma_max_dd'], s.get('rsi_max_dd', 100)) <= max_dd]
    
    def filter_by_win_rate(self, min_win_rate=60):
        """按胜率筛选"""
        return [s for s in self.stocks if max(s['ma_win_rate'], s['rsi_win_rate']) >= min_win_rate]
    
    def filter_by_sharpe(self, min_sharpe=1.0):
        """按夏普比率筛选"""
        return [s for s in self.stocks if max(s['ma_sharpe'], s['rsi_sharpe']) >= min_sharpe]
    
    def filter_by_price(self, min_price=50, max_price=500):
        """按价格区间筛选"""
        return [s for s in self.stocks if min_price <= s['price'] <= max_price]
    
    def filter_gainers(self):
        """筛选上涨标的"""
        return [s for s in self.stocks if s['change_pct'] > 0]
    
    def filter_dippers(self):
        """筛选下跌标的（超跌机会）"""
        return [s for s in self.stocks if s['change_pct'] < 0]
    
    def get_best_for_risk(self):
        """风险控制最佳标的"""
        return sorted(self.stocks, key=lambda x: min(x['ma_max_dd'], x.get('rsi_max_dd', 100)))
    
    def get_best_for_return(self):
        """收益最佳标的"""
        return sorted(self.stocks, key=lambda x: max(x['ma_return'], x['rsi_return']), reverse=True)
    
    def get_best_for_win_rate(self):
        """胜率最佳标的"""
        return sorted(self.stocks, key=lambda x: max(x['ma_win_rate'], x['rsi_win_rate']), reverse=True)

def display_stocks(stocks, title="筛选结果"):
    """显示筛选结果"""
    print(f"\n{'='*70}")
    print(f"     {title}")
    print(f"{'='*70}")
    
    if not stocks:
        print("\n   ❌ 没有符合条件的标的")
        return
    
    print(f"\n   {'排名':<4} {'股票代码':<12} {'价格':>10} {'涨幅':>8} {'RSI':>6} {'评分':>8} {'策略':<8}")
    print("   " + "-"*70)
    
    for i, stock in enumerate(stocks, 1):
        change_color = "🟢" if stock['change_pct'] > 0 else "🔴"
        print(f"   {i:<4} {stock['symbol']:<12} {stock['price']:>10.2f} {change_color}{stock['change_pct']:>+7.2f}% "
              f"{stock['rsi']:>6.1f} {stock['final_score']:>8.1f} {stock['best_strategy']:<8}")
    
    print(f"\n   共 {len(stocks)} 只标的")

def main():
    print("="*70)
    print("     🎯 标的精细筛选工具")
    print("="*70)
    
    filter = StockFilter(today_stocks)
    
    print("\n📊 筛选选项:")
    print("   1. 综合评分最高")
    print("   2. RSI适中（30-70）")
    print("   3. 回撤控制最佳")
    print("   4. 胜率最高")
    print("   5. 夏普比率最高")
    print("   6. 上涨标的")
    print("   7. 超跌标的")
    print("   8. 低风险组合")
    print("   9. 稳健组合（综合筛选）")
    
    # 自动执行多种筛选
    print("\n" + "="*70)
    print("     🏆 自动筛选结果")
    print("="*70)
    
    # 1. 综合评分TOP
    top_score = filter.filter_by_score(100)
    display_stocks(top_score, "🎯 综合评分TOP（≥100分）")
    
    # 2. RSI适中
    rsi_ok = filter.filter_by_rsi(30, 70)
    display_stocks(rsi_ok, "📊 RSI适中（30-70）")
    
    # 3. 回撤控制
    low_dd = filter.filter_by_max_dd(18)
    display_stocks(low_dd, "🛡️ 回撤控制（≤18%）")
    
    # 4. 高胜率
    high_win = filter.filter_by_win_rate(70)
    display_stocks(high_win, "🎯 高胜率（≥70%）")
    
    # 5. 夏普比率
    high_sharpe = filter.filter_by_sharpe(1.5)
    display_stocks(high_sharpe, "📈 高夏普比率（≥1.5）")
    
    # 6. 稳健组合（综合筛选）
    robust = [s for s in today_stocks 
              if s['final_score'] >= 95 and 
              s['rsi'] <= 75 and 
              min(s['ma_max_dd'], s.get('rsi_max_dd', 100)) <= 20 and
              max(s['ma_win_rate'], s['rsi_win_rate']) >= 60]
    
    display_stocks(robust, "⭐ 稳健组合（综合筛选）")
    
    print("\n" + "="*70)
    print("     💡 推荐建议")
    print("="*70)
    
    if robust:
        print(f"\n   🏆 今日首选稳健标的: {robust[0]['symbol']}")
        print(f"      评分: {robust[0]['final_score']:.1f}")
        print(f"      策略: {robust[0]['best_strategy']}")
        print(f"      建议仓位: 20%")
        
        if len(robust) > 1:
            print(f"\n   📈 次选标的: {robust[1]['symbol']}")
            print(f"      评分: {robust[1]['final_score']:.1f}")
            print(f"      建议仓位: 10%")
    
    print("\n" + "="*70)
    print("✅ 筛选完成！")
    print("="*70)

if __name__ == "__main__":
    main()
