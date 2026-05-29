import pandas as pd
import numpy as np
import logging
from config import LIMIT_UP_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LimitUpRadar:
    def __init__(self):
        self.limit_up_stocks = []
        self.monitored_stocks = []
        self.history = []
    
    def detect_limit_up(self, stocks_df):
        if stocks_df.empty:
            return pd.DataFrame()
        
        limit_up = stocks_df[stocks_df['change_pct'] >= LIMIT_UP_THRESHOLD].copy()
        limit_up = limit_up.sort_values('change_pct', ascending=False)
        
        return limit_up
    
    def analyze_limit_up_stocks(self, limit_up_df):
        if limit_up_df.empty:
            return []
        
        analysis_results = []
        
        for _, row in limit_up_df.iterrows():
            analysis = {
                'code': row['code'],
                'name': row['name'],
                'price': row['price'],
                'change_pct': row['change_pct'],
                'change_amount': row['change_amount'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'volume': row['volume'],
                'turnover': row['turnover'],
                'turnover_rate': row['turnover_rate'],
                'pe': row['pe'],
                'pb': row['pb'],
                'high_limit': row['high_limit'],
                'prev_close': row['prev_close'],
                'analysis': self._analyze_single_stock(row),
                'risk_level': self._calculate_risk_level(row),
            }
            analysis_results.append(analysis)
        
        return analysis_results
    
    def _analyze_single_stock(self, row):
        factors = []
        
        if row['turnover_rate'] > 20:
            factors.append('高换手率')
        elif row['turnover_rate'] > 10:
            factors.append('换手率较高')
        
        if row['volume'] > 1000000:
            factors.append('成交量巨大')
        
        if row['change_pct'] >= 9.95:
            factors.append('强势涨停')
        elif row['change_pct'] >= 9.9:
            factors.append('接近涨停')
        
        if row['open'] == row['high_limit']:
            factors.append('开盘涨停')
        elif row['low'] == row['high_limit']:
            factors.append('低位拉涨停')
        
        if row['pe'] > 100:
            factors.append('高市盈率')
        elif row['pe'] < 10:
            factors.append('低市盈率')
        
        if not factors:
            factors.append('正常涨停')
        
        return factors
    
    def _calculate_risk_level(self, row):
        risk_score = 0
        
        if row['turnover_rate'] > 20:
            risk_score += 2
        elif row['turnover_rate'] > 10:
            risk_score += 1
        
        if row['pe'] > 100:
            risk_score += 2
        elif row['pe'] > 50:
            risk_score += 1
        
        if row['change_pct'] >= 9.95 and row['volume'] > 500000:
            risk_score += 1
        
        if risk_score >= 4:
            return '高风险'
        elif risk_score >= 2:
            return '中风险'
        else:
            return '低风险'
    
    def add_monitor_stock(self, code, name):
        if code not in [s['code'] for s in self.monitored_stocks]:
            self.monitored_stocks.append({'code': code, 'name': name})
            logger.info(f"已添加监控股票: {code} {name}")
    
    def remove_monitor_stock(self, code):
        self.monitored_stocks = [s for s in self.monitored_stocks if s['code'] != code]
        logger.info(f"已移除监控股票: {code}")
    
    def get_monitored_stocks(self):
        return self.monitored_stocks
    
    def save_history(self, analysis_results, timestamp):
        record = {
            'timestamp': timestamp,
            'count': len(analysis_results),
            'stocks': analysis_results
        }
        self.history.append(record)
        
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def get_history_summary(self):
        if not self.history:
            return None
        
        recent = self.history[-5:]
        avg_count = np.mean([r['count'] for r in recent])
        max_count = max([r['count'] for r in recent])
        min_count = min([r['count'] for r in recent])
        
        return {
            'recent_count': len(recent),
            'avg_limit_up': round(avg_count, 2),
            'max_limit_up': max_count,
            'min_limit_up': min_count,
        }

def format_stock_info(stock):
    info = f"""【{stock['name']}】({stock['code']})
├── 当前价格: {stock['price']:.2f} 元
├── 涨幅: {stock['change_pct']:.2f}%
├── 涨跌额: {stock['change_amount']:.2f} 元
├── 开盘价: {stock['open']:.2f} 元
├── 最高价: {stock['high']:.2f} 元
├── 最低价: {stock['low']:.2f} 元
├── 成交量: {format_volume(stock['volume'])}
├── 成交额: {format_turnover(stock['turnover'])}
├── 换手率: {stock['turnover_rate']:.2f}%
├── 市盈率: {stock['pe']:.2f}
├── 市净率: {stock['pb']:.2f}
├── 涨停价: {stock['high_limit']:.2f} 元
├── 分析: {', '.join(stock['analysis'])}
└── 风险等级: {stock['risk_level']}"""
    return info

def format_volume(volume):
    if volume >= 100000000:
        return f"{volume / 100000000:.2f} 亿"
    elif volume >= 10000:
        return f"{volume / 10000:.2f} 万"
    return f"{volume}"

def format_turnover(turnover):
    if turnover >= 100000000:
        return f"{turnover / 100000000:.2f} 亿元"
    elif turnover >= 10000:
        return f"{turnover / 10000:.2f} 万元"
    return f"{turnover} 元"

if __name__ == '__main__':
    from stock_data import fetch_all_stocks
    
    radar = LimitUpRadar()
    stocks = fetch_all_stocks()
    
    if not stocks.empty:
        limit_up = radar.detect_limit_up(stocks)
        print(f"检测到 {len(limit_up)} 只涨停股票")
        
        if not limit_up.empty:
            analysis = radar.analyze_limit_up_stocks(limit_up)
            for stock in analysis[:5]:
                print(format_stock_info(stock))
                print()
