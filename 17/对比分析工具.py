import pandas as pd
import numpy as np
from datetime import datetime


def compare_all_sources():
    print("=" * 80)
    print("多交易软件数据对比分析")
    print("=" * 80)
    
    print("\n正在读取各软件的数据...")
    
    try:
        tonghuashun = pd.read_csv("同花顺数据记录模板.csv")
        print(f"✓ 同花顺数据: {len(tonghuashun)} 行")
    except Exception as e:
        print(f"✗ 读取同花顺数据失败: {e}")
        tonghuashun = None
    
    try:
        tongdaxin = pd.read_csv("通达信数据记录模板.csv")
        print(f"✓ 通达信数据: {len(tongdaxin)} 行")
    except Exception as e:
        print(f"✗ 读取通达信数据失败: {e}")
        tongdaxin = None
    
    try:
        daxuezh = pd.read_csv("大智慧数据记录模板.csv")
        print(f"✓ 大智慧数据: {len(daxuezh)} 行")
    except Exception as e:
        print(f"✗ 读取大智慧数据失败: {e}")
        daxuezh = None
    
    if tonghuashun is not None and tongdaxin is not None:
        print("\n" + "=" * 80)
        print("同花顺 vs 通达信 对比分析")
        print("=" * 80)
        
        merged = pd.merge(tonghuashun, tongdaxin, on='Date', how='outer', suffixes=('_ths', '_tdx'))
        
        if 'Close_ths' in merged.columns and 'Close_tdx' in merged.columns:
            merged['Close_Diff'] = merged['Close_ths'] - merged['Close_tdx']
            merged['Close_Diff_Pct'] = (merged['Close_Diff'] / merged['Close_ths'] * 100).round(2)
            
            print("\n收盘价差异分析:")
            print(f"  平均差异: ${merged['Close_Diff'].mean():.2f}")
            print(f"  最大差异: ${merged['Close_Diff'].abs().max():.2f}")
            print(f"  差异标准差: ${merged['Close_Diff'].std():.2f}")
            
            significant_diff = merged[merged['Close_Diff_Pct'].abs() > 0.5]
            if len(significant_diff) > 0:
                print(f"\n显著差异 (>0.5%):")
                print("  日期          同花顺    通达信    差异")
                for _, row in significant_diff.head(10).iterrows():
                    print(f"  {row['Date']}  ${row['Close_ths']:.2f}   ${row['Close_tdx']:.2f}   {row['Close_Diff_Pct']:+.2f}%")
        
        if 'Volume_ths' in merged.columns and 'Volume_tdx' in merged.columns:
            merged['Volume_Diff_Pct'] = ((merged['Volume_ths'] - merged['Volume_tdx']) / merged['Volume_ths'] * 100).round(2)
            
            print("\n成交量差异分析:")
            print(f"  平均差异: {merged['Volume_Diff_Pct'].mean():.2f}%")
            print(f"  最大差异: {merged['Volume_Diff_Pct'].abs().max():.2f}%")
    
    if tonghuashun is not None and daxuezh is not None:
        print("\n" + "=" * 80)
        print("同花顺 vs 大智慧 对比分析")
        print("=" * 80)
        
        merged = pd.merge(tonghuashun, daxuezh, on='Date', how='outer', suffixes=('_ths', '_dxz'))
        
        if 'Close_ths' in merged.columns and 'Close_dxz' in merged.columns:
            merged['Close_Diff'] = merged['Close_ths'] - merged['Close_dxz']
            merged['Close_Diff_Pct'] = (merged['Close_Diff'] / merged['Close_ths'] * 100).round(2)
            
            print("\n收盘价差异分析:")
            print(f"  平均差异: ${merged['Close_Diff'].mean():.2f}")
            print(f"  最大差异: ${merged['Close_Diff'].abs().max():.2f}")
    
    if tongdaxin is not None and daxuezh is not None:
        print("\n" + "=" * 80)
        print("通达信 vs 大智慧 对比分析")
        print("=" * 80)
        
        merged = pd.merge(tongdaxin, daxuezh, on='Date', how='outer', suffixes=('_tdx', '_dxz'))
        
        if 'Close_tdx' in merged.columns and 'Close_dxz' in merged.columns:
            merged['Close_Diff'] = merged['Close_tdx'] - merged['Close_dxz']
            merged['Close_Diff_Pct'] = (merged['Close_Diff'] / merged['Close_tdx'] * 100).round(2)
            
            print("\n收盘价差异分析:")
            print(f"  平均差异: ${merged['Close_Diff'].mean():.2f}")
            print(f"  最大差异: ${merged['Close_Diff'].abs().max():.2f}")
    
    print("\n" + "=" * 80)
    print("差异原因分析")
    print("=" * 80)
    print("""
1. 复权方式不同
   - 前复权: 调整历史价格，使K线连续
   - 后复权: 调整最新价格，保持历史价格不变
   - 不复权: 使用原始价格

2. 数据更新时机
   - 盘中: 实时更新
   - 盘后: 收盘后15-30分钟内更新
   - 日终: 当日结算后更新

3. 成交量统计差异
   - 部分软件不统计集合竞价成交量
   - 成交单位可能不同（手 vs 股）

4. 时间格式差异
   - 部分软件使用交易日时间
   - 部分软件使用北京时间
   - 可能存在时区转换差异

5. 数据源差异
   - 不同券商可能使用不同的行情源
   - 行情源的数据质量和更新速度不同
""")
    
    print("\n" + "=" * 80)
    print("数据质量评估标准")
    print("=" * 80)
    print("""
如果差异在以下范围内，数据可视为基本一致：

| 指标           | 可接受差异 |
|----------------|----------|
| 收盘价         | < 0.5%   |
| 最高/最低价    | < 0.3%   |
| 成交量         | < 5%     |
| 涨跌幅         | < 0.1%   |

如果差异超过以上阈值，建议：
1. 检查复权方式是否一致
2. 确认数据是否为同一时间段
3. 核实数据来源是否可靠
4. 考虑使用更权威的数据源
""")


def create_comparison_template():
    template = """Date,Software1_Close,Software1_Volume,Software2_Close,Software2_Volume,Software3_Close,Software3_Volume
2020-01-02,,,,,,
2020-01-03,,,,,,
2020-01-06,,,,,,
2020-01-07,,,,,,
2020-01-08,,,,,,
2020-01-09,,,,,,
2020-01-10,,,,,,
"""
    
    with open("交易软件数据汇总.csv", 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✓ 已创建汇总模板: 交易软件数据汇总.csv")


if __name__ == "__main__":
    compare_all_sources()
    create_comparison_template()
