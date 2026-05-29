import json
import os

def analyze_buy_conditions():
    save_dir = 'backups/saves'
    files = [f for f in os.listdir(save_dir) if f.startswith('monitor_signals')]
    
    if not files:
        print('❌ 未找到信号文件')
        return
    
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(save_dir, latest_file)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stock_scores = []
    
    for item in data:
        symbol = item.get('symbol', '')
        price = item.get('price', 0)
        ma5 = item.get('ma5', 0)
        ma20 = item.get('ma20', 0)
        rsi = item.get('rsi', 50)
        bb_pos = item.get('bb_position', 0)
        
        score = 0
        reasons = []
        
        if rsi < 35:
            score += (35 - rsi) * 2
            reasons.append(f"RSI接近超卖 ({rsi})")
        elif rsi < 45:
            score += (45 - rsi)
            reasons.append(f"RSI偏低 ({rsi})")
        
        if ma5 > 0 and price > 0:
            ma5_distance = abs(price - ma5) / ma5 * 100
            if ma5_distance < 3:
                score += (3 - ma5_distance) * 3
                if price < ma5:
                    reasons.append(f"接近MA5下方 ({ma5_distance:.1f}%)")
                else:
                    reasons.append(f"接近MA5 ({ma5_distance:.1f}%)")
        
        if bb_pos < 0.3:
            score += (0.3 - bb_pos) * 50
            reasons.append(f"布林带位置较低 ({bb_pos:.2f})")
        elif bb_pos < 0.5:
            score += (0.5 - bb_pos) * 20
            reasons.append(f"布林带中位偏下 ({bb_pos:.2f})")
        
        if ma20 > 0 and price > 0:
            ma20_distance = abs(price - ma20) / ma20 * 100
            if ma20_distance < 5:
                score += (5 - ma20_distance)
                reasons.append(f"接近MA20 ({ma20_distance:.1f}%)")
        
        stock_scores.append({
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'ma5': ma5,
            'ma20': ma20,
            'bb_pos': bb_pos,
            'score': score,
            'reasons': reasons
        })
    
    stock_scores.sort(key=lambda x: x['score'], reverse=True)
    
    print('📊 接近买入条件的股票排名')
    print('=' * 60)
    print(f"分析时间: {latest_file.split('_')[2]} {latest_file.split('_')[3].replace('.json', '')}")
    print(f"监控股票总数: {len(data)}")
    print('=' * 60)
    
    print(f"\n{'排名':<4} {'股票代码':<12} {'价格':<8} {'RSI':<6} {'BB位置':<8} {'接近度':<6} {'原因'}")
    print('-' * 60)
    
    for i, stock in enumerate(stock_scores[:10], 1):
        reason_text = '; '.join(stock['reasons']) if stock['reasons'] else '暂无'
        print(f"{i:<4} {stock['symbol']:<12} {stock['price']:<8.2f} {stock['rsi']:<6.1f} {stock['bb_pos']:<8.2f} {stock['score']:<6.1f} {reason_text}")
    
    print('\n📝 评分说明:')
    print('  • RSI接近30以下: 权重较高')
    print('  • 价格接近MA5: 权重较高')
    print('  • 布林带位置较低: 权重中等')
    print('  • 价格接近MA20: 权重较低')
    print('\n⚠️ 注意: 这只是技术指标分析，不构成投资建议')

if __name__ == '__main__':
    analyze_buy_conditions()