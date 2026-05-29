# -*- coding: utf-8 -*-
"""
策略模块单元测试
覆盖所有策略的核心功能
"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.basic_strategies import (
    StrategyMaCross,
    StrategyRsi,
    StrategyRsiEnhanced,
    StrategyRsiAdaptive,
    StrategyBollinger,
    StrategyMultiFactor,
    StrategyGrid,
    StrategyGridAdvanced,
    StrategyGridScalping
)


def generate_test_data(days=100, trend='up'):
    """
    生成测试用的价格数据
    
    参数:
        days: 数据天数
        trend: 趋势类型 ('up', 'down', 'range')
    
    返回:
        DataFrame: 包含 OHLCV 数据
    """
    np.random.seed(42)  # 固定随机数种子便于复现
    
    dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
    
    # 基础价格
    if trend == 'up':
        base_prices = np.linspace(100, 150, days)
    elif trend == 'down':
        base_prices = np.linspace(150, 100, days)
    else:
        base_prices = 125 + np.sin(np.linspace(0, 4*np.pi, days)) * 20
    
    # 添加随机噪声
    noise = np.random.normal(0, 2, days)
    close_prices = base_prices + noise
    
    # 生成 OHLC
    high_prices = close_prices + np.random.uniform(0, 5, days)
    low_prices = close_prices - np.random.uniform(0, 5, days)
    open_prices = low_prices + np.random.uniform(0, high_prices - low_prices, days)
    volumes = np.random.randint(100000, 1000000, days)
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    return df


class TestStrategyMaCross:
    """均线交叉策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyMaCross(short_period=5, long_period=20)
        assert strategy.short_period == 5
        assert strategy.long_period == 20
    
    def test_generate_signals_up_trend(self):
        """测试上升趋势中的信号生成"""
        df = generate_test_data(days=100, trend='up')
        strategy = StrategyMaCross()
        signals = strategy.generate_signals(df)
        
        # 检查信号格式
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(df)
        
        # 应该有买入信号
        assert 1 in signals.values
    
    def test_generate_signals_down_trend(self):
        """测试下降趋势中的信号生成"""
        df = generate_test_data(days=100, trend='down')
        strategy = StrategyMaCross()
        signals = strategy.generate_signals(df)
        
        # 应该有卖出信号
        assert -1 in signals.values
    
    def test_insufficient_data(self):
        """测试数据不足的情况"""
        df = generate_test_data(days=5)
        strategy = StrategyMaCross()
        signals = strategy.generate_signals(df)
        # 即使数据少也应该返回信号
        assert isinstance(signals, pd.Series)


class TestStrategyRsi:
    """基础RSI策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyRsi(oversold=30, overbought=70)
        assert strategy.oversold == 30
        assert strategy.overbought == 70
    
    def test_generate_signals(self):
        """测试信号生成"""
        df = generate_test_data(days=100, trend='range')
        strategy = StrategyRsi()
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
        # 可能有买入和卖出信号
        assert set(signals.unique()).issubset({0, 1, -1})
    
    def test_custom_thresholds(self):
        """测试自定义阈值"""
        df = generate_test_data(days=100)
        strategy = StrategyRsi(oversold=20, overbought=80)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)


class TestStrategyRsiEnhanced:
    """增强版RSI策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyRsiEnhanced(
            oversold=30,
            overbought=70,
            stop_loss_pct=0.08,
            take_profit_pct=0.20,
            max_holding_days=60,
            use_trend_filter=True
        )
        assert strategy.oversold == 30
        assert strategy.stop_loss_pct == 0.08
        assert strategy.use_trend_filter is True
    
    def test_buy_signal_with_trend_filter(self):
        """测试带趋势过滤的买入信号"""
        df = generate_test_data(days=100, trend='up')
        strategy = StrategyRsiEnhanced(use_trend_filter=True)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
    
    def test_without_trend_filter(self):
        """测试不带趋势过滤"""
        df = generate_test_data(days=100)
        strategy = StrategyRsiEnhanced(use_trend_filter=False)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)


class TestStrategyRsiAdaptive:
    """自适应RSI策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyRsiAdaptive(
            oversold=30,
            overbought=70,
            bull_stop_loss=0.10,
            bear_stop_loss=0.05,
            use_atr_tp=True,
            use_trailing_stop=True
        )
        assert strategy.oversold == 30
        assert strategy.use_atr_tp is True
        assert strategy.use_trailing_stop is True
    
    def test_market_regime_detection(self):
        """测试市场状态检测"""
        df = generate_test_data(days=100, trend='up')
        strategy = StrategyRsiAdaptive()
        
        # 调用内部方法测试
        # 注意：_identify_market_regime是内部方法
        regime = strategy._identify_market_regime(df, 99)
        assert regime in ['bull', 'bear', 'neutral']
    
    def test_generate_signals_full(self):
        """测试完整信号生成"""
        df = generate_test_data(days=100)
        strategy = StrategyRsiAdaptive(use_atr_tp=True, use_trailing_stop=True)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
    
    def test_without_optional_features(self):
        """测试不使用可选功能"""
        df = generate_test_data(days=100)
        strategy = StrategyRsiAdaptive(use_atr_tp=False, use_trailing_stop=False)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)


class TestStrategyBollinger:
    """布林带策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyBollinger()
        # 简单验证
        assert strategy is not None
    
    def test_generate_signals(self):
        """测试信号生成"""
        df = generate_test_data(days=100, trend='range')
        strategy = StrategyBollinger()
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
    
    def test_signals_in_range(self):
        """测试震荡市场的信号"""
        df = generate_test_data(days=100, trend='range')
        strategy = StrategyBollinger()
        signals = strategy.generate_signals(df)
        
        # 震荡市场应该有更多信号
        assert 1 in signals.values or -1 in signals.values


class TestStrategyMultiFactor:
    """多因子策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyMultiFactor()
        assert strategy is not None
    
    def test_generate_signals(self):
        """测试信号生成"""
        df = generate_test_data(days=100)
        strategy = StrategyMultiFactor()
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
        assert set(signals.unique()).issubset({0, 1, -1})


class TestStrategyGrid:
    """基础网格策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyGrid(
            grid_levels=5,
            grid_range_pct=0.10,
            auto_adjust=True
        )
        assert strategy.grid_levels == 5
        assert strategy.grid_range_pct == 0.10
    
    def test_calculate_grid_lines(self):
        """测试网格线计算"""
        df = generate_test_data(days=60)
        strategy = StrategyGrid(grid_levels=5)
        grid_lines = strategy.calculate_grid_lines(df)
        
        assert isinstance(grid_lines, list)
        assert len(grid_lines) == 6  # 5层网格 + 边界
    
    def test_generate_signals(self):
        """测试信号生成"""
        df = generate_test_data(days=100, trend='range')
        strategy = StrategyGrid(grid_levels=5)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
    
    def test_insufficient_data_grid_lines(self):
        """测试数据不足时网格线计算"""
        df = generate_test_data(days=20)  # 少于30天
        strategy = StrategyGrid()
        grid_lines = strategy.calculate_grid_lines(df)
        
        assert grid_lines == []  # 应该返回空列表
    
    def test_get_grid_info(self):
        """测试获取网格信息"""
        df = generate_test_data(days=60)
        strategy = StrategyGrid(grid_levels=8)
        strategy.calculate_grid_lines(df)
        info = strategy.get_grid_info()
        
        assert isinstance(info, dict)
        assert 'levels' in info
        assert 'grid_lines' in info


class TestStrategyGridAdvanced:
    """进阶网格策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyGridAdvanced(
            grid_levels=5,
            grid_range_pct=0.10,
            volume_filter=True,
            rsi_filter=True,
            take_profit_pct=0.02
        )
        assert strategy.volume_filter is True
        assert strategy.take_profit_pct == 0.02
    
    def test_calculate_grid_lines_with_volatility(self):
        """测试考虑波动率的网格线计算"""
        df = generate_test_data(days=60)
        strategy = StrategyGridAdvanced()
        grid_lines = strategy.calculate_grid_lines(df)
        
        assert isinstance(grid_lines, list)
        assert len(grid_lines) >= 2
    
    def test_generate_signals_with_filters(self):
        """测试带过滤器的信号生成"""
        df = generate_test_data(days=100)
        strategy = StrategyGridAdvanced(volume_filter=True, rsi_filter=True)
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)
    
    def test_get_grid_info(self):
        """测试获取网格信息"""
        strategy = StrategyGridAdvanced()
        info = strategy.get_grid_info()
        
        assert isinstance(info, dict)
        assert 'volume_filter' in info
        assert 'rsi_filter' in info


class TestStrategyGridScalping:
    """网格高频策略测试"""
    
    def test_init(self):
        """测试初始化"""
        strategy = StrategyGridScalping(
            tick_size=0.01,
            profit_target=0.002,
            loss_limit=0.005,
            min_volume=100
        )
        assert strategy.profit_target == 0.002
        assert strategy.min_volume == 100
    
    def test_generate_signals(self):
        """测试信号生成"""
        df = generate_test_data(days=100)
        strategy = StrategyGridScalping()
        signals = strategy.generate_signals(df)
        
        assert isinstance(signals, pd.Series)


def test_all_strategies_compatibility():
    """测试所有策略的兼容性"""
    df = generate_test_data(days=100)
    
    strategies = [
        StrategyMaCross(),
        StrategyRsi(),
        StrategyRsiEnhanced(),
        StrategyRsiAdaptive(),
        StrategyBollinger(),
        StrategyMultiFactor(),
        StrategyGrid(),
        StrategyGridAdvanced(),
        StrategyGridScalping(),
    ]
    
    for strategy in strategies:
        signals = strategy.generate_signals(df)
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(df)
        # 信号值应该在合理范围内
        assert set(signals.unique()).issubset({0, 1, -1})


def test_empty_data():
    """测试空数据处理"""
    df = pd.DataFrame()  # 空DataFrame
    
    # 测试策略处理空数据
    for strategy_class in [
        StrategyMaCross,
        StrategyRsi,
        StrategyBollinger,
        StrategyMultiFactor
    ]:
        strategy = strategy_class()
        try:
            signals = strategy.generate_signals(df)
            # 如果不抛异常，验证返回值类型
            assert isinstance(signals, pd.Series)
        except:
            # 允许策略在空数据时抛异常
            pass


if __name__ == '__main__':
    print("=" * 70)
    print("策略模块单元测试")
    print("=" * 70)
    print("\n注意：请使用 pytest 运行完整测试套件")
    print("命令：pytest tests/test_strategies.py -v")
    print("\n或者运行单例测试：")
    print("python -m pytest tests/test_strategies.py::TestStrategyMaCross -v")
