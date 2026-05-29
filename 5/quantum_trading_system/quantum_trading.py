#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quantum Trading System v3.0 - 全功能量化交易系统
整合策略回测、实时监控、参数优化、风险管理等核心功能
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_fetcher import DataFetcher
from core.data_engine import DataEngine
from core.indicators import calculate_indicators, calculate_kdj
from core.risk_engine import RiskEngine
from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor, StrategyGrid, StrategyGridAdvanced, StrategyGridScalping
from strategies.optimizer import StrategyOptimizer, StrategyPortfolio
from backtest.engine import BacktestEngine
from backtest.enhanced_engine import EnhancedBacktestEngine
from monitor.realtime_monitor import RealtimeMonitor
from utils.auto_manager import AutoManager
from config import config, save_config


def print_logo():
    logo = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        QUANTUM TRADING SYSTEM v3.0                                ║
║          全功能量化交易系统                                        ║
║                                                                   ║
║        ████████╗██████╗  █████╗ ███╗   ██╗███████╗██████╗       ║
║        ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔══██╗      ║
║           ██║   ██████╔╝███████║██╔██╗ ██║█████╗  ██████╔╝      ║
║           ██║   ██╔══██╗██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗      ║
║           ██║   ██║  ██║██║  ██║██║ ╚████║███████╗██║  ██║      ║
║           ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(logo)


def print_main_menu():
    menu = """
┌───────────────────────────────────────────────────────────────────┐
│                        主菜单                                     │
├───────────────────────────────────────────────────────────────────┤
│  [1]  快速回测        - 测试策略历史表现                           │
│  [2]  策略对比        - 多策略横向比较                             │
│  [3]  参数优化        - 网格搜索优化策略参数                       │
│  [4]  策略组合        - 多策略权重配置与分析                       │
│  [5]  实时监控        - 监控观察列表信号                           │
│  [6]  网格交易        - 网格策略回测与优化                         │
│  [7]  蒙特卡洛        - 风险模拟分析                               │
│  [8]  滚动窗口        - Walk-Forward分析                          │
│  [9]  数据管理        - 备份、恢复、清理                           │
│  [A]  系统设置        - 修改配置参数                               │
│  [0]  退出                                                         │
└───────────────────────────────────────────────────────────────────┘
    """
    print(menu)


def run_quick_backtest():
    print("\n" + "="*80)
    print("  快速回测")
    print("="*80)

    symbols = config['watchlist']
    if not symbols:
        symbols = ['000001.SZ', '600519.SH', 'BTCUSDT']

    print("\n可选标的:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\n选择标的 (1-{}, 回车选择全部): ".format(len(symbols)))
    selected_symbols = []
    if choice.strip() == "":
        selected_symbols = symbols[:5]
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(symbols):
                selected_symbols = [symbols[idx]]
        except:
            pass

    if not selected_symbols:
        print("未选择标的")
        return

    print("\n可选策略:")
    strategies = [
        ("ma_cross", "均线交叉", StrategyMaCross()),
        ("rsi", "RSI策略", StrategyRsi()),
        ("bollinger", "布林带", StrategyBollinger()),
        ("multifactor", "多因子", StrategyMultiFactor())
    ]

    for i, (name, desc, _) in enumerate(strategies, 1):
        print(f"  [{i}] {desc}")

    choice = input("\n选择策略 (1-{}, 回车选择全部): ".format(len(strategies)))
    selected_strategies = []
    if choice.strip() == "":
        selected_strategies = strategies
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(strategies):
                selected_strategies = [strategies[idx]]
        except:
            pass

    if not selected_strategies:
        print("未选择策略")
        return

    fetcher = DataFetcher()
    engine = EnhancedBacktestEngine()

    print("\n" + "="*110)
    print(f"{'标的':12} {'策略':12} {'收益率':10} {'最大回撤':10} {'夏普比率':8} {'交易数':8} {'胜率':8}")
    print("="*110)

    all_results = []

    for symbol in selected_symbols:
        if symbol.endswith('.SZ') or symbol.endswith('.SH'):
            df = fetcher.get_stock_data(symbol)
        else:
            df = fetcher.get_crypto_data(symbol)

        if df is None or len(df) < 60:
            print(f"{symbol:12} {'-':12} {'-':10} {'-':10} {'-':8} {'-':8} {'-':8}")
            continue

        for name, desc, strategy in selected_strategies:
            signals = strategy.generate_signals(df)
            result = engine.run_backtest(df, signals)

            if result:
                all_results.append({
                    'symbol': symbol,
                    'strategy': name,
                    'strategy_desc': desc,
                    **result
                })

                print(f"{symbol:12} {desc:12} {result['total_return_pct']:+10.2f}% "
                      f"{result['max_drawdown_pct']:10.2f}% {result['sharpe_ratio']:8.2f} "
                      f"{result['total_trades']:8} {result['win_rate_pct']:8.2f}%")

    print("="*110)

    if all_results:
        AutoManager().auto_save(all_results, 'backtest_results')

    input("\n按回车继续...")


def compare_strategies():
    print("\n" + "="*80)
    print("  策略对比分析")
    print("="*80)

    symbols = config['watchlist'][:5] if config['watchlist'] else ['000001.SZ']
    strategies = [
        ("ma_cross", "均线交叉", StrategyMaCross()),
        ("rsi", "RSI策略", StrategyRsi()),
        ("bollinger", "布林带", StrategyBollinger()),
        ("multifactor", "多因子", StrategyMultiFactor())
    ]

    fetcher = DataFetcher()
    engine = EnhancedBacktestEngine()

    print("\n" + "="*110)
    print(f"{'标的':12} {'策略':12} {'收益率':10} {'最大回撤':10} {'夏普比率':8} {'交易数':8} {'胜率':8}")
    print("="*110)

    all_comparisons = []

    for symbol in symbols:
        if symbol.endswith('.SZ') or symbol.endswith('.SH'):
            df = fetcher.get_stock_data(symbol)
        else:
            df = fetcher.get_crypto_data(symbol)

        if df is None or len(df) < 60:
            continue

        for name, desc, strategy in strategies:
            signals = strategy.generate_signals(df)
            result = engine.run_backtest(df, signals)

            if result:
                all_comparisons.append({
                    'symbol': symbol,
                    'strategy': name,
                    'strategy_desc': desc,
                    **result
                })

                print(f"{symbol:12} {desc:12} {result['total_return_pct']:+10.2f}% "
                      f"{result['max_drawdown_pct']:10.2f}% {result['sharpe_ratio']:8.2f} "
                      f"{result['total_trades']:8} {result['win_rate_pct']:8.2f}%")

    print("="*110)

    AutoManager().auto_save(all_comparisons, 'strategy_comparison')

    input("\n按回车继续...")


def optimize_parameters():
    print("\n" + "="*80)
    print("  策略参数优化")
    print("="*80)

    symbols = config['watchlist'][:3] if config['watchlist'] else ['000001.SZ']
    print("\n可选标的:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\n选择标的: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(symbols):
            symbol = symbols[idx]
        else:
            symbol = symbols[0]
    except:
        symbol = symbols[0]

    print(f"\n选择优化策略:")
    print("  [1] 均线交叉策略")
    print("  [2] RSI策略")

    choice = input("\n选择: ")
    optimizer = StrategyOptimizer()
    fetcher = DataFetcher()

    if symbol.endswith('.SZ') or symbol.endswith('.SH'):
        df = fetcher.get_stock_data(symbol)
    else:
        df = fetcher.get_crypto_data(symbol)

    if df is None or len(df) < 100:
        print("数据不足")
        return

    if choice == "2":
        result = optimizer.optimize_rsi(df)
    else:
        result = optimizer.optimize_ma_cross(df)

    if result:
        print(f"\n最优参数: {result['params']}")
        print(f"夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"收益率: {result['total_return_pct']:+.2f}%")

    input("\n按回车继续...")


def portfolio_analysis():
    print("\n" + "="*80)
    print("  策略组合分析")
    print("="*80)

    symbols = config['watchlist'][:3] if config['watchlist'] else ['000001.SZ']
    print("\n可选标的:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\n选择标的: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(symbols):
            symbol = symbols[idx]
        else:
            symbol = symbols[0]
    except:
        symbol = symbols[0]

    portfolio = StrategyPortfolio()

    print("\n选择组合策略 (空格分隔):")
    print("  [1] 均线交叉")
    print("  [2] RSI策略")
    print("  [3] 布林带")
    print("  [4] 多因子")

    choices = input("\n输入数字 (如: 1 2 4): ").strip().split()

    strategy_map = {
        '1': ('均线交叉', StrategyMaCross()),
        '2': ('RSI策略', StrategyRsi()),
        '3': ('布林带', StrategyBollinger()),
        '4': ('多因子', StrategyMultiFactor())
    }

    for c in choices:
        if c in strategy_map:
            name, strategy = strategy_map[c]
            portfolio.add_strategy(strategy, name=name)

    if not portfolio.strategies:
        print("未选择任何策略")
        return

    fetcher = DataFetcher()

    if symbol.endswith('.SZ') or symbol.endswith('.SH'):
        df = fetcher.get_stock_data(symbol)
    else:
        df = fetcher.get_crypto_data(symbol)

    if df is None or len(df) < 60:
        print("数据不足")
        return

    result = portfolio.get_strategy_performance(df)
    print("\n" + "="*80)
    print(result.to_string(index=False))
    print("="*80)

    input("\n按回车继续...")


def run_monitor():
    monitor = RealtimeMonitor(strict_mode=False)
    interval = config['monitor']['refresh_interval']
    print(f"\n启动实时监控，刷新间隔: {interval}秒")
    monitor.run_monitor(interval=interval)


def grid_trading():
    print("\n" + "="*80)
    print("  网格交易策略")
    print("="*80)

    symbols = config['watchlist'][:3] if config['watchlist'] else ['000001.SZ', 'BTCUSDT']
    print("\n可选标的:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\n选择标的: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(symbols):
            symbol = symbols[idx]
        else:
            symbol = symbols[0]
    except:
        symbol = symbols[0]

    print("\n选择网格策略:")
    print("  [1] 基础网格 - 固定区间网格交易")
    print("  [2] 增强网格 - 带过滤条件的动态网格")
    print("  [3] 高频网格 - 短线剥头皮策略")

    choice = input("\n选择策略 (1-3): ")
    
    if choice == "2":
        strategy = StrategyGridAdvanced(grid_levels=5, grid_range_pct=0.10, 
                                       volume_filter=True, rsi_filter=True)
        strategy_name = "增强网格"
    elif choice == "3":
        strategy = StrategyGridScalping(profit_target=0.003, loss_limit=0.008)
        strategy_name = "高频网格"
    else:
        strategy = StrategyGrid(grid_levels=5, grid_range_pct=0.10)
        strategy_name = "基础网格"

    fetcher = DataFetcher()
    engine = EnhancedBacktestEngine()

    if symbol.endswith('.SZ') or symbol.endswith('.SH'):
        df = fetcher.get_stock_data(symbol)
    else:
        df = fetcher.get_crypto_data(symbol)

    if df is None or len(df) < 100:
        print("数据不足")
        return

    signals = strategy.generate_signals(df)
    result = engine.run_backtest(df, signals)

    if result:
        print(f"\n{strategy_name} 回测结果:")
        print("-" * 80)
        print(f"标的: {symbol}")
        print(f"收益率: {result['total_return_pct']:+.2f}%")
        print(f"最大回撤: {result['max_drawdown_pct']:.2f}%")
        print(f"夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate_pct']:.2f}%")

        if hasattr(strategy, 'get_grid_info'):
            grid_info = strategy.get_grid_info()
            print(f"\n网格参数:")
            print(f"  网格层数: {grid_info.get('levels', 5)}")
            print(f"  网格范围: {grid_info.get('range_pct', 0.10) * 100:.1f}%")
            if grid_info.get('grid_lines'):
                print(f"  网格线数量: {len(grid_info['grid_lines'])}")

    input("\n按回车继续...")


def monte_carlo_simulation():
    print("\n" + "="*80)
    print("  蒙特卡洛风险模拟")
    print("="*80)

    symbols = config['watchlist'][:3] if config['watchlist'] else ['000001.SZ']
    print("\n可选标的:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\n选择标的: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(symbols):
            symbol = symbols[idx]
        else:
            symbol = symbols[0]
    except:
        symbol = symbols[0]

    fetcher = DataFetcher()
    engine = EnhancedBacktestEngine()

    if symbol.endswith('.SZ') or symbol.endswith('.SH'):
        df = fetcher.get_stock_data(symbol)
    else:
        df = fetcher.get_crypto_data(symbol)

    if df is None or len(df) < 100:
        print("数据不足")
        return

    strategy = StrategyMultiFactor()
    signals = strategy.generate_signals(df)

    n_simulations = input("输入模拟次数 (默认1000): ")
    try:
        n_simulations = int(n_simulations)
    except:
        n_simulations = 1000

    engine.run_monte_carlo(df, signals, n_simulations=n_simulations)

    input("\n按回车继续...")


def walk_forward_analysis():
    print("\n" + "="*80)
    print("  滚动窗口分析 (Walk-Forward)")
    print("="*80)

    symbols = config['watchlist'][:3] if config['watchlist'] else ['000001.SZ']
    print("\n可选标的:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\n选择标的: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(symbols):
            symbol = symbols[idx]
        else:
            symbol = symbols[0]
    except:
        symbol = symbols[0]

    fetcher = DataFetcher()
    engine = EnhancedBacktestEngine()

    if symbol.endswith('.SZ') or symbol.endswith('.SH'):
        df = fetcher.get_stock_data(symbol)
    else:
        df = fetcher.get_crypto_data(symbol)

    if df is None or len(df) < 360:
        print("数据不足（需要至少360天数据）")
        return

    strategy = StrategyMultiFactor()
    signals = strategy.generate_signals(df)

    engine.run_walk_forward_analysis(df, signals)

    input("\n按回车继续...")


def data_management():
    auto_manager = AutoManager()

    while True:
        print("\n" + "="*80)
        print("  数据管理")
        print("="*80)
        print("""
┌───────────────────────────────────────────────────────────────────┐
│  [1]  列出备份                                                     │
│  [2]  立即备份                                                     │
│  [3]  恢复备份                                                     │
│  [4]  清理旧备份                                                   │
│  [0]  返回                                                         │
└───────────────────────────────────────────────────────────────────┘
        """)

        choice = input("选择操作: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            backups = auto_manager.list_backups()
            print("\n备份列表:")
            for i, bk in enumerate(backups, 1):
                size_mb = bk['size'] / 1024 / 1024
                print(f"  [{i}] {bk['name']} - {size_mb:.2f}MB - {bk['time'].strftime('%Y-%m-%d %H:%M')}")
        elif choice == "2":
            print("\n正在备份...")
            result = auto_manager.auto_backup(force=True)
            if result:
                print(f"备份完成: {result}")
        elif choice == "3":
            backups = auto_manager.list_backups()
            if not backups:
                print("\n无可用备份")
                continue
            print("\n选择要恢复的备份:")
            for i, bk in enumerate(backups, 1):
                print(f"  [{i}] {bk['name']}")
            idx = input("\n输入序号: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(backups):
                    auto_manager.restore_backup(backups[idx]['name'])
            except:
                print("无效选择")
        elif choice == "4":
            auto_manager.cleanup_old_backups()
            print("清理完成")


def system_settings():
    print("\n" + "="*80)
    print("  系统设置")
    print("="*80)

    print(f"\n当前配置:")
    print(f"  自动保存: {'启用' if config['auto_save'] else '禁用'}")
    print(f"  自动备份: {'启用' if config['auto_backup'] else '禁用'}")
    print(f"  备份间隔: {config['backup_interval_hours']} 小时")
    print(f"  初始资金: {config['trading']['initial_capital']:,}")
    print(f"  手续费率: {config['trading']['fee_rate']*10000:.1f}‰")
    print(f"  监控间隔: {config['monitor']['refresh_interval']} 秒")

    while True:
        print("""
┌───────────────────────────────────────────────────────────────────┐
│  [1]  修改观察列表                                                 │
│  [2]  切换自动保存                                                 │
│  [3]  切换自动备份                                                 │
│  [4]  修改初始资金                                                 │
│  [5]  修改监控间隔                                                 │
│  [0]  返回                                                         │
└───────────────────────────────────────────────────────────────────┘
        """)

        choice = input("选择操作: ").strip()

        if choice == "0":
            save_config(config)
            break
        elif choice == "1":
            print(f"\n当前观察列表: {', '.join(config['watchlist'][:5])}" + ("..." if len(config['watchlist']) > 5 else ""))
            new_list = input("输入新观察列表 (逗号分隔): ").strip()
            if new_list:
                config['watchlist'] = [s.strip() for s in new_list.split(',')]
                print("已更新")
        elif choice == "2":
            config['auto_save'] = not config['auto_save']
            print(f"自动保存: {'启用' if config['auto_save'] else '禁用'}")
        elif choice == "3":
            config['auto_backup'] = not config['auto_backup']
            print(f"自动备份: {'启用' if config['auto_backup'] else '禁用'}")
        elif choice == "4":
            capital = input("输入初始资金: ").strip()
            try:
                config['trading']['initial_capital'] = float(capital)
                print("已更新")
            except:
                print("无效输入")
        elif choice == "5":
            interval = input("输入监控间隔(秒): ").strip()
            try:
                config['monitor']['refresh_interval'] = int(interval)
                print("已更新")
            except:
                print("无效输入")


def main():
    print_logo()

    AutoManager().auto_backup()

    while True:
        print_main_menu()
        choice = input("选择功能 (0-9, A): ").strip()

        if choice == "0":
            AutoManager().auto_backup(force=True)
            print("\n感谢使用 量子交易系统! 再见!\n")
            break
        elif choice == "1":
            run_quick_backtest()
        elif choice == "2":
            compare_strategies()
        elif choice == "3":
            optimize_parameters()
        elif choice == "4":
            portfolio_analysis()
        elif choice == "5":
            run_monitor()
        elif choice == "6":
            grid_trading()
        elif choice == "7":
            monte_carlo_simulation()
        elif choice == "8":
            walk_forward_analysis()
        elif choice == "9":
            data_management()
        elif choice.upper() == "A":
            system_settings()


if __name__ == "__main__":
    main()