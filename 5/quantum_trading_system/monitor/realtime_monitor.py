import sys
import os
import time
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import DataFetcher
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross, StrategyMultiFactor
from utils.auto_manager import AutoManager
from utils.stock_names import get_stock_name
from config import config


class RealtimeMonitor:
    def __init__(self, strict_mode=False):
        self.fetcher = DataFetcher(strict_mode=strict_mode)
        self.auto_manager = AutoManager()
        self.strict_mode = strict_mode
        self.strategies = {
            'macross': StrategyMaCross(),
            'multifactor': StrategyMultiFactor()
        }
        self.stock_names = {
            '600519.SH': '贵州茅台',
            '601318.SH': '中国平安',
            '600036.SH': '招商银行',
            '600030.SH': '中信证券',
            '601888.SH': '中国中免',
            '600276.SH': '恒瑞医药',
            '601328.SH': '交通银行',
            '600887.SH': '伊利股份',
            '600900.SH': '长江电力',
            '600028.SH': '中国石化',
            '000001.SZ': '平安银行',
            '000002.SZ': '万科A',
            '000858.SZ': '五粮液',
            '002415.SZ': '海康威视',
            '000333.SZ': '美的集团',
            '002594.SZ': '比亚迪',
            '300750.SZ': '宁德时代',
            '002371.SZ': '北方华创',
            '688981.SH': '中芯国际',
            '300015.SZ': '爱尔眼科',
            '600585.SH': '海螺水泥',
            '600104.SH': '上汽集团',
            '002475.SZ': '立讯精密',
            '000651.SZ': '格力电器',
            '002714.SZ': '牧原股份',
            '601012.SH': '隆基绿能',
            '603501.SH': '韦尔股份',
            '600690.SH': '海尔智家',
            '002459.SZ': '晶澳科技',
            '000063.SZ': '中兴通讯',
            '601398.SH': '工商银行',
            '601390.SH': '中国中铁',
            '001979.SZ': '招商蛇口',
            '601288.SH': '农业银行',
            '601939.SH': '建设银行',
            '002410.SZ': '广联达',
            '300059.SZ': '东方财富',
            '002601.SZ': '龙蟒佰利',
            '601211.SH': '国泰君安',
            '000725.SZ': '京东方A',
            '300760.SZ': '迈瑞医疗',
            '600009.SH': '上海机场',
            '600600.SH': '青岛啤酒',
            '600588.SH': '用友网络',
            '601601.SH': '中国太保',
            '600019.SH': '宝钢股份',
            '601238.SH': '广汽集团',
            '002555.SZ': '三七互娱',
            '300122.SZ': '智飞生物',
            '300142.SZ': '沃森生物',
            'BTCUSDT': '比特币',
            'ETHUSDT': '以太坊',
            '600130.SH': '波导股份',
            '601138.SH': '工业富联',
            '301275.SZ': '汉朔科技',
            '603118.SH': '共进股份',
            '603660.SH': '苏州科达',
            '002079.SZ': '苏州固锝',
            '603688.SH': '石英股份',
            '603778.SH': '国晟科技',
            '603681.SH': '永冠新材',
            '002222.SZ': '福晶科技',
            '603045.SH': '福达合金',
            '001339.SZ': '智微智能',
            '002276.SZ': '万马股份',
            '603738.SH': '泰晶科技',
            '002918.SZ': '蒙娜丽莎',
            '603007.SH': '花王股份',
            '600530.SH': '交大昂立',
            '600076.SH': '康欣新材',
            '600736.SH': '苏州高新',
            '002229.SZ': '鸿博股份',
            '601991.SH': '大唐发电',
            '600685.SH': '华东重机',
            '002491.SZ': '通鼎互联',
            '002655.SZ': '共达电声',
            '000977.SZ': '浪潮信息',
            '605289.SH': '罗曼股份',
            '002361.SZ': '神剑股份',
            '002291.SZ': '遥望科技',
            '605399.SH': '晨光新材',
            '600152.SH': '维科技术',
            '002602.SZ': '世纪华通',
            '603618.SH': '杭电股份',
            '600584.SH': '长电科技',
            '002363.SZ': '隆基机械',
            '601985.SH': '中国核电',
            '605298.SH': '舒华体育',
            '002553.SZ': '南方精工',
            '601088.SH': '中国神华',
            '002565.SZ': '顺灏股份',
            '603890.SH': '春秋电子',
            '603933.SH': '睿能科技',
            '002217.SZ': '合力泰'
        }

    def get_stock_name(self, symbol):
        if symbol in self.stock_names:
            return self.stock_names[symbol]
        if '.' in symbol:
            code = symbol.split('.')[0]
            name = get_stock_name(code)
            if name != code:
                return name
        return symbol

    def check_signals(self, symbol):
        if symbol.endswith('.SZ') or symbol.endswith('.SH'):
            df = self.fetcher.get_stock_data(symbol)
        else:
            df = self.fetcher.get_crypto_data(symbol)

        if df is None or len(df) < 60:
            return None

        df = calculate_indicators(df)

        signals = {}
        for name, strategy in self.strategies.items():
            sig = strategy.generate_signals(df)
            if len(sig) > 0:
                last_signal = sig.iloc[-1]
                signals[name] = last_signal

        latest = df.iloc[-1]

        return {
            'symbol': symbol,
            'price': latest['close'],
            'ma5': latest.get('ma5', None),
            'ma20': latest.get('ma20', None),
            'rsi': latest.get('rsi', None),
            'bb_position': latest.get('bb_position', None),
            'signals': signals,
            'data': df
        }

    def run_monitor(self, symbols=None, interval=60):
        if symbols is None:
            symbols = config['watchlist']

        print(f"\n{'='*80}")
        print(f"{'量子交易系统 - 实时监控':^80}")
        print(f"{'='*80}\n")

        self.auto_manager.auto_backup()

        try:
            while True:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在扫描...")
                print("-" * 80)

                all_signals = []
                buy_signals = []
                sell_signals = []

                for symbol in symbols:
                    try:
                        result = self.check_signals(symbol)
                        if result:
                            all_signals.append(result)
                            self._print_signal(result)
                            
                            for sig in result['signals'].values():
                                if sig == 1:
                                    buy_signals.append(symbol)
                                elif sig == -1:
                                    sell_signals.append(symbol)
                    except Exception as e:
                        stock_name = self.get_stock_name(symbol)
                        print(f"{stock_name} ({symbol}) 检查失败: {e}")

                if buy_signals or sell_signals:
                    print("\n" + "="*80)
                    print("🎯 交易信号提醒")
                    print("="*80)
                    if buy_signals:
                        print(f"💰 买入信号 ({len(buy_signals)}只):")
                        for s in buy_signals:
                            print(f"   • {self.get_stock_name(s)}")
                    if sell_signals:
                        print(f"⚠️ 卖出信号 ({len(sell_signals)}只):")
                        for s in sell_signals:
                            print(f"   • {self.get_stock_name(s)}")

                if all_signals:
                    self.auto_manager.auto_save(all_signals, 'monitor_signals')

                self.auto_manager.auto_backup()
                self.auto_manager.auto_cleanup()

                print(f"\n等待 {interval} 秒后更新... (按 Ctrl+C 退出)")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n监控已停止")

    def _print_signal(self, result):
        symbol = result['symbol']
        stock_name = self.get_stock_name(symbol)
        price = result['price']
        rsi = result.get('rsi', 0)
        bb_pos = result.get('bb_position', 0)

        signal_text = []
        for name, sig in result['signals'].items():
            if sig == 1:
                strategy_name = '均线交叉' if name == 'macross' else '多因子'
                signal_text.append(f"[💰{strategy_name}:买入]")
            elif sig == -1:
                strategy_name = '均线交叉' if name == 'macross' else '多因子'
                signal_text.append(f"[⚠️{strategy_name}:卖出]")

        signal_str = " ".join(signal_text) if signal_text else "[无信号]"

        print(f"{stock_name:10} {symbol:12} 价格: {price:8.2f} | RSI: {rsi:5.1f} | BB: {bb_pos:.2f} | {signal_str}")
