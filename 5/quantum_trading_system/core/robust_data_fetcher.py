#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据获取模块
包含：智能降级机制 + 自动重试逻辑 + 健康监控
确保网络波动时自动切换数据源
"""

import requests
import time
import random
import threading
from datetime import datetime, timedelta
from collections import deque
import traceback


class RetryConfig:
    """重试配置"""
    MAX_RETRIES = 3
    BASE_DELAY = 1.0
    MAX_DELAY = 10.0
    BACKOFF_FACTOR = 2.0
    JITTER = True
    JITTER_RANGE = (0.5, 1.5)


class LogLevel:
    """日志级别"""
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class Logger:
    """日志记录器"""

    def __init__(self, level=LogLevel.INFO):
        self.level = level

    def _log(self, level, tag, message):
        """内部日志方法"""
        if level < self.level:
            return

        level_str = {
            LogLevel.DEBUG: "[DEBUG]",
            LogLevel.INFO: "[INFO]",
            LogLevel.WARN: "[WARN]",
            LogLevel.ERROR: "[ERROR]"
        }.get(level, "[INFO]")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"{timestamp} {level_str} [{tag}] {message}")

    def debug(self, tag, message):
        self._log(LogLevel.DEBUG, tag, message)

    def info(self, tag, message):
        self._log(LogLevel.INFO, tag, message)

    def warn(self, tag, message):
        self._log(LogLevel.WARN, tag, message)

    def error(self, tag, message):
        self._log(LogLevel.ERROR, tag, message)


# 创建全局日志实例
logger = Logger(LogLevel.DEBUG)


class ErrorClassifier:
    """错误分类器"""

    @staticmethod
    def classify(error):
        """分类错误类型"""
        error_str = str(error).lower()
        original_error = str(error)[:100]

        if 'timeout' in error_str:
            logger.debug("ErrorClassifier", f"分类为timeout: {original_error}")
            return 'timeout'
        elif 'connection' in error_str or 'remote' in error_str:
            logger.debug("ErrorClassifier", f"分类为connection: {original_error}")
            return 'connection'
        elif 'reset' in error_str or 'refused' in error_str:
            logger.debug("ErrorClassifier", f"分类为connection_reset: {original_error}")
            return 'connection_reset'
        elif '429' in error_str or 'rate' in error_str:
            logger.debug("ErrorClassifier", f"分类为rate_limit: {original_error}")
            return 'rate_limit'
        elif 'decode' in error_str or 'parse' in error_str:
            logger.debug("ErrorClassifier", f"分类为parse_error: {original_error}")
            return 'parse_error'
        elif 'ssl' in error_str or 'certificate' in error_str:
            logger.debug("ErrorClassifier", f"分类为ssl_error: {original_error}")
            return 'ssl_error'
        elif 'dns' in error_str:
            logger.debug("ErrorClassifier", f"分类为dns_error: {original_error}")
            return 'dns_error'
        elif 'proxy' in error_str:
            logger.debug("ErrorClassifier", f"分类为proxy_error: {original_error}")
            return 'proxy_error'
        else:
            logger.debug("ErrorClassifier", f"分类为unknown: {original_error}")
            return 'unknown'

    @staticmethod
    def should_retry(error_type):
        """判断是否应该重试"""
        retryable_errors = {
            'timeout', 'connection', 'connection_reset',
            'rate_limit', 'parse_error', 'ssl_error', 'unknown'
        }
        non_retryable = {'dns_error', 'proxy_error'}
        should = error_type in retryable_errors
        logger.debug("ErrorClassifier", f"错误类型 {error_type} 是否可重试: {should}")
        return should


class BackoffCalculator:
    """退避计算器"""

    @staticmethod
    def calculate(attempt, error_type, base_delay=None, factor=None, max_delay=None):
        """计算延迟时间"""
        if base_delay is None:
            base_delay = RetryConfig.BASE_DELAY
        if factor is None:
            factor = RetryConfig.BACKOFF_FACTOR
        if max_delay is None:
            max_delay = RetryConfig.MAX_DELAY

        # 基础延迟
        delay = base_delay * (factor ** attempt)

        # 错误类型调整
        multiplier = 1.0
        if error_type == 'timeout':
            multiplier = 1.5
        elif error_type == 'connection':
            multiplier = 1.2
        elif error_type == 'rate_limit':
            multiplier = 2.0
        elif error_type == 'parse_error':
            multiplier = 0.5

        delay *= multiplier

        # 限制最大延迟
        delay = min(delay, max_delay)

        # 添加抖动
        jitter = 1.0
        if RetryConfig.JITTER:
            jitter = random.uniform(*RetryConfig.JITTER_RANGE)
            delay *= jitter

        logger.debug("BackoffCalculator",
                     f"计算延迟: attempt={attempt}, error_type={error_type}, "
                     f"基础延迟={base_delay}, 系数={factor}, 倍数={multiplier}, "
                     f"抖动={jitter:.2f}, 最终延迟={delay:.2f}秒")

        return delay


class HealthMonitor:
    """数据源健康监控"""

    def __init__(self):
        self.stats = {}
        self.lock = threading.Lock()
        self.sources = ['SinaAPI', 'TencentAPI', 'EastmoneyAPI', 'AKShare']
        self.init_stats()

        # 健康度配置
        self.min_samples = 3
        self.healthy_threshold = 50
        self.recovery_threshold = 70

        logger.info("HealthMonitor", "健康监控器初始化完成")

    def init_stats(self):
        """初始化统计"""
        for source in self.sources:
            self.stats[source] = {
                'success': 0,
                'fail': 0,
                'total': 0,
                'total_response_time': 0,
                'consecutive_fails': 0,
                'last_success': None,
                'last_fail': None,
                'recent_results': deque(maxlen=10),
                'health_score': 50,
                'previous_health_score': 50
            }
            logger.debug("HealthMonitor", f"初始化数据源统计: {source}")

    def record_result(self, source, success, response_time=0, error_type=None):
        """记录结果"""
        with self.lock:
            stats = self.stats[source]
            stats['total'] += 1
            prev_consecutive_fails = stats['consecutive_fails']
            prev_health_score = stats['health_score']

            if success:
                stats['success'] += 1
                stats['consecutive_fails'] = 0
                stats['last_success'] = datetime.now()
                stats['total_response_time'] += response_time

                logger.info("HealthMonitor",
                            f"[{source}] 请求成功 | 响应时间={response_time:.3f}秒 | "
                            f"累计成功={stats['success']} | 累计失败={stats['fail']}")
            else:
                stats['fail'] += 1
                stats['consecutive_fails'] += 1
                stats['last_fail'] = datetime.now()

                logger.warn("HealthMonitor",
                            f"[{source}] 请求失败 | 错误类型={error_type} | "
                            f"连续失败={stats['consecutive_fails']} | "
                            f"累计失败={stats['fail']}")

            # 记录最近结果
            stats['recent_results'].append({
                'success': success,
                'time': datetime.now(),
                'error_type': error_type
            })

            # 更新健康分数
            self.update_health_score(source)

            # 检查健康状态变化
            if prev_consecutive_fails != stats['consecutive_fails']:
                if stats['consecutive_fails'] >= 3:
                    logger.warn("HealthMonitor",
                                f"[{source}] 连续失败达到3次，状态变为不稳定")
                elif prev_consecutive_fails >= 3 and stats['consecutive_fails'] == 0:
                    logger.info("HealthMonitor",
                                f"[{source}] 恢复成功，连续失败重置")

            # 检查健康分数变化
            if abs(prev_health_score - stats['health_score']) >= 10:
                logger.info("HealthMonitor",
                            f"[{source}] 健康分数变化显著: {prev_health_score:.1f} -> {stats['health_score']:.1f}")

    def update_health_score(self, source):
        """更新健康分数"""
        stats = self.stats[source]
        stats['previous_health_score'] = stats['health_score']
        total = stats['total']

        if total < self.min_samples:
            stats['health_score'] = 50
            logger.debug("HealthMonitor",
                        f"[{source}] 样本不足({total}/{self.min_samples})，健康分保持50")
            return

        # 计算成功率
        success_rate = stats['success'] / total * 100

        # 连续失败惩罚
        consecutive_penalty = min(stats['consecutive_fails'] * 5, 30)

        # 时间衰减（最近失败影响更大）
        time_penalty = 0
        if stats['last_fail']:
            seconds_since_fail = (datetime.now() - stats['last_fail']).total_seconds()
            if seconds_since_fail < 300:
                time_penalty = 15 * (1 - seconds_since_fail / 300)

        # 计算最终分数
        score = max(0, min(100, success_rate - consecutive_penalty - time_penalty))
        stats['health_score'] = score

        logger.debug("HealthMonitor",
                    f"[{source}] 健康分计算: 成功率={success_rate:.1f}% | "
                    f"连续失败惩罚={consecutive_penalty:.1f} | "
                    f"时间衰减惩罚={time_penalty:.1f} | "
                    f"最终分数={score:.1f}")

    def is_healthy(self, source):
        """判断是否健康"""
        stats = self.stats[source]

        # 样本不足，认为健康
        if stats['total'] < self.min_samples:
            result = True
            logger.debug("HealthMonitor",
                        f"[{source}] 样本不足({stats['total']}/{self.min_samples})，判定为健康")
            return result

        # 健康分数检查
        if stats['health_score'] < self.healthy_threshold:
            result = False
            logger.debug("HealthMonitor",
                        f"[{source}] 健康分不足({stats['health_score']}<{self.healthy_threshold})，判定为不健康")
            return result

        # 连续失败检查
        if stats['consecutive_fails'] >= 3:
            result = False
            logger.debug("HealthMonitor",
                        f"[{source}] 连续失败>=3次({stats['consecutive_fails']})，判定为不健康")
            return result

        result = True
        logger.debug("HealthMonitor",
                    f"[{source}] 判定为健康: 健康分={stats['health_score']:.1f}, 连续失败={stats['consecutive_fails']}")
        return result

    def should_skip(self, source):
        """判断是否应跳过"""
        stats = self.stats[source]

        # 连续失败超过5次，跳过
        if stats['consecutive_fails'] >= 5:
            logger.warn("HealthMonitor",
                        f"[{source}] 连续失败>=5次，跳过该数据源")
            return True

        # 大量失败后需要冷却
        if stats['health_score'] < 20:
            logger.warn("HealthMonitor",
                        f"[{source}] 健康分<20({stats['health_score']})，跳过该数据源")
            return True

        logger.debug("HealthMonitor", f"[{source}] 不跳过")
        return False

    def get_best_source(self):
        """获取最健康的数据源"""
        healthy_sources = [s for s in self.sources if self.is_healthy(s)]

        if not healthy_sources:
            # 如果没有健康源，返回样本最少的
            min_source = min(self.sources, key=lambda s: self.stats[s]['total'])
            logger.warn("HealthMonitor",
                        f"没有健康数据源，返回样本最少的: {min_source}")
            return min_source

        # 按健康分数排序
        sorted_sources = sorted(
            healthy_sources,
            key=lambda s: (self.stats[s]['health_score'], -self.stats[s]['consecutive_fails']),
            reverse=True
        )

        best = sorted_sources[0]
        logger.info("HealthMonitor",
                    f"最佳数据源: {best} (健康分={self.stats[best]['health_score']:.1f})")
        return best

    def get_working_sources(self):
        """获取所有可用数据源（按健康度排序）"""
        working = [s for s in self.sources if not self.should_skip(s)]
        sorted_working = sorted(working, key=lambda s: self.stats[s]['health_score'], reverse=True)

        logger.debug("HealthMonitor",
                    f"可用数据源: {sorted_working} (共{len(sorted_working)}个)")
        return sorted_working

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("数据源健康监控")
        print("=" * 80)
        print(f"{'数据源':<15} {'总数':<8} {'成功':<8} {'失败':<8} {'连续失败':<10} {'健康分':<10} {'状态':<10}")
        print("-" * 80)

        for source in self.sources:
            stats = self.stats[source]
            status = "正常" if self.is_healthy(source) else "不稳定"
            if stats['consecutive_fails'] >= 5:
                status = "离线"

            print(f"{source:<15} {stats['total']:<8} {stats['success']:<8} "
                  f"{stats['fail']:<8} {stats['consecutive_fails']:<10} "
                  f"{stats['health_score']:<10.1f} {status:<10}")

        print("-" * 80)
        print(f"推荐使用: {self.get_best_source()}")
        print("=" * 80)


class DataSourceProvider:
    """数据源提供者基类"""

    def __init__(self, name):
        self.name = name
        self.session = None
        self.init_session()

    def init_session(self):
        """初始化会话"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def get_price(self, code):
        """获取价格 - 子类实现"""
        raise NotImplementedError


class SinaProvider(DataSourceProvider):
    """新浪数据源"""

    def __init__(self):
        super().__init__('SinaAPI')

    def get_price(self, code):
        try:
            symbol_code = code.replace('.SZ', '').replace('.SH', '')
            market = 'sz' if code.endswith('.SZ') else 'sh'
            url = f'http://hq.sinajs.cn/list={market}{symbol_code}'

            headers = {
                'Referer': 'https://finance.sina.com.cn/',
            }

            logger.debug("SinaProvider", f"请求: {url}")
            r = self.session.get(url, headers=headers, timeout=5)

            if r.status_code == 200:
                text = r.text
                parts = text.split(',')
                if len(parts) > 3:
                    price = float(parts[3])
                    if price > 0:
                        logger.debug("SinaProvider",
                                    f"解析成功: {code} -> {price:.2f}元")
                        return {
                            'price': price,
                            'prev_close': float(parts[2]),
                            'open': float(parts[1]),
                            'high': float(parts[4]),
                            'low': float(parts[5]),
                            'volume': int(parts[8]) if parts[8] else 0,
                            'source': self.name
                        }
                else:
                    logger.debug("SinaProvider", f"数据格式不完整: {text[:50]}...")
            else:
                logger.debug("SinaProvider", f"HTTP状态码: {r.status_code}")

        except Exception as e:
            logger.error("SinaProvider", f"请求失败: {e}")
        return None


class TencentProvider(DataSourceProvider):
    """腾讯数据源 - 优化版"""

    def __init__(self):
        super().__init__('TencentAPI')

    def get_price(self, code):
        try:
            symbol_code = code.replace('.SZ', '').replace('.SH', '')
            market = '1' if code.endswith('.SZ') else '0'
            url = f'https://qt.gtimg.cn/q={market}{symbol_code}'

            headers = {
                'Referer': 'https://stockapp.finance.qq.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }

            logger.debug("TencentProvider", f"请求: {url}")
            r = self.session.get(url, headers=headers, timeout=10, verify=False)

            if r.status_code == 200:
                text = r.text.strip()
                if text.startswith('pv_') and '~' in text:
                    parts = text.split('~')
                    if len(parts) > 33:
                        price = float(parts[3])
                        if price > 0:
                            logger.debug("TencentProvider",
                                        f"解析成功: {code} -> {price:.2f}元")
                            return {
                                'price': price,
                                'prev_close': float(parts[4]),
                                'open': float(parts[5]),
                                'high': float(parts[33]),
                                'low': float(parts[34]),
                                'volume': int(parts[36]) if parts[36] else 0,
                                'time': parts[30] if len(parts) > 30 else '',
                                'source': self.name
                            }
                    else:
                        logger.debug("TencentProvider", f"数据字段不足: {len(parts)}个")
                else:
                    logger.debug("TencentProvider", f"数据格式错误: {text[:50]}...")
            else:
                logger.debug("TencentProvider", f"HTTP状态码: {r.status_code}")

        except Exception as e:
            logger.error("TencentProvider", f"请求失败: {e}")
        return None


class EastmoneyProvider(DataSourceProvider):
    """东方财富数据源 - 双协议版"""

    def __init__(self):
        super().__init__('EastmoneyAPI')

    def get_price(self, code):
        symbol_code = code.replace('.SZ', '').replace('.SH', '')
        market = '0' if code.endswith('.SZ') else '1'

        urls = [
            f'https://push2.eastmoney.com/api/qt/stock/get?secid={market}.{symbol_code}&fields=f57,f58,f43,f44,f45,f46,f47,f48',
            f'http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{symbol_code}&fields=f57,f58,f43,f44,f45,f46,f47,f48'
        ]

        headers = {
            'Referer': 'https://quote.eastmoney.com/',
        }

        for i, url in enumerate(urls):
            protocol = 'HTTPS' if i == 0 else 'HTTP'
            try:
                logger.debug("EastmoneyProvider", f"尝试{protocol}: {url}")
                r = self.session.get(url, headers=headers, timeout=8)

                if r.status_code == 200:
                    data = r.json()
                    if data and data.get('data'):
                        d = data['data']
                        price = d.get('f43', 0)
                        if price and price > 0:
                            logger.debug("EastmoneyProvider",
                                        f"{protocol}解析成功: {code} -> {price/100:.2f}元")
                            return {
                                'price': price / 100,
                                'open': d.get('f46', 0) / 100,
                                'high': d.get('f44', 0) / 100,
                                'low': d.get('f45', 0) / 100,
                                'time': d.get('f57', ''),
                                'source': self.name
                            }
                    else:
                        logger.debug("EastmoneyProvider", f"{protocol}返回数据为空")
                else:
                    logger.debug("EastmoneyProvider", f"{protocol} HTTP状态码: {r.status_code}")

            except Exception as e:
                logger.debug("EastmoneyProvider", f"{protocol}失败: {e}")
                continue

        logger.debug("EastmoneyProvider", "所有协议均失败")
        return None


class AKShareProvider(DataSourceProvider):
    """AKShare数据源 - 增强版"""

    def __init__(self):
        super().__init__('AKShare')

    def get_price(self, code):
        try:
            import akshare as ak
            symbol_code = code.replace('.SZ', '').replace('.SH', '')

            logger.debug("AKShareProvider", f"获取A股实时数据")
            df = ak.stock_zh_a_spot()

            if df is not None and not df.empty:
                mask = df['代码'] == symbol_code
                if mask.any():
                    row = df[mask].iloc[0]
                    price = row.get('最新价')

                    if price and isinstance(price, (int, float)) and price > 0:
                        logger.debug("AKShareProvider",
                                    f"解析成功: {code} -> {price:.2f}元")
                        return {
                            'price': float(price),
                            'name': str(row.get('名称', '')),
                            'source': self.name
                        }
                else:
                    logger.debug("AKShareProvider", f"未找到股票: {symbol_code}")
            else:
                logger.debug("AKShareProvider", "返回数据为空")

        except Exception as e:
            logger.error("AKShareProvider", f"请求失败: {e}")
        return None


class SmartDataFetcher:
    """智能数据获取器 - 核心类"""

    def __init__(self):
        self.health_monitor = HealthMonitor()
        self.cache = {}
        self.cache_duration = 5
        self.cache_lock = threading.Lock()

        self.providers = {
            'SinaAPI': SinaProvider(),
            'TencentAPI': TencentProvider(),
            'EastmoneyAPI': EastmoneyProvider(),
            'AKShare': AKShareProvider()
        }

        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'source_switches': 0,
            'retry_attempts': 0
        }

        logger.info("SmartDataFetcher", "智能数据获取器初始化完成")

    def _is_cache_valid(self, code):
        """检查缓存是否有效"""
        with self.cache_lock:
            if code not in self.cache:
                logger.debug("SmartDataFetcher", f"缓存不存在: {code}")
                return False

            cache_entry = self.cache[code]
            elapsed = (datetime.now() - cache_entry['time']).total_seconds()
            valid = elapsed < self.cache_duration

            if valid:
                logger.debug("SmartDataFetcher",
                            f"缓存有效: {code} (已缓存{elapsed:.1f}秒)")
            else:
                logger.debug("SmartDataFetcher",
                            f"缓存过期: {code} (已缓存{elapsed:.1f}秒)")

            return valid

    def _get_from_cache(self, code):
        """从缓存获取"""
        with self.cache_lock:
            if code in self.cache:
                self.stats['cache_hits'] += 1
                data = self.cache[code]['data']
                logger.info("SmartDataFetcher",
                            f"命中缓存: {code} -> {data['price']:.2f}元")
                return data
        return None

    def _save_to_cache(self, code, data):
        """保存到缓存"""
        with self.cache_lock:
            self.cache[code] = {
                'data': data,
                'time': datetime.now()
            }
            logger.debug("SmartDataFetcher", f"保存缓存: {code}")

    def get_price_with_smart_retry(self, code, force_refresh=False):
        """智能重试获取价格"""
        request_id = f"{code}-{int(time.time())}"
        self.stats['total_requests'] += 1

        logger.info("SmartDataFetcher",
                    f"========== 请求开始 [{request_id}] ==========")
        logger.info("SmartDataFetcher", f"获取股票价格: {code}")
        logger.info("SmartDataFetcher", f"强制刷新: {force_refresh}")

        # 检查缓存
        if not force_refresh and self._is_cache_valid(code):
            cached = self._get_from_cache(code)
            logger.info("SmartDataFetcher",
                        f"========== 请求结束 [{request_id}] - 缓存命中 ==========")
            return cached

        # 获取可用数据源（按健康度排序）
        working_sources = self.health_monitor.get_working_sources()
        logger.info("SmartDataFetcher",
                    f"可用数据源: {working_sources} (共{len(working_sources)}个)")

        if not working_sources:
            logger.warn("SmartDataFetcher", "所有数据源都不可用")
            cached_data = self._get_from_cache(code)
            if cached_data:
                logger.info("SmartDataFetcher", "使用过期缓存作为后备")
            logger.info("SmartDataFetcher",
                        f"========== 请求结束 [{request_id}] - 所有源失败 ==========")
            return cached_data

        last_error = None
        best_source = working_sources[0]
        total_retries = 0

        # 按优先级尝试所有可用数据源
        for source_idx, source_name in enumerate(working_sources):
            provider = self.providers.get(source_name)
            if not provider:
                logger.warn("SmartDataFetcher", f"数据源不存在: {source_name}")
                continue

            logger.info("SmartDataFetcher",
                        f"尝试数据源 [{source_idx+1}/{len(working_sources)}]: {source_name}")

            # 指数退避重试
            for attempt in range(RetryConfig.MAX_RETRIES):
                self.stats['retry_attempts'] += 1
                attempt_info = f"尝试 [{attempt+1}/{RetryConfig.MAX_RETRIES}]"

                try:
                    logger.debug("SmartDataFetcher",
                                f"{attempt_info} 发起请求: {source_name} -> {code}")

                    start_time = time.time()
                    data = provider.get_price(code)
                    response_time = time.time() - start_time

                    if data and 'price' in data and data['price'] > 0:
                        # 成功！
                        logger.info("SmartDataFetcher",
                                    f"{attempt_info} ✅ 成功! 价格={data['price']:.2f}元, "
                                    f"来源={data['source']}, 耗时={response_time:.3f}秒")

                        self.health_monitor.record_result(source_name, True, response_time)
                        self._save_to_cache(code, data)

                        if source_name != best_source:
                            self.stats['source_switches'] += 1
                            logger.info("SmartDataFetcher",
                                        f"触发数据源切换: {best_source} -> {source_name}")

                        logger.info("SmartDataFetcher",
                                    f"========== 请求成功 [{request_id}] ==========")
                        return data
                    else:
                        last_error = Exception("No data returned")
                        error_type = ErrorClassifier.classify(last_error)

                        if attempt < RetryConfig.MAX_RETRIES - 1:
                            delay = BackoffCalculator.calculate(attempt, error_type)
                            total_retries += 1

                            logger.warn("SmartDataFetcher",
                                        f"{attempt_info} ⚠️ 无数据, 错误类型={error_type}, "
                                        f"{delay:.1f}秒后重试")
                            time.sleep(delay)
                        else:
                            logger.warn("SmartDataFetcher",
                                        f"{attempt_info} ⚠️ 无数据, 已达最大重试次数")

                except Exception as e:
                    last_error = e
                    error_type = ErrorClassifier.classify(e)

                    self.health_monitor.record_result(source_name, False, error_type=error_type)

                    if not ErrorClassifier.should_retry(error_type):
                        logger.error("SmartDataFetcher",
                                    f"{attempt_info} ❌ 不可重试的错误: {error_type}")
                        break

                    if attempt < RetryConfig.MAX_RETRIES - 1:
                        delay = BackoffCalculator.calculate(attempt, error_type)
                        total_retries += 1

                        logger.warn("SmartDataFetcher",
                                    f"{attempt_info} ❌ 错误: {error_type}, "
                                    f"{delay:.1f}秒后重试")
                        time.sleep(delay)
                    else:
                        logger.error("SmartDataFetcher",
                                    f"{attempt_info} ❌ 错误: {error_type}, "
                                    f"已达最大重试次数")

            # 该数据源完全失败，尝试下一个
            if source_name != working_sources[-1]:
                logger.warn("SmartDataFetcher",
                            f"数据源 {source_name} 完全失败，切换到下一个")
                self.stats['source_switches'] += 1

        # 所有数据源都失败
        logger.error("SmartDataFetcher", f"所有数据源都失败，无法获取 {code} 的数据")
        logger.error("SmartDataFetcher", f"最后错误: {last_error}")

        # 返回过期缓存
        cached_data = self._get_from_cache(code)
        if cached_data:
            logger.info("SmartDataFetcher",
                        f"使用过期缓存作为后备: {code} -> {cached_data['price']:.2f}元")

        logger.info("SmartDataFetcher",
                    f"========== 请求结束 [{request_id}] - 失败 ==========")

        return cached_data

    def batch_get_prices(self, codes, delay=0.2):
        """批量获取价格"""
        results = {}
        logger.info("SmartDataFetcher", f"批量获取 {len(codes)} 只股票")

        for i, code in enumerate(codes):
            logger.debug("SmartDataFetcher", f"批量获取 [{i+1}/{len(codes)}]: {code}")
            results[code] = self.get_price_with_smart_retry(code)

            if i < len(codes) - 1:
                logger.debug("SmartDataFetcher", f"等待 {delay}秒后继续")
                time.sleep(delay)

        logger.info("SmartDataFetcher", f"批量获取完成，成功{sum(1 for v in results.values() if v)}个")
        return results

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("智能数据获取器统计")
        print("=" * 80)
        print(f"总请求数: {self.stats['total_requests']}")
        print(f"缓存命中: {self.stats['cache_hits']}")
        print(f"源切换次数: {self.stats['source_switches']}")
        print(f"重试尝试次数: {self.stats['retry_attempts']}")

        if self.stats['total_requests'] > 0:
            cache_rate = self.stats['cache_hits'] / self.stats['total_requests'] * 100
            print(f"缓存命中率: {cache_rate:.1f}%")

        print("=" * 80)

    def probe_all_sources(self, test_code='600519.SH'):
        """探测所有数据源"""
        logger.info("SmartDataFetcher", f"探测所有数据源，测试股票: {test_code}")
        print("\n=== 探测数据源健康状态 ===")

        for source_name, provider in self.providers.items():
            try:
                start_time = time.time()
                data = provider.get_price(test_code)
                response_time = time.time() - start_time

                if data and 'price' in data and data['price'] > 0:
                    self.health_monitor.record_result(source_name, True, response_time)
                    print(f"[{source_name}] ✓ 成功 - {data['price']:.2f}元 ({response_time:.3f}秒)")
                else:
                    self.health_monitor.record_result(source_name, False)
                    print(f"[{source_name}] ✗ 失败 - 无数据")

            except Exception as e:
                error_type = ErrorClassifier.classify(e)
                self.health_monitor.record_result(source_name, False, error_type=error_type)
                print(f"[{source_name}] ✗ 错误 - {error_type}")

        self.health_monitor.print_stats()


def main():
    """主函数 - 测试"""
    print("=" * 80)
    print("智能数据获取器测试")
    print("=" * 80)

    fetcher = SmartDataFetcher()

    fetcher.probe_all_sources()

    test_stocks = [
        '600519.SH', '000001.SZ', '300750.SZ', '002938.SZ',
        '000020.SZ', '000099.SZ', '000066.SZ', '000016.SZ',
        '000011.SZ', '000088.SZ', '000022.SZ', '000055.SZ', '000017.SZ'
    ]

    print("\n=== 批量获取测试 ===")
    print("-" * 80)

    results = fetcher.batch_get_prices(test_stocks)

    print("\n=== 获取结果 ===")
    print("-" * 80)
    print(f"{'代码':<12} {'价格':<12} {'来源':<15} {'状态'}")
    print("-" * 80)

    for code in test_stocks:
        data = results.get(code)
        if data:
            print(f"{code:<12} {data['price']:>10.2f}  {data['source']:<15} ✓")
        else:
            print(f"{code:<12} {'--':<10} {'--':<15} ✗")

    fetcher.print_stats()

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()
