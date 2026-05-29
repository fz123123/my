# -*- coding: utf-8 -*-

import os
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
CACHE_DIR = DATA_DIR / 'cache'
BACKTEST_DIR = DATA_DIR / 'backtest'
REPORT_DIR = DATA_DIR / 'reports'
LOG_DIR = DATA_DIR / 'logs'
BACKUP_DIR = BASE_DIR / 'backups'

for dir_path in [DATA_DIR, CACHE_DIR, BACKTEST_DIR, REPORT_DIR, LOG_DIR, BACKUP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = BASE_DIR / 'system_config.json'

DEFAULT_CONFIG = {
    'version': '3.0',
    'auto_save': True,
    'auto_backup': True,
    'backup_interval_hours': 24,
    'data_sources': {
        'akshare': True,
        'tushare': False,
        'binance': True
    },
    'trading': {
        'initial_capital': 100000,
        'fee_rate': 0.0004,
        'slippage': 0.0005,
        'max_position_ratio': 0.3
    },
    'risk_control': {
        'max_drawdown': 0.15,
        'stop_loss_default': 0.05,
        'take_profit_default': 0.10
    },
    'monitor': {
        'refresh_interval': 60,
        'enable_sound': True,
        'enable_notification': False
    },
    'watchlist': [
        '600519.SH', '000858.SZ', '603217.SH', '300750.SZ', '601318.SH',
        '000001.SZ', '000002.SZ', '600036.SH', '002594.SZ', '688981.SH',
        '601012.SH', '603501.SH', '002371.SZ', '600030.SH', '002415.SZ',
        '000333.SZ', '600150.SH', '600031.SH', '000651.SZ', '601899.SH',
        '000063.SZ', '002236.SZ', '600547.SH', '002456.SZ', '600436.SH',
        '600276.SH', '002142.SZ', '601398.SH', '601939.SH', '601328.SH',
        '601166.SH', '600000.SH', '000008.SZ', '000060.SZ', '000538.SZ',
        '000568.SZ', '000625.SZ', '000725.SZ', '000895.SZ', '000938.SZ'
    ],
    'last_updated': None
}

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return {**DEFAULT_CONFIG, **config}
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    config['last_updated'] = str(Path(__file__).stat().st_mtime)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()
