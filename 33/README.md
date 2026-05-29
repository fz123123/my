# 量化交易系统

基于TypeScript构建的专业量化交易系统，支持T+1策略回测。

## ✨ 功能特性

- 📊 多种策略支持：均线交叉、RSI、MACD、T+1策略
- 📈 真实数据接口：Tushare A股数据集成
- 📉 回测引擎：完整的回测分析和绩效指标
- 💰 风险控制：止损止盈、仓位管理
- 📝 模拟交易成本：佣金、滑点、冲击成本

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置Tushare Token

**方法一：使用配置文件**

复制 `config.example.json` 为 `config.json`，填入你的Tushare Token：

```json
{
  "tushare": {
    "token": "你的Token",
    "enabled": true
  },
  "data": {
    "cacheDir": "./data/cache",
    "useTushare": true
  }
}
```

**方法二：使用设置脚本**

```bash
npm run setup
```

### 3. 运行回测

```bash
# 运行T+1策略回测
npm run t1

# 运行所有策略回测
npm start
```

## 📁 项目结构

```
quant-trading-system/
├── src/
│   ├── config.ts              # 配置管理
│   ├── types/                 # 类型定义
│   ├── data/
│   │   ├── DataFetcher.ts     # 数据获取
│   │   └── TushareClient.ts   # Tushare接口
│   ├── strategy/
│   │   ├── Indicator.ts       # 技术指标
│   │   ├── Strategy.ts        # 策略基类
│   │   └── IntradayStrategy.ts # T+1策略
│   ├── backtest/
│   │   └── Backtester.ts      # 回测引擎
│   ├── risk/
│   │   └── RiskManager.ts     # 风控管理
│   ├── utils/
│   │   └── Logger.ts          # 日志工具
│   ├── index.ts
│   ├── t1-backtest.ts
│   └── setup-tushare.ts
├── config.json                # 配置文件
├── package.json
└── tsconfig.json
```

## 💡 使用说明

### T+1策略特点

- **买入时机**：尾盘选股，符合多因子条件
- **卖出时机**：次日择机卖出
- **策略参数**：
  - 止盈：1.5%
  - 止损：2%
  - 持仓：不超过2天

### 数据获取

- 默认使用Tushare获取真实A股数据
- 数据会自动缓存到 `data/cache` 目录
- 如Tushare不可用，自动回退到模拟数据

## 📊 回测指标

- 总收益率
- 年化收益率
- 最大回撤
- 夏普比率
- 胜率
- 盈亏比

## 🔧 开发说明

### 添加新策略

继承 `Strategy` 基类，实现 `generateSignal` 方法：

```typescript
import { Strategy, StrategyConfig, BarData, TradeSignal } from './types'

class MyStrategy extends Strategy {
  generateSignal(data: BarData[], index: number): TradeSignal {
    // 实现你的策略逻辑
    return {
      timestamp: data[index].timestamp,
      type: 'hold',
      symbol: 'DEFAULT',
      price: data[index].close,
      reason: 'No signal'
    }
  }
}
```

## 📝 注意事项

- 本系统仅供学习和研究使用
- 真实交易前请充分回测验证
- 投资有风险，入市需谨慎

## 📄 许可证

MIT License
