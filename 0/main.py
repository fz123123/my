import pandas as pd
import numpy as np
from data_processor import DataProcessor
from strategy import Strategy
from backtest import Backtester
import warnings
warnings.filterwarnings('ignore')

def generate_realistic_test_data():
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
    
    n = len(dates)
    base_price = 75
    trend = np.linspace(0, 100, n)
    seasonality = np.sin(np.linspace(0, 16 * np.pi, n)) * 15
    noise = np.random.randn(n) * 8
    prices = base_price + trend + seasonality + noise
    
    df = pd.DataFrame({
        'open': prices,
        'high': prices + np.random.rand(n) * 5,
        'low': prices - np.random.rand(n) * 5,
        'close': prices,
        'volume': np.random.randint(100000, 5000000, n)
    }, index=dates)
    
    return df

def run_backtest_with_real_data(ticker: str = 'AAPL', years: int = 5, strategy_type: str = 'combined'):
    print(f"📊 正在获取 {ticker} 的真实股票数据...")
    processor = DataProcessor()
    df = processor.get_market_data(ticker, years)
    
    if df.empty:
        print(f"❌ 无法获取 {ticker} 的数据，使用模拟数据")
        df = generate_realistic_test_data()
    
    print(f"✅ 数据获取完成，共 {len(df)} 条数据")
    print(f"📅 数据时间范围: {df.index[0].date()} 至 {df.index[-1].date()}")
    
    strategy = Strategy(strategy_type=strategy_type)
    backtester = Backtester(initial_capital=100000, transaction_cost=0.001)
    
    print(f"\n⚡ 正在运行 {strategy.name} ({strategy_type})...")
    signals = strategy.execute(df)
    
    print("\n🔄 正在执行回测...")
    results = backtester.run_backtest(signals)
    
    print("\n📈 === 回测指标 ===")
    metrics = backtester.calculate_metrics()
    
    key_metrics = ['Total Return', 'Total Return (Net)', 'Annualized Return', 'Annualized Return (Net)',
                   'Volatility', 'Sharpe Ratio', 'Sharpe Ratio (Net)', 'Max Drawdown', 'Max Drawdown (Net)',
                   'Win Rate', 'Profit Factor', 'Number of Trades']
    
    for key in key_metrics:
        print(f"{key}: {metrics[key]}")
    
    print("\n📉 生成交互式回测图...")
    backtester.plot_interactive(save_path=f'backtest_result_{ticker}.html')
    
    print("\n📋 生成回测报告...")
    backtester.generate_report(filename=f'backtest_report_{ticker}.html')
    
    print(f"\n✅ {ticker} 回测完成！")
    print(f"   - 交互式图表: backtest_result_{ticker}.html")
    print(f"   - 回测报告: backtest_report_{ticker}.html")
    
    return backtester, metrics

def run_multi_strategy_comparison(ticker: str = 'AAPL', years: int = 5):
    strategies = ['combined', 'sma_crossover', 'rsi', 'macd', 'bollinger', 'trend_following', 'mean_reversion']
    results = []
    
    print(f"🔬 正在比较 {len(strategies)} 种策略...")
    
    for strategy_type in strategies:
        print(f"\n--- {strategy_type} ---")
        
        processor = DataProcessor()
        df = processor.get_market_data(ticker, years)
        
        if df.empty:
            df = generate_realistic_test_data()
        
        strategy = Strategy(strategy_type=strategy_type)
        backtester = Backtester(initial_capital=100000, transaction_cost=0.001)
        
        signals = strategy.execute(df)
        backtester.run_backtest(signals)
        metrics = backtester.calculate_metrics()
        
        results.append({
            '策略': strategy_type,
            '总收益(净)': metrics['Total Return (Net)'],
            '年化收益(净)': metrics['Annualized Return (Net)'],
            '夏普比率(净)': metrics['Sharpe Ratio (Net)'],
            '最大回撤(净)': metrics['Max Drawdown (Net)'],
            '胜率': metrics['Win Rate (Net)'],
            '交易次数': metrics['Number of Trades']
        })
    
    print("\n📊 策略对比结果:")
    comparison_df = pd.DataFrame(results)
    print(comparison_df.to_string(index=False))
    
    comparison_df.to_csv('strategy_comparison.csv', index=False)
    print("\n✅ 策略对比完成，结果已保存到 strategy_comparison.csv")
    
    return comparison_df

def main():
    print("=" * 60)
    print("        🐉 龙量化回测系统 v2.0")
    print("=" * 60)
    print("\n请选择操作:")
    print("1. 单策略回测（真实数据）")
    print("2. 多策略对比")
    print("3. 使用模拟数据回测")
    
    choice = input("\n输入选择 (1/2/3): ").strip()
    
    if choice == '1':
        ticker = input("输入股票代码 (默认 AAPL): ").strip() or 'AAPL'
        years = int(input("输入回测年限 (默认 5): ").strip() or 5)
        strategy_type = input("输入策略类型 (默认 combined): ").strip() or 'combined'
        
        run_backtest_with_real_data(ticker, years, strategy_type)
    
    elif choice == '2':
        ticker = input("输入股票代码 (默认 AAPL): ").strip() or 'AAPL'
        years = int(input("输入回测年限 (默认 5): ").strip() or 5)
        
        run_multi_strategy_comparison(ticker, years)
    
    elif choice == '3':
        print("\n📊 使用模拟数据进行回测...")
        
        data = generate_realistic_test_data()
        print(f"✅ 模拟数据生成完成，共 {len(data)} 条数据")
        
        strategy = Strategy(strategy_type='combined')
        backtester = Backtester(initial_capital=100000)
        
        print("\n⚡ 正在运行策略...")
        signals = strategy.execute(data)
        
        print("\n🔄 正在执行回测...")
        results = backtester.run_backtest(signals)
        
        print("\n📈 === 回测指标 ===")
        metrics = backtester.calculate_metrics()
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        print("\n📉 生成交互式回测图...")
        backtester.plot_interactive(save_path='backtest_result.html')
        
        print("\n📋 生成回测报告...")
        backtester.generate_report(filename='backtest_report.html')
        
        print("\n✅ 模拟数据回测完成！")
        print("   - 交互式图表: backtest_result.html")
        print("   - 回测报告: backtest_report.html")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()