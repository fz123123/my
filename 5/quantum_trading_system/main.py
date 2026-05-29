import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_fetcher import DataFetcher
from backtest.engine import BacktestEngine
from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor
from core.indicators import calculate_indicators
from utils.auto_manager import AutoManager
from monitor.realtime_monitor import RealtimeMonitor
from config import config, save_config


def print_logo():
    logo = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        QUANTUM TRADING SYSTEM v3.0                                ║
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


def print_menu():
    menu = """
┌───────────────────────────────────────────────────────────────────┐
│                        MAIN MENU                                 │
├───────────────────────────────────────────────────────────────────┤
│  [1]  Quick Backtest    - Test strategy performance              │
│  [2]  Strategy Compare  - Compare different strategies           │
│  [3]  Real-time Monitor - Monitor watchlist signals              │
│  [4]  Data Management   - View and backup data                   │
│  [5]  System Settings   - Modify configuration                   │
│  [0]  Exit                                                       │
└───────────────────────────────────────────────────────────────────┘
    """
    print(menu)


def run_backtest():
    print("\n" + "="*80)
    print("  Quick Backtest")
    print("="*80)

    symbols = config['watchlist']

    print("\nAvailable symbols:")
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}] {sym}")

    choice = input("\nSelect symbol (1-{}, enter for all): ".format(len(symbols)))

    selected_symbols = []
    if choice.strip() == "":
        selected_symbols = symbols
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(symbols):
                selected_symbols = [symbols[idx]]
        except:
            pass

    if not selected_symbols:
        print("No symbols selected")
        return

    print("\nAvailable strategies:")
    strategies = [
        ("ma_cross", "MA Cross", StrategyMaCross()),
        ("rsi", "RSI", StrategyRsi()),
        ("bollinger", "Bollinger", StrategyBollinger()),
        ("multifactor", "Multi-Factor", StrategyMultiFactor())
    ]

    for i, (name, desc, _) in enumerate(strategies, 1):
        print(f"  [{i}] {desc}")

    choice = input("\nSelect strategy (1-{}, enter for all): ".format(len(strategies)))

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
        print("No strategy selected")
        return

    fetcher = DataFetcher()
    engine = BacktestEngine()
    auto_manager = AutoManager()

    all_results = []

    for symbol in selected_symbols:
        print(f"\n{'─'*80}")
        print(f"Backtesting: {symbol}")
        print('─'*80)

        if symbol.endswith('.SZ') or symbol.endswith('.SH'):
            df = fetcher.get_stock_data(symbol)
        else:
            df = fetcher.get_crypto_data(symbol)

        if df is None or len(df) < 60:
            print(f"Insufficient data, skipping {symbol}")
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

                print(f"\nStrategy: {desc}")
                print(f"  Total Return: {result['total_return_pct']:+.2f}%")
                print(f"  Max Drawdown: {result['max_drawdown_pct']:.2f}%")
                print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
                print(f"  Total Trades: {result['total_trades']}")
                print(f"  Win Rate: {result['win_rate_pct']:.2f}%")

    if all_results:
        auto_manager.auto_save(all_results, 'backtest_results')
        auto_manager.auto_backup(force=True)

    input("\nPress Enter to continue...")


def compare_strategies():
    print("\n" + "="*80)
    print("  Strategy Comparison")
    print("="*80)

    symbols = config['watchlist']
    strategies = [
        ("ma_cross", "MA Cross", StrategyMaCross()),
        ("rsi", "RSI", StrategyRsi()),
        ("bollinger", "Bollinger", StrategyBollinger()),
        ("multifactor", "Multi-Factor", StrategyMultiFactor())
    ]

    fetcher = DataFetcher()
    engine = BacktestEngine()

    print("\n" + "="*110)
    print(f"{'Symbol':12} {'Strategy':12} {'Return':10} {'Drawdown':10} {'Sharpe':8} {'Trades':8} {'Win%':8}")
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

    input("\nPress Enter to continue...")


def run_monitor():
    monitor = RealtimeMonitor()
    interval = config['monitor']['refresh_interval']
    monitor.run_monitor(interval=interval)


def data_management():
    auto_manager = AutoManager()

    print("\n" + "="*80)
    print("  Data Management")
    print("="*80)

    while True:
        print("""
┌───────────────────────────────────────────────────────────────────┐
│  [1]  List backups                                               │
│  [2]  Backup now                                                 │
│  [3]  Restore backup                                             │
│  [4]  Clean old backups                                          │
│  [0]  Return                                                     │
└───────────────────────────────────────────────────────────────────┘
        """)

        choice = input("Select option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            backups = auto_manager.list_backups()
            print("\nBackup list:")
            for i, bk in enumerate(backups, 1):
                size_mb = bk['size'] / 1024 / 1024
                print(f"  [{i}] {bk['name']} - {size_mb:.2f}MB - {bk['time'].strftime('%Y-%m-%d %H:%M')}")
        elif choice == "2":
            print("\nStarting backup...")
            result = auto_manager.auto_backup(force=True)
            if result:
                print(f"Backup completed: {result}")
        elif choice == "3":
            backups = auto_manager.list_backups()
            if not backups:
                print("\nNo backups available")
                continue
            print("\nSelect backup to restore:")
            for i, bk in enumerate(backups, 1):
                print(f"  [{i}] {bk['name']}")
            idx = input("\nEnter number: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(backups):
                    auto_manager.restore_backup(backups[idx]['name'])
            except:
                print("Invalid selection")
        elif choice == "4":
            auto_manager.auto_cleanup()
            print("Cleanup completed")


def system_settings():
    print("\n" + "="*80)
    print("  System Settings")
    print("="*80)

    print(f"\nCurrent configuration:")
    print(f"  Auto Save: {'Enabled' if config['auto_save'] else 'Disabled'}")
    print(f"  Auto Backup: {'Enabled' if config['auto_backup'] else 'Disabled'}")
    print(f"  Backup Interval: {config['backup_interval_hours']} hours")
    print(f"  Initial Capital: {config['trading']['initial_capital']}")
    print(f"  Monitor Interval: {config['monitor']['refresh_interval']} seconds")

    while True:
        print("""
┌───────────────────────────────────────────────────────────────────┐
│  [1]  Modify watchlist                                           │
│  [2]  Toggle auto save                                           │
│  [3]  Toggle auto backup                                         │
│  [4]  Modify backup interval                                     │
│  [5]  Modify initial capital                                     │
│  [0]  Return                                                     │
└───────────────────────────────────────────────────────────────────┘
        """)

        choice = input("Select option: ").strip()

        if choice == "0":
            save_config(config)
            break
        elif choice == "1":
            print(f"\nCurrent watchlist: {', '.join(config['watchlist'])}")
            new_list = input("Enter new watchlist (comma separated): ").strip()
            if new_list:
                config['watchlist'] = [s.strip() for s in new_list.split(',')]
                print("Updated")
        elif choice == "2":
            config['auto_save'] = not config['auto_save']
            print(f"Auto Save: {'Enabled' if config['auto_save'] else 'Disabled'}")
        elif choice == "3":
            config['auto_backup'] = not config['auto_backup']
            print(f"Auto Backup: {'Enabled' if config['auto_backup'] else 'Disabled'}")
        elif choice == "4":
            hours = input("Enter backup interval (hours): ").strip()
            try:
                config['backup_interval_hours'] = int(hours)
                print("Updated")
            except:
                print("Invalid input")
        elif choice == "5":
            capital = input("Enter initial capital: ").strip()
            try:
                config['trading']['initial_capital'] = float(capital)
                print("Updated")
            except:
                print("Invalid input")


def main():
    print_logo()

    AutoManager().auto_backup()

    while True:
        print_menu()
        choice = input("Select function (0-5): ").strip()

        if choice == "0":
            AutoManager().auto_backup(force=True)
            print("\nThank you for using Quantum Trading System! Goodbye!\n")
            break
        elif choice == "1":
            run_backtest()
        elif choice == "2":
            compare_strategies()
        elif choice == "3":
            run_monitor()
        elif choice == "4":
            data_management()
        elif choice == "5":
            system_settings()


if __name__ == "__main__":
    main()
