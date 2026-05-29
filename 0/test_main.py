import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy import Strategy
from backtest import Backtester
import warnings
warnings.filterwarnings('ignore')

def generate_test_data():
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    
    base_price = 100
    price_change = np.random.randn(len(dates)) * 2
    prices = base_price + np.cumsum(price_change)
    
    df = pd.DataFrame({
        'Open': prices,
        'High': prices + np.random.rand(len(dates)) * 3,
        'Low': prices - np.random.rand(len(dates)) * 3,
        'Close': prices,
        'Volume': np.random.randint(1000, 5000, len(dates))
    }, index=dates)
    
    return df

def main():
    print("生成测试数据...")
    data = generate_test_data()
    print(f"测试数据生成完成，共 {len(data)} 条数据")
    
    strategy = Strategy()
    backtester = Backtester(initial_capital=100000)
    
    print("\n正在运行策略...")
    signals = strategy.execute(data)
    
    print("\n正在执行回测...")
    results = backtester.run_backtest(signals)
    
    print("\n=== 回测指标 ===")
    metrics = backtester.calculate_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    print("\n生成交互式回测图...")
    backtester.plot_interactive(save_path='backtest_result.html')
    print("交互式图表已保存")

if __name__ == "__main__":
    main()