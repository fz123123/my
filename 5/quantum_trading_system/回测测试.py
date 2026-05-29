#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode = True

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross
from backtest.enhanced_engine import EnhancedBacktestEngine

def test_backtest():
    print("="*70)
    print("     量子量化系统 - 策略回测测试")
    print("="*70)
    print()

    print("📊 测试配置:")
    print("   - 股票代码: 000001.SZ (平安银行)")
    print("   - 回测策略: 均线交叉策略")
    print("   - 初始资金: 100,000")
    print()

    print("🔄 步骤1: 初始化数据引擎...")
    try:
        data_engine = DataEngine()
        print("   ✅ 数据引擎初始化成功")
    except Exception as e:
        print(f"   ❌ 数据引擎初始化失败: {e}")
        return False

    print()
    print("📥 步骤2: 从akshare获取股票数据...")
    try:
        print("   正在从网络获取数据，请稍候...")
        df = data_engine.get_stock_data("000001.SZ")
        
        if df is None or len(df) == 0:
            print("   ❌ 数据获取失败")
            return False
        
        print(f"   ✅ 数据获取成功！")
        print(f"   - 数据条数: {len(df)} 条")
        print(f"   - 时间范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"   - 最新收盘价: {df['close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ❌ 数据获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("📊 步骤3: 计算技术指标...")
    try:
        df = calculate_indicators(df)
        print(f"   ✅ 指标计算完成")
        print(f"   - MA5: {df['ma5'].iloc[-1]:.2f}")
        print(f"   - MA20: {df['ma20'].iloc[-1]:.2f}")
        print(f"   - RSI: {df['rsi'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ❌ 指标计算失败: {e}")
        return False

    print()
    print("🎯 步骤4: 生成交易信号...")
    try:
        strategy = StrategyMaCross(short_period=5, long_period=20)
        signals = strategy.generate_signals(df)
        
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        
        print(f"   ✅ 信号生成完成")
        print(f"   - 买入信号: {buy_signals} 次")
        print(f"   - 卖出信号: {sell_signals} 次")
    except Exception as e:
        print(f"   ❌ 信号生成失败: {e}")
        return False

    print()
    print("🔄 步骤5: 运行回测引擎...")
    try:
        engine = EnhancedBacktestEngine(initial_capital=100000)
        result = engine.run_backtest(df, signals)
        
        if result is None:
            print("   ❌ 回测引擎运行失败")
            return False
        
        print("   ✅ 回测完成！")
    except Exception as e:
        print(f"   ❌ 回测运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("="*70)
    print("     回测结果")
    print("="*70)
    print()
    
    print(f"📈 收益指标:")
    print(f"   总收益率: {result['total_return_pct']:+.2f}%")
    print(f"   最终资金: ¥{result['final_equity']:,.2f}")
    print()
    
    print(f"📊 风险指标:")
    print(f"   最大回撤: {result['max_drawdown_pct']:.2f}%")
    print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
    print()
    
    print(f"🎯 交易统计:")
    print(f"   总交易次数: {result['total_trades']}")
    print(f"   胜率: {result['win_rate_pct']:.2f}%")
    print()
    
    if 'equity_curve' in result and len(result['equity_curve']) > 0:
        print("📉 净值曲线:")
        equity_df = result['equity_curve']
        print(f"   起始净值: {equity_df['equity'].iloc[0]:,.2f}")
        print(f"   最终净值: {equity_df['equity'].iloc[-1]:,.2f}")
        print()

    print("="*70)
    print("✅ 测试完成！akshare数据自动下载功能正常！")
    print("="*70)
    print()
    
    return True

if __name__ == "__main__":
    success = test_backtest()
    sys.exit(0 if success else 1)
