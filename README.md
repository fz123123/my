# 量化交易项目集

一个包含多个量化交易策略的完整项目集，包括实时数据监控、恐慌盘策略、回测系统等。

## 📁 项目结构

```
trae_projects/
├── 0/                      # 简单回测项目
│   ├── src/                # 源代码
│   ├── tests/              # 单元测试
│   ├── package.json        # 项目配置
│   └── README.md           # 项目说明
│
├── 17/                     # 量化分析项目
│   ├── src/                # 源代码
│   ├── tests/              # 单元测试
│   ├── package.json        # 项目配置
│   └── README.md           # 项目说明
│
├── 33/                     # 恐慌盘扫描系统
│   ├── src/                # TypeScript源代码
│   ├── dist/               # 编译输出
│   ├── tests/              # 单元测试
│   ├── package.json        # 项目配置
│   └── README.md           # 项目说明
│
├── 88/                     # 涨停先知实时监控
│   ├── src/                # 源代码
│   ├── dist/               # 编译输出
│   ├── tests/              # 单元测试
│   ├── package.json        # 项目配置
│   └── README.md           # 项目说明
│
├── .github/                # GitHub配置
│   └── workflows/
│       └── simple-ci.yml   # CI/CD配置文件
│
├── run_all_tests.py        # 统一测试运行器
├── requirements.txt        # Python依赖
└── .gitignore              # Git忽略规则
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/fz123123/my.git
cd my
```

### 2. 安装依赖

```bash
# Python项目依赖
pip install -r requirements.txt

# 各项目依赖
cd 0 && pip install -r requirements.txt
cd ../17 && pip install -r requirements.txt
cd ../33 && npm install
cd ../88 && pip install -r requirements.txt
```

### 3. 运行单元测试

```bash
# 运行所有项目的测试
python run_all_tests.py

# 或单独运行各项目测试
cd 0 && python tests/test_backtest.py
cd ../17 && python tests/test_quant_analysis.py
cd ../33 && npx ts-node tests/panic_strategy.test.ts
cd ../88 && python tests/test_eagle_strategy.py
```

## 📊 项目详情

### 项目0 - 简单回测系统

**功能：**
- 基础策略回测框架
- 支持多种技术指标（MA、RSI等）
- 简单的买入卖出信号生成

**技术栈：**
- Python 3.12+
- pandas、numpy

### 项目17 - 量化分析

**功能：**
- 量化数据分析
- 统计分析工具
- 数据验证和清洗

**技术栈：**
- Python 3.12+
- pandas、numpy

### 项目33 - 恐慌盘扫描系统

**功能：**
- 恐慌盘识别和扫描
- 实时市场监控
- 风险管理和止损策略

**技术栈：**
- TypeScript
- Node.js 22
- 通达信数据接口

### 项目88 - 涨停先知实时监控

**功能：**
- 涨停板实时监控
- 自选股实时数据更新
- 技术指标计算和展示

**技术栈：**
- Python 3.12+
- pandas、requests、ta

## 🧪 单元测试

所有项目都包含完整的单元测试，确保代码质量和逻辑正确性：

| 项目 | 测试框架 | 测试数量 | 状态 |
|------|---------|---------|------|
| 项目0 | pytest | 7 | ✅ 通过 |
| 项目17 | pytest | 3 | ✅ 通过 |
| 项目33 | Jest | 5 | ✅ 通过 |
| 项目88 | pytest | 7 | ✅ 通过 |

**运行测试：**

```bash
# Python项目
cd <project_dir>
python -m pytest tests/ -v

# TypeScript项目 (项目33)
cd 33
npm test
```

## 🔄 CI/CD 流水线

本项目使用 GitHub Actions 实现持续集成和持续部署：

### 工作流程

1. **代码推送** → 自动触发CI/CD
2. **环境设置** → Python 3.12 + Node.js 22
3. **依赖安装** → 自动安装所有依赖
4. **运行测试** → 执行所有单元测试
5. **结果上传** → 测试结果自动归档

### 查看CI/CD状态

访问 [GitHub Actions](https://github.com/fz123123/my/actions) 查看流水线运行状态。

### 手动触发

```bash
# 在本地推送代码
git add .
git commit -m "Your commit message"
git push origin main
```

## 📦 依赖说明

### Python依赖

- `pandas` - 数据处理
- `numpy` - 数值计算
- `requests` - HTTP请求
- `yfinance` - Yahoo Finance数据
- `ta` - 技术指标库
- `tushare` - A股数据接口

### Node.js依赖 (项目33)

- `typescript` - TypeScript支持
- `ts-node` - TypeScript运行器
- `jest` - 测试框架

## 📝 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

- GitHub: [@fz123123](https://github.com/fz123123)

## 🙏 致谢

- 通达信数据接口
- Yahoo Finance
- TuShare
- 所有开源库贡献者

---

**⭐ 如果这个项目对您有帮助，请为它点个星！**
