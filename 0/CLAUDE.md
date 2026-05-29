# 龙量化策略项目

## 项目概述
这是一个基于 Python 的量化交易策略回测系统，用于开发和验证股票量化策略。

## 技术栈
- **语言**: Python 3.12+
- **主要库**:
  - pandas (数据处理)
  - numpy (数值计算)
  - matplotlib (静态绘图)
  - plotly (交互式绘图)
  - mplfinance (金融K线图)
  - ta-lib / ta (技术指标)

## 项目结构
```
0/
├── strategy.py          # 策略核心逻辑
├── backtest.py          # 回测引擎
├── main.py              # 主程序入口
├── test_main.py         # 测试版本
├── requirements.txt     # Python依赖
├── backtest_result.html # 交互式回测图表
└── .claude/            # Claude Code配置
```

## 核心模块

### strategy.py
- `Strategy` 类：策略执行引擎
- 主要指标：SMA、RSI、MACD、布林带、ATR
- 信号生成逻辑

### backtest.py
- `Backtester` 类：回测计算引擎
- 回测指标：总收益、年化收益、夏普比率、最大回撤、胜率等
- 可视化功能：静态图表 + 交互式图表

## 编码规范
- 使用类型注解 (Type Hints)
- 模块化设计，可扩展性强
- 遵循 PEP 8 规范
- 有详细的 docstring

## 运行项目
```bash
python main.py
```

## 工作流
1. 修改 `strategy.py` 中的策略逻辑
2. 运行 `main.py` 进行回测
3. 查看 `backtest_result.html` 分析结果
4. 迭代优化策略
