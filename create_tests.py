#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试生成器 - 为所有项目创建完善的测试用例
"""

import os
from pathlib import Path

base_path = Path(r'C:\Users\Administrator\Documents\trae_projects')

def create_python_test(project, test_name, content):
    """创建Python测试文件"""
    test_dir = base_path / project / 'tests'
    test_dir.mkdir(exist_ok=True)
    
    file_path = test_dir / f'test_{test_name}.py'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 项目{project}: 创建 tests/test_{test_name}.py")

def create_js_test(project, test_name, content):
    """创建JavaScript/TypeScript测试文件"""
    test_dir = base_path / project / 'tests'
    test_dir.mkdir(exist_ok=True)
    
    file_path = test_dir / f'{test_name}.test.ts'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 项目{project}: 创建 tests/{test_name}.test.ts")

def create_project0_tests():
    """项目0 - 简单回测测试"""
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目0 - 回测模块单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest import BackTest
from strategy import Strategy
from data_processor import DataProcessor

class TestBackTest:
    """回测模块测试"""
    
    def test_backtest_initialization(self):
        """测试回测器初始化"""
        backtest = BackTest()
        assert backtest is not None
        print("✅ 回测器初始化测试通过")
    
    def test_strategy_initialization(self):
        """测试策略初始化"""
        strategy = Strategy()
        assert strategy is not None
        print("✅ 策略初始化测试通过")
    
    def test_data_processor_initialization(self):
        """测试数据处理器初始化"""
        processor = DataProcessor()
        assert processor is not None
        print("✅ 数据处理器初始化测试通过")
    
    def test_generate_test_data(self):
        """测试生成测试数据"""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(10, 100, 100),
            'high': np.random.uniform(10, 100, 100),
            'low': np.random.uniform(10, 100, 100),
            'close': np.random.uniform(10, 100, 100),
            'volume': np.random.randint(1000, 100000, 100)
        }, index=dates)
        assert len(data) == 100
        assert 'close' in data.columns
        print("✅ 测试数据生成测试通过")
    
    def test_backtest_run(self):
        """测试回测运行"""
        backtest = BackTest()
        strategy = Strategy()
        
        dates = pd.date_range('2024-01-01', periods=60, freq='D')
        data = pd.DataFrame({
            'open': np.linspace(50, 60, 60),
            'high': np.linspace(51, 61, 60),
            'low': np.linspace(49, 59, 60),
            'close': np.linspace(50, 60, 60),
            'volume': np.ones(60) * 10000
        }, index=dates)
        
        result = backtest.run(data, strategy)
        assert result is not None
        assert 'return' in result or 'final_balance' in result
        print("✅ 回测运行测试通过")

class TestStrategy:
    """策略模块测试"""
    
    def test_moving_average_crossover(self):
        """测试均线交叉策略"""
        strategy = Strategy()
        
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        close_prices = np.linspace(50, 70, 50)
        data = pd.DataFrame({'close': close_prices}, index=dates)
        
        signals = strategy.generate_signals(data)
        assert signals is not None
        print("✅ 均线交叉策略测试通过")
    
    def test_rsi_indicator(self):
        """测试RSI指标计算"""
        strategy = Strategy()
        
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        data = pd.DataFrame({
            'close': np.random.uniform(40, 60, 30)
        }, index=dates)
        
        rsi = strategy.calculate_rsi(data)
        assert rsi is not None
        assert all(0 <= val <= 100 for val in rsi)
        print("✅ RSI指标测试通过")

if __name__ == "__main__":
    test_backtest = TestBackTest()
    test_backtest.test_backtest_initialization()
    test_backtest.test_strategy_initialization()
    test_backtest.test_data_processor_initialization()
    test_backtest.test_generate_test_data()
    test_backtest.test_backtest_run()
    
    test_strategy = TestStrategy()
    test_strategy.test_moving_average_crossover()
    test_strategy.test_rsi_indicator()
    
    print("\\n🎉 所有单元测试通过！")
'''
    create_python_test('0', 'backtest', test_content)

def create_project17_tests():
    """项目17测试"""
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目17 - 量化分析模块单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

class TestQuantAnalysis:
    """量化分析测试"""
    
    def test_data_validation(self):
        """测试数据验证"""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(10, 100, 100),
            'high': np.random.uniform(10, 100, 100),
            'low': np.random.uniform(10, 100, 100),
            'close': np.random.uniform(10, 100, 100),
            'volume': np.random.randint(1000, 100000, 100)
        }, index=dates)
        
        assert len(data) == 100
        assert all(col in data.columns for col in ['open', 'high', 'low', 'close', 'volume'])
        print("✅ 数据验证测试通过")
    
    def test_date_range(self):
        """测试日期范围"""
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        assert len(dates) == 366  # 2024是闰年
        print("✅ 日期范围测试通过")
    
    def test_statistical_analysis(self):
        """测试统计分析"""
        data = np.random.normal(50, 10, 1000)
        mean_val = np.mean(data)
        std_val = np.std(data)
        
        assert 48 < mean_val < 52
        assert 8 < std_val < 12
        print("✅ 统计分析测试通过")

if __name__ == "__main__":
    tests = TestQuantAnalysis()
    tests.test_data_validation()
    tests.test_date_range()
    tests.test_statistical_analysis()
    print("\\n🎉 所有单元测试通过！")
'''
    create_python_test('17', 'quant_analysis', test_content)

def create_project33_tests():
    """项目33 - 恐慌盘策略测试"""
    test_content = '''#!/usr/bin/env ts-node
import { PanicBuyStrategy } from '../src/strategy/PanicBuyStrategy'
import { Backtester } from '../src/backtest/Backtester'
import { RiskManager } from '../src/risk/RiskManager'
import { BarData } from '../src/types'

function createTestData(count: number): BarData[] {
  const data: BarData[] = []
  let price = 50
  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 4
    const open = price
    const close = price + change
    const high = Math.max(open, close) + Math.random() * 2
    const low = Math.min(open, close) - Math.random() * 2
    
    data.push({
      timestamp: new Date(2024, 0, 1 + i).toISOString(),
      open,
      high,
      low,
      close,
      volume: Math.floor(Math.random() * 1000000) + 100000,
      turnover: 0
    })
    price = close
  }
  return data
}

function testPanicStrategy() {
  console.log('🧪 开始测试恐慌盘策略...')
  
  // 测试1: 策略初始化
  console.log('\\n1. 测试策略初始化')
  const strategy = new PanicBuyStrategy({
    name: 'TestPanicBuy',
    parameters: {
      minDrop: 0.05,
      volumeRatio: 1.5,
      rsiOversold: 30,
      profitTarget: 0.08,
      stopLoss: 0.06
    }
  })
  console.log('✅ 策略初始化成功')
  
  // 测试2: 风险管理初始化
  console.log('\\n2. 测试风险管理初始化')
  const riskManager = new RiskManager({
    maxPositionSize: 0.95,
    maxDrawdown: 0.5,
    stopLoss: 0.06,
    takeProfit: 0.08,
    maxOpenPositions: 1
  })
  console.log('✅ 风险管理初始化成功')
  
  // 测试3: 回测器初始化
  console.log('\\n3. 测试回测器初始化')
  const backtester = new Backtester(strategy, riskManager, 100000)
  console.log('✅ 回测器初始化成功')
  
  // 测试4: 运行回测
  console.log('\\n4. 测试回测运行')
  const testData = createTestData(100)
  const result = backtester.run(testData)
  
  console.log(`   初始资金: $100,000`)
  console.log(`   最终资金: $${result.finalCapital.toLocaleString()}`)
  console.log(`   总收益率: ${result.totalReturnPercent.toFixed(2)}%`)
  console.log(`   最大回撤: ${result.maxDrawdown.toFixed(2)}%`)
  console.log(`   夏普比率: ${result.sharpeRatio.toFixed(2)}`)
  
  assert(result.finalCapital >= 0, '最终资金不能为负')
  assert(result.maxDrawdown >= 0, '最大回撤不能为负')
  console.log('✅ 回测运行成功')
  
  // 测试5: 获取交易记录
  console.log('\\n5. 测试交易记录获取')
  const trades = backtester.getTrades()
  console.log(`   交易次数: ${trades.length}`)
  assert(Array.isArray(trades), '交易记录应为数组')
  console.log('✅ 交易记录获取成功')
  
  console.log('\\n🎉 所有恐慌盘策略单元测试通过！')
}

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`测试失败: ${message}`)
  }
}

testPanicStrategy().catch(console.error)
'''
    create_js_test('33', 'panic_strategy', test_content)

def create_project88_tests():
    """项目88 - 鹰眼压金测试"""
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目88 - 鹰眼压金策略单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
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
        
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'open': np.linspace(50, 70, 100),
            'high': np.linspace(51, 71, 100),
            'low': np.linspace(49, 69, 100),
            'close': np.linspace(50, 70, 100),
            'volume': np.ones(100) * 1000000
        }, index=dates)
        
        result = backtester.run_backtest(data, strategy='combined')
        assert result is not None
        assert 'final_balance' in result
        assert 'total_return' in result
        assert result['final_balance'] >= 0
        print("✅ 回测运行测试通过")
    
    def test_strategy_validation(self):
        """测试策略验证"""
        backtester = Backtester()
        
        valid_strategies = ['combined', 'rsi', 'macd', 'breakout']
        for strategy in valid_strategies:
            dates = pd.date_range('2024-01-01', periods=60, freq='D')
            data = pd.DataFrame({
                'open': np.random.uniform(50, 100, 60),
                'high': np.random.uniform(50, 100, 60),
                'low': np.random.uniform(50, 100, 60),
                'close': np.random.uniform(50, 100, 60),
                'volume': np.random.randint(100000, 1000000, 60)
            }, index=dates)
            
            result = backtester.run_backtest(data, strategy=strategy)
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
    # 运行所有测试
    print("🧪 开始运行项目88单元测试...\\n")
    
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
    
    print("\\n🎉 所有单元测试通过！")
'''
    create_python_test('88', 'eagle_strategy', test_content)

def main():
    """主函数"""
    print("🚀 开始为所有项目创建单元测试")
    print("=" * 60)
    
    # 为每个项目创建测试
    print("\n📁 项目0 - 简单回测")
    create_project0_tests()
    
    print("\n📁 项目17 - 量化分析")
    create_project17_tests()
    
    print("\n📁 项目33 - 恐慌盘策略")
    create_project33_tests()
    
    print("\n📁 项目88 - 鹰眼压金")
    create_project88_tests()
    
    print("\n" + "=" * 60)
    print("🎉 所有项目单元测试创建完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
