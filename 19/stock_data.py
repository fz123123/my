import requests
import pandas as pd
import time
import logging
from config import HEADERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SINA_API_URL = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"

def fetch_all_stocks(max_retries=3):
    params = {
        'page': 1,
        'num': 40,
        'sort': 'changepercent',
        'asc': 0,
        'node': 'hs_a',
        'symbol': '',
        '_s_r_a': 'page'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(SINA_API_URL, params=params, headers=HEADERS, timeout=30)
            response.raise_for_status()
            response.encoding = 'gbk'
            
            text = response.text
            if not text or text == 'null':
                logger.warning("API返回数据为空")
                return pd.DataFrame()
            
            import re
            json_str = re.search(r'\[.*\]', text)
            if not json_str:
                logger.warning("无法解析JSON数据")
                return pd.DataFrame()
            
            import json
            data = json.loads(json_str.group())
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            
            df['symbol'] = df['symbol'].str.replace('sh', '').str.replace('sz', '').str.replace('bj', '')
            df['code'] = df['symbol']
            
            df = df.rename(columns={
                'name': 'name',
                'trade': 'price',
                'pricechange': 'change_amount',
                'changepercent': 'change_pct',
                'settlement': 'prev_close',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'volume': 'volume',
                'amount': 'turnover',
                'turnoverratio': 'turnover_rate',
                'per': 'pe',
                'pb': 'pb',
            })
            
            for col in ['price', 'change_amount', 'change_pct', 'prev_close', 'open', 'high', 'low', 'volume', 'turnover', 'turnover_rate', 'pe', 'pb']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['high_limit'] = df['prev_close'] * 1.1
            df['low_limit'] = df['prev_close'] * 0.9
            
            return df
            
        except Exception as e:
            logger.warning(f"获取股票列表失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    logger.error(f"获取股票列表失败，已重试 {max_retries} 次")
    return pd.DataFrame()

def fetch_stock_by_code(code):
    try:
        symbol = f'sh{code}' if code.startswith('6') else f'sz{code}'
        url = f'https://hq.sinajs.cn/list={symbol}'
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'gbk'
        
        text = response.text
        if '="="' in text:
            return None
        
        data = text.split('"')[1].split(',')
        
        return {
            'code': code,
            'name': data[0],
            'price': float(data[3]),
            'prev_close': float(data[2]),
            'open': float(data[1]),
            'volume': float(data[8]) * 100,
            'turnover': float(data[9]),
            'high': float(data[4]),
            'low': float(data[5]),
            'change_pct': (float(data[3]) - float(data[2])) / float(data[2]) * 100 if float(data[2]) != 0 else 0,
            'change_amount': float(data[3]) - float(data[2]),
            'turnover_rate': 0.0,
            'pe': 0.0,
            'pb': 0.0,
            'high_limit': float(data[2]) * 1.1,
            'low_limit': float(data[2]) * 0.9,
        }
    except Exception as e:
        logger.error(f"获取股票 {code} 数据失败: {e}")
        return None

def get_market_code(code):
    if code.startswith('6'):
        return '1'
    elif code.startswith('0') or code.startswith('3'):
        return '0'
    return '1'

if __name__ == '__main__':
    stocks = fetch_all_stocks()
    print(f"获取到 {len(stocks)} 只股票")
    if not stocks.empty:
        print(stocks[['code', 'name', 'price', 'change_pct']].head())
