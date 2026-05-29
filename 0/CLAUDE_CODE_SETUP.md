# Claude Code + 龙量化 完整配置指南

## 🎉 好消息！Node.js 已成功安装！

## 下一步安装 Claude Code

### 方案一：网页版（推荐，无需安装！）
1. 访问：https://claude.ai/code
2. 登录您的 Claude.ai 账户
3. 点击 "Open Folder" 或 "Add to Workspace"
4. 选择此文件夹：`c:\Users\Administrator\Documents\trae_projects\0`
5. 开始使用！

### 方案二：安装桌面版（完全本地）

#### 1. 重启终端
**重要！** 关闭所有 PowerShell/终端窗口，然后重新打开一个新的。

#### 2. 验证 Node.js
```powershell
node --version
npm --version
```

#### 3. 安装 Claude Code
```powershell
npm install -g @anthropic-ai/claude-code
```

#### 4. 运行 Claude Code
```powershell
cd c:\Users\Administrator\Documents\trae_projects\0
claude
```

## 项目已为 Claude Code 配置完成！

### 已创建的配置文件：
1. **.claude/config.json** - Claude Code 配置
2. **CLAUDE.md** - 项目介绍（Claude Code 自动识别）
3. **BACKTEST_CHART_GUIDE.md** - 图表查看指南

## 如何使用 Claude Code 优化策略

### 示例对话：
> "帮我优化 strategy.py 中的策略逻辑，提高收益率"
>
> "分析一下回测结果，看看哪里出了问题"
>
> "添加止损止盈功能到策略中"
>
> "优化策略参数，测试不同的指标组合"

### 推荐工作流：
1. 在 Claude Code 中打开项目文件夹
2. 运行 `python main.py` 查看当前回测结果
3. 让 Claude 分析 `backtest_result.html`
4. 让 Claude 修改策略
5. 再次运行回测验证效果
6. 迭代优化

## 当前项目状态

### 已完成：
✅ 策略框架搭建
✅ 回测引擎实现
✅ 交互式回测图表
✅ 买卖点标记
✅ Claude Code 项目配置

### 待优化（可让 Claude 协助）：
- 策略收益率目前为负数，需要优化
- 可添加更多技术指标
- 可添加止损止盈机制
- 可优化参数配置
- 可接入真实市场数据

## 快捷命令

```powershell
# 运行回测
python main.py

# 打开回测图表
start backtest_result.html
```

## 祝您量化顺利，财运亨通！💰📈

---
*有问题随时问！让 AI 助力您的量化之旅！*
