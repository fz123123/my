# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from business.subscription_manager import SubscriptionManager


class AnalyticsEngine:
    def __init__(self):
        self.sub_manager = SubscriptionManager()
        self.analytics_dir = Path(__file__).parent.parent / 'data' / 'analytics'
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
    
    def track_event(self, event_type, user_id, event_data):
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'data': event_data
        }
        
        self._save_event(event)
    
    def _save_event(self, event):
        filename = self.analytics_dir / f"events_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    def get_user_metrics(self):
        users = self.sub_manager.get_all_users()
        
        if not users:
            return {
                'total_users': 0,
                'active_users': 0,
                'new_users_today': 0,
                'new_users_week': 0,
                'new_users_month': 0
            }
        
        total = len(users)
        active = len([u for u in users if u['status'] == 'active'])
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        new_today = len([
            u for u in users 
            if u['created_at'] and datetime.fromisoformat(u['created_at']).date() == today
        ])
        
        new_week = len([
            u for u in users 
            if u['created_at'] and week_ago <= datetime.fromisoformat(u['created_at']).date() <= today
        ])
        
        new_month = len([
            u for u in users 
            if u['created_at'] and month_ago <= datetime.fromisoformat(u['created_at']).date() <= today
        ])
        
        return {
            'total_users': total,
            'active_users': active,
            'new_users_today': new_today,
            'new_users_week': new_week,
            'new_users_month': new_month,
            'inactive_users': total - active
        }
    
    def get_subscription_metrics(self):
        users = self.sub_manager.get_all_users()
        
        plan_distribution = {}
        for user in users:
            plan = user.get('plan', 'free')
            plan_distribution[plan] = plan_distribution.get(plan, 0) + 1
        
        total_users = len(users)
        
        plan_percentages = {}
        for plan, count in plan_distribution.items():
            plan_percentages[plan] = (count / total_users * 100) if total_users > 0 else 0
        
        return {
            'plan_distribution': plan_distribution,
            'plan_percentages': plan_percentages,
            'total_users': total_users
        }
    
    def get_revenue_metrics(self):
        users = self.sub_manager.get_all_users()
        
        pricing = {
            'free': 0,
            'basic': 99,
            'pro': 299,
            'enterprise': 999
        }
        
        mrr = 0
        paid_users = 0
        
        for user in users:
            plan = user.get('plan', 'free')
            if plan in pricing and pricing[plan] > 0:
                mrr += pricing[plan]
                paid_users += 1
        
        arpu = mrr / paid_users if paid_users > 0 else 0
        
        return {
            'monthly_recurring_revenue': mrr,
            'annual_recurring_revenue': mrr * 12,
            'paid_users': paid_users,
            'arpu': arpu,
            'arpu_annual': arpu * 12
        }
    
    def get_usage_metrics(self):
        users = self.sub_manager.get_all_users()
        
        total_backtests = 0
        total_strategies = 0
        
        for user in users:
            usage = self.sub_manager.get_usage_stats(user['user_id'], days=30)
            total_backtests += usage.get('backtest', 0)
            total_strategies += usage.get('strategy_created', 0)
        
        return {
            'total_backtests_30d': total_backtests,
            'total_strategies_created': total_strategies,
            'avg_backtests_per_user': total_backtests / len(users) if users else 0
        }
    
    def get_conversion_metrics(self):
        users = self.sub_manager.get_all_users()
        
        total_users = len(users)
        paid_users = len([u for u in users if u.get('plan') != 'free'])
        
        conversion_rate = (paid_users / total_users * 100) if total_users > 0 else 0
        
        free_users = len([u for u in users if u.get('plan') == 'free'])
        
        return {
            'total_users': total_users,
            'free_users': free_users,
            'paid_users': paid_users,
            'conversion_rate': conversion_rate,
            'potential_conversion': free_users
        }
    
    def get_retention_metrics(self, cohort_period='month'):
        users = self.sub_manager.get_all_users()
        
        if not users:
            return {}
        
        retention_data = {}
        
        now = datetime.now()
        
        if cohort_period == 'month':
            for i in range(12):
                cohort_month = (now - timedelta(days=30 * i)).strftime('%Y-%m')
                
                cohort_users = [
                    u for u in users 
                    if u.get('created_at') and 
                    u['created_at'].startswith(cohort_month)
                ]
                
                if cohort_users:
                    retained = len([
                        u for u in cohort_users 
                        if u.get('status') == 'active'
                    ])
                    
                    retention_data[cohort_month] = {
                        'cohort_size': len(cohort_users),
                        'retained': retained,
                        'retention_rate': (retained / len(cohort_users) * 100)
                    }
        
        return retention_data
    
    def generate_dashboard_data(self):
        return {
            'user_metrics': self.get_user_metrics(),
            'subscription_metrics': self.get_subscription_metrics(),
            'revenue_metrics': self.get_revenue_metrics(),
            'usage_metrics': self.get_usage_metrics(),
            'conversion_metrics': self.get_conversion_metrics(),
            'retention_metrics': self.get_retention_metrics(),
            'generated_at': datetime.now().isoformat()
        }
    
    def export_report(self, format='json'):
        data = self.generate_dashboard_data()
        
        if format == 'json':
            filename = self.analytics_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return str(filename)
        
        elif format == 'csv':
            filename = self.analytics_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            summary_data = []
            
            summary_data.append({
                'Metric': 'Total Users',
                'Value': data['user_metrics']['total_users']
            })
            summary_data.append({
                'Metric': 'Active Users',
                'Value': data['user_metrics']['active_users']
            })
            summary_data.append({
                'Metric': 'Monthly Recurring Revenue',
                'Value': data['revenue_metrics']['monthly_recurring_revenue']
            })
            summary_data.append({
                'Metric': 'Conversion Rate',
                'Value': data['conversion_metrics']['conversion_rate']
            })
            
            df = pd.DataFrame(summary_data)
            df.to_csv(filename, index=False)
            return str(filename)
        
        return None


class CommunityManager:
    def __init__(self):
        self.community_dir = Path(__file__).parent.parent / 'data' / 'community'
        self.community_dir.mkdir(parents=True, exist_ok=True)
    
    def create_post(self, user_id, title, content, tags=None):
        post = {
            'post_id': f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'user_id': user_id,
            'title': title,
            'content': content,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'views': 0,
            'likes': 0,
            'comments': []
        }
        
        filename = self.community_dir / f"{post['post_id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
        
        return post
    
    def get_posts(self, limit=20):
        posts = []
        
        for post_file in self.community_dir.glob('post_*.json'):
            with open(post_file, 'r', encoding='utf-8') as f:
                try:
                    post = json.load(f)
                    posts.append(post)
                except:
                    continue
        
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return posts[:limit]
    
    def add_comment(self, post_id, user_id, comment):
        post_file = self.community_dir / f"{post_id}.json"
        
        if not post_file.exists():
            return False
        
        with open(post_file, 'r', encoding='utf-8') as f:
            post = json.load(f)
        
        new_comment = {
            'comment_id': f"comment_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'user_id': user_id,
            'content': comment,
            'created_at': datetime.now().isoformat()
        }
        
        post['comments'].append(new_comment)
        
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
        
        return True
    
    def like_post(self, post_id):
        post_file = self.community_dir / f"{post_id}.json"
        
        if not post_file.exists():
            return False
        
        with open(post_file, 'r', encoding='utf-8') as f:
            post = json.load(f)
        
        post['likes'] = post.get('likes', 0) + 1
        
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
        
        return True


class NotificationManager:
    def __init__(self):
        self.notification_dir = Path(__file__).parent.parent / 'data' / 'notifications'
        self.notification_dir.mkdir(parents=True, exist_ok=True)
    
    def send_notification(self, user_id, title, content, notification_type='info'):
        notification = {
            'notification_id': f"notif_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'user_id': user_id,
            'title': title,
            'content': content,
            'type': notification_type,
            'read': False,
            'created_at': datetime.now().isoformat()
        }
        
        filename = self.notification_dir / f"{user_id}_{notification['notification_id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(notification, f, ensure_ascii=False, indent=2)
        
        return notification
    
    def get_notifications(self, user_id, unread_only=False):
        notifications = []
        
        pattern = f"{user_id}_notif_*.json" if unread_only else "*_notif_*.json"
        
        for notif_file in self.notification_dir.glob(pattern):
            if unread_only and f"{user_id}_" not in notif_file.name:
                continue
            
            with open(notif_file, 'r', encoding='utf-8') as f:
                try:
                    notification = json.load(f)
                    if notification['user_id'] == user_id:
                        notifications.append(notification)
                except:
                    continue
        
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return notifications
    
    def mark_as_read(self, notification_id, user_id):
        notif_file = None
        
        for f in self.notification_dir.glob(f"{user_id}_*.json"):
            with open(f, 'r', encoding='utf-8') as file:
                try:
                    notif = json.load(file)
                    if notif['notification_id'] == notification_id:
                        notif_file = f
                        notification = notif
                        break
                except:
                    continue
        
        if notif_file and notification:
            notification['read'] = True
            
            with open(notif_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False, indent=2)
            
            return True
        
        return False
    
    def get_unread_count(self, user_id):
        notifications = self.get_notifications(user_id, unread_only=True)
        return len([n for n in notifications if not n['read']])
