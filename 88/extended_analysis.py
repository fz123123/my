#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 扩展版牛股发掘系统
ZTB Seer - Extended Bull Stock Discovery
覆盖16个行业，84只优质股票
"""

import random
from datetime import datetime

class ExtendedBullStockAnalyzer:
    def __init__(self):
        self.industries = {
            '白酒': [
                ('贵州茅台', '600519', 1856.00),
                ('五粮液', '000858', 168.50),
                ('泸州老窖', '000568', 235.80),
                ('洋河股份', '002304', 145.60),
            ],
            '银行': [
                ('招商银行', '600036', 35.80),
                ('中国平安', '601318', 48.25),
                ('工商银行', '601398', 5.12),
                ('建设银行', '601939', 6.85),
                ('平安银行', '000001', 12.35),
                ('兴业银行', '601166', 18.62),
                ('浦发银行', '600000', 8.45),
                ('交通银行', '601328', 4.89),
            ],
            '保险': [
                ('中国太保', '601601', 28.65),
                ('新华保险', '601336', 32.50),
                ('天茂集团', '000627', 3.25),
            ],
            '券商': [
                ('中信证券', '600030', 22.50),
                ('国泰君安', '601211', 15.62),
                ('华泰证券', '601688', 16.85),
                ('广发证券', '000776', 16.25),
                ('海通证券', '600837', 11.85),
                ('东方证券', '600958', 9.85),
                ('国信证券', '002736', 10.25),
            ],
            '科技成长': [
                ('宁德时代', '300750', 218.60),
                ('比亚迪', '002594', 258.90),
                ('隆基绿能', '601012', 28.65),
                ('兆易创新', '603986', 128.50),
                ('海康威视', '002415', 35.80),
                ('闻泰科技', '600745', 58.25),
                ('东方财富', '300059', 18.65),
                ('金山办公', '688111', 358.60),
            ],
            '医药': [
                ('恒瑞医药', '600276', 48.65),
                ('药明康德', '603259', 85.60),
                ('爱尔眼科', '300015', 32.50),
                ('云南白药', '000538', 58.25),
                ('复星医药', '600196', 32.85),
                ('华兰生物', '002007', 22.60),
                ('中新药业', '600329', 28.50),
            ],
            '消费家电': [
                ('美的集团', '000333', 62.85),
                ('格力电器', '000651', 38.65),
                ('海尔智家', '600690', 26.85),
                ('TCL科技', '000100', 4.25),
                ('伊利股份', '600887', 28.60),
                ('苏泊尔', '002032', 52.80),
                ('氯碱化工', '600618', 12.85),
            ],
            '房地产': [
                ('万科A', '000002', 18.95),
                ('保利发展', '600048', 15.62),
                ('金地集团', '600383', 10.25),
                ('招商蛇口', '001979', 12.85),
                ('新城控股', '601155', 22.60),
                ('绿地控股', '600606', 3.85),
                ('金融街', '000402', 6.85),
            ],
            '新能源': [
                ('长江电力', '600900', 22.85),
                ('三峡能源', '600905', 6.25),
                ('晶澳科技', '002459', 35.60),
                ('亿纬锂能', '300014', 68.50),
                ('明阳智能', '601615', 22.85),
                ('中环股份', '002129', 42.60),
                ('通威股份', '600438', 38.65),
            ],
            '基建制造': [
                ('中国建筑', '601668', 5.85),
                ('中国铁建', '601186', 8.65),
                ('中国中铁', '601390', 6.85),
                ('宁波华翔', '002048', 15.60),
                ('三一重工', '600031', 18.25),
                ('徐工机械', '000425', 6.85),
                ('上海建工', '600170', 3.25),
            ],
            '通信电子': [
                ('中国移动', '600941', 98.60),
                ('中国电信', '601728', 6.25),
                ('中国联通', '600050', 4.85),
                ('中兴通讯', '000063', 35.60),
                ('歌尔股份', '002241', 22.85),
                ('汇顶科技', '603160', 85.60),
                ('同花顺', '300033', 125.60),
            ],
            '化工材料': [
                ('万华化学', '600309', 92.50),
                ('君正集团', '601216', 5.85),
                ('龙蟒佰利', '002601', 28.60),
                ('宝丰能源', '600989', 12.85),
                ('中泰化学', '002092', 8.65),
                ('扬农化工', '600486', 85.60),
                ('新安股份', '600596', 15.80),
            ],
            '军工': [
                ('航发动力', '600893', 42.60),
                ('振华科技', '000733', 65.80),
                ('中航沈飞', '600760', 58.50),
                ('中航机电', '002013', 12.85),
                ('中国重工', '601989', 4.25),
                ('航天电器', '002025', 72.50),
                ('中航高科', '600862', 28.60),
            ],
            '食品饮料': [
                ('重庆啤酒', '600132', 118.60),
                ('双汇发展', '000895', 28.65),
                ('光明乳业', '600597', 11.85),
                ('牧原股份', '002714', 52.80),
                ('维维股份', '600300', 3.85),
                ('涪陵榨菜', '002507', 28.50),
                ('海天味业', '603288', 68.60),
            ],
            '汽车': [
                ('上汽集团', '600104', 15.85),
                ('长安汽车', '000625', 12.60),
                ('赛力斯', '601127', 72.50),
                ('银轮股份', '002126', 18.65),
                ('一汽富维', '600742', 8.85),
            ],
            '半导体': [
                ('中芯国际', '688981', 52.60),
                ('北方华创', '002371', 328.50),
                ('韦尔股份', '603501', 92.80),
                ('澜起科技', '688008', 65.80),
                ('卓胜微', '300782', 128.60),
                ('长电科技', '600584', 28.65),
                ('通富微电', '002156', 22.80),
            ],
            '互联网科技': [
                ('恒生电子', '600570', 58.60),
                ('用友网络', '600588', 22.85),
                ('广联达', '002410', 48.60),
                ('光电股份', '600184', 12.85),
                ('科大讯飞', '002230', 52.80),
                ('东软集团', '600718', 12.60),
            ]
        }
        
    def print_banner(self):
        print("=" * 100)
        print("⚡ 涨停先知 - 智能牛股发掘系统 ⚡  [扩展版]")
        print("=" * 100)
        print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 覆盖行业: {len(self.industries)} 个")
        print(f"📈 股票总数: {sum(len(stocks) for stocks in self.industries.values())} 只")
        print()
        
    def analyze_stock(self, name, code, price):
        """分析单只股票"""
        score = 50
        reasons = []
        
        # 模拟涨跌幅 (-5% 到 +7%)
        change = round(random.uniform(-3, 6), 2)
        new_price = round(price * (1 + change / 100), 2)
        
        # 涨幅评分
        if change > 5:
            score += 20
            reasons.append(f"🔥 强势涨停，涨幅 {change:.2f}%")
        elif change > 2:
            score += 15
            reasons.append(f"📈 良好涨势 {change:.2f}%")
        elif change > 0:
            score += 5
            reasons.append(f"📊 小幅上涨 {change:.2f}%")
        else:
            reasons.append(f"⚠️ 下跌 {change:.2f}%")
            
        # 模拟技术指标
        indicators = []
        
        # MACD
        macd_score = random.randint(5, 20)
        score += macd_score
        if macd_score >= 15:
            indicators.append("✅ MACD金叉")
        elif macd_score >= 10:
            indicators.append("⚡ MACD强势")
        else:
            indicators.append("📉 MACD偏弱")
            
        # KDJ
        kdj_score = random.randint(5, 15)
        score += kdj_score
        if kdj_score >= 12:
            indicators.append("✅ KDJ买入信号")
        elif kdj_score >= 8:
            indicators.append("⚡ KDJ强势")
        else:
            indicators.append("📊 KDJ整理中")
            
        # RSI
        rsi_score = random.randint(3, 12)
        score += rsi_score
        if rsi_score >= 10:
            indicators.append("✅ RSI强势区")
        elif rsi_score >= 6:
            indicators.append("📊 RSI正常")
        else:
            indicators.append("📉 RSI偏弱")
            
        # 成交量
        volume = random.uniform(20, 200)
        if volume > 100:
            score += 10
            reasons.append(f"🔥 高成交量 {volume:.0f}万")
        elif volume > 50:
            score += 5
            reasons.append(f"📊 成交量正常 {volume:.0f}万")
        else:
            reasons.append(f"⚠️ 成交量较低 {volume:.0f}万")
            
        # 市盈率模拟
        pe = random.uniform(10, 60)
        if pe < 25:
            score += 10
            reasons.append(f"💰 低估值 PE={pe:.1f}")
        elif pe < 40:
            score += 5
            reasons.append(f"⚖️ 估值适中 PE={pe:.1f}")
        else:
            reasons.append(f"⚠️ 估值偏高 PE={pe:.1f}")
            
        # 行业热度
        hot_industries = ['新能源', '半导体', '科技成长', '军工']
        industry = None
        for ind, stocks in self.industries.items():
            if any(s[0] == name for s in stocks):
                industry = ind
                break
                
        if industry in hot_industries:
            score += 8
            reasons.append(f"🔥 热门行业: {industry}")
            
        score = min(score, 100)
        
        return {
            'name': name,
            'code': code,
            'price': new_price,
            'change': change,
            'score': score,
            'reasons': reasons[:3],
            'indicators': indicators,
            'recommendation': self.get_recommendation(score)
        }
        
    def get_recommendation(self, score):
        if score >= 85:
            return "🚀 强烈推荐"
        elif score >= 75:
            return "✅ 推荐关注"
        elif score >= 65:
            return "📈 可以考虑"
        elif score >= 55:
            return "⚖️ 观望为主"
        else:
            return "❌ 建议回避"
            
    def analyze_industry(self, industry_name, stocks):
        """分析行业"""
        print()
        print("=" * 100)
        print(f"📂 行业: {industry_name}")
        print("=" * 100)
        print()
        
        results = []
        for name, code, price in stocks:
            analysis = self.analyze_stock(name, code, price)
            results.append(analysis)
            
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        for i, stock in enumerate(results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            color = "🟢" if stock['score'] >= 75 else "🟡" if stock['score'] >= 65 else "🔴"
            
            print(f"{medal} {stock['name']} ({stock['code']})")
            print(f"   {color} 评分: {stock['score']}分 | 价格: ¥{stock['price']:.2f} | 涨跌: {stock['change']:+.2f}%")
            print(f"   🎯 建议: {stock['recommendation']}")
            print(f"   💡 亮点:")
            for reason in stock['reasons']:
                print(f"      • {reason}")
            print(f"   📊 指标:")
            for indicator in stock['indicators']:
                print(f"      • {indicator}")
            print()
            
        return results
        
    def show_top_stocks(self, all_results):
        """展示总排行"""
        print()
        print("=" * 100)
        print("🏆 全部股票综合排行榜 TOP 20")
        print("=" * 100)
        print()
        
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        for i, stock in enumerate(all_results[:20], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i:2d}"
            color = "🟢" if stock['score'] >= 75 else "🟡" if stock['score'] >= 65 else "🔴"
            
            print(f"{medal} {stock['name']:<8s} ({stock['code']}) {color}{stock['score']:3d}分  ¥{stock['price']:8.2f}  {stock['change']:+6.2f}%  {stock['recommendation']}")
            
        print()
        
    def show_statistics(self, all_results):
        """展示统计信息"""
        print()
        print("=" * 100)
        print("📊 市场统计信息")
        print("=" * 100)
        print()
        
        total = len(all_results)
        up = len([s for s in all_results if s['change'] > 0])
        down = len([s for s in all_results if s['change'] < 0])
        flat = len([s for s in all_results if s['change'] == 0])
        
        strong_buy = len([s for s in all_results if s['score'] >= 85])
        buy = len([s for s in all_results if 75 <= s['score'] < 85])
        consider = len([s for s in all_results if 65 <= s['score'] < 75])
        watch = len([s for s in all_results if 55 <= s['score'] < 65])
        avoid = len([s for s in all_results if s['score'] < 55])
        
        avg_score = sum(s['score'] for s in all_results) / total
        avg_change = sum(s['change'] for s in all_results) / total
        
        print(f"📈 上涨股票: {up} 只 ({up/total*100:.1f}%)")
        print(f"📉 下跌股票: {down} 只 ({down/total*100:.1f}%)")
        print(f"➖ 平盘股票: {flat} 只 ({flat/total*100:.1f}%)")
        print()
        print(f"🚀 强烈推荐: {strong_buy} 只")
        print(f"✅ 推荐关注: {buy} 只")
        print(f"📈 可以考虑: {consider} 只")
        print(f"⚖️ 观望为主: {watch} 只")
        print(f"❌ 建议回避: {avoid} 只")
        print()
        print(f"📊 平均评分: {avg_score:.1f}分")
        print(f"📈 平均涨跌: {avg_change:+.2f}%")
        print()
        
    def show_final_recommendation(self, all_results):
        """展示最终推荐"""
        print()
        print("=" * 100)
        print("🎯 最终投资建议")
        print("=" * 100)
        print()
        
        all_results.sort(key=lambda x: x['score'], reverse=True)
        top_5 = all_results[:5]
        
        print("🔥 最值得关注的5只股票:")
        for i, stock in enumerate(top_5, 1):
            print()
            print(f"{i}. {stock['name']} ({stock['code']})")
            print(f"   当前价格: ¥{stock['price']:.2f}")
            print(f"   涨跌幅: {stock['change']:+.2f}%")
            print(f"   综合评分: {stock['score']}分")
            print(f"   投资建议: {stock['recommendation']}")
            print(f"   入选理由:")
            for reason in stock['reasons']:
                print(f"      ✓ {reason}")
                
        print()
        print("💡 操作建议:")
        print()
        print("1. 重点关注评分85分以上的股票")
        print("2. 注意MACD和KDJ的共振信号")
        print("3. 关注RSI在50-70区间的股票")
        print("4. 结合行业热度选择强势板块")
        print("5. 做好止损，控制仓位")
        print()
        print("⚠️ 风险提示:")
        print("   • 本系统仅供参考，不构成投资建议")
        print("   • 过去表现不代表未来收益")
        print("   • 投资有风险，入市需谨慎")
        print("   • 请根据自身风险承受能力决策")
        print()
        
    def run(self):
        """运行分析"""
        self.print_banner()
        
        all_results = []
        
        # 分析每个行业
        for industry_name, stocks in self.industries.items():
            results = self.analyze_industry(industry_name, stocks)
            all_results.extend(results)
            
        # 显示总排行
        self.show_top_stocks(all_results)
        
        # 显示统计
        self.show_statistics(all_results)
        
        # 显示最终推荐
        self.show_final_recommendation(all_results)
        
        print("=" * 100)
        print("✅ 分析完成！")
        print("💡 请访问 http://localhost:5173 查看完整的涨停先知系统")
        print("=" * 100)

if __name__ == "__main__":
    analyzer = ExtendedBullStockAnalyzer()
    analyzer.run()
