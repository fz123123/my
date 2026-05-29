# 涨停先知 (ZTB Seer) - 智能股票分析系统

## 📋 项目简介

涨停先知是一款基于Vue 3的智能股票分析系统，集成了实时行情、技术指标分析和智能选股功能。

**核心特点**：
- ⚡ 实时行情对接新浪财经API
- 📊 专业K线图和技术指标分析
- 🎯 多维度智能选股评分
- 💡 涨停预测分析

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
# 或
npx vite --host 0.0.0.0 --port 5173
```

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 📁 项目结构

```
stock-analysis/
├── src/
│   ├── views/              # 页面组件
│   │   ├── Home.vue        # 首页 - 潜力牛股推荐
│   │   ├── StockList.vue   # 股票列表页
│   │   └── StockDetail.vue # 股票详情页
│   ├── services/
│   │   └── stockService.js # 股票数据服务
│   ├── utils/
│   │   ├── indicators.js    # 技术指标计算
│   │   └── stockSelector.js # 选股策略
│   ├── router/
│   │   └── index.js        # 路由配置
│   ├── App.vue             # 主应用组件
│   └── main.js             # 入口文件
├── index.html
├── vite.config.js          # Vite配置
└── package.json
```

## 🔌 API配置

### 实时数据源

项目使用以下免费API：

1. **新浪财经** - 实时行情数据
   - 代理路径: `/api/sina`
   - 原始URL: `http://hq.sinajs.cn`
   - 功能: 股票实时价格、涨跌幅、成交量

2. **东方财富** - 历史K线数据
   - 代理路径: `/api/emhis`
   - 原始URL: `http://push2his.eastmoney.com`
   - 功能: 90天日K线历史数据

### Vite代理配置

代理配置位于 [vite.config.js](vite.config.js)：

```javascript
server: {
  proxy: {
    '/api/sina': {
      target: 'http://hq.sinajs.cn',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api\/sina/, '/list=')
    },
    '/api/emhis': {
      target: 'http://push2his.eastmoney.com',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api\/emhis/, '')
    }
  }
}
```

### 自定义API

如需使用其他数据源，修改 [stockService.js](src/services/stockService.js) 中的API地址。

## 📊 技术指标

系统集成了以下技术指标：

- **均线 (MA)**: MA5, MA10, MA20, MA60
- **MACD**: 指数平滑异同移动平均线
- **KDJ**: 随机指标
- **RSI**: 相对强弱指标
- **BOLL**: 布林带

## 🎯 选股策略

选股评分基于以下维度：

1. 价格变化（涨幅>2% +15分）
2. 市盈率（PE<30 +10分）
3. MACD信号（金叉+15分）
4. KDJ信号（K>D且K<70 +10分）
5. RSI区间（50-70区间 +10分）
6. 成交量（>50万 +5分）
7. 布林带位置（价格在均线以上 +5分）

## ⚠️ 注意事项

1. **网络要求**: 实时数据需要稳定的网络连接
2. **数据延迟**: 新浪财经数据约3-5秒延迟
3. **API限制**: 免费API可能有请求频率限制
4. **数据备份**: API不可用时自动回退到模拟数据

## 🔧 性能优化

- 数据缓存机制（30秒缓存）
- ECharts按需加载
- 代理超时设置（15秒）
- 自动降级策略

## 📝 免责声明

本系统仅供学习研究使用，不构成任何投资建议。股票投资有风险，决策需谨慎。

## 🛠️ 技术栈

- Vue 3.4.21
- Vite 5.1.6
- Vue Router 4.3.0
- Axios 1.6.8
- ECharts 5.5.0

## 📧 联系方式

如有问题或建议，请联系开发者。

---

**⚡ 涨停先知 - 让每一次涨停都不再错过**
