# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False


class DataEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'market_data.db'
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        self.cache = {}
        self.cache_timeout = 300
        
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_daily (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                source TEXT,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_daily (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                source TEXT,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_data (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fundamentals (
                symbol TEXT,
                date TEXT,
                pe REAL,
                pb REAL,
                market_cap REAL,
                revenue REAL,
                profit REAL,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stock_data_akshare(self, symbol, start_date=None, end_date=None):
        if not AKSHARE_AVAILABLE:
            return None
            
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
            df = ak.stock_zh_a_hist(
                symbol=symbol_code,
                period='daily',
                start_date=start_date,
                end_date=end_date,
                adjust='qfq'
            )
            
            if not df.empty:
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                })
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                df['source'] = 'akshare'
                return df
        except Exception as e:
            print(f"akshare获取{symbol}失败: {e}")
        
        return None
    
    def get_stock_data_baostock(self, symbol, start_date=None, end_date=None):
        if not BAOSTOCK_AVAILABLE:
            return None
            
        try:
            bs.login()
            
            symbol_code = symbol.replace('.SZ', '.SZ').replace('.SH', '.SH')
            if 'SZ' in symbol:
                bs_code = f"sz{symbol.replace('.SZ', '')}"
            else:
                bs_code = f"sh{symbol.replace('.SH', '')}"
            
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,volume",
                start_date=start_date,
                end_date=end_date,
                frequency='d'
            )
            
            data_list = []
            while rs.error_code == '0' and rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if data_list:
                df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                df['source'] = 'baostock'
                return df
                
        except Exception as e:
            print(f"baostock获取{symbol}失败: {e}")
            try:
                bs.logout()
            except:
                pass
        
        return None
    
    def get_stock_data(self, symbol, start_date=None, end_date=None):
        cache_key = f"stock_{symbol}_{start_date}_{end_date}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        df = self.get_stock_data_akshare(symbol, start_date, end_date)
        
        if df is None:
            df = self.get_stock_data_baostock(symbol, start_date, end_date)
        
        if df is None:
            df = self._get_mock_data(symbol, start_date, end_date)
        
        if df is not None and len(df) > 0:
            self.cache[cache_key] = df
            self._save_to_db(symbol, df, 'stock_daily')
        
        return df
    
    def get_crypto_data_binance(self, symbol, interval='1d', limit=365):
        if not REQUESTS_AVAILABLE:
            return self._get_mock_crypto_data(symbol)
        
        cache_key = f"crypto_{symbol}_{interval}_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol.upper(),
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df.set_index('date')
                
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col])
                
                df = df.sort_index()
                df['source'] = 'binance'
                
                self.cache[cache_key] = df
                return df
                
        except Exception as e:
            print(f"Binance获取{symbol}失败: {e}")
        
        return self._get_mock_crypto_data(symbol)
    
    def get_index_data(self, index_code='000001.SH', start_date=None, end_date=None):
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        cache_key = f"index_{index_code}_{start_date}_{end_date}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if AKSHARE_AVAILABLE:
            try:
                df = ak.stock_zh_index_daily(symbol=index_code)
                df = df.rename(columns={
                    'date': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume'
                })
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                
                self.cache[cache_key] = df
                return df
            except Exception as e:
                print(f"获取指数{index_code}失败: {e}")
        
        return None
    
    def get_fundamental_data(self, symbol, date=None):
        if BAOSTOCK_AVAILABLE:
            try:
                bs.login()
                
                symbol_code = symbol.replace('.SZ', '').replace('.SH', '')
                if 'SZ' in symbol:
                    bs_code = f"sz{symbol_code}"
                else:
                    bs_code = f"sh{symbol_code}"
                
                if date is None:
                    date = datetime.now().strftime('%Y-%m-%d')
                
                rs = bs.query_profit_sheet(bs_code, date)
                
                data_list = []
                while rs.error_code == '0' and rs.next():
                    data_list.append(rs.get_row_data())
                
                bs.logout()
                
                if data_list:
                    return {'date': date, 'data': data_list}
                    
            except Exception as e:
                print(f"获取基本面数据失败: {e}")
                try:
                    bs.logout()
                except:
                    pass
        
        return None
    
    def _get_mock_data(self, symbol, start_date=None, end_date=None):
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365))
        else:
            start_date = datetime.strptime(start_date, '%Y%m%d')
        
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y%m%d')
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(hash(symbol) % 10000)
        
        base_price = 100
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
            'high': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
            'low': prices * (1 - np.random.uniform(0, 0.02, len(dates))),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        df['source'] = 'mock'
        return df
    
    def _get_mock_crypto_data(self, symbol):
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        np.random.seed(hash(symbol) % 10000)
        
        base_price = 1000
        returns = np.random.normal(0.002, 0.03, len(dates))
        prices = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.01, len(dates))),
            'high': prices * (1 + np.random.uniform(0, 0.05, len(dates))),
            'low': prices * (1 - np.random.uniform(0, 0.05, len(dates))),
            'close': prices,
            'volume': np.random.randint(10000, 100000, len(dates))
        }, index=dates)
        
        df['source'] = 'mock'
        return df
    
    def _save_to_db(self, symbol, df, table_name):
        try:
            conn = sqlite3.connect(self.db_path)
            
            df_reset = df.reset_index()
            df_reset['symbol'] = symbol
            df_reset['date'] = df_reset['date'].astype(str)
            
            df_reset.to_sql(table_name, conn, if_exists='append', index=False)
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
    
    def load_from_db(self, symbol, table_name='stock_daily', limit=365):
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f"""
                SELECT * FROM {table_name}
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(query, conn, params=[symbol, limit])
            conn.close()
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                return df
                
        except Exception as e:
            print(f"从数据库加载失败: {e}")
        
        return None
    
    def clear_cache(self):
        self.cache = {}
    
    def get_available_stocks(self):
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                "SELECT DISTINCT symbol FROM stock_daily",
                conn
            )
            conn.close()
            return df['symbol'].tolist()
        except:
            return []
    
    def get_data_status(self):
        conn = sqlite3.connect(self.db_path)
        
        stock_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM stock_daily", conn
        )['count'].iloc[0]
        
        crypto_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM crypto_daily", conn
        )['count'].iloc[0]
        
        stock_symbols = pd.read_sql_query(
            "SELECT COUNT(DISTINCT symbol) as count FROM stock_daily", conn
        )['count'].iloc[0]
        
        conn.close()
        
        return {
            'stock_records': stock_count,
            'crypto_records': crypto_count,
            'stock_symbols': stock_symbols,
            'cache_size': len(self.cache)
        }