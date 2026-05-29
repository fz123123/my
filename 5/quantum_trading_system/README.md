# 量子量化平台 Pro (QuantumQuant Pro)

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Mac-orange" alt="Platform">
</p>

## 📋 项目简介

**量子量化平台 Pro** 是一个企业级量化投资平台，集策略开发、回测优化、实时监控、风险管理于一体。

### ✨ 核心功能

- 📊 **策略回测** - 支持多种技术指标和策略
- 🔍 **策略优化** - 参数优化、敏感性分析
- 📈 **策略组合** - 多策略组合、权重优化
- 💹 **实时监控** - 自选股信号监控
- ⚠️ **风险管理** - 止损止盈、仓位管理
- 📑 **报告生成** - 专业HTML/PDF报告

## 🚀 快速开始

### 方法一：双击启动（Windows）

双击 `启动平台.bat`，选择启动模式：
- **Web界面** - 推荐，适合可视化操作
- **命令行** - 适合高级用户

### 方法二：命令行启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Web界面
streamlit run web_app.py

# 或启动命令行版本
python main.py
```

### 方法三：用户中心

```bash
# 启动用户认证系统
streamlit run user_center.py
```

## 📁 项目结构

```
quantum_trading_system/
├── core/                      # 核心模块
│   ├── data_engine.py         # 多数据源管理
│   ├── data_fetcher.py        # 数据获取
│   ├── indicators.py          # 技术指标
│   └── risk_engine.py         # 风险管理
├── strategies/                # 策略库
│   ├── basic_strategies.py   # 基础策略
│   └── optimizer.py          # 策略优化
├── backtest/                 # 回测引擎
│   ├── engine.py             # 基础回测
│   └── enhanced_engine.py    # 增强回测
├── dashboard/                # 可视化
│   └── visualizer.py        # Dashboard图表
├── reports/                  # 报告生成
│   └── generator.py         # 报告工具
├── business/                 # 商业化模块
│   ├── subscription_manager.py  # 订阅管理
│   └── analytics.py          # 数据分析
├── monitor/                  # 监控模块
│   └── realtime_monitor.py  # 实时监控
├── utils/                    # 工具
│   └── auto_manager.py      # 自动管理
├── web_app.py               # Web主应用
├── user_center.py           # 用户中心
├── main.py                  # 命令行入口
├── config.py                # 配置文件
└── requirements.txt         # 依赖列表
```

## 🎯 功能详解

### 1. 策略回测

**支持的数据源：**
- A股市场（akshare、baostock）
- 加密货币（Binance）
- 指数数据

**内置策略：**
- 均线交叉策略（MA5/MA20）
- RSI超买超卖策略
- 布林带策略
- 多因子策略
- KDJ策略

**回测指标：**
- 总收益率
- 夏普比率
- 最大回撤
- 胜率
- 盈亏比
- Calmar比率

### 2. 策略优化

**优化方法：**
- 网格搜索（Grid Search）
- 参数敏感性分析
- Walk-Forward分析

**优化目标：**
- 夏普比率最大化
- 收益率最大化
- 回撤最小化
- 胜率最大化

### 3. 风险管理

**风控功能：**
- 固定止损/移动止损
- 固定止盈/跟踪止盈
- 仓位管理
- 日亏损熔断
- 单笔交易限制

### 4. 策略组合

**组合功能：**
- 多策略同时运行
- 策略权重优化
- 风险分散

### 5. 实时监控

**监控功能：**
- 多标的实时监控
- 买卖信号提示
- 技术指标显示
- 自动刷新

### 6. 报告系统

**报告格式：**
- HTML可视化报告
- JSON数据报告
- 文本摘要

**报告内容：**
- 性能指标摘要
- 权益曲线图
- 回撤分析图
- 交易记录表

## 💰 订阅计划

| 版本 | 价格 | 功能 |
|------|------|------|
| **免费版** | ¥0 | 3个策略、每日10次回测、延迟数据 |
| **专业版** | ¥99/月 | 10个策略、实时数据、邮件支持 |
| **高级版** | ¥299/月 | 100个策略、API接口、高级指标 |
| **企业版** | ¥999/月 | 无限策略、完整API、24/7支持 |

## 🛠️ 配置文件

编辑 `config.py` 自定义系统配置：

```python
config = {
    'auto_save': True,              # 自动保存
    'auto_backup': True,             # 自动备份
    'backup_interval_hours': 24,    # 备份间隔
    'trading': {
        'initial_capital': 100000,  # 初始资金
        'fee_rate': 0.0004,         # 手续费
        'slippage': 0.0005          # 滑点
    },
    'risk_control': {
        'stop_loss_default': 0.05,   # 默认止损
        'take_profit_default': 0.10, # 默认止盈
        'max_drawdown': 0.15         # 最大回撤
    },
    'monitor': {
        'refresh_interval': 60       # 监控刷新间隔
    },
    'watchlist': [
        '000001.SZ',
        '000002.SZ',
        '600000.SH',
        'BTCUSDT',
        'ETHUSDT'
    ]
}
```

## 📊 技术栈

- **Python 3.8+** - 主语言
- **Pandas** - 数据分析
- **NumPy** - 数值计算
- **akshare** - A股数据
- **baostock** - 备用数据源
- **Streamlit** - Web框架
- **Plotly** - 数据可视化
- **SQLite** - 数据存储

## 🔧 常见问题

### Q1: 数据获取失败？

检查网络连接，确保可以访问：
- akshare API
- Binance API
- baostock API

### Q2: 回测结果不准确？

可能原因：
- 数据质量差
- 滑点设置不当
- 未考虑交易费用

建议：
- 使用前复权数据
- 合理设置滑点
- 开启风控模块

### Q3: Web界面无法启动？

检查：
1. Python版本是否3.8+
2. 依赖是否安装成功
3. 端口8501是否被占用

解决方法：
```bash
# 检查Python版本
python --version

# 重新安装依赖
pip install -r requirements.txt

# 指定端口启动
streamlit run web_app.py --server.port 8502
```

## 📈 发展规划

### v3.1 (计划中)
- [ ] 机器学习策略
- [ ] 实盘交易对接
- [ ] 移动端App

### v4.0 (规划中)
- [ ] 云端策略市场
- [ ] 社区功能
- [ ] 量化培训课程

## 📞 技术支持

- 📧 邮箱: support@quantumquant.com
- 💬 在线客服: 开发中
- 📖 文档: https://docs.quantumquant.com

## ⚠️ 免责声明

本平台仅供学习和研究使用，不构成任何投资建议。量化交易存在风险，请谨慎投资，盈亏自负。

---

**© 2024 量子量化平台 Pro | QuantumQuant Pro**

**Made with ❤️ for quantitative trading**
