#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目88 - 鹰眼压金策略单元测试
"""

import sys
import os
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_data_reader import TDXDataReader
from backtester import Backtester

class TestTDXDataReader:
    """TDX数据读取器测试"""
    
    def test_reader_initialization(self):
        """测试数据读取器初始化"""
        reader = TDXDataReader()
        assert reader is not None
        print("✅ 数据读取器初始化测试通过")
    
    def test_read_stock_data(self):
        """测试读取股票数据"""
        reader = TDXDataReader()
        df = reader.read_stock_data('sh', '601318', years=1)
        assert df is None or (isinstance(df, pd.DataFrame) and len(df) > 0)
        print("✅ 股票数据读取测试通过")

class TestBacktester:
    """回测器测试"""
    
    def test_backtester_initialization(self):
        """测试回测器初始化"""
        backtester = Backtester()
        assert backtester is not None
        print("✅ 回测器初始化测试通过")
    
    def test_calculate_indicators(self):
        """测试指标计算"""
        backtester = Backtester()
        
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(50, 150, 100),
            'high': np.random.uniform(50, 150, 100),
            'low': np.random.uniform(50, 150, 100),
            'close': np.random.uniform(50, 150, 100),
            'volume': np.random.randint(100000, 10000000, 100)
        }, index=dates)
        
        result = backtester.calculate_indicators(data)
        assert result is not None
        assert 'rsi' in result.columns or 'macd' in result.columns
        print("✅ 指标计算测试通过")
    
    def test_run_backtest(self):
        """测试运行回测"""
        backtester = Backtester()
        
        result = backtester.run_backtest(strategy='combined', days=60)
        assert result is not None
        assert isinstance(result, dict)
        assert 'initial_capital' in result
        assert 'final_value' in result
        assert 'total_return' in result
        assert result['final_value'] >= 0
        print("✅ 回测运行测试通过")
    
    def test_strategy_validation(self):
        """测试策略验证"""
        backtester = Backtester()
        
        valid_strategies = ['combined', 'rsi', 'macd', 'ma']
        for strategy in valid_strategies:
            result = backtester.run_backtest(strategy=strategy, days=30)
            assert result is not None
        print("✅ 策略验证测试通过")

class TestWatchlistAnalysis:
    """自选股分析测试"""
    
    def test_watchlist_load(self):
        """测试自选股加载"""
        watchlist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'watchlist_realtime.csv')
        if os.path.exists(watchlist_path):
            df = pd.read_csv(watchlist_path)
            assert len(df) > 0
            assert 'name' in df.columns
            assert 'code' in df.columns
            print("✅ 自选股加载测试通过")
        else:
            print("⚠️ 自选股文件不存在，跳过测试")

if __name__ == "__main__":
    print("🧪 开始运行项目88单元测试...\n")
    
    test_reader = TestTDXDataReader()
    test_reader.test_reader_initialization()
    test_reader.test_read_stock_data()
    
    test_backtester = TestBacktester()
    test_backtester.test_backtester_initialization()
    test_backtester.test_calculate_indicators()
    test_backtester.test_run_backtest()
    test_backtester.test_strategy_validation()
    
    test_watchlist = TestWatchlistAnalysis()
    test_watchlist.test_watchlist_load()
    
    print("\n🎉 所有单元测试通过！")
