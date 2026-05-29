#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌盘扫描工具 - 实时数据更新脚本
从Tushare获取最新A股数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
import time

class TushareDataUpdater:
    def __init__(self, token):
        ts.set_token(token)
        self.pro = ts.pro_api()
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data', 'tdx')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_today_data(self):
        """获取今日A股行情数据"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            df = self.pro.daily(trade_date=today)
            
            if df.empty:
                print("⚠️ 今日无交易数据，尝试获取最近交易日数据")
                last_trade_day = self.pro.trade_cal(exchange='SSE', start_date=today, end_date=today)
                if not last_trade_day.empty and last_trade_day.iloc[0]['is_open'] == 0:
                    for i in range(1, 7):
                        check_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                        df = self.pro.daily(trade_date=check_date)
                        if not df.empty:
                            print(f"✅ 获取到 {check_date} 的数据")
                            break
            
            return df
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_basic(self):
        """获取股票基础信息"""
        try:
            return self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry,list_date')
        except Exception as e:
            print(f"❌ 获取股票基础信息失败: {e}")
            return pd.DataFrame()
    
    def save_today_data(self):
        """保存今日数据到CSV"""
        df = self.get_today_data()
        if df.empty:
            print("❌ 未获取到数据")
            return False
        
        # 选择需要的字段并重命名
        df = df[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']]
        df.columns = ['股票代码', '日期', '开盘', '最高', '最低', '收盘', '成交量']
        
        # 转换日期格式
        df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
        
        # 保存文件
        file_path = os.path.join(self.data_dir, 'today_data.csv')
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"✅ 已保存 {len(df)} 条数据到 {file_path}")
        
        return True
    
    def update_all_stock_data(self, days=30):
        """更新最近N天的股票数据"""
        print(f"🔄 正在更新最近 {days} 天的数据...")
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        try:
            # 获取股票列表
            stocks = self.get_stock_basic()
            if stocks.empty:
                print("❌ 无法获取股票列表")
                return
            
            # 获取日线数据
            df = self.pro.daily(ts_code='', start_date=start_date, end_date=end_date)
            
            if df.empty:
                print("❌ 未获取到历史数据")
                return
            
            # 按股票代码分组保存
            grouped = df.groupby('ts_code')
            saved_count = 0
            
            for ts_code, group in grouped:
                file_path = os.path.join(self.data_dir, f'{ts_code}.csv')
                group = group[['trade_date', 'open', 'high', 'low', 'close', 'vol']]
                group.columns = ['日期', '开盘', '最高', '最低', '收盘', '成交量']
                group['日期'] = pd.to_datetime(group['日期'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
                group.to_csv(file_path, index=False, encoding='utf-8')
                saved_count += 1
            
            print(f"✅ 已更新 {saved_count} 只股票的数据")
            return True
            
        except Exception as e:
            print(f"❌ 更新数据失败: {e}")
            return False
    
    def run_scheduled_update(self, interval_minutes=30):
        """定时更新数据"""
        print(f"⏰ 启动定时更新服务，间隔 {interval_minutes} 分钟")
        
        while True:
            print(f"\n{'='*60}")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            try:
                self.save_today_data()
                print("✅ 数据更新完成")
            except Exception as e:
                print(f"❌ 更新失败: {e}")
            
            print(f"\n💤 等待 {interval_minutes} 分钟...")
            time.sleep(interval_minutes * 60)

def main():
    # 从配置文件读取Token
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        token = config.get('tushare', {}).get('token', '')
    else:
        token = '7d0dd36274a8de55f02ade04218afa62625bfcd5bfcd4acb8cd4f8ae'
    
    if not token:
        print("❌ 未配置Tushare Token")
        return
    
    updater = TushareDataUpdater(token)
    
    print("请选择模式：")
    print("1. 单次更新今日数据")
    print("2. 更新最近30天历史数据")
    print("3. 启动定时更新服务(每30分钟)")
    
    choice = input("\n请输入选择 (1/2/3，默认1): ").strip() or "1"
    
    if choice == "2":
        updater.update_all_stock_data(30)
    elif choice == "3":
        updater.run_scheduled_update(30)
    else:
        updater.save_today_data()

if __name__ == "__main__":
    main()