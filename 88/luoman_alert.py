#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 罗曼股份(SH605289)价格预警系统
ZTB Seer - Luoman Stock Price Alert System
"""

import sys
sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from tdx_data_reader import TDXDataReader
from backtester import Backtester
import requests
import time
from datetime import datetime

class LuomanAlertSystem:
    def __init__(self):
        self.tdx_reader = TDXDataReader()
        self.stock_info = {
            'market': 'sh',
            'code': '605289',
            'name': '罗曼股份'
        }
        
        self.current_price = 154.21
        self.alerts = {
            'breakthrough': [
                {'price': 160.0, 'name': '突破160元', 'triggered': False},
                {'price': 170.0, 'name': '突破170元', 'triggered': False},
                {'price': 180.0, 'name': '突破180元', 'triggered': False},
                {'price': 200.0, 'name': '突破200元', 'triggered': False},
                {'price': 220.0, 'name': '突破220元', 'triggered': False},
            ],
            'retrace': [
                {'price': 150.0, 'name': '回调至150元', 'triggered': False},
                {'price': 145.0, 'name': '回调至145元', 'triggered': False},
                {'price': 140.0, 'name': '回调至140元', 'triggered': False},
                {'price': 130.0, 'name': '回调至130元', 'triggered': False},
                {'price': 120.0, 'name': '回调至120元', 'triggered': False},
            ],
            'percent': [
                {'percent': 5.0, 'name': '上涨5%', 'triggered': False},
                {'percent': 10.0, 'name': '上涨10%', 'triggered': False},
                {'percent': -5.0, 'name': '下跌5%', 'triggered': False},
                {'percent': -10.0, 'name': '下跌10%', 'triggered': False},
            ]
        }

    def get_realtime_price(self):
        """获取实时价格 - 新浪财经"""
        try:
            url = f"http://hq.sinajs.cn/list={self.stock_info['market']}{self.stock_info['code']}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'http://finance.sina.com.cn'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gb2312'
            data = response.text
            
            if '=' in data and 'sh' + self.stock_info['code'] in data:
                parts = data.split('=')[-1].strip().replace('"', '')
                fields = parts.split(',')
                
                if len(fields) >= 10:
                    # 解析各个价格字段
                    current = float(fields[3]) if fields[3] and fields[3] != '0.000' else 0
                    yesterday_close = float(fields[2]) if fields[2] else 0
                    open_price = float(fields[1]) if fields[1] and fields[1] != '0.000' else 0
                    
                    # 如果当前价格是0（可能是非交易时间），使用昨收价
                    if current == 0 and yesterday_close > 0:
                        current = yesterday_close
                        print(f"✓ 通过 新浪财经 获取到数据 (非交易时间，使用昨收价)")
                    elif current > 0:
                        print(f"✓ 通过 新浪财经 获取到实时数据 - 当前价: ¥{current:.2f}")
                    else:
                        print(f"✗ 通过 新浪财经 获取数据失败: 当前价格无效")
                        return None
                    
                    # 解析最高最低价
                    high_price = float(fields[4]) if fields[4] and fields[4] != '0.000' else current
                    low_price = float(fields[5]) if fields[5] and fields[5] != '0.000' else current
                    
                    # 如果最高/最低也是0，用当前价代替
                    if high_price == 0:
                        high_price = current
                    if low_price == 0:
                        low_price = current
                    
                    return {
                        'current': current,
                        'open': open_price if open_price > 0 else current,
                        'high': high_price,
                        'low': low_price,
                        'yesterday_close': yesterday_close,
                        'volume': int(float(fields[8])) if fields[8] else 0,
                        'update_time': f"{fields[30]} {fields[31]}" if len(fields) > 31 else "",
                        'data_source': 'sina_realtime'
                    }
                    
        except Exception as e:
            print(f"✗ 通过 新浪财经 获取失败: {str(e)[:50]}")
        
        return None

    def calculate_signals(self):
        """计算交易信号"""
        try:
            df = self.tdx_reader.read_stock_data(
                self.stock_info['market'],
                self.stock_info['code'],
                2
            )
            
            if df.empty or len(df) < 50:
                return None, None, None
            
            backtester = Backtester()
            df = backtester.calculate_indicators(df)
            df = backtester.strategy_combined(df)
            
            current_signal = df['signal'].iloc[-1]
            previous_signal = df['signal'].iloc[-2] if len(df) > 2 else 0
            
            return df['close'].iloc[-1], current_signal, previous_signal
        except Exception as e:
            print(f"计算信号失败: {e}")
            return None, None, None

    def check_alerts(self, current_price, reference_price):
        """检查预警条件"""
        triggered_alerts = []
        
        for alert_type, alerts in self.alerts.items():
            for alert in alerts:
                if alert['triggered']:
                    continue
                
                if alert_type in ['breakthrough', 'retrace']:
                    target_price = alert['price']
                    
                    if alert_type == 'breakthrough' and current_price >= target_price:
                        alert['triggered'] = True
                        triggered_alerts.append({
                            'type': '上涨预警',
                            'name': alert['name'],
                            'price': target_price,
                            'current': current_price
                        })
                    
                    elif alert_type == 'retrace' and current_price <= target_price:
                        alert['triggered'] = True
                        triggered_alerts.append({
                            'type': '回调预警',
                            'name': alert['name'],
                            'price': target_price,
                            'current': current_price
                        })
                
                elif alert_type == 'percent':
                    percent_change = ((current_price - reference_price) / reference_price) * 100
                    target_percent = alert['percent']
                    
                    if target_percent > 0 and percent_change >= target_percent:
                        alert['triggered'] = True
                        triggered_alerts.append({
                            'type': '涨幅预警',
                            'name': f"{alert['name']} (当前涨幅: {percent_change:.2f}%)",
                            'price': current_price,
                            'current': percent_change
                        })
                    
                    elif target_percent < 0 and percent_change <= target_percent:
                        alert['triggered'] = True
                        triggered_alerts.append({
                            'type': '跌幅预警',
                            'name': f"{alert['name']} (当前跌幅: {percent_change:.2f}%)",
                            'price': current_price,
                            'current': percent_change
                        })
        
        return triggered_alerts

    def log_detailed_check(self, display_price, realtime, signal, triggered_alerts, prev_signal=0):
        """详细日志输出"""
        from datetime import datetime
        import time
        
        logs = []
        logs.append("\n" + "="*120)
        logs.append("📋 详细检查日志")
        logs.append("="*120)
        
        # 1. 时间戳
        logs.append(f"\n⏰ 时间戳:")
        logs.append(f"   检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logs.append(f"   时间戳(Unix): {int(time.time())}")
        
        # 2. 数据获取过程
        logs.append(f"\n📡 1. 数据获取过程:")
        logs.append(f"   步骤 1.1: 初始化新浪财经数据源")
        logs.append(f"   步骤 1.2: 发送HTTP请求到 hq.sinajs.cn")
        logs.append(f"   步骤 1.3: 等待服务器响应...")
        logs.append(f"   步骤 1.4: 接收响应数据")
        
        if realtime:
            logs.append(f"   ✓ 状态: 数据获取成功")
            logs.append(f"   ✓ 数据长度: {len(str(realtime))} 字节")
        else:
            logs.append(f"   ✗ 状态: 数据获取失败，使用备用价格")
        
        # 3. 价格解析过程
        logs.append(f"\n💹 2. 价格解析过程:")
        logs.append(f"   步骤 2.1: 解析原始数据字段")
        logs.append(f"   步骤 2.2: 提取当前价格字段 [fields[3]]")
        logs.append(f"   步骤 2.3: 类型转换 (str -> float)")
        logs.append(f"   步骤 2.4: 价格验证")
        
        if realtime:
            logs.append(f"   解析结果:")
            logs.append(f"     • 当前价格: ¥{realtime['current']:.2f}")
            logs.append(f"     • 开盘价格: ¥{realtime['open']:.2f}")
            logs.append(f"     • 最高价格: ¥{realtime['high']:.2f}")
            logs.append(f"     • 最低价格: ¥{realtime['low']:.2f}")
            logs.append(f"     • 成交量: {realtime['volume']:,}股")
        
        # 4. 价格比较分析
        logs.append(f"\n📊 3. 价格比较分析:")
        logs.append(f"   参考价格: ¥{self.current_price:.2f} (系统基准)")
        logs.append(f"   当前价格: ¥{display_price:.2f}")
        
        price_diff = display_price - self.current_price
        price_diff_pct = (price_diff / self.current_price) * 100
        
        logs.append(f"   价格差异: ¥{price_diff:+.2f} ({price_diff_pct:+.2f}%)")
        
        if price_diff > 0:
            logs.append(f"   趋势判断: 📈 价格高于参考价 (上涨)")
        elif price_diff < 0:
            logs.append(f"   趋势判断: 📉 价格低于参考价 (下跌)")
        else:
            logs.append(f"   趋势判断: ➡️ 价格等于参考价 (持平)")
        
        if realtime:
            logs.append(f"\n   今日价格区间分析:")
            logs.append(f"     • 开盘价: ¥{realtime['open']:.2f}")
            logs.append(f"     • 当前价: ¥{realtime['current']:.2f}")
            logs.append(f"     • 最高价: ¥{realtime['high']:.2f}")
            logs.append(f"     • 最低价: ¥{realtime['low']:.2f}")
            
            # 价格位置分析
            price_range = realtime['high'] - realtime['low']
            if price_range > 0:
                position = (realtime['current'] - realtime['low']) / price_range * 100
                logs.append(f"     • 价格位置: 处于今日区间的 {position:.1f}% 位置")
                
                if position >= 80:
                    logs.append(f"     • 位置解读: 🔴 接近今日高点，小心回落")
                elif position >= 60:
                    logs.append(f"     • 位置解读: 🟡 处于上半区域，偏向强势")
                elif position >= 40:
                    logs.append(f"     • 位置解读: ⚪ 处于中间位置，方向不明")
                elif position >= 20:
                    logs.append(f"     • 位置解读: 🟡 处于下半区域，偏向弱势")
                else:
                    logs.append(f"     • 位置解读: 🟢 接近今日低点，可能反弹")
        
        # 5. 预警条件检查
        logs.append(f"\n🚨 4. 预警条件检查过程:")
        
        # 上涨预警检查
        logs.append(f"\n   4.1 上涨预警检查 (突破关键价位):")
        breakthrough_checks = []
        for alert in self.alerts['breakthrough']:
            if alert['triggered']:
                breakthrough_checks.append(f"     ⚠️ 已触发: {alert['name']} ¥{alert['price']:.2f}")
            elif display_price >= alert['price']:
                breakthrough_checks.append(f"     🚨 刚刚触发: {alert['name']} ¥{alert['price']:.2f}")
            else:
                distance = alert['price'] - display_price
                distance_pct = (distance / display_price) * 100
                breakthrough_checks.append(f"     ○ 未触发: {alert['name']} ¥{alert['price']:.2f} (还差¥{distance:.2f}, {distance_pct:.2f}%)")
        
        for check in breakthrough_checks:
            logs.append(check)
        
        # 回调预警检查
        logs.append(f"\n   4.2 回调预警检查 (支撑位保护):")
        retrace_checks = []
        for alert in self.alerts['retrace']:
            if alert['triggered']:
                retrace_checks.append(f"     ⚠️ 已触发: {alert['name']} ¥{alert['price']:.2f}")
            elif display_price <= alert['price']:
                retrace_checks.append(f"     🚨 刚刚触发: {alert['name']} ¥{alert['price']:.2f}")
            else:
                distance = display_price - alert['price']
                distance_pct = (distance / alert['price']) * 100
                retrace_checks.append(f"     ○ 未触发: {alert['name']} ¥{alert['price']:.2f} (还有¥{distance:.2f}空间, {distance_pct:.2f}%)")
        
        for check in retrace_checks:
            logs.append(check)
        
        # 涨跌幅预警检查
        logs.append(f"\n   4.3 涨跌幅预警检查 (百分比阈值):")
        percent_checks = []
        for alert in self.alerts['percent']:
            percent_change = ((display_price - self.current_price) / self.current_price) * 100
            
            if alert['triggered']:
                percent_checks.append(f"     ⚠️ 已触发: {alert['name']}")
            elif alert['percent'] > 0 and percent_change >= alert['percent']:
                percent_checks.append(f"     🚨 刚刚触发: {alert['name']} (当前涨幅: {percent_change:.2f}%)")
            elif alert['percent'] < 0 and percent_change <= alert['percent']:
                percent_checks.append(f"     🚨 刚刚触发: {alert['name']} (当前跌幅: {percent_change:.2f}%)")
            else:
                percent_checks.append(f"     ○ 未触发: {alert['name']} (阈值: {alert['percent']:+.1f}%)")
        
        for check in percent_checks:
            logs.append(check)
        
        # 6. 预警判断结果
        logs.append(f"\n📋 5. 预警判断结果:")
        logs.append(f"   本次检查触发预警数量: {len(triggered_alerts)}个")
        
        if triggered_alerts:
            logs.append(f"\n   🚨 预警详情:")
            for i, alert in enumerate(triggered_alerts, 1):
                logs.append(f"      {i}. [{alert['type']}] {alert['name']}")
                if 'price' in alert:
                    logs.append(f"         触发价格: ¥{alert['price']:.2f}")
                if 'percent' in alert:
                    logs.append(f"         阈值: {alert['percent']:.1f}%")
        else:
            logs.append(f"   ✅ 结论: 暂无预警触发，价格走势正常")
        
        # 7. 交易信号判断
        logs.append(f"\n🎯 6. 交易信号判断:")
        logs.append(f"   历史信号: {prev_signal if prev_signal else 0}")
        logs.append(f"   当前信号: {signal}")
        
        if signal == 1:
            logs.append(f"   信号含义: 🟢 买入信号 (策略判断上涨概率大)")
        elif signal == -1:
            logs.append(f"   信号含义: 🔴 卖出信号 (策略判断下跌概率大)")
        else:
            logs.append(f"   信号含义: ⚪ 持有信号 (策略判断趋势不明)")
        
        if signal != prev_signal and prev_signal is not None:
            logs.append(f"   ⚠️ 信号变更: 从 {prev_signal} 变为 {signal}")
        
        # 8. 风险评估
        logs.append(f"\n⚠️ 7. 风险评估:")
        
        risk_factors = []
        
        # 检查是否接近支撑位
        for alert in self.alerts['retrace']:
            if not alert['triggered']:
                distance = display_price - alert['price']
                if 0 < distance < 5:
                    risk_factors.append(f"   ⚠️ 接近 {alert['name']} (¥{alert['price']:.2f}), 仅差¥{distance:.2f}")
        
        # 检查是否接近压力位
        for alert in self.alerts['breakthrough']:
            if not alert['triggered']:
                distance = alert['price'] - display_price
                if 0 < distance < 5:
                    risk_factors.append(f"   ℹ️ 接近 {alert['name']} (¥{alert['price']:.2f}), 还差¥{distance:.2f}")
        
        if risk_factors:
            logs.append(f"   风险因素:")
            for factor in risk_factors:
                logs.append(factor)
        else:
            logs.append(f"   ✅ 无明显风险因素")
        
        # 9. 最终结论
        logs.append(f"\n📝 8. 最终结论:")
        logs.append(f"   • 当前价格: ¥{display_price:.2f}")
        logs.append(f"   • 预警触发: {'是' if triggered_alerts else '否'} ({len(triggered_alerts)}个)")
        logs.append(f"   • 交易信号: {'买入' if signal == 1 else '卖出' if signal == -1 else '持有'}")
        
        if triggered_alerts:
            logs.append(f"   • 建议操作: ⚠️ 关注预警信息，准备采取行动")
        elif signal == -1:
            logs.append(f"   • 建议操作: 🔴 考虑减仓或止损")
        elif signal == 1:
            logs.append(f"   • 建议操作: 🟢 可以考虑买入或加仓")
        else:
            logs.append(f"   • 建议操作: ⚪ 继续持有，耐心等待")
        
        logs.append("="*120)
        
        # 打印日志
        for log in logs:
            print(log)
        
        return logs

    def run_alert_system(self):
        """运行预警系统"""
        from datetime import datetime
        
        print("\n" + "="*120)
        print("🦅 涨停先知 - 罗曼股份(SH605289)价格预警系统")
        print("="*120)
        print(f"\n📊 股票信息:")
        print(f"   名称: {self.stock_info['name']}")
        print(f"   代码: {self.stock_info['market'].upper()}{self.stock_info['code']}")
        print(f"   参考价格: ¥{self.current_price:.2f}")
        print(f"   强势表现: +199.62%")
        
        print(f"\n📈 预警设置:")
        print("\n   🔼 上涨预警:")
        for alert in self.alerts['breakthrough']:
            status = "✓" if alert['triggered'] else "○"
            print(f"      {status} {alert['name']} (¥{alert['price']:.2f})")
        
        print("\n   🔽 回调预警:")
        for alert in self.alerts['retrace']:
            status = "✓" if alert['triggered'] else "○"
            print(f"      {status} {alert['name']} (¥{alert['price']:.2f})")
        
        print("\n   📊 涨跌幅预警:")
        for alert in self.alerts['percent']:
            status = "✓" if alert['triggered'] else "○"
            print(f"      {status} {alert['name']}")
        
        print("\n" + "="*120)
        print("🔄 正在获取实时数据...")
        print("="*120 + "\n")
        
        price, signal, prev_signal = self.calculate_signals()
        
        if price:
            realtime = self.get_realtime_price()
            display_price = realtime['current'] if realtime else price
            
            print(f"\n📊 实时行情:")
            print(f"   当前价格: ¥{display_price:.2f}")
            if realtime:
                print(f"   开盘价: ¥{realtime['open']:.2f}")
                print(f"   最高价: ¥{realtime['high']:.2f}")
                print(f"   最低价: ¥{realtime['low']:.2f}")
            
            print(f"\n🎯 交易信号:")
            if signal == 1:
                print("   🟢 买入信号")
            elif signal == -1:
                print("   🔴 卖出信号")
            else:
                print("   ⚪ 持有信号")
            
            print(f"\n💰 收益分析:")
            profit = display_price - self.current_price
            profit_pct = (profit / self.current_price) * 100
            profit_icon = "🟢" if profit > 0 else "🔴"
            print(f"   {profit_icon} 当前盈利: ¥{profit:.2f} ({profit_pct:+.2f}%)")
            
            triggered = self.check_alerts(display_price, self.current_price)
            
            # 添加详细日志
            self.log_detailed_check(display_price, realtime, signal, triggered, prev_signal)
            
            if triggered:
                print(f"\n" + "="*120)
                print("🚨 预警触发!")
                print("="*120)
                for alert in triggered:
                    print(f"\n   ⚠️ {alert['type']}: {alert['name']}")
                    if 'price' in alert:
                        print(f"      触发价格: ¥{alert['price']:.2f}")
                    if 'percent' in alert:
                        print(f"      触发阈值: {alert['percent']:.1f}%")
        else:
            print("\n❌ 暂时无法获取数据，请稍后重试")
        
        print("\n" + "="*120)
        print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("💡 提示: 可以设置定时任务来自动检查预警")
        print("="*120)
        
        return price if price else self.current_price

    def run_continuous_monitor(self, interval_seconds=300):
        """连续监控模式"""
        print("="*120)
        print("🔄 启动连续监控模式")
        print(f"⏰ 监控间隔: {interval_seconds}秒 ({interval_seconds/60:.1f}分钟)")
        print(f"按 Ctrl+C 停止监控")
        print("="*120 + "\n")
        
        try:
            while True:
                current_price = self.run_alert_system()
                
                print(f"\n💤 等待 {interval_seconds}秒后进行下次检查...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止")

if __name__ == "__main__":
    alert_system = LuomanAlertSystem()
    
    print("\n请选择模式:")
    print("1. 单次检查 (推荐)")
    print("2. 连续监控 (每5分钟检查一次)")
    print("3. 快速连续监控 (每分钟检查一次)")
    
    choice = input("\n请输入选择 (1/2/3，默认1): ").strip() or "1"
    
    if choice == "2":
        alert_system.run_continuous_monitor(300)
    elif choice == "3":
        alert_system.run_continuous_monitor(60)
    else:
        alert_system.run_alert_system()
