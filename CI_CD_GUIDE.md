# CI/CD 集成指南
====================

## 概览

本指南说明如何将项目中的量化交易项目集成到CI/CD流水线中。

## 📁 项目结构

```
trae_projects/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml          # 通用CI/CD配置 (Linux环境
│       ├── windows-ci.yml    # Windows专用CI配置
│       └── simple-ci.yml     # 简化版CI配置
├── 0/
├── 17/
├── 33/
├── 88/
├── run_all_tests.py           # 统一测试运行脚本
├── requirements.txt           # 公共Python依赖
├── check_projects.py          # 项目检查脚本
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 1. 本地运行测试

```bash
# 运行所有项目的单元测试
python run_all_tests.py
```

### 2. 推送到GitHub后自动运行

只需将代码推送到GitHub仓库，CI/CD将自动触发。

## 🏗️ CI/CD 配置说明

---

## 📋 配置文件说明

### 1. simple-ci.yml (推荐使用)

这是简化的CI配置，适用于：

- 使用Windows环境
- 统一测试所有项目
- 自动安装依赖
- 运行全部测试

### 2. windows-ci.yml

专门针对Windows环境优化的配置

### 3. ci-cd.yml

跨平台配置，支持并行测试

## 🔧 配置步骤

### Step 1: 创建GitHub仓库

1. 初始化Git仓库
   ```bash
   cd trae_projects
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

### Step 2: 启用GitHub Actions

无需额外配置，.github/workflows/目录下的YAML文件会自动被GitHub识别。

### Step 3: 推送到GitHub

推送到 main/master/develop分支后自动触发CI/CD。

## 📊 测试覆盖

### 项目0 (Python项目
- 回测器初始化
- 策略模块
- 数据处理模块

### 项目17 (Python项目)
- 数据分析
- 统计分析

### 项目33 (TypeScript项目)
- 恐慌盘策略
- 回测系统

### 项目88 (Python项目)
- 通达信数据读取
- 回测系统

## 🔍 CI/CD 流水线步骤

```
1. Checkout Code
   ↓
2. Setup Python 3.12
   ↓
3. Setup Node.js 20
   ↓
4. Install Dependencies
   ↓
5. Build TypeScript (项目33)
   ↓
6. Run All Tests
   ↓
7. Upload Results
```

## 🛠️ 本地测试命令

```bash
# 安装所有Python依赖
pip install -r requirements.txt

# 运行项目88测试
cd 88
python tests/test_eagle_strategy.py

# 项目33测试
cd 33
npm install
npm run build
npx ts-node tests/panic_strategy.test.ts

# 运行所有测试
cd ..
python run_all_tests.py
```

## ✅ 测试成功标志

- ✅ 所有项目通过CI/CD

## 📌 GitHub Actions 监控

访问您的GitHub仓库页面，点击 `Actions` 标签页查看流水线运行状态。

## 🔧 故障排查

### 问题: 测试失败
检查：
1. 本地运行 `python run_all_tests.py` 
2. 查看具体失败的测试文件
3. 检查依赖是否正确安装

### 问题: Node.js 依赖安装失败
确认项目33中的package.json正确配置

## 📞 更多帮助

参考GitHub Actions文档: https://docs.github.com/en/actions

## 📄 许可证

MIT License
