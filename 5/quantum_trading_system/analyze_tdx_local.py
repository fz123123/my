# -*- coding: utf-8 -*-
"""
使用通达信本地盘后数据进行分析
"""

import os
import struct
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TDX_PATH = r"C:\new_tdx"

def read_tdx_block_file(filepath):
    """读取通达信板块文件"""
    stocks = []
    if not os.path.exists(filepath):
        return stocks
    
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        lines = data.decode('gbk', errors='ignore').split('\r\n')
        
        for line in lines:
            line = line.strip()
            if len(line) >= 7 and line[:7].isdigit():
                code_part = line[:6]
                market_code = line[6]
                
                if market_code == '5':
                    market = 'SH'
                    if code_part.startswith('1'):
                        code = '6' + code_part[1:]
                    else:
                        code = code_part
                else:
                    market = 'SZ'
                    code = code_part
                
                if code.isdigit() and len(code) == 6:
                    full_code = f"{code}.{market}"
                    if full_code not in stocks:
                        stocks.append(full_code)
    except Exception as e:
        print(f"读取板块文件失败: {e}")
    
    return stocks

def read_tdx_day_data(code, market):
    """读取通达信日线数据"""
    market_dir = 'sh' if market == 'SH' else 'sz'
    code_prefix = code[:3]
    
    folder_map = {
        '000': 'lday',
        '001': 'lday',
        '002': 'lday',
        '003': 'lday',
        '004': 'lday',
        '005': 'lday',
        '006': 'lday',
        '007': 'lday',
        '008': 'lday',
        '009': 'lday',
        '010': 'lday',
        '011': 'lday',
        '012': 'lday',
        '013': 'lday',
        '015': 'lday',
        '016': 'lday',
        '018': 'lday',
        '030': 'lday',
        '039': 'lday',
        '068': 'lday',
        '086': 'lday',
        '159': 'lday',
        '160': 'fund',
        '161': 'fund',
        '162': 'fund',
        '163': 'fund',
        '164': 'fund',
        '165': 'fund',
        '166': 'fund',
        '167': 'fund',
        '168': 'fund',
        '169': 'fund',
        '510': 'fund',
        '512': 'fund',
        '513': 'fund',
        '515': 'fund',
        '516': 'fund',
        '518': 'fund',
        '519': 'fund',
        '520': 'fund',
        '521': 'fund',
        '522': 'fund',
        '523': 'fund',
        '588': 'fund',
        '600': 'lday',
        '601': 'lday',
        '603': 'lday',
        '605': 'lday',
        '660': 'lday',
        '688': 'lday',
        '900': 'lday'
    }
    
    folder = folder_map.get(code_prefix, 'lday')
    
    data_path = os.path.join(TDX_PATH, 'vipdoc', market_dir, folder, f"{market_dir}{code}.day")
    
    if not os.path.exists(data_path):
        return None
    
    try:
        with open(data_path, 'rb') as f:
            data = f.read()
        
        records = []
        length = len(data)
        record_size = 32
        
        for i in range(0, length, record_size):
            record = data[i:i+record_size]
            if len(record) < record_size:
                continue
            
            date = struct.unpack('<I', record[0:4])[0]
            open_price = struct.unpack('<f', record[4:8])[0]
            high_price = struct.unpack('<f', record[8:12])[0]
            low_price = struct.unpack('<f', record[12:16])[0]
            close_price = struct.unpack('<f', record[16:20])[0]
            volume = struct.unpack('<I', record[20:24])[0]
            amount = struct.unpack('<I', record[24:28])[0]
            
            date_str = str(date)
            date_obj = datetime(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
            
            records.append({
                'date': date_obj,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': amount
            })
        
        if not records:
            return None
        
        df = pd.DataFrame(records)
        df = df.sort_values('date')
        df = df.set_index('date')
        df['change'] = df['close'].diff()
        df['change_pct'] = df['close'].pct_change() * 100
        
        return df
    
    except Exception as e:
        print(f"读取日线数据失败 {code}.{market}: {e}")
        return None

def calculate_indicators(df):
    """计算技术指标"""
    df = df.copy()
    
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, 0.001)
    df['rsi'] = 100 - (100 / (1 + rs))
    
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    bb_mid = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = bb_mid + 2 * bb_std
    df['bb_lower'] = bb_mid - 2 * bb_std
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower']).replace(0, 0.001)
    
    low_min = df['low'].rolling(window=9).min()
    high_max = df['high'].rolling(window=9).max()
    df['kdj_k'] = ((df['close'] - low_min) / (high_max - low_min).replace(0, 0.001)) * 100
    df['kdj_d'] = df['kdj_k'].rolling(window=3).mean()
    df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
    
    return df

def analyze_stock(df, symbol):
    """分析单个股票"""
    if df is None or len(df) < 60:
        return None
    
    df = calculate_indicators(df)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    analysis = {
        'symbol': symbol,
        'current_price': latest['close'],
        'price_change': round(latest['close'] - prev['close'], 2),
        'price_change_pct': round((latest['close'] - prev['close']) / prev['close'] * 100, 2),
        'volume': latest['volume'],
        'ma5': round(latest.get('ma5', 0), 2),
        'ma20': round(latest.get('ma20', 0), 2),
        'ma60': round(latest.get('ma60', 0), 2),
        'rsi': round(latest.get('rsi', 0), 1),
        'macd': round(latest.get('macd', 0), 4),
        'macd_signal': round(latest.get('macd_signal', 0), 4),
        'bb_position': round(latest.get('bb_position', 0), 2),
        'kdj_k': round(latest.get('kdj_k', 0), 1),
        'kdj_d': round(latest.get('kdj_d', 0), 1),
        'kdj_j': round(latest.get('kdj_j', 0), 1)
    }
    
    analysis['ma_status'] = analyze_ma(analysis)
    analysis['rsi_status'] = analyze_rsi(analysis)
    analysis['macd_status'] = analyze_macd(analysis)
    analysis['bb_status'] = analyze_bollinger(analysis)
    analysis['kdj_status'] = analyze_kdj(analysis)
    
    analysis['score'] = calculate_score(analysis)
    analysis['recommendation'] = get_recommendation(analysis['score'])
    
    return analysis

def analyze_ma(data):
    if data['ma5'] == 0 or data['ma20'] == 0:
        return '数据不足'
    if data['current_price'] > data['ma5'] > data['ma20']:
        return '多头排列'
    elif data['current_price'] < data['ma5'] < data['ma20']:
        return '空头排列'
    elif data['ma5'] > data['ma20']:
        return '短期强势'
    else:
        return '短期弱势'

def analyze_rsi(data):
    if data['rsi'] == 0:
        return '数据不足'
    if data['rsi'] < 30:
        return '超卖区'
    elif data['rsi'] > 70:
        return '超买区'
    elif data['rsi'] < 50:
        return '偏弱'
    else:
        return '偏强'

def analyze_macd(data):
    if data['macd'] == 0 or data['macd_signal'] == 0:
        return '数据不足'
    if data['macd'] > data['macd_signal']:
        return 'MACD金叉'
    else:
        return 'MACD死叉'

def analyze_bollinger(data):
    if data['bb_position'] == 0:
        return '数据不足'
    if data['bb_position'] < 0.2:
        return '接近下轨'
    elif data['bb_position'] > 0.8:
        return '接近上轨'
    else:
        return '区间中部'

def analyze_kdj(data):
    if data['kdj_k'] == 0 or data['kdj_d'] == 0:
        return '数据不足'
    if data['kdj_j'] < 20:
        return 'KDJ超卖'
    elif data['kdj_j'] > 80:
        return 'KDJ超买'
    elif data['kdj_k'] > data['kdj_d']:
        return 'KDJ金叉'
    else:
        return 'KDJ死叉'

def calculate_score(analysis):
    score = 0
    
    if analysis['ma_status'] in ['多头排列', '短期强势']:
        score += 2
    elif analysis['ma_status'] in ['空头排列', '短期弱势']:
        score -= 2
    
    if analysis['rsi_status'] == '超卖区':
        score += 1
    elif analysis['rsi_status'] == '超买区':
        score -= 1
    
    if analysis['macd_status'] == 'MACD金叉':
        score += 2
    elif analysis['macd_status'] == 'MACD死叉':
        score -= 2
    
    if analysis['bb_status'] == '接近下轨':
        score += 1
    elif analysis['bb_status'] == '接近上轨':
        score -= 1
    
    if analysis['kdj_status'] == 'KDJ超卖':
        score += 1
    elif analysis['kdj_status'] == 'KDJ超买':
        score -= 1
    
    return score

def get_recommendation(score):
    if score >= 5:
        return '强烈买入'
    elif score >= 3:
        return '买入'
    elif score >= 1:
        return '谨慎买入'
    elif score <= -5:
        return '强烈卖出'
    elif score <= -3:
        return '卖出'
    elif score <= -1:
        return '谨慎卖出'
    else:
        return '观望'

def main():
    print(f"\n{'='*80}")
    print(f"  📊 通达信本地盘后数据全盘分析报告")
    print(f"     {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print(f"{'='*80}")
    
    zxg_path = os.path.join(TDX_PATH, "T0002", "blocknew", "zxg.blk")
    stocks = read_tdx_block_file(zxg_path)
    
    if not stocks:
        print("\n❌ 未找到自选股数据")
        return
    
    print(f"\n📂 发现 {len(stocks)} 只自选股")
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(stocks, 1):
        print(f"\r正在分析: {i}/{len(stocks)} {symbol}...", end='', flush=True)
        
        try:
            code, market = symbol.split('.')
            df = read_tdx_day_data(code, market)
            
            if df is None or len(df) < 60:
                fail_count += 1
                continue
            
            analysis = analyze_stock(df, symbol)
            if analysis:
                results.append(analysis)
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            fail_count += 1
            continue
    
    print(f"\r{'='*80}\r")
    print(f"\n✅ 分析完成: 成功 {success_count} 只, 失败 {fail_count} 只")
    
    if not results:
        print("\n❌ 没有有效分析结果")
        return
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('score', ascending=False)
    
    generate_report(results_df)
    save_report(results_df)

def generate_report(df):
    print(f"\n{'='*80}")
    print("  🥇 强烈买入信号 (评分 >= 5)")
    print(f"{'='*80}")
    
    buy_signals = df[df['recommendation'] == '强烈买入']
    if not buy_signals.empty:
        for _, row in buy_signals.iterrows():
            print(f"\n📈 {row['symbol']}")
            print(f"   收盘价: {row['current_price']:.2f} | 涨跌幅: {row['price_change_pct']:+.2f}%")
            print(f"   评分: {row['score']} | 均线: {row['ma_status']} | RSI: {row['rsi']:.1f}")
            print(f"   MACD: {row['macd_status']} | KDJ: {row['kdj_status']}")
    else:
        print("   暂无强烈买入信号")
    
    print(f"\n{'='*80}")
    print("  🔔 买入信号 (评分 3-4)")
    print(f"{'='*80}")
    
    buy_careful = df[(df['recommendation'] == '买入') | (df['recommendation'] == '谨慎买入')]
    if not buy_careful.empty:
        for _, row in buy_careful.iterrows():
            print(f"\n📊 {row['symbol']}")
            print(f"   收盘价: {row['current_price']:.2f} | 涨跌幅: {row['price_change_pct']:+.2f}%")
            print(f"   评分: {row['score']} | 建议: {row['recommendation']}")
    else:
        print("   暂无买入信号")
    
    print(f"\n{'='*80}")
    print("  ⚠️ 卖出信号")
    print(f"{'='*80}")
    
    sell_signals = df[df['recommendation'].str.contains('卖出')]
    if not sell_signals.empty:
        for _, row in sell_signals.iterrows():
            print(f"\n📉 {row['symbol']}")
            print(f"   收盘价: {row['current_price']:.2f} | 涨跌幅: {row['price_change_pct']:+.2f}%")
            print(f"   评分: {row['score']} | 建议: {row['recommendation']}")
    else:
        print("   暂无卖出信号")
    
    print(f"\n{'='*80}")
    print("  📊 综合统计")
    print(f"{'='*80}")
    
    rec_counts = df['recommendation'].value_counts()
    print(f"\n信号分布:")
    for rec, count in rec_counts.items():
        print(f"   {rec}: {count}只 ({count/len(df)*100:.1f}%)")
    
    avg_score = df['score'].mean()
    print(f"\n平均评分: {avg_score:.2f}")
    print(f"最高评分: {df['score'].max()} | 最低评分: {df['score'].min()}")

def save_report(df):
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    md_report_name = f"通达信盘后分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    md_report_path = os.path.join(report_dir, md_report_name)
    
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 通达信本地盘后数据全盘分析报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"**分析股票数量**: {len(df)}\n\n")
        
        f.write("## 🥇 强烈买入信号\n\n")
        buy_signals = df[df['recommendation'] == '强烈买入']
        if not buy_signals.empty:
            for _, row in buy_signals.iterrows():
                f.write(f"- **{row['symbol']}**: {row['current_price']:.2f}元, 评分:{row['score']}, {row['ma_status']}, RSI:{row['rsi']:.1f}\n")
        else:
            f.write("暂无强烈买入信号\n")
        
        f.write("\n## 🔔 买入信号\n\n")
        buy_careful = df[(df['recommendation'] == '买入') | (df['recommendation'] == '谨慎买入')]
        if not buy_careful.empty:
            for _, row in buy_careful.iterrows():
                f.write(f"- **{row['symbol']}**: {row['current_price']:.2f}元, {row['recommendation']}\n")
        else:
            f.write("暂无买入信号\n")
        
        f.write("\n## ⚠️ 卖出信号\n\n")
        sell_signals = df[df['recommendation'].str.contains('卖出')]
        if not sell_signals.empty:
            for _, row in sell_signals.iterrows():
                f.write(f"- **{row['symbol']}**: {row['current_price']:.2f}元, {row['recommendation']}\n")
        else:
            f.write("暂无卖出信号\n")
        
        f.write("\n## 📊 综合统计\n\n")
        f.write(f"- 平均评分: {df['score'].mean():.2f}\n")
        f.write(f"- 最高评分: {df['score'].max()}\n")
        f.write(f"- 最低评分: {df['score'].min()}\n")
    
    print(f"\n📝 报告已保存: {md_report_path}")

if __name__ == "__main__":
    main()