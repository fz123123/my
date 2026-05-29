# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine import BacktestEngine


class EnhancedBacktestEngine(BacktestEngine):
    def __init__(self, initial_capital=None):
        super().__init__(initial_capital)
        
    def run_monte_carlo(self, df, signals, n_simulations=1000, initial_capital=None):
        print(f"\n{'='*80}")
        print(f"  蒙特卡洛模拟")
        print(f"{'='*80}")
        print(f"模拟次数: {n_simulations}")
        
        if initial_capital is None:
            initial_capital = self.initial_capital
        
        df = df.copy()
        df['signal'] = signals
        df = df.dropna(subset=['signal'])
        
        if len(df) == 0:
            return None
        
        daily_returns = df['close'].pct_change().dropna()
        mean_return = daily_returns.mean()
        std_return = daily_returns.std()
        
        simulation_results = []
        
        for i in range(n_simulations):
            returns = np.random.normal(mean_return, std_return, len(daily_returns))
            final_value = initial_capital * np.prod(1 + returns)
            
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (running_max - cumulative_returns) / running_max
            max_drawdown = np.max(drawdowns)
            
            simulation_results.append({
                'final_value': final_value,
                'total_return': (final_value - initial_capital) / initial_capital,
                'max_drawdown': max_drawdown
            })
        
        results_df = pd.DataFrame(simulation_results)
        
        percentiles = [5, 25, 50, 75, 95]
        stats = {
            'mean_return': results_df['total_return'].mean() * 100,
            'median_return': results_df['total_return'].median() * 100,
            'std_return': results_df['total_return'].std() * 100,
            'mean_drawdown': results_df['max_drawdown'].mean() * 100,
            'median_drawdown': results_df['max_drawdown'].median() * 100,
            'VaR_95': np.percentile(results_df['total_return'], 5) * 100,
            'VaR_99': np.percentile(results_df['total_return'], 1) * 100,
        }
        
        for p in percentiles:
            stats[f'final_value_p{p}'] = np.percentile(results_df['final_value'], p)
        
        stats['probability_positive'] = (results_df['total_return'] > 0).mean() * 100
        stats['probability_loss_10pct'] = (results_df['total_return'] < -0.1).mean() * 100
        
        print("\n蒙特卡洛统计结果:")
        print("-" * 80)
        print(f"平均收益率: {stats['mean_return']:+.2f}%")
        print(f"中位数收益率: {stats['median_return']:+.2f}%")
        print(f"收益率标准差: {stats['std_return']:.2f}%")
        print(f"平均最大回撤: {stats['mean_drawdown']:.2f}%")
        print(f"中位数最大回撤: {stats['median_drawdown']:.2f}%")
        print(f"95% VaR: {stats['VaR_95']:.2f}%")
        print(f"99% VaR: {stats['VaR_99']:.2f}%")
        print(f"盈利概率: {stats['probability_positive']:.1f}%")
        print(f"亏损10%概率: {stats['probability_loss_10pct']:.1f}%")
        
        print("\n最终价值分布:")
        for p in percentiles:
            print(f"  P{p}: {stats[f'final_value_p{p}']:,.2f}")
        
        return {
            'stats': stats,
            'simulation_results': results_df,
            'n_simulations': n_simulations
        }
    
    def run_sensitivity_analysis(self, df, base_params, param_ranges, metric='total_return_pct'):
        print(f"\n{'='*80}")
        print(f"  敏感性分析")
        print(f"{'='*80}")
        print(f"基准参数: {base_params}")
        print(f"参数范围: {param_ranges}")
        
        results = []
        
        for param_name, values in param_ranges.items():
            param_results = []
            
            for value in values:
                test_params = base_params.copy()
                test_params[param_name] = value
                
                try:
                    result = self._backtest_with_params(df, test_params)
                    if result:
                        param_results.append({
                            'param_value': value,
                            'metric_value': result.get(metric, 0)
                        })
                except Exception as e:
                    print(f"参数 {param_name}={value} 测试失败: {e}")
            
            if param_results:
                results.append({
                    'param_name': param_name,
                    'values': param_results
                })
        
        print("\n敏感性分析结果:")
        for result in results:
            print(f"\n参数: {result['param_name']}")
            print("-" * 60)
            
            best = max(result['values'], key=lambda x: x['metric_value'])
            worst = min(result['values'], key=lambda x: x['metric_value'])
            
            print(f"最优值: {best['param_value']} ({best['metric_value']:.2f})")
            print(f"最差值: {worst['param_value']} ({worst['metric_value']:.2f})")
            
            sensitivity = abs(best['metric_value'] - worst['metric_value'])
            print(f"敏感度: {sensitivity:.2f}")
        
        return results
    
    def _backtest_with_params(self, df, params):
        return super().run_backtest(df, pd.Series(0, index=df.index))
    
    def run_walk_forward_analysis(self, df, signals, train_period=240, test_period=60, step=60):
        print(f"\n{'='*80}")
        print(f"  滚动窗口分析")
        print(f"{'='*80}")
        print(f"训练周期: {train_period}天")
        print(f"测试周期: {test_period}天")
        print(f"步长: {step}天")
        
        results = []
        n_windows = 0
        
        start_idx = train_period
        while start_idx + test_period <= len(df):
            train_df = df.iloc[start_idx - train_period:start_idx]
            test_df = df.iloc[start_idx:start_idx + test_period]
            
            train_signals = signals.iloc[start_idx - train_period:start_idx]
            test_signals = signals.iloc[start_idx:start_idx + test_period]
            
            train_result = self.run_backtest(train_df, train_signals)
            test_result = self.run_backtest(test_df, test_signals)
            
            if train_result and test_result:
                results.append({
                    'window_start': df.index[start_idx],
                    'window_end': df.index[start_idx + test_period - 1],
                    'train_return': train_result['total_return_pct'],
                    'test_return': test_result['total_return_pct'],
                    'train_sharpe': train_result['sharpe_ratio'],
                    'test_sharpe': test_result['sharpe_ratio'],
                    'train_drawdown': train_result['max_drawdown_pct'],
                    'test_drawdown': test_result['max_drawdown_pct']
                })
                
                n_windows += 1
                
                if n_windows % 5 == 0:
                    print(f"完成窗口 {n_windows}: "
                          f"训练收益 {train_result['total_return_pct']:+.2f}%, "
                          f"测试收益 {test_result['total_return_pct']:+.2f}%")
            
            start_idx += step
        
        if results:
            results_df = pd.DataFrame(results)
            
            print(f"\n滚动窗口统计:")
            print("-" * 80)
            print(f"总窗口数: {n_windows}")
            print(f"平均训练收益: {results_df['train_return'].mean():.2f}%")
            print(f"平均测试收益: {results_df['test_return'].mean():.2f}%")
            print(f"平均训练夏普: {results_df['train_sharpe'].mean():.2f}")
            print(f"平均测试夏普: {results_df['test_sharpe'].mean():.2f}")
            
            stability = (results_df['test_return'] > 0).mean() * 100
            print(f"测试期盈利比例: {stability:.1f}%")
            
            return results_df
        
        return None
    
    def calculate_risk_metrics(self, equity_curve):
        if len(equity_curve) < 2:
            return None
        
        returns = equity_curve.pct_change().dropna()
        
        metrics = {
            'total_return': (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0],
            'annualized_return': self._calculate_annualized_return(equity_curve),
            'annualized_volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'calmar_ratio': self._calculate_calmar_ratio(equity_curve),
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'var_95': np.percentile(returns, 5),
            'cvar_95': returns[returns <= np.percentile(returns, 5)].mean(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
        
        return metrics
    
    def _calculate_annualized_return(self, equity_curve):
        if len(equity_curve) < 2:
            return 0
        
        total_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
        n_days = len(equity_curve)
        years = n_days / 252
        
        if years > 0:
            return (1 + total_return) ** (1 / years) - 1
        return 0
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.03):
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def _calculate_sortino_ratio(self, returns, risk_free_rate=0.03, target_return=0):
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < target_return]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        downside_std = downside_returns.std()
        return np.sqrt(252) * excess_returns.mean() / downside_std
    
    def _calculate_calmar_ratio(self, equity_curve):
        if len(equity_curve) < 2:
            return 0
        
        annualized_return = self._calculate_annualized_return(equity_curve)
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        if max_drawdown == 0:
            return 0
        
        return annualized_return / max_drawdown
    
    def _calculate_max_drawdown(self, equity_curve):
        if len(equity_curve) == 0:
            return 0
        
        cummax = equity_curve.expanding().max()
        drawdown = (equity_curve - cummax) / cummax
        
        return abs(drawdown.min())
    
    def generate_comprehensive_report(self, df, signals):
        print(f"\n{'='*80}")
        print(f"  综合回测报告")
        print(f"{'='*80}")
        
        result = self.run_backtest(df, signals)
        
        if not result:
            print("回测失败")
            return None
        
        print("\n基本指标:")
        print("-" * 80)
        print(f"总收益率: {result['total_return_pct']:+.2f}%")
        print(f"总交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate_pct']:.2f}%")
        print(f"夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"最大回撤: {result['max_drawdown_pct']:.2f}%")
        
        equity_curve = result.get('equity_curve')
        if equity_curve is not None and len(equity_curve) > 0:
            risk_metrics = self.calculate_risk_metrics(equity_curve['equity'])
            
            if risk_metrics:
                print("\n风险指标:")
                print("-" * 80)
                print(f"年化收益率: {risk_metrics['annualized_return']:.2%}")
                print(f"年化波动率: {risk_metrics['annualized_volatility']:.2%}")
                print(f"索提诺比率: {risk_metrics['sortino_ratio']:.2f}")
                print(f"Calmar比率: {risk_metrics['calmar_ratio']:.2f}")
                print(f"VaR (95%): {risk_metrics['var_95']:.2%}")
                print(f"CVaR (95%): {risk_metrics['cvar_95']:.2%}")
                print(f"偏度: {risk_metrics['skewness']:.3f}")
                print(f"峰度: {risk_metrics['kurtosis']:.3f}")
        
        return result