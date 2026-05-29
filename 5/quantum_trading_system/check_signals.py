import json
import os

def check_latest_signals():
    save_dir = 'backups/saves'
    files = [f for f in os.listdir(save_dir) if f.startswith('monitor_signals')]
    
    if not files:
        print('❌ 未找到信号文件')
        return
    
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(save_dir, latest_file)
    
    print('📊 最新信号文件分析')
    print('=' * 40)
    print(f'文件名: {latest_file}')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'股票数量: {len(data)}')
    print()
    print('📈 最新价格示例:')
    for item in data[:5]:
        print(f"  {item.get('symbol', '')}: {item.get('price', 0):.2f}")
    
    buy_count = 0
    sell_count = 0
    buy_stocks = []
    sell_stocks = []
    
    for item in data:
        signals = item.get('signals', {})
        if signals.get('multifactor') == 'buy' or signals.get('macross') == 'buy':
            buy_count += 1
            buy_stocks.append(item)
        if signals.get('multifactor') == 'sell' or signals.get('macross') == 'sell':
            sell_count += 1
            sell_stocks.append(item)
    
    print()
    print('📊 信号统计:')
    print(f'  买入信号: {buy_count}')
    print(f'  卖出信号: {sell_count}')
    
    if buy_stocks:
        print()
        print('🟢 买入信号列表:')
        for stock in buy_stocks:
            print(f"  - {stock.get('symbol', '')}: {stock.get('price', 0):.2f}")
    
    if sell_stocks:
        print()
        print('🔴 卖出信号列表:')
        for stock in sell_stocks:
            print(f"  - {stock.get('symbol', '')}: {stock.get('price', 0):.2f}")

if __name__ == '__main__':
    check_latest_signals()