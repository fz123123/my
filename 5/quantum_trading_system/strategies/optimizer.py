# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from itertools import product
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor, StrategyGrid, StrategyGridAdvanced
from backtest.engine import BacktestEngine


class StrategyOptimizer:
    def __init__(self):
        self.best_params = {}
        self.optimization_results = []
        
    def grid_search(self, strategy_class, df, param_grid, metric='sharpe_ratio'):
        print(f"\n{'='*80}")
        print(f"  参数优化: {strategy_class.__name__}")
        print(f"{'='*80}")
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        param_combinations = list(product(*param_values))
        total_combinations = len(param_combinations)
        
        print(f"参数组合总数: {total_combinations}")
        print(f"参数范围: {param_grid}")
        print()
        
        results = []
        
        for i, params in enumerate(param_combinations, 1):
            param_dict = dict(zip(param_names, params))
            
            try:
                strategy = strategy_class(**param_dict)
                signals = strategy.generate_signals(df)
                
                engine = BacktestEngine()
                result = engine.run_backtest(df, signals)
                
                if result:
                    result['params'] = param_dict
                    result['params_str'] = str(param_dict)
                    
                    if metric == 'sharpe_ratio':
                        score = result['sharpe_ratio']
                    elif metric == 'total_return_pct':
                        score = result['total_return_pct']
                    elif metric == 'win_rate_pct':
                        score = result['win_rate_pct']
                    elif metric == 'calmar_ratio':
                        if result['max_drawdown_pct'] > 0:
                            score = result['total_return_pct'] / result['max_drawdown_pct']
                        else:
                            score = 0
                    else:
                        score = result.get(metric, 0)
                    
                    result['score'] = score
                    results.append(result)
                    
                    if i % 10 == 0 or i == 1:
                        print(f"[{i}/{total_combinations}] 参数: {param_dict}, {metric}: {score:.2f}")
                        
            except Exception as e:
                print(f"参数组合 {param_dict} 测试失败: {e}")
        
        if results:
            results = sorted(results, key=lambda x: x['score'], reverse=True)
            
            print(f"\n优化完成，测试了 {len(results)} 个组合")
            print(f"\n前5个最优参数组合")
            print("-" * 80)
            
            for i, result in enumerate(results[:5], 1):
                print(f"\n#{i} {metric}: {result['score']:.4f}")
                print(f"参数: {result['params']}")
                print(f"收益: {result['total_return_pct']:+.2f}%, "
                      f"夏普: {result['sharpe_ratio']:.2f}, "
                      f"回撤: {result['max_drawdown_pct']:.2f}%, "
                      f"胜率: {result['win_rate_pct']:.2f}%")
            
            self.best_params[strategy_class.__name__] = results[0]['params']
            self.optimization_results = results
            
            return results[0]
        
        return None
    
    def optimize_ma_cross(self, df, short_range=(3, 10), long_range=(15, 60), metric='sharpe_ratio'):
        param_grid = {
            'short_period': range(short_range[0], short_range[1] + 1),
            'long_period': range(long_range[0], long_range[1] + 1)
        }
        
        return self.grid_search(StrategyMaCross, df, param_grid, metric)
    
    def optimize_rsi(self, df, oversold_range=(20, 40), overbought_range=(60, 80), metric='sharpe_ratio'):
        param_grid = {
            'oversold': range(oversold_range[0], oversold_range[1] + 1),
            'overbought': range(overbought_range[0], overbought_range[1] + 1)
        }
        
        return self.grid_search(StrategyRsi, df, param_grid, metric)
    
    def optimize_grid(self, df, levels_range=(3, 10), range_pct_range=(0.05, 0.20, 0.05), metric='sharpe_ratio'):
        levels_list = list(range(levels_range[0], levels_range[1] + 1))
        pct_list = []
        current = range_pct_range[0]
        while current <= range_pct_range[1]:
            pct_list.append(round(current, 2))
            current += range_pct_range[2]
        
        param_grid = {
            'grid_levels': levels_list,
            'grid_range_pct': pct_list
        }
        
        return self.grid_search(StrategyGrid, df, param_grid, metric)
    
    def optimize_grid_advanced(self, df, levels_range=(3, 10), range_pct_range=(0.05, 0.20, 0.05), metric='sharpe_ratio'):
        levels_list = list(range(levels_range[0], levels_range[1] + 1))
        pct_list = []
        current = range_pct_range[0]
        while current <= range_pct_range[1]:
            pct_list.append(round(current, 2))
            current += range_pct_range[2]
        
        param_grid = {
            'grid_levels': levels_list,
            'grid_range_pct': pct_list,
            'volume_filter': [True, False],
            'rsi_filter': [True, False]
        }
        
        return self.grid_search(StrategyGridAdvanced, df, param_grid, metric)
    
    def analyze_parameter_sensitivity(self, results, param_name):
        if not results:
            return None
        
        param_values = [r['params'][param_name] for r in results]
        scores = [r['score'] for r in results]
        
        df = pd.DataFrame({
            param_name: param_values,
            'score': scores
        })
        
        grouped = df.groupby(param_name)['score'].agg(['mean', 'std', 'count'])
        
        return grouped
    
    def get_robust_parameters(self, results, top_n=10):
        if len(results) < top_n:
            return results
        
        top_results = results[:top_n]
        
        param_importance = {}
        for result in top_results:
            for param_name, param_value in result['params'].items():
                if param_name not in param_importance:
                    param_importance[param_name] = {}
                param_importance[param_name][param_value] = param_importance[param_name].get(param_value, 0) + 1
        
        robust_params = {}
        for param_name, value_counts in param_importance.items():
            most_common_value = max(value_counts.items(), key=lambda x: x[1])
            robust_params[param_name] = most_common_value[0]
        
        return robust_params


class StrategyPortfolio:
    def __init__(self):
        self.strategies = []
        self.strategy_weights = {}
        
    def add_strategy(self, strategy, weight=1.0, name=None):
        if name is None:
            name = strategy.__class__.__name__
        
        self.strategies.append({
            'name': name,
            'strategy': strategy,
            'weight': weight
        })
        
        self.strategy_weights[name] = weight
        
    def generate_combined_signals(self, df):
        all_signals = []
        
        for strategy_info in self.strategies:
            strategy = strategy_info['strategy']
            weight = strategy_info['weight']
            name = strategy_info['name']
            
            try:
                signals = strategy.generate_signals(df)
                weighted_signals = signals * weight
                all_signals.append(weighted_signals)
            except Exception as e:
                print(f"策略 {name} 信号生成失败: {e}")
        
        if not all_signals:
            return pd.Series(0, index=df.index)
        
        combined = sum(all_signals) / sum(self.strategy_weights.values())
        
        final_signals = pd.Series(0, index=df.index)
        final_signals[combined > 0.5] = 1
        final_signals[combined < -0.5] = -1
        
        return final_signals
    
    def rebalance(self, new_weights):
        total_weight = sum(new_weights.values())
        
        for strategy_info in self.strategies:
            name = strategy_info['name']
            if name in new_weights:
                strategy_info['weight'] = new_weights[name] / total_weight
                self.strategy_weights[name] = new_weights[name] / total_weight
    
    def get_strategy_performance(self, df):
        performances = []
        
        for strategy_info in self.strategies:
            strategy = strategy_info['strategy']
            name = strategy_info['name']
            weight = strategy_info['weight']
            
            try:
                signals = strategy.generate_signals(df)
                engine = BacktestEngine()
                result = engine.run_backtest(df, signals)
                
                if result:
                    performances.append({
                        'name': name,
                        'weight': weight,
                        'return_pct': result['total_return_pct'],
                        'sharpe': result['sharpe_ratio'],
                        'max_drawdown': result['max_drawdown_pct'],
                        'win_rate': result['win_rate_pct'],
                        'trades': result['total_trades']
                    })
            except Exception as e:
                print(f"策略 {name} 回测失败: {e}")
        
        if performances:
            engine = BacktestEngine()
            combined_signals = self.generate_combined_signals(df)
            combined_result = engine.run_backtest(df, combined_signals)
            
            if combined_result:
                performances.append({
                    'name': '组合策略',
                    'weight': 1.0,
                    'return_pct': combined_result['total_return_pct'],
                    'sharpe': combined_result['sharpe_ratio'],
                    'max_drawdown': combined_result['max_drawdown_pct'],
                    'win_rate': combined_result['win_rate_pct'],
                    'trades': combined_result['total_trades']
                })
        
        return pd.DataFrame(performances)
    
    def optimize_weights(self, df, metric='sharpe_ratio'):
        print(f"\n{'='*80}")
        print(f"  策略组合权重优化")
        print(f"{'='*80}")
        
        performances = self.get_strategy_performance(df)
        
        if performances.empty:
            print("无法获取策略表现")
            return None
        
        print("\n各策略表现")
        print(performances.to_string(index=False))
        
        if metric == 'sharpe':
            performances = performances.sort_values('sharpe', ascending=False)
        elif metric == 'return':
            performances = performances.sort_values('return_pct', ascending=False)
        elif metric == 'risk':
            performances = performances.sort_values('max_drawdown')
        
        print(f"\n最优权重分配(基于 {metric})")
        print(performances[['name', 'weight', metric if metric != 'risk' else 'max_drawdown']].to_string(index=False))
        
        return performances
    
    def remove_strategy(self, name):
        self.strategies = [s for s in self.strategies if s['name'] != name]
        if name in self.strategy_weights:
            del self.strategy_weights[name]
    
    def clear_all(self):
        self.strategies = []
        self.strategy_weights = {}
    
    def get_portfolio_info(self):
        return {
            'strategy_count': len(self.strategies),
            'strategies': [s['name'] for s in self.strategies],
            'weights': self.strategy_weights,
            'total_weight': sum(self.strategy_weights.values())
        }
