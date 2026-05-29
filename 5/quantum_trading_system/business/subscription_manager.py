# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from pathlib import Path
import hashlib


class SubscriptionManager:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / 'data' / 'subscriptions.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT,
                created_at TEXT,
                last_login TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                user_id TEXT,
                plan TEXT,
                status TEXT,
                start_date TEXT,
                end_date TEXT,
                auto_renew BOOLEAN DEFAULT 1,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                details TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            user_id = hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, self.hash_password(password), 
                  datetime.now().isoformat(), 'active'))
            
            cursor.execute('''
                INSERT INTO subscriptions (subscription_id, user_id, plan, status, start_date, end_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                hashlib.md5(f"sub{user_id}".encode()).hexdigest(),
                user_id,
                'free',
                'active',
                datetime.now().isoformat(),
                (datetime.now() + timedelta(days=365)).isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id}
            
        except Exception as e:
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def login(self, username, password):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, email, status FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, self.hash_password(password)))
        
        user = cursor.fetchone()
        
        if user:
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE user_id = ?
            ''', (datetime.now().isoformat(), user[0]))
            conn.commit()
            
            cursor.execute('''
                SELECT plan, status, end_date FROM subscriptions WHERE user_id = ?
            ''', (user[0],))
            
            sub = cursor.fetchone()
            conn.close()
            
            return {
                'success': True,
                'user': {
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'status': user[3]
                },
                'subscription': {
                    'plan': sub[0] if sub else 'free',
                    'status': sub[1] if sub else 'inactive',
                    'end_date': sub[2] if sub else None
                }
            }
        
        conn.close()
        return {'success': False, 'error': 'Invalid credentials'}
    
    def get_user_subscription(self, user_id):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT plan, status, start_date, end_date, auto_renew
            FROM subscriptions WHERE user_id = ?
        ''', (user_id,))
        
        sub = cursor.fetchone()
        conn.close()
        
        if sub:
            return {
                'plan': sub[0],
                'status': sub[1],
                'start_date': sub[2],
                'end_date': sub[3],
                'auto_renew': bool(sub[4])
            }
        
        return None
    
    def upgrade_subscription(self, user_id, plan, duration_days=30):
        import sqlite3
        
        plans = {
            'free': 0,
            'basic': 99,
            'pro': 299,
            'enterprise': 999
        }
        
        if plan not in plans:
            return {'success': False, 'error': 'Invalid plan'}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT end_date FROM subscriptions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        start_date = datetime.now()
        
        if result and result[0]:
            existing_end = datetime.fromisoformat(result[0])
            if existing_end > start_date:
                start_date = existing_end
        
        end_date = start_date + timedelta(days=duration_days)
        
        cursor.execute('''
            UPDATE subscriptions 
            SET plan = ?, status = 'active', start_date = ?, end_date = ?, auto_renew = 1
            WHERE user_id = ?
        ''', (plan, start_date.isoformat(), end_date.isoformat(), user_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'plan': plan,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'price': plans[plan] * (duration_days / 30)
        }
    
    def check_plan_limits(self, user_id, action):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT plan FROM subscriptions WHERE user_id = ? AND status = 'active'
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        plan = result[0] if result else 'free'
        
        limits = {
            'free': {
                'strategies': 3,
                'backtests_per_day': 10,
                'real_time_data': False,
                'advanced_indicators': False,
                'api_access': False,
                'priority_support': False
            },
            'basic': {
                'strategies': 10,
                'backtests_per_day': 50,
                'real_time_data': True,
                'advanced_indicators': False,
                'api_access': False,
                'priority_support': False
            },
            'pro': {
                'strategies': 100,
                'backtests_per_day': 500,
                'real_time_data': True,
                'advanced_indicators': True,
                'api_access': True,
                'priority_support': False
            },
            'enterprise': {
                'strategies': float('inf'),
                'backtests_per_day': float('inf'),
                'real_time_data': True,
                'advanced_indicators': True,
                'api_access': True,
                'priority_support': True
            }
        }
        
        return limits.get(plan, limits['free'])
    
    def log_usage(self, user_id, action, details=None):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usage_logs (user_id, action, details, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, json.dumps(details) if details else None, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_usage_stats(self, user_id, days=30):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT action, COUNT(*) as count
            FROM usage_logs
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY action
        ''', (user_id, start_date))
        
        stats = cursor.fetchall()
        conn.close()
        
        return {action: count for action, count in stats}
    
    def get_all_users(self):
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id, u.username, u.email, u.created_at, s.plan, s.status
            FROM users u
            LEFT JOIN subscriptions s ON u.user_id = s.user_id
            ORDER BY u.created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'created_at': user[3],
                'plan': user[4] if len(user) > 4 else 'free',
                'status': user[5] if len(user) > 5 else 'active'
            }
            for user in users
        ]


class PricingManager:
    def __init__(self):
        self.plans = self._load_plans()
    
    def _load_plans(self):
        return {
            'free': {
                'name': '鍏嶈垂鐗?,
                'price': 0,
                'period': '姘镐箙',
                'features': [
                    '3涓瓥鐣?,
                    '姣忔棩10娆″洖娴?,
                    '寤惰繜15鍒嗛挓鏁版嵁',
                    '鍩虹鎶€鏈寚鏍?,
                    '绀惧尯鏀寔'
                ],
                'limits': {
                    'strategies': 3,
                    'backtests_per_day': 10,
                    'data_delay_minutes': 15,
                    'advanced_indicators': False,
                    'api_access': False
                }
            },
            'basic': {
                'name': '涓撲笟鐗?,
                'price': 99,
                'period': '鏈?,
                'features': [
                    '10涓瓥鐣?,
                    '姣忔棩50娆″洖娴?,
                    '瀹炴椂鏁版嵁',
                    '鍩虹鎶€鏈寚鏍?,
                    '閭欢鏀寔',
                    '鏍囧噯鎶ュ憡'
                ],
                'limits': {
                    'strategies': 10,
                    'backtests_per_day': 50,
                    'data_delay_minutes': 0,
                    'advanced_indicators': False,
                    'api_access': False
                }
            },
            'pro': {
                'name': '楂樼骇鐗?,
                'price': 299,
                'period': '鏈?,
                'features': [
                    '100涓瓥鐣?,
                    '姣忔棩500娆″洖娴?,
                    '瀹炴椂鏁版嵁',
                    '楂樼骇鎶€鏈寚鏍?,
                    'API鎺ュ彛',
                    '浼樺厛鏀寔',
                    '楂樼骇鎶ュ憡',
                    '绛栫暐浼樺寲宸ュ叿'
                ],
                'limits': {
                    'strategies': 100,
                    'backtests_per_day': 500,
                    'data_delay_minutes': 0,
                    'advanced_indicators': True,
                    'api_access': True
                }
            },
            'enterprise': {
                'name': '浼佷笟鐗?,
                'price': 999,
                'period': '鏈?,
                'features': [
                    '鏃犻檺绛栫暐',
                    '鏃犻檺鍥炴祴',
                    '瀹炴椂鏁版嵁',
                    '鍏ㄩ儴楂樼骇鎸囨爣',
                    '瀹屾暣API鎺ュ彛',
                    '24/7浼樺厛鏀寔',
                    '瀹氬埗鎶ュ憡',
                    '鐧芥爣鏂规',
                    '澶氱敤鎴峰崗浣?,
                    '绉佹湁閮ㄧ讲閫夐」'
                ],
                'limits': {
                    'strategies': float('inf'),
                    'backtests_per_day': float('inf'),
                    'data_delay_minutes': 0,
                    'advanced_indicators': True,
                    'api_access': True
                }
            }
        }
    
    def get_plan_info(self, plan_name):
        return self.plans.get(plan_name)
    
    def get_all_plans(self):
        return self.plans
    
    def calculate_price(self, plan_name, duration_months=1, discount_code=None):
        plan = self.plans.get(plan_name)
        if not plan:
            return None
        
        base_price = plan['price'] * duration_months
        
        discount = 0
        if discount_code:
            discount = self._apply_discount(discount_code, base_price)
        
        final_price = base_price - discount
        
        return {
            'plan': plan_name,
            'duration_months': duration_months,
            'base_price': base_price,
            'discount': discount,
            'final_price': max(0, final_price),
            'price_per_month': final_price / duration_months if duration_months > 0 else 0
        }
    
    def _apply_discount(self, code, amount):
        discounts = {
            'QUANTUM20': 0.20,
            'EARLYBIRD': 0.30,
            'ANNUAL': 0.15,
            'STUDENT': 0.50
        }
        
        if code.upper() in discounts:
            return amount * discounts[code.upper()]
        
        return 0
    
    def get_popular_plan(self):
        return 'pro'
    
    def get_recommended_plan(self, user_requirements):
        if user_requirements.get('api_access'):
            return 'pro'
        elif user_requirements.get('advanced_indicators'):
            return 'pro'
        elif user_requirements.get('real_time_data'):
            return 'basic'
        else:
            return 'free'
