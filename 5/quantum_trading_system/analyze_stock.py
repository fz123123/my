import json

def analyze_stock(stock_name):
    with open('backups/saves/monitor_signals_20260521_160731.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        signals = data.get('signals', [])
        stocks = data.get('stocks', [])
        
        found_stock = None
        found_signal = None
        
        for stock in stocks:
            if stock_name in stock.get('name', ''):
                found_stock = stock
                break
        
        for sig in signals:
            if stock_name in sig.get('name', ''):
                found_signal = sig
                break
        
        print('📊 ' + stock_name + ' 分析报告')
        print('=' * 40)
        
        if found_stock:
            print('股票代码:', found_stock.get('code', 'N/A'))
            print('股票名称:', found_stock.get('name', 'N/A'))
            print('最新价格:', round(found_stock.get('close', 0), 2))
            print('MA5:', round(found_stock.get('ma5', 0), 2))
            print('MA13:', round(found_stock.get('ma13', 0), 2))
            print('MA20:', round(found_stock.get('ma20', 0), 2))
            print('MA30:', round(found_stock.get('ma30', 0), 2))
            print('RSI:', round(found_stock.get('rsi', 0), 2))
            print('布林带位置:', round(found_stock.get('bb_position', 0), 2))
            print('成交量:', found_stock.get('volume', 0))
            print('涨跌幅:', str(round(found_stock.get('change_pct', 0), 2)) + '%')
            print()
            
            close = found_stock.get('close', 0)
            ma5 = found_stock.get('ma5', 0)
            ma13 = found_stock.get('ma13', 0)
            ma20 = found_stock.get('ma20', 0)
            rsi = found_stock.get('rsi', 0)
            
            print('📈 技术分析:')
            
            if close > ma5 and ma5 > ma13 and ma13 > ma20:
                print('   ✅ 均线多头排列，趋势向上')
            elif close < ma5 and ma5 < ma13 and ma13 < ma20:
                print('   ❌ 均线空头排列，趋势向下')
            else:
                print('   ⚠️ 均线缠绕，震荡行情')
            
            if close > ma5:
                print('   ✅ 价格在MA5之上')
            else:
                print('   ⚠️ 价格在MA5之下')
            
            if rsi > 70:
                print('   ⚠️ RSI超买，注意回调风险')
            elif rsi < 30:
                print('   ✅ RSI超卖，可能反弹')
            else:
                print('   ✅ RSI处于正常区间')
            
        else:
            print('❌ 未找到 ' + stock_name + ' 的数据')
        
        if found_signal:
            print()
            print('📊 交易信号:')
            if found_signal['signal'] == 'buy':
                print('   🟢 买入信号')
            else:
                print('   🔴 卖出信号')
            print('   信号来源:', found_signal.get('strategy', 'N/A'))
            print('   信号时间:', found_signal.get('datetime', 'N/A'))
        else:
            print()
            print('📊 交易信号:')
            print('   ⏳ 暂无明确信号，建议观望')

if __name__ == '__main__':
    analyze_stock('龙蟠科技')