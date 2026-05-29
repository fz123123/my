# Claude Code 安装指南

## 前置条件
- 需要 Node.js 18 或更高版本
- 需要有 Claude.ai 或 Claude Console 账户

## 安装步骤

### 方法一：官方安装脚本（推荐）

#### Windows (PowerShell)
```powershell
irm https://claude.ai/install.ps1 | iex
```

#### macOS / Linux (Bash)
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 方法二：通过 NPM 安装

#### 1. 先安装 Node.js
- 访问 [nodejs.org](https://nodejs.org/) 下载并安装 LTS 版本
- 安装完成后，在终端中验证：
  ```bash
  node --version
  npm --version
  ```

#### 2. 安装 Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

## 使用方式

### 启动 Claude Code
```bash
# 进入项目目录
cd c:\Users\Administrator\Documents\trae_projects\0

# 启动 Claude Code
claude
```

### 首次使用
1. 启动后会提示登录
2. 按照提示访问提供的 URL
3. 使用您的 Claude.ai 账户登录
4. 授权后即可开始使用

## 常用命令

```bash
# 查看帮助
claude --help

# 在特定目录启动
claude --dir /path/to/project

# 直接执行单条指令
claude -p "修复这个bug"
```

## 支持的平台

- **终端**：直接在终端中使用
- **VS Code**：安装 VS Code 扩展
- **JetBrains**：安装 JetBrains 插件
- **桌面应用**：下载桌面版
- **网页版**：访问 [claude.ai/code](https://claude.ai/code)

## 更多资源

- **官方文档**：[code.claude.com/docs](https://code.claude.com/docs)
- **快速入门**：[code.claude.com/docs/quickstart](https://code.claude.com/docs/quickstart)
- **VS Code 扩展**：[VS Code 市场](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
