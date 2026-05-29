# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

st.set_page_config(
    page_title="量子量化平台 Pro - 简化版",
    page_icon="🐲",
    layout="wide"
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
    .stock-list {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def load_config():
    config_file = Path(__file__).parent / 'system_config.json'
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'watchlist': []}

def main():
    st.markdown('<h1 class="main-header">🐲 量子量化平台 Pro - 自选股监控</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666;">通达信自选股监控 | 更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
    
    config = load_config()
    watchlist = config.get('watchlist', [])
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 自选股总数", len(watchlist))
    
    with col2:
        sh_count = sum(1 for s in watchlist if '.SH' in s)
        st.metric("📈 上海主板", sh_count)
    
    with col3:
        sz_count = sum(1 for s in watchlist if '.SZ' in s)
        st.metric("📉 深圳主板", sz_count)
    
    st.divider()
    
    st.header("📋 自选股列表")
    
    if watchlist:
        df = pd.DataFrame({
            '序号': range(1, len(watchlist) + 1),
            '股票代码': [s.split('.')[0] for s in watchlist],
            '市场': [s.split('.')[1] if '.' in s else 'N/A' for s in watchlist],
            '完整代码': watchlist
        })
        
        st.dataframe(
            df,
            use_container_width=True,
            height=600
        )
        
        st.divider()
        
        st.subheader("📥 导出选项")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv_data = '\n'.join(watchlist)
            st.download_button(
                label="📥 下载 CSV",
                data=csv_data,
                file_name=f"自选股_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col_exp2:
            st.info(f"✅ 已成功加载 {len(watchlist)} 只自选股")
    
    else:
        st.error("❌ 未找到自选股，请先运行导入脚本")
        st.code("python import_tdx_stocks.py")
    
    st.divider()
    
    st.subheader("🔧 功能说明")
    
    st.info("""
    **当前版本为简化版，仅显示自选股列表。**
    
    **完整功能需要修复数据库问题：**
    1. 修复 DataEngine 数据库初始化
    2. 重新启动 Web 应用
    3. 使用完整版 web_app.py
    """)
    
    st.divider()
    
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🐲 量子量化平台 Pro | 通达信自选股监控</p>
        <p>所有股票数据仅供参考，不构成投资建议</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
