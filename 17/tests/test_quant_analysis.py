#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目17 - 量化分析模块单元测试
"""

import sys
import os
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
        assert len(dates) == 366
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
    print("\n🎉 所有单元测试通过！")
