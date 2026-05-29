#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停先知 - 实时数据测试工具
测试网络连接和数据源可用性
"""

import requests
import time
from datetime import datetime

def test_sina_realtime():
    """测试新浪财经实时数据"""
    print("\n" + "="*80)
    print("📡 测试新浪财经数据源")
    print("="*80)
    
    stock_code = "sh605289"
    url = f"http://hq.sinajs.cn/list={stock_code}"
    
    print(f"\n尝试连接: {url}")
    print(f"超时设置: 15秒")
    
    for attempt in range(1, 4):
        print(f"\n第 {attempt} 次尝试...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'http://finance.sina.com.cn'
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=15)
            elapsed = time.time() - start_time
            
            print(f"✓ 连接成功! 耗时: {elapsed:.2f}秒")
            print(f"响应状态码: {response.status_code}")
            print(f"响应长度: {len(response.text)} 字节")
            
            response.encoding = 'gb2312'
            data = response.text
            
            print(f"\n原始数据:")
            print(data[:200])
            
            if '=' in data:
                parts = data.split('=')[-1].strip().replace('"', '')
                fields = parts.split(',')
                
                if len(fields) >= 10:
                    print(f"\n✅ 解析成功!")
                    print(f"\n📊 罗曼股份(SH605289) 实时行情:")
                    print(f"   股票名称: {fields[0]}")
                    print(f"   今日开盘价: ¥{fields[1]}")
                    print(f"   昨日收盘价: ¥{fields[2]}")
                    print(f"   当前价格: ¥{fields[3]}")
                    print(f"   今日最高价: ¥{fields[4]}")
                    print(f"   今日最低价: ¥{fields[5]}")
                    print(f"   成交金额: ¥{float(fields[6]):,.2f}")
                    print(f"   成交量: {int(float(fields[7])):,}股")
                    print(f"   更新时间: {fields[30] if len(fields) > 30 else fields[31]}")
                    
                    return True
                    
        except requests.exceptions.Timeout:
            print(f"✗ 第 {attempt} 次尝试超时")
        except requests.exceptions.ConnectionError as e:
            print(f"✗ 第 {attempt} 次尝试连接失败: 网络错误")
        except Exception as e:
            print(f"✗ 第 {attempt} 次尝试失败: {e}")
        
        if attempt < 3:
            print(f"等待 3 秒后重试...")
            time.sleep(3)
    
    return False

def test_eastmoney_realtime():
    """测试东方财富实时数据"""
    print("\n" + "="*80)
    print("📡 测试东方财富数据源")
    print("="*80)
    
    stock_code = "605289"
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid=0.{stock_code}&fields=f43,f44,f45,f46,f47,f48,f57,f58"
    
    print(f"\n尝试连接: {url}")
    
    for attempt in range(1, 4):
        print(f"\n第 {attempt} 次尝试...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=15)
            elapsed = time.time() - start_time
            
            print(f"✓ 连接成功! 耗时: {elapsed:.2f}秒")
            print(f"响应状态码: {response.status_code}")
            
            import json
            data = response.json()
            
            if 'data' in data:
                d = data['data']
                print(f"\n✅ 获取到实时数据!")
                print(f"\n📊 罗曼股份(605289) 实时行情:")
                print(f"   当前价格: ¥{d.get('f43', 0) / 100:.2f}")
                print(f"   最高价: ¥{d.get('f44', 0) / 100:.2f}")
                print(f"   最低价: ¥{d.get('f45', 0) / 100:.2f}")
                print(f"   开盘价: ¥{d.get('f46', 0) / 100:.2f}")
                print(f"   成交量: {d.get('f47', 0):,}股")
                print(f"   股票名称: {d.get('f58', '未知')}")
                return True
                
        except requests.exceptions.Timeout:
            print(f"✗ 第 {attempt} 次尝试超时")
        except Exception as e:
            print(f"✗ 第 {attempt} 次尝试失败: {e}")
        
        if attempt < 3:
            time.sleep(2)
    
    return False

def check_network():
    """检查网络状态"""
    print("\n" + "="*80)
    print("🌐 网络状态检查")
    print("="*80)
    
    test_urls = [
        ("百度", "https://www.baidu.com"),
        ("新浪财经", "http://hq.sinajs.cn"),
        ("东方财富", "http://push2.eastmoney.com"),
    ]
    
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✓ {name}: 正常 (状态码: {response.status_code})")
        except:
            print(f"✗ {name}: 无法访问")

def main():
    print("\n" + "="*80)
    print("🦅 涨停先知 - 实时数据测试工具")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    check_network()
    
    success = test_sina_realtime()
    
    if not success:
        print("\n" + "="*80)
        print("⚠️  新浪财经数据源不可用")
        print("="*80)
        
        if test_eastmoney_realtime():
            print("\n✓ 东方财富数据源可用，将使用东方财富获取实时数据")
    else:
        print("\n✓ 新浪财经数据源正常工作")
    
    print("\n" + "="*80)
    print("💡 提示:")
    print("   - 如果所有数据源都不可用，可能是网络防火墙或代理问题")
    print("   - 可以尝试使用VPN或检查系统代理设置")
    print("   - 实时数据在交易时间内(9:30-15:00)更新最频繁")
    print("="*80)

if __name__ == "__main__":
    main()
