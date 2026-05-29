import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

def plot_limit_up_distribution(analysis_results):
    if not analysis_results:
        print("没有数据可绘制")
        return
    
    risk_counts = {'高风险': 0, '中风险': 0, '低风险': 0}
    for stock in analysis_results:
        risk_counts[stock['risk_level']] += 1
    
    labels = list(risk_counts.keys())
    sizes = list(risk_counts.values())
    colors = ['#ff6b6b', '#ffd93d', '#6bcb77']
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    plt.title(f'涨停股票风险分布 ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})')
    plt.axis('equal')
    plt.show(block=False)

def plot_top_stocks(analysis_results, top_n=10):
    if not analysis_results:
        print("没有数据可绘制")
        return
    
    top_stocks = analysis_results[:top_n]
    names = [stock['name'] for stock in top_stocks]
    change_pcts = [stock['change_pct'] for stock in top_stocks]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(names, change_pcts, color='#ff6b6b')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}%', ha='center', va='bottom')
    
    plt.title(f'涨停股票涨幅排行 (TOP {top_n})')
    plt.xlabel('股票名称')
    plt.ylabel('涨幅 (%)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show(block=False)

def plot_volume_distribution(analysis_results):
    if not analysis_results:
        print("没有数据可绘制")
        return
    
    volumes = [stock['volume'] / 10000 for stock in analysis_results]
    
    plt.figure(figsize=(10, 6))
    plt.hist(volumes, bins=20, edgecolor='black', color='#4dabf7')
    plt.title('涨停股票成交量分布')
    plt.xlabel('成交量 (万手)')
    plt.ylabel('股票数量')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show(block=False)

def print_summary_table(analysis_results):
    if not analysis_results:
        print("暂无涨停股票数据")
        return
    
    df = pd.DataFrame(analysis_results)
    df = df[['name', 'code', 'price', 'change_pct', 'turnover_rate', 'risk_level']]
    df.columns = ['名称', '代码', '价格', '涨幅(%)', '换手率(%)', '风险等级']
    
    print("\n" + "="*80)
    print(f"                    涨停雷达监控报告 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)

def print_detailed_report(analysis_results):
    if not analysis_results:
        print("暂无涨停股票数据")
        return
    
    from radar import format_stock_info
    
    print("\n" + "="*80)
    print(f"                涨停雷达详细分析报告 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("="*80)
    
    for i, stock in enumerate(analysis_results, 1):
        print(f"\n【{i}】{format_stock_info(stock)}")
        if i < len(analysis_results):
            print("-" * 60)
    
    print("\n" + "="*80)

if __name__ == '__main__':
    from radar import LimitUpRadar
    from stock_data import fetch_all_stocks
    
    radar = LimitUpRadar()
    stocks = fetch_all_stocks()
    
    if not stocks.empty:
        limit_up = radar.detect_limit_up(stocks)
        analysis = radar.analyze_limit_up_stocks(limit_up)
        
        print_summary_table(analysis)
        plot_limit_up_distribution(analysis)
        plot_top_stocks(analysis)
        
        plt.show()
