#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从通达信导入自选股到系统配置
"""

import os
import json
from pathlib import Path

def main():
    print("="*60)
    print("    更新系统观察列表 - 从通达信导入")
    print("="*60)
    
    # 读取监控列表中的股票
    monitor_file = Path(__file__).parent / 'monitor' / 'stocks.txt'
    
    if not monitor_file.exists():
        print(f"❌ 监控文件不存在: {monitor_file}")
        print("请先运行: python import_tdx_stocks.py")
        return
    
    with open(monitor_file, 'r', encoding='utf-8') as f:
        stocks = [line.strip() for line in f if line.strip()]
    
    print(f"\n📂 从监控文件读取到 {len(stocks)} 只股票")
    
    # 更新配置文件
    config_file = Path(__file__).parent / 'system_config.json'
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    config['watchlist'] = stocks
    config['last_updated'] = str(os.path.getmtime(__file__))
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已成功更新系统配置！")
    print(f"📊 观察列表已包含 {len(stocks)} 只股票")
    print(f"📁 配置文件: {config_file}")
    
    print(f"\n💡 现在刷新 Web 页面即可看到更新后的自选股列表")

if __name__ == "__main__":
    main()
