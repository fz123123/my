
# 量子交易系统 v3.0

整合了所有量化功能的自动化交易系统。

## 功能特点

✅ **自动保存** - 自动保存所有数据和结果  
✅ **自动备份** - 定期自动备份系统数据  
✅ **自动管理** - 自动清理旧备份，保持系统整洁  
✅ **策略回测** - 快速测试和对比多种策略  
✅ **实时监控** - 监控自选股信号  
✅ **多策略** - 均线交叉、RSI、布林带、多因子  

## 快速开始

### 方法一：双击启动（推荐）

直接双击 `启动系统.bat`

### 方法二：命令行启动

```bash
cd quantum_trading_system
python main.py
```

## 系统结构

```
quantum_trading_system/
├── core/              # 核心模块
│   ├── data_fetcher.py    # 数据获取
│   └── indicators.py      # 技术指标
├── strategies/        # 策略库
│   └── basic_strategies.py
├── backtest/          # 回测引擎
│   └── engine.py
├── monitor/           # 监控模块
│   └── realtime_monitor.py
├── utils/             # 工具
│   └── auto_manager.py   # 自动管理
├── data/              # 数据目录
├── backups/           # 备份目录
├── config.py          # 配置文件
├── main.py            # 主入口
└── requirements.txt   # 依赖
```

## 配置说明

系统配置在 `config.py` 中，或者通过系统菜单修改。

## 自动功能

- **自动保存**：每次运行结果自动保存到 backups/saves/
- **自动备份**：每24小时自动备份一次
- **自动清理**：自动删除10个以前的旧备份

## 策略说明

1. **均线交叉** - MA5上穿MA20买入，下穿卖出
2. **RSI策略** - RSI&lt;30买入，&gt;70卖出
3. **布林带** - 价格跌破下轨买入，突破上轨卖出
4. **多因子** - 结合多个指标的复合策略

