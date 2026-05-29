# -*- coding: utf-8 -*-

import sys
sys.dont_write_bytecode = True

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_engine import DataEngine
from core.indicators import calculate_indicators
from strategies.basic_strategies import StrategyMaCross, StrategyRsi, StrategyBollinger, StrategyMultiFactor
from backtest.engine import BacktestEngine
from backtest.enhanced_engine import EnhancedBacktestEngine
from strategies.optimizer import StrategyOptimizer, StrategyPortfolio
from core.risk_engine import RiskEngine
from config import config

st.set_page_config(
    page_title="量子量化平台 Pro",
    page_icon="🐲",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .success-metric {
        color: #28a745;
        font-weight: bold;
    }
    .danger-metric {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-metric {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if 'data_engine' not in st.session_state:
        st.session_state.data_engine = DataEngine()
    
    if 'risk_engine' not in st.session_state:
        st.session_state.risk_engine = RiskEngine()
    
    if 'backtest_engine' not in st.session_state:
        st.session_state.backtest_engine = EnhancedBacktestEngine()
    
    if 'optimizer' not in st.session_state:
        st.session_state.optimizer = StrategyOptimizer()
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = StrategyPortfolio()


def main():
    st.markdown('<h1 class="main-header">🐲 量子量化平台 Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">企业级量化交易平台 - 策略开发 | 回测优化 | 实时监控</p>', unsafe_allow_html=True)
    
    init_session_state()
    
    menu = ["📊 策略回测", "⚙️ 策略优化", "💼 策略组合", "📈 实时监控", "🔧 系统设置"]
    choice = st.sidebar.selectbox("功能导航", menu)
    
    if choice == "📊 策略回测":
        show_backtest_page()
    elif choice == "⚙️ 策略优化":
        show_optimizer_page()
    elif choice == "💼 策略组合":
        show_portfolio_page()
    elif choice == "📈 实时监控":
        show_monitor_page()
    elif choice == "🔧 系统设置":
        show_settings_page()


def show_backtest_page():
    st.header("📊 策略回测")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("回测配置")
        
        symbol = st.text_input("股票代码", value="000001.SZ")
        
        strategy_options = {
            "均线交叉": StrategyMaCross,
            "RSI策略": StrategyRsi,
            "布林带": StrategyBollinger,
            "多因子": StrategyMultiFactor
        }
        
        selected_strategy_name = st.selectbox("选择策略", list(strategy_options.keys()))
        selected_strategy_class = strategy_options[selected_strategy_name]
        
        if selected_strategy_name == "均线交叉":
            short_period = st.slider("短期均线周期", 3, 20, 5)
            long_period = st.slider("长期均线周期", 15, 60, 20)
        elif selected_strategy_name == "RSI策略":
            oversold = st.slider("超卖阈值", 20, 40, 30)
            overbought = st.slider("超买阈值", 60, 80, 70)
        
        initial_capital = st.number_input("初始资金", value=100000, step=10000)
        
        if st.button("开始回测", type="primary"):
            with st.spinner("正在获取数据..."):
                data_engine = st.session_state.data_engine
                df = data_engine.get_stock_data(symbol)
                
                if df is not None and len(df) > 60:
                    with st.spinner("正在计算指标..."):
                        df = calculate_indicators(df)
                        
                        if selected_strategy_name == "均线交叉":
                            strategy = selected_strategy_class(short_period, long_period)
                        elif selected_strategy_name == "RSI策略":
                            strategy = selected_strategy_class(oversold, overbought)
                        else:
                            strategy = selected_strategy_class()
                        
                        signals = strategy.generate_signals(df)
                        
                        with st.spinner("正在回测..."):
                            engine = st.session_state.backtest_engine
                            result = engine.run_backtest(df, signals)
                            
                            if result:
                                st.session_state.backtest_result = result
                                st.session_state.backtest_df = df
                                st.session_state.backtest_signals = signals
                                st.success("回测完成！")
                            else:
                                st.error("回测失败")
                else:
                    st.error("数据不足")

    with col2:
        if 'backtest_result' in st.session_state:
            result = st.session_state.backtest_result
            
            st.subheader("回测结果")
            
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                return_color = "success" if result['total_return_pct'] > 0 else "danger"
                st.metric(
                    "总收益率",
                    f"{result['total_return_pct']:+.2f}%",
                    delta=f"{result['final_equity'] - result['total_return']:.2f}"
                )
            
            with metric_cols[1]:
                st.metric("夏普比率", f"{result['sharpe_ratio']:.2f}")
            
            with metric_cols[2]:
                st.metric("最大回撤", f"{result['max_drawdown_pct']:.2f}%")
            
            with metric_cols[3]:
                st.metric("胜率", f"{result['win_rate_pct']:.2f}%")
            
            st.divider()
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("净值曲线")
                if 'equity_curve' in result:
                    equity_df = result['equity_curve']
                    st.line_chart(equity_df['equity'])
            
            with col_chart2:
                st.subheader("价格走势")
                df = st.session_state.backtest_df
                st.line_chart(df['close'])
            
            st.divider()
            
            st.subheader("交易记录")
            if 'trades' in result and result['trades']:
                trades_df = pd.DataFrame(result['trades'])
                trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(trades_df, use_container_width=True)
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.info(f"总交易次数: {result['total_trades']}")
                with col_info2:
                    win_trades = sum(1 for i in range(0, len(result['trades']) - 1, 2) 
                                   if i + 1 < len(result['trades']) and 
                                   result['trades'][i + 1]['price'] > result['trades'][i]['price'])
                    st.info(f"盈利交易: {win_trades}")


def show_optimizer_page():
    st.header("⚙️ 策略参数优化")
    
    st.info("使用网格搜索找到最优参数组合")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        symbol = st.text_input("股票代码", value="000001.SZ")
        
        strategy_to_optimize = st.selectbox(
            "优化策略",
            ["均线交叉", "RSI策略"]
        )
        
        if strategy_to_optimize == "均线交叉":
            st.subheader("参数范围")
            short_min, short_max = st.slider("短期均线范围", 3, 15, (3, 10))
            long_min, long_max = st.slider("长期均线范围", 15, 60, (20, 40))
        elif strategy_to_optimize == "RSI策略":
            st.subheader("参数范围")
            oversold_min, oversold_max = st.slider("超卖范围", 20, 40, (25, 35))
            overbought_min, overbought_max = st.slider("超买范围", 60, 80, (65, 75))
        
        optimization_metric = st.selectbox(
            "优化目标",
            ["sharpe_ratio", "total_return_pct", "win_rate_pct"],
            format_func=lambda x: {
                "sharpe_ratio": "夏普比率",
                "total_return_pct": "总收益率",
                "win_rate_pct": "胜率"
            }.get(x, x)
        )
        
        if st.button("开始优化", type="primary"):
            with st.spinner("正在优化..."):
                data_engine = st.session_state.data_engine
                df = data_engine.get_stock_data(symbol)
                
                if df is not None:
                    df = calculate_indicators(df)
                    optimizer = st.session_state.optimizer
                    
                    if strategy_to_optimize == "均线交叉":
                        best = optimizer.optimize_ma_cross(
                            df, 
                            short_range=(short_min, short_max),
                            long_range=(long_min, long_max),
                            metric=optimization_metric
                        )
                    elif strategy_to_optimize == "RSI策略":
                        best = optimizer.optimize_rsi(
                            df,
                            oversold_range=(oversold_min, oversold_max),
                            overbought_range=(overbought_min, overbought_max),
                            metric=optimization_metric
                        )
                    
                    if best:
                        st.session_state.optimization_result = best
                        st.success("优化完成！")

    with col2:
        if 'optimization_result' in st.session_state:
            result = st.session_state.optimization_result
            
            st.subheader("最优参数")
            st.json(result['params'])
            
            col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
            
            with col_metrics1:
                st.metric("最优得分", f"{result['score']:.4f}")
            
            with col_metrics2:
                st.metric("收益率", f"{result['total_return_pct']:+.2f}%")
            
            with col_metrics3:
                st.metric("夏普比率", f"{result['sharpe_ratio']:.2f}")


def show_portfolio_page():
    st.header("💼 策略组合管理")
    
    st.info("组合多个策略，分散风险，提高收益")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("添加策略到组合")
        
        portfolio_strategies = []
        
        if st.checkbox("均线交叉"):
            short = st.slider("短期均线", 3, 20, 5)
            long = st.slider("长期均线", 15, 60, 20)
            weight = st.slider("权重", 0.1, 2.0, 1.0)
            portfolio_strategies.append({
                'class': StrategyMaCross(short, long),
                'name': '均线交叉',
                'weight': weight
            })
        
        if st.checkbox("RSI策略"):
            oversold = st.slider("超卖", 20, 40, 30, key='rsi_oversold')
            overbought = st.slider("超买", 60, 80, 70, key='rsi_overbought')
            weight = st.slider("权重", 0.1, 2.0, 1.0, key='rsi_weight')
            portfolio_strategies.append({
                'class': StrategyRsi(oversold, overbought),
                'name': 'RSI策略',
                'weight': weight
            })
        
        if st.checkbox("布林带"):
            weight = st.slider("权重", 0.1, 2.0, 1.0, key='bb_weight')
            portfolio_strategies.append({
                'class': StrategyBollinger(),
                'name': '布林带',
                'weight': weight
            })
        
        if st.button("分析组合", type="primary"):
            if portfolio_strategies:
                symbol = st.text_input("股票代码", value="000001.SZ", key="portfolio_symbol")
                
                with st.spinner("正在分析..."):
                    data_engine = st.session_state.data_engine
                    df = data_engine.get_stock_data(symbol)
                    
                    if df is not None:
                        df = calculate_indicators(df)
                        
                        portfolio = st.session_state.portfolio
                        portfolio.clear_all()
                        
                        for strat in portfolio_strategies:
                            portfolio.add_strategy(
                                strat['class'],
                                weight=strat['weight'],
                                name=strat['name']
                            )
                        
                        performances = portfolio.get_strategy_performance(df)
                        
                        st.session_state.portfolio_results = performances
                        st.success("分析完成！")

    with col2:
        if 'portfolio_results' in st.session_state:
            st.subheader("组合表现")
            
            results_df = st.session_state.portfolio_results
            
            st.dataframe(
                results_df.style.background_gradient(subset=['return_pct'], cmap='RdYlGn'),
                use_container_width=True
            )
            
            if len(results_df) > 1:
                st.subheader("策略对比")
                
                chart_data = results_df.set_index('name')[['return_pct', 'sharpe', 'max_drawdown']]
                st.bar_chart(chart_data)


def show_monitor_page():
    st.header("📈 实时监控")
    
    st.warning("⚠️ 实时监控功能需要在实际市场时间进行")
    
    watchlist = config.get('watchlist', [])[:20]
    
    symbols = st.multiselect(
        "选择监控股票",
        watchlist if watchlist else ['000001.SZ', '000002.SZ', '600000.SH', '600519.SH'],
        default=watchlist[:5] if watchlist else ['000001.SZ']
    )
    
    interval = st.slider("更新间隔(秒)", 30, 300, 60)
    
    if st.button("开始监控", type="primary"):
        data_engine = st.session_state.data_engine
        
        for symbol in symbols:
            with st.container():
                st.subheader(f"📊 {symbol}")
                
                df = data_engine.get_stock_data(symbol)
                
                if df is not None:
                    df = calculate_indicators(df)
                    
                    latest = df.iloc[-1]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("最新价", f"{latest['close']:.2f}")
                    
                    with col2:
                        if 'ma5' in latest and not pd.isna(latest['ma5']):
                            st.metric("MA5", f"{latest['ma5']:.2f}")
                    
                    with col3:
                        if 'rsi' in latest and not pd.isna(latest['rsi']):
                            rsi_value = latest['rsi']
                            st.metric("RSI", f"{rsi_value:.1f}")
                    
                    with col4:
                        if 'volume_ratio' in latest and not pd.isna(latest['volume_ratio']):
                            st.metric("成交量比", f"{latest['volume_ratio']:.2f}")
                    
                    st.divider()


def show_settings_page():
    st.header("🔧 系统设置")
    
    risk_engine = st.session_state.risk_engine
    
    st.subheader("风险参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stop_loss = st.slider("止损比例", 0.01, 0.15, risk_engine.stop_loss_pct, 0.01)
        take_profit = st.slider("止盈比例", 0.01, 0.30, risk_engine.take_profit_pct, 0.01)
    
    with col2:
        max_position = st.slider("最大持仓比例", 0.1, 0.8, risk_engine.max_position_ratio, 0.05)
        max_daily_loss = st.slider("日最大亏损", 0.05, 0.20, risk_engine.max_daily_loss_pct, 0.01)
    
    if st.button("更新风险参数", type="primary"):
        risk_engine.update_config(
            stop_loss_pct=stop_loss,
            take_profit_pct=take_profit,
            max_position_ratio=max_position,
            max_daily_loss_pct=max_daily_loss
        )
        st.success("风险参数已更新！")
    
    st.divider()
    
    st.subheader("系统状态")
    
    data_status = st.session_state.data_engine.get_data_status()
    
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        st.metric("股票记录数", f"{data_status['stock_records']:,}")
    
    with col_status2:
        st.metric("加密货币记录数", f"{data_status['crypto_records']:,}")
    
    with col_status3:
        st.metric("缓存大小", f"{data_status['cache_size']}")
    
    st.divider()
    
    st.subheader("风险配置概要")
    config_summary = risk_engine.get_config_summary()
    st.json(config_summary)


if __name__ == "__main__":
    main()
