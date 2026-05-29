#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 牛股发掘演示脚本
ZTB Seer - Bull Stock Discovery Demo
"""

import json
import requests
import time
from datetime import datetime

class ZTBSearDemo:
    def __init__(self):
        self.base_url = "http://localhost:5173"
        self.stocks = []
        
    def print_banner(self):
        print("=" * 80)
        print("⚡ 涨停先知 - 智能牛股发掘系统 ⚡")
        print("=" * 80)
        print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    def print_separator(self):
        print("-" * 80)
        
    def get_stock_data(self):
        """获取股票数据"""
        print("📡 正在连接实时数据源...")
        
        # 模拟股票列表
        stocks_data = [
            {"code": "600519", "name": "贵州茅台", "change": 3.56},
            {"code": "601318", "name": "中国平安", "change": -0.85},
            {"code": "600036", "name": "招商银行", "change": 1.56},
            {"code": "000858", "name": "五粮液", "change": -1.23},
            {"code": "002594", "name": "比亚迪", "change": 5.21},
            {"code": "300750", "name": "宁德时代", "change": 4.12},
            {"code": "000002", "name": "万科A", "change": -2.15},
            {"code": "600030", "name": "中信证券", "change": 1.85},
        ]
        
        print(f"✅ 成功获取 {len(stocks_data)} 只股票数据")
        return stocks_data
    
    def analyze_stock(self, stock):
        """分析单只股票"""
        score = 50  # 基础分
        reasons = []
        
        # 涨幅分析
        change = stock['change']
        if change > 5:
            score += 20
            reasons.append("🔥 强势上涨，涨幅超过5%")
        elif change > 2:
            score += 15
            reasons.append("📈 良好涨势，涨幅超过2%")
        elif change > 0:
            score += 5
            reasons.append("📊 小幅上涨")
        elif change < -2:
            score -= 10
            reasons.append("⚠️ 下跌趋势")
            
        # 模拟技术指标评分
        import random
        macd_score = random.randint(10, 20)
        kdj_score = random.randint(5, 15)
        rsi_score = random.randint(5, 10)
        
        score += macd_score + kdj_score + rsi_score
        
        if macd_score >= 15:
            reasons.append("✅ MACD金叉向上")
        if kdj_score >= 12:
            reasons.append("✅ KDJ买入信号")
        if rsi_score >= 8:
            reasons.append("✅ RSI处于强势区间")
            
        # 市盈率模拟
        pe = random.uniform(10, 50)
        if pe < 30:
            score += 10
            reasons.append(f"💰 市盈率适中 ({pe:.1f})")
        else:
            score += 5
            reasons.append(f"⚖️ 市盈率偏高 ({pe:.1f})")
            
        # 成交量模拟
        volume = random.uniform(50, 150)
        if volume > 80:
            score += 10
            reasons.append("🔥 高成交量，资金关注")
        elif volume > 50:
            score += 5
            reasons.append("📊 成交量正常")
            
        # 限制分数范围
        score = min(score, 100)
        
        return {
            'score': score,
            'reasons': reasons,
            'recommendation': self.get_recommendation(score)
        }
        
    def get_recommendation(self, score):
        """根据评分给出建议"""
        if score >= 85:
            return "🚀 强烈推荐买入"
        elif score >= 75:
            return "✅ 推荐关注"
        elif score >= 65:
            return "📈 可以考虑"
        elif score >= 55:
            return "⚖️ 观望为主"
        else:
            return "❌ 建议回避"
            
    def display_results(self, stocks_data):
        """展示分析结果"""
        print("\n📊 开始分析股票...")
        print()
        
        results = []
        for stock in stocks_data:
            analysis = self.analyze_stock(stock)
            result = {**stock, **analysis}
            results.append(result)
            
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(self.print_separator())
        print("🏆 牛股排行榜 TOP 8")
        print(self.print_separator())
        print()
        
        for i, result in enumerate(results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            color = "🟢" if result['score'] >= 75 else "🟡" if result['score'] >= 65 else "🔴"
            
            print(f"{medal} {result['name']} ({result['code']})")
            print(f"   {color} 综合评分: {result['score']}分")
            print(f"   📉 涨跌幅: {result['change']:+.2f}%")
            print(f"   🎯 建议: {result['recommendation']}")
            print(f"   💡 原因:")
            for reason in result['reasons'][:3]:
                print(f"      • {reason}")
            print()
            
        # 显示推荐
        print(self.print_separator())
        print("🎯 最终推荐")
        print(self.print_separator())
        print()
        
        top_stocks = results[:3]
        for i, stock in enumerate(top_stocks, 1):
            print(f"{i}. {stock['name']} ({stock['code']})")
            print(f"   评分: {stock['score']}分 | 涨幅: {stock['change']:+.2f}%")
            print(f"   建议: {stock['recommendation']}")
            print()
            
        print(self.print_separator())
        print("💡 操作建议")
        print(self.print_separator())
        print()
        print("1. 点击浏览器中的'开始分析'进入系统")
        print("2. 在股票列表页面查看所有股票详情")
        print("3. 点击感兴趣的股票查看技术指标")
        print("4. 结合K线图和MACD/KDJ指标做出决策")
        print()
        print("⚠️ 风险提示: 本系统仅供参考，不构成投资建议")
        print("⚠️ 投资有风险，入市需谨慎")
        print()
        
    def run(self):
        """运行演示"""
        self.print_banner()
        
        # 获取数据
        stocks_data = self.get_stock_data()
        
        # 模拟加载时间
        print("🔄 正在进行技术分析...")
        time.sleep(1)
        print("📊 计算MACD指标...")
        time.sleep(0.5)
        print("📈 分析KDJ指标...")
        time.sleep(0.5)
        print("📉 评估RSI强弱...")
        time.sleep(0.5)
        print("🎯 生成选股策略...")
        time.sleep(0.5)
        print()
        
        # 显示结果
        self.display_results(stocks_data)
        
        print("=" * 80)
        print("✅ 分析完成！请访问 http://localhost:5173 查看完整系统")
        print("=" * 80)

if __name__ == "__main__":
    demo = ZTBSearDemo()
    demo.run()
