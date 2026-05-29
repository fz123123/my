import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

STOCK_API_URL = "https://push2.eastmoney.com/api/qt/clist/get"

LIMIT_UP_THRESHOLD = 9.8

UPDATE_INTERVAL = 60

STOCK_CODES_FILE = os.path.join(DATA_DIR, 'stock_codes.txt')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'http://quote.eastmoney.com/',
}
