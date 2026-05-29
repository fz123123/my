#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版鹰眼压金 - 智能量化交易系统 v2.0
集成涨停先知回测引擎
支持多种策略回测、参数优化、风险控制
"""

import subprocess
import time
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class EagleEyeSystem:
    def __init__(self):
        self.initial_capital = 100000
        self.commission = 0.0015
        self.stop_loss = 0.08
        self.take_profit = 0.15
        
    def print_banner(self):
        os.system('cls')
        print("""
   ██████╗  █████╗ ██╗   ██╗██╗  ██╗███████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
   ██╔══██╗██╔══██╗██║   ██║██║ ██╔╝██╔════╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝
   ██████╔╝███████║██║   ██║█████╔╝ ███████╗    ███████║██║   ██║██╔██╗ ██║   ██║   
   ██╔═══╝ ██╔══██║██║   ██║██╔═██╗ ╚════██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   
   ██║     ██║  ██║╚██████╔╝██║  ██╗███████║    ██║  ██║╚██████╔╝██║ ╚████║   ██║   
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
                                                                                        
    ╔══════════════════════════════════════════════════════════════╗
    ║      🦅 鹰眼压金 - 智能量化交易系统 v2.0                  ║
    ║                                                              ║
    ║         ⚡ 涨停先知回测引擎 ⚡                              ║
    ║         📊 支持5大策略 + 参数优化                           ║
    ║         🛡️ 智能止损止盈 + 风险控制                          ║
    ╚══════════════════════════════════════════════════════════════╝
        """)
    
    def menu(self):
        print("\n" + "="*80)
        print("📋 系统功能菜单")
        print("="*80)
        print("  1. 📊 策略回测 (MACD / KDJ / MA / RSI / 组合)")
        print("  2. 🏆 策略对比分析")
        print("  3. 🔧 参数优化")
        print("  4. 📈 实时行情监控")
        print("  5. 💰 低吸扫描")
        print("  6. 🎯 技术分析")
        print("  7. 💼 持仓管理")
        print("  8. ⚙️ 系统设置")
        print("  9. 📖 使用帮助")
        print("  0. 🚪 退出系统")
        print("="*80)
    
    def generate_data(self, days=250, trend='bull'):
        """生成模拟历史数据"""
        dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
        
        data = {
            'date': dates,
            'open': [], 'high': [], 'low': [], 'close': [], 'volume': []
        }
        
        if trend == 'bull':
            base_return = 0.0004
            volatility = 0.015
        elif trend == 'bear':
            base_return = -0.0003
            volatility = 0.02
        else:
            base_return = 0.0002
            volatility = 0.018
            
        price = 25.0
        for i in range(days):
            daily_return = np.random.normal(base_return, volatility)
            open_price = price * (1 + np.random.normal(0, 0.005))
            close_price = price * (1 + daily_return)
            high_price = max(open_price, close_price) * (1 + abs(np.random.uniform(0, 0.015)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.uniform(0, 0.015)))
            volume = int(np.random.normal(500000, 200000))
            
            data['open'].append(round(open_price, 2))
            data['high'].append(round(high_price, 2))
            data['low'].append(round(low_price, 2))
            data['close'].append(round(close_price, 2))
            data['volume'].append(max(100000, volume))
            price = close_price
            
        return pd.DataFrame(data).set_index('date')
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['dif'] = (df['ema12'] - df['ema26']).round(4)
        df['dea'] = df['dif'].ewm(span=9, adjust=False).mean().round(4)
        df['macd'] = ((df['dif'] - df['dea']) * 2).round(4)
        
        low_min = df['low'].rolling(9).min()
        high_max = df['high'].rolling(9).max()
        df['rsv'] = ((df['close'] - low_min) / (high_max - low_min) * 100).round(2)
        df['k'] = df['rsv'].ewm(com=2, adjust=False).mean().round(2)
        df['d'] = df['k'].ewm(com=2, adjust=False).mean().round(2)
        df['j'] = (3 * df['k'] - 2 * df['d']).round(2)
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = (100 - (100 / (1 + rs))).round(2)
        
        df['boll_mid'] = df['close'].rolling(20).mean()
        df['boll_std'] = df['close'].rolling(20).std()
        df['boll_upper'] = (df['boll_mid'] + 2 * df['boll_std']).round(2)
        df['boll_lower'] = (df['boll_mid'] - 2 * df['boll_std']).round(2)
        
        df['volume_ma5'] = df['volume'].rolling(5).mean()
        df['volume_ratio'] = (df['volume'] / df['volume_ma5']).round(2)
        
        return df
    
    def macd_strategy(self, df):
        """MACD策略"""
        df['signal'] = 0
        for i in range(1, len(df)):
            dif, dea = df['dif'].iloc[i], df['dea'].iloc[i]
            dif_prev, dea_prev = df['dif'].iloc[i-1], df['dea'].iloc[i-1]
            
            if dif_prev <= dea_prev and dif > dea:
                df.loc[df.index[i], 'signal'] = 1
            elif dif_prev >= dea_prev and dif < dea:
                df.loc[df.index[i], 'signal'] = -1
        return df
    
    def kdj_strategy(self, df):
        """KDJ策略"""
        df['signal'] = 0
        for i in range(1, len(df)):
            k, d = df['k'].iloc[i], df['d'].iloc[i]
            k_prev, d_prev = df['k'].iloc[i-1], df['d'].iloc[i-1]
            
            if k_prev <= d_prev and k > d and k < 30:
                df.loc[df.index[i], 'signal'] = 1
            elif k_prev >= d_prev and k < d and k > 70:
                df.loc[df.index[i], 'signal'] = -1
        return df
    
    def ma_strategy(self, df):
        """均线策略"""
        df['signal'] = 0
        for i in range(1, len(df)):
            ma5, ma20 = df['ma5'].iloc[i], df['ma20'].iloc[i]
            ma5_prev, ma20_prev = df['ma5'].iloc[i-1], df['ma20'].iloc[i-1]
            
            if pd.notna(ma5) and pd.notna(ma20):
                if ma5_prev <= ma20_prev and ma5 > ma20:
                    df.loc[df.index[i], 'signal'] = 1
                elif ma5_prev >= ma20_prev and ma5 < ma20:
                    df.loc[df.index[i], 'signal'] = -1
        return df
    
    def rsi_strategy(self, df):
        """RSI策略"""
        df['signal'] = 0
        for i in range(len(df)):
            rsi = df['rsi'].iloc[i]
            if pd.notna(rsi):
                if rsi < 30:
                    df.loc[df.index[i], 'signal'] = 1
                elif rsi > 70:
                    df.loc[df.index[i], 'signal'] = -1
        return df
    
    def combined_strategy(self, df):
        """组合策略"""
        df = self.macd_strategy(df.copy())
        df['macd_s'] = df['signal']
        
        df = self.kdj_strategy(df.copy())
        df['kdj_s'] = df['signal']
        
        df = self.ma_strategy(df.copy())
        df['ma_s'] = df['signal']
        
        df = self.rsi_strategy(df.copy())
        df['rsi_s'] = df['signal']
        
        df['signal'] = 0
        for i in range(len(df)):
            buy = sum([df['macd_s'].iloc[i]==1, df['kdj_s'].iloc[i]==1, 
                      df['ma_s'].iloc[i]==1, df['rsi_s'].iloc[i]==1])
            sell = sum([df['macd_s'].iloc[i]==-1, df['kdj_s'].iloc[i]==-1, 
                       df['ma_s'].iloc[i]==-1, df['rsi_s'].iloc[i]==-1])
            
            if buy >= 2:
                df.loc[df.index[i], 'signal'] = 1
            elif sell >= 2:
                df.loc[df.index[i], 'signal'] = -1
                
        return df
    
    def run_backtest(self, df, strategy='macd', stop_loss=0.08, take_profit=0.15):
        """运行回测"""
        data = self.calculate_indicators(df.copy())
        
        if strategy == 'macd':
            data = self.macd_strategy(data)
        elif strategy == 'kdj':
            data = self.kdj_strategy(data)
        elif strategy == 'ma':
            data = self.ma_strategy(data)
        elif strategy == 'rsi':
            data = self.rsi_strategy(data)
        else:
            data = self.combined_strategy(data)
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        portfolio = []
        
        for date, row in data.iterrows():
            price = row['close']
            signal = row['signal']
            
            if position > 0:
                profit_pct = (price - entry_price) / entry_price
                
                if profit_pct <= -stop_loss:
                    capital += position * price * (1 - self.commission)
                    trades.append(('sell', date, price, position, '止损'))
                    position = 0
                elif profit_pct >= take_profit:
                    capital += position * price * (1 - self.commission)
                    trades.append(('sell', date, price, position, '止盈'))
                    position = 0
                elif signal == -1:
                    capital += position * price * (1 - self.commission)
                    trades.append(('sell', date, price, position, '信号'))
                    position = 0
            else:
                if signal == 1:
                    shares = int(capital / price / 100) * 100
                    cost = shares * price * (1 + self.commission)
                    if cost <= capital and shares > 0:
                        position = shares
                        entry_price = price
                        capital -= cost
                        trades.append(('buy', date, price, shares, ''))
            
            portfolio.append(capital + position * price)
        
        data['portfolio'] = portfolio
        
        initial = self.initial_capital
        final = portfolio[-1]
        total_return = (final - initial) / initial * 100
        
        days = len(data)
        years = days / 250
        ann_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        peak = portfolio[0]
        max_drawdown = 0
        for val in portfolio:
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100
            if dd > max_drawdown:
                max_drawdown = dd
        
        sell_trades = [t for t in trades if t[0] == 'sell']
        win = sum(1 for i in range(0, len(sell_trades), 1) 
                 if i+1 < len(trades) and 
                 trades[i*2+1][2] > trades[i*2][2] if i*2+1 < len(trades))
        win_rate = win / len(sell_trades) * 100 if sell_trades else 0
        
        return {
            'strategy': strategy,
            'initial': initial,
            'final': round(final, 2),
            'return': round(total_return, 2),
            'ann_return': round(ann_return, 2),
            'max_dd': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'trades': len(sell_trades),
            'trades_detail': trades,
            'portfolio': portfolio,
            'data': data
        }
    
    def run_all_strategies(self):
        """运行所有策略对比"""
        print("\n" + "="*80)
        print("🏆 策略对比分析")
        print("="*80)
        
        data = self.generate_data(days=250, trend='bull')
        strategies = ['macd', 'kdj', 'ma', 'rsi', 'combined']
        results = {}
        
        for strategy in strategies:
            print(f"\n📊 运行 {strategy.upper()} 策略回测...", end=' ')
            result = self.run_backtest(data.copy(), strategy)
            results[strategy] = result
            print("✅")
        
        print("\n" + "="*80)
        print("📈 回测结果汇总")
        print("="*80)
        print(f"{'策略':<12} {'总收益':<12} {'年化':<12} {'最大回撤':<12} {'胜率':<10} {'交易次数':<10} {'夏普比率':<10}")
        print("-"*80)
        
        sorted_results = sorted(results.items(), key=lambda x: -x[1]['return'])
        
        for name, res in sorted_results:
            print(f"{name.upper():<12} {res['return']:>10.2f}%   {res['ann_return']:>10.2f}%   {res['max_dd']:>10.2f}%   {res['win_rate']:>8.2f}%   {res['trades']:>8d}   {'0.00':>8}")
        
        best = sorted_results[0]
        
        print("\n" + "="*80)
        print(f"🥇 最优策略: {best[0].upper()}")
        print("="*80)
        print(f"   总收益: {best[1]['return']}%")
        print(f"   年化收益: {best[1]['ann_return']}%")
        print(f"   最大回撤: {best[1]['max_dd']}%")
        print(f"   胜率: {best[1]['win_rate']}%")
        print(f"   交易次数: {best[1]['trades']}次")
        
        return results, best
    
    def optimize_parameters(self):
        """参数优化"""
        print("\n" + "="*80)
        print("🔧 参数优化")
        print("="*80)
        
        data = self.generate_data(days=250, trend='bull')
        
        print("\n📊 正在测试不同止损止盈参数...")
        
        best_return = float('-inf')
        best_params = None
        all_results = []
        
        for stop_loss in [0.05, 0.08, 0.10, 0.12]:
            for take_profit in [0.10, 0.15, 0.20, 0.25]:
                result = self.run_backtest(data.copy(), 'kdj', stop_loss, take_profit)
                all_results.append({
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    **result
                })
                
                if result['return'] > best_return:
                    best_return = result['return']
                    best_params = (stop_loss, take_profit)
        
        all_results.sort(key=lambda x: -x['return'])
        
        print("\n🏅 TOP 5 参数组合:")
        print("-"*80)
        print(f"{'止损':<10} {'止盈':<10} {'总收益':<12} {'年化':<12} {'最大回撤':<12} {'胜率':<10}")
        print("-"*80)
        
        for res in all_results[:5]:
            print(f"{res['stop_loss']*100:>8.0f}%   {res['take_profit']*100:>8.0f}%   {res['return']:>10.2f}%   {res['ann_return']:>10.2f}%   {res['max_dd']:>10.2f}%   {res['win_rate']:>8.2f}%")
        
        print(f"\n✅ 最优参数:")
        print(f"   止损: {best_params[0]*100}%")
        print(f"   止盈: {best_params[1]*100}%")
        print(f"   预期收益: {best_return}%")
        
        return best_params
    
    def single_backtest(self, strategy='combined'):
        """单策略详细回测"""
        print(f"\n{'='*80}")
        print(f"📊 {strategy.upper()} 策略详细回测")
        print(f"{'='*80}")
        
        data = self.generate_data(days=250, trend='bull')
        result = self.run_backtest(data.copy(), strategy)
        
        print(f"\n📈 核心指标:")
        print(f"   初始资金: ¥{result['initial']:,}")
        print(f"   最终资金: ¥{result['final']:,}")
        print(f"   总收益: {result['return']}%")
        print(f"   年化收益: {result['ann_return']}%")
        print(f"   最大回撤: {result['max_dd']}%")
        print(f"   胜率: {result['win_rate']}%")
        print(f"   交易次数: {result['trades']}次")
        
        print(f"\n💹 交易记录:")
        trades = result['trades_detail']
        buy_count = 0
        sell_count = 0
        
        for trade in trades:
            if trade[0] == 'buy':
                buy_count += 1
                print(f"\n{buy_count}. {trade[1].strftime('%Y-%m-%d')} 🟢 买入")
                print(f"   价格: ¥{trade[2]:.2f} | 数量: {trade[3]}股 | 成本: ¥{trade[2]*trade[3]:.2f}")
            else:
                sell_count += 1
                reason_icon = "🛑" if trade[4]=='止损' else "🎯" if trade[4]=='止盈' else "📊"
                print(f"   {sell_count}. {trade[1].strftime('%Y-%m-%d')} 🔴 {reason_icon} {trade[4]}")
                print(f"   价格: ¥{trade[2]:.2f} | 数量: {trade[3]}股")
                if buy_count > 0:
                    buy_price = trades[buy_count*2-2][2]
                    profit = (trade[2] - buy_price) * trade[3]
                    profit_icon = "🟢" if profit > 0 else "🔴"
                    print(f"   盈亏: {profit_icon} ¥{profit:.2f}")
        
        print(f"\n📉 收益曲线:")
        print("-"*80)
        portfolio = result['portfolio']
        dates = result['data'].index
        
        min_val = min(portfolio)
        max_val = max(portfolio)
        normalized = [(v - min_val) / (max_val - min_val) * 25 for v in portfolio]
        
        step = max(1, len(dates) // 15)
        for i in range(0, len(dates), step):
            date_str = dates[i].strftime('%m-%d')
            bar = "█" * int(normalized[i]) + "░" * (25 - int(normalized[i]))
            value = f"¥{portfolio[i]:,.0f}"
            marker = "▲" if portfolio[i] >= self.initial_capital else "▼"
            print(f"{date_str} {marker} {bar} {value}")
        
        return result
    
    def start_original_system(self):
        """启动原系统"""
        print("\n🚀 正在启动鹰眼压金全能版...")
        try:
            subprocess.Popen(
                'start cmd /k "python C:\\Users\\Administrator\\Desktop\\鹰眼压金_全能版.py"',
                shell=True
            )
            print("✅ 原系统已启动!")
        except Exception as e:
            print(f"❌ 启动失败: {e}")
    
    def run(self):
        """运行主程序"""
        self.print_banner()
        
        while True:
            self.menu()
            choice = input("\n请输入选择 (0-9): ").strip()
            
            if choice == '1':
                strategy = input("选择策略 (macd/kdj/ma/rsi/combined): ").strip().lower()
                if strategy not in ['macd', 'kdj', 'ma', 'rsi', 'combined']:
                    strategy = 'combined'
                self.single_backtest(strategy)
                input("\n按回车键继续...")
                
            elif choice == '2':
                self.run_all_strategies()
                input("\n按回车键继续...")
                
            elif choice == '3':
                self.optimize_parameters()
                input("\n按回车键继续...")
                
            elif choice == '4':
                print("\n📈 实时行情监控功能")
                print("请访问 http://localhost:5174 查看涨停先知系统")
                input("\n按回车键继续...")
                
            elif choice == '5':
                print("\n💰 低吸扫描功能")
                print("功能开发中...")
                input("\n按回车键继续...")
                
            elif choice == '6':
                print("\n🎯 技术分析功能")
                print("功能开发中...")
                input("\n按回车键继续...")
                
            elif choice == '7':
                print("\n💼 持仓管理功能")
                print("功能开发中...")
                input("\n按回车键继续...")
                
            elif choice == '8':
                print("\n⚙️ 系统设置")
                self.initial_capital = float(input(f"初始资金 (当前: ¥{self.initial_capital}): ").strip() or self.initial_capital)
                self.stop_loss = float(input(f"止损比例 (当前: {self.stop_loss*100}%): ").strip() or self.stop_loss) / 100
                self.take_profit = float(input(f"止盈比例 (当前: {self.take_profit*100}%): ").strip() or self.take_profit) / 100
                print(f"\n✅ 设置已保存:")
                print(f"   初始资金: ¥{self.initial_capital:,}")
                print(f"   止损: {self.stop_loss*100}%")
                print(f"   止盈: {self.take_profit*100}%")
                input("\n按回车键继续...")
                
            elif choice == '9':
                print("""
\n📖 使用帮助
================

1. 策略回测: 选择策略进行详细回测分析
2. 策略对比: 对比所有策略表现
3. 参数优化: 优化止损止盈参数
4. 实时行情: 查看实时股票数据
5-7. 其他功能: 功能开发中

策略说明:
- MACD: 趋势跟踪策略
- KDJ: 超买超卖策略  
- MA: 均线交叉策略
- RSI: 相对强弱策略
- COMBINED: 多指标组合策略

风险提示:
- 回测结果仅供参考
- 过去表现不代表未来
- 投资有风险,入市需谨慎
                """)
                input("\n按回车键继续...")
                
            elif choice == '0':
                print("\n" + "="*80)
                print("🦅 感谢使用鹰眼压金智能量化交易系统!")
                print("="*80)
                break
                
            elif choice == 'x':
                self.start_original_system()
                input("\n按回车键继续...")
                
            else:
                print("\n❌ 无效选择,请重试!")

if __name__ == "__main__":
    system = EagleEyeSystem()
    system.run()