#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 实时数据分析系统
ZTB Seer - Real-time Data Analysis System
实时获取新浪财经股票数据
"""

import requests
import time
from datetime import datetime

class RealTimeStockAnalyzer:
    def __init__(self):
        self.base_url = "http://hq.sinajs.cn/list="
        self.stock_codes = {
            '600584': '长电科技',
            '600519': '贵州茅台',
            '000858': '五粮液',
            '300750': '宁德时代',
            '002594': '比亚迪',
            '600036': '招商银行',
            '601318': '中国平安',
            '600030': '中信证券',
            '688981': '中芯国际',
            '002371': '北方华创',
            '601012': '隆基绿能',
            '603501': '韦尔股份',
            '000333': '美的集团',
            '600276': '恒瑞医药',
            '300015': '爱尔眼科'
        }
        
    def get_realtime_data(self):
        """获取实时股票数据"""
        results = []
        
        for code, name in self.stock_codes.items():
            try:
                # 构建完整代码
                full_code = f"sh{code}" if code.startswith('6') else f"sz{code}"
                url = f"{self.base_url}{full_code}"
                
                response = requests.get(url, timeout=5)
                response.encoding = 'gb2312'
                
                data = response.text
                if not data or '=' not in data:
                    continue
                
                # 解析数据
                parts = data.split('=')[-1].strip().replace('"', '')
                fields = parts.split(',')
                
                if len(fields) >= 11:
                    result = {
                        'code': code,
                        'name': name,
                        'price': float(fields[3]),
                        'change': float(fields[4]),
                        'change_pct': float(fields[5]),
                        'open': float(fields[1]),
                        'high': float(fields[4]),
                        'low': float(fields[5]),
                        'volume': int(fields[8]) / 100,
                        'amount': float(fields[9]) / 10000,
                        'time': fields[30] if len(fields) > 30 else datetime.now().strftime('%H:%M:%S')
                    }
                    results.append(result)
                    
            except Exception as e:
                print(f"获取 {name} 数据失败: {e}")
                continue
        
        return results
    
    def analyze_stock(self, stock):
        """分析单只股票"""
        score = 50
        reasons = []
        
        # 涨幅评分
        change = stock['change_pct']
        if change > 3:
            score += 20
            reasons.append(f"🔥 强势上涨 {change:.2f}%")
        elif change > 1:
            score += 10
            reasons.append(f"📈 上涨 {change:.2f}%")
        elif change > 0:
            score += 5
            reasons.append(f"📊 小幅上涨 {change:.2f}%")
        elif change < -2:
            score -= 10
            reasons.append(f"⚠️ 下跌 {change:.2f}%")
        else:
            reasons.append(f"➖ 震荡整理 {change:.2f}%")
            
        # 成交量评分
        volume = stock['volume']
        if volume > 100000:
            score += 15
            reasons.append(f"🔥 高成交量 {volume/10000:.1f}万手")
        elif volume > 50000:
            score += 10
            reasons.append(f"📊 成交量活跃 {volume/10000:.1f}万手")
        else:
            score += 5
            reasons.append(f"⚡ 成交量正常 {volume/10000:.1f}万手")
            
        # 价格位置评分
        range_pct = (stock['price'] - stock['low']) / (stock['high'] - stock['low']) if (stock['high'] - stock['low']) > 0 else 0
        if 0.3 < range_pct < 0.7:
            score += 10
            reasons.append("✅ 价格处于合理区间")
        elif range_pct >= 0.7:
            score += 5
            reasons.append("⚡ 接近日内高点")
        else:
            score += 5
            reasons.append("📉 接近日内低点")
            
        # 量比评分（简单估算）
        if volume > 80000:
            score += 10
            reasons.append("✅ 量比健康")
            
        score = min(score, 100)
        
        return {
            'score': score,
            'reasons': reasons[:3],
            'recommendation': self.get_recommendation(score)
        }
        
    def get_recommendation(self, score):
        if score >= 85:
            return "🚀 强烈推荐"
        elif score >= 75:
            return "✅ 推荐关注"
        elif score >= 65:
            return "📈 可以考虑"
        else:
            return "⚖️ 观望为主"
            
    def print_results(self, stocks):
        """打印分析结果"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'='*100}")
        print(f"⚡ 涨停先知 - 实时数据分析 ⚡")
        print(f"⏰ 更新时间: {now}")
        print(f"📊 股票数量: {len(stocks)} 只")
        print(f"{'='*100}")
        
        # 按涨幅排序
        stocks.sort(key=lambda x: x['change_pct'], reverse=True)
        
        print("\n📈 实时行情排行:")
        print("-" * 100)
        print(f"{'排名':<4} {'股票':<10} {'代码':<8} {'价格':<10} {'涨跌':<10} {'成交量':<12} {'时间':<8}")
        print("-" * 100)
        
        for i, stock in enumerate(stocks, 1):
            color = "🟢" if stock['change_pct'] > 0 else "🔴" if stock['change_pct'] < 0 else "⬜"
            print(f"{i:<4} {stock['name']:<10} {stock['code']:<8} ¥{stock['price']:<9.2f} {color}{stock['change_pct']:>9.2f}% {stock['volume']/10000:<11.1f}万手 {stock['time']:<8}")
        
        print("\n🎯 智能分析推荐:")
        print("-" * 100)
        
        for stock in stocks:
            analysis = self.analyze_stock(stock)
            color = "🟢" if analysis['score'] >= 75 else "🟡" if analysis['score'] >= 65 else "🔴"
            
            if analysis['score'] >= 70:
                print(f"\n{stock['name']} ({stock['code']})")
                print(f"   {color} 综合评分: {analysis['score']}分")
                print(f"   📈 价格: ¥{stock['price']:.2f}")
                print(f"   📉 涨跌: {stock['change_pct']:+.2f}%")
                print(f"   🎯 建议: {analysis['recommendation']}")
                print(f"   💡 理由:")
                for reason in analysis['reasons']:
                    print(f"      • {reason}")
        
        print("\n" + "="*100)
        
    def run(self, iterations=5):
        """运行实时分析"""
        print("🚀 启动实时数据分析系统...")
        print("按 Ctrl+C 停止")
        print()
        
        try:
            for i in range(iterations):
                print(f"\n{'='*50} 第 {i+1}/{iterations} 次更新 {'='*50}")
                
                stocks = self.get_realtime_data()
                
                if stocks:
                    self.print_results(stocks)
                else:
                    print("❌ 获取数据失败，使用模拟数据")
                    self.print_results(self.get_fallback_data())
                
                if i < iterations - 1:
                    print("\n⏳ 等待30秒后更新...")
                    time.sleep(30)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 用户停止")
            
    def get_fallback_data(self):
        """回退数据"""
        return [
            {'code': '600584', 'name': '长电科技', 'price': 28.65, 'change_pct': 1.95, 'open': 28.10, 'high': 29.05, 'low': 28.05, 'volume': 625000, 'amount': 17985.6, 'time': '14:30:00'},
            {'code': '600519', 'name': '贵州茅台', 'price': 1856.00, 'change_pct': 3.56, 'open': 1798.00, 'high': 1868.00, 'low': 1792.00, 'volume': 158000, 'amount': 293248.0, 'time': '14:30:00'},
            {'code': '300750', 'name': '宁德时代', 'price': 218.60, 'change_pct': 4.12, 'open': 210.00, 'high': 221.50, 'low': 208.50, 'volume': 567000, 'amount': 123846.2, 'time': '14:30:00'},
            {'code': '002594', 'name': '比亚迪', 'price': 258.90, 'change_pct': 5.21, 'open': 246.50, 'high': 262.80, 'low': 245.20, 'volume': 675000, 'amount': 174857.5, 'time': '14:30:00'},
            {'code': '600036', 'name': '招商银行', 'price': 35.80, 'change_pct': 1.56, 'open': 35.20, 'high': 36.10, 'low': 34.90, 'volume': 789000, 'amount': 28246.2, 'time': '14:30:00'},
            {'code': '688981', 'name': '中芯国际', 'price': 52.60, 'change_pct': 3.15, 'open': 51.00, 'high': 53.40, 'low': 50.85, 'volume': 856000, 'amount': 45025.6, 'time': '14:30:00'},
            {'code': '002371', 'name': '北方华创', 'price': 328.50, 'change_pct': 4.25, 'open': 315.00, 'high': 333.50, 'low': 314.50, 'volume': 225000, 'amount': 74062.5, 'time': '14:30:00'},
            {'code': '601012', 'name': '隆基绿能', 'price': 28.65, 'change_pct': 3.25, 'open': 27.75, 'high': 29.10, 'low': 27.60, 'volume': 1258000, 'amount': 36031.7, 'time': '14:30:00'}
        ]

if __name__ == "__main__":
    analyzer = RealTimeStockAnalyzer()
    analyzer.run(iterations=3)
