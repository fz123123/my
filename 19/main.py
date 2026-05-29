import time
import os
from datetime import datetime
from stock_data import fetch_all_stocks, fetch_stock_by_code
from radar import LimitUpRadar, format_stock_info
from visualization import print_summary_table, print_detailed_report, plot_limit_up_distribution, plot_top_stocks

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\n" + "="*60)
    print("                    涨停雷达 v1.0")
    print("="*60)
    print("1. 实时监控")
    print("2. 单次扫描")
    print("3. 添加监控股票")
    print("4. 查看监控列表")
    print("5. 详细分析")
    print("6. 可视化展示")
    print("7. 退出")
    print("="*60)
    choice = input("请输入选择 (1-7): ")
    return choice

def run_real_time_monitor(radar):
    print("\n启动实时监控模式，按 Ctrl+C 退出...")
    print("="*60)
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在扫描...")
            
            stocks = fetch_all_stocks()
            
            if stocks.empty:
                print("获取股票数据失败，稍后重试...")
                time.sleep(10)
                continue
            
            limit_up = radar.detect_limit_up(stocks)
            analysis = radar.analyze_limit_up_stocks(limit_up)
            
            radar.save_history(analysis, datetime.now())
            
            if analysis:
                print(f"检测到 {len(analysis)} 只涨停股票:")
                for stock in analysis[:5]:
                    print(f"  [{stock['code']}] {stock['name']}  {stock['price']:.2f}元  +{stock['change_pct']:.2f}%")
                
                if len(analysis) > 5:
                    print(f"  ... 还有 {len(analysis) - 5} 只涨停股票")
            else:
                print("当前无涨停股票")
            
            history_summary = radar.get_history_summary()
            if history_summary:
                print(f"\n近期统计: 平均涨停 {history_summary['avg_limit_up']:.1f} 只")
            
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n监控已停止")

def run_single_scan(radar):
    print("\n正在执行单次扫描...")
    print("="*60)
    
    stocks = fetch_all_stocks()
    
    if stocks.empty:
        print("获取股票数据失败")
        return
    
    limit_up = radar.detect_limit_up(stocks)
    analysis = radar.analyze_limit_up_stocks(limit_up)
    
    radar.save_history(analysis, datetime.now())
    
    print_summary_table(analysis)
    
    if analysis:
        view_detail = input("\n是否查看详细信息? (y/n): ").strip().lower()
        if view_detail == 'y':
            print_detailed_report(analysis)

def add_monitor_stock(radar):
    code = input("请输入股票代码: ").strip()
    
    if not code:
        print("股票代码不能为空")
        return
    
    stock = fetch_stock_by_code(code)
    
    if stock:
        radar.add_monitor_stock(stock['code'], stock['name'])
        print(f"已添加监控: {stock['code']} {stock['name']}")
    else:
        print(f"无法找到股票代码: {code}")

def view_monitor_list(radar):
    monitored = radar.get_monitored_stocks()
    
    if not monitored:
        print("\n监控列表为空")
        return
    
    print("\n" + "="*60)
    print("                    监控股票列表")
    print("="*60)
    
    for i, stock in enumerate(monitored, 1):
        print(f"{i}. [{stock['code']}] {stock['name']}")
    
    print("="*60)
    
    code_to_remove = input("\n输入要移除的股票代码(回车跳过): ").strip()
    if code_to_remove:
        radar.remove_monitor_stock(code_to_remove)
        print(f"已移除监控: {code_to_remove}")

def run_detailed_analysis(radar):
    print("\n正在执行详细分析...")
    print("="*60)
    
    stocks = fetch_all_stocks()
    
    if stocks.empty:
        print("获取股票数据失败")
        return
    
    limit_up = radar.detect_limit_up(stocks)
    analysis = radar.analyze_limit_up_stocks(limit_up)
    
    print_detailed_report(analysis)

def run_visualization(radar):
    print("\n正在生成可视化图表...")
    print("="*60)
    
    stocks = fetch_all_stocks()
    
    if stocks.empty:
        print("获取股票数据失败")
        return
    
    limit_up = radar.detect_limit_up(stocks)
    analysis = radar.analyze_limit_up_stocks(limit_up)
    
    if not analysis:
        print("暂无涨停股票数据")
        return
    
    print_summary_table(analysis)
    
    try:
        plot_limit_up_distribution(analysis)
        plot_top_stocks(analysis)
        input("\n按回车键关闭图表...")
    except Exception as e:
        print(f"图表生成失败: {e}")

def main():
    radar = LimitUpRadar()
    
    while True:
        clear_screen()
        choice = print_menu()
        
        if choice == '1':
            run_real_time_monitor(radar)
        elif choice == '2':
            run_single_scan(radar)
            input("\n按回车键继续...")
        elif choice == '3':
            add_monitor_stock(radar)
            input("\n按回车键继续...")
        elif choice == '4':
            view_monitor_list(radar)
            input("\n按回车键继续...")
        elif choice == '5':
            run_detailed_analysis(radar)
            input("\n按回车键继续...")
        elif choice == '6':
            run_visualization(radar)
        elif choice == '7':
            print("感谢使用涨停雷达，再见！")
            break
        else:
            print("无效选择，请输入 1-7")
            input("\n按回车键继续...")

if __name__ == '__main__':
    main()
