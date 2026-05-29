# 量子量化平台 - CI/CD 集成指南

**版本**: v3.0  
**更新日期**: 2026-05-20

---

## 📋 目录

1. [快速开始](#快速开始)
2. [本地测试](#本地测试)
3. [Git钩子](#git钩子)
4. [GitHub Actions](#github-actions)
5. [GitLab CI](#gitlab-ci)
6. [CI/CD配置说明](#cicd配置说明)

---

## 🚀 快速开始

### 一键初始化Git仓库（推荐）

```bash
# 在项目根目录下运行
scripts\init_repo.bat
```

这个脚本会自动：
- 初始化Git仓库
- 创建.gitignore文件
- 进行首次提交
- 安装Git钩子

---

## 💻 本地测试

### 运行完整CI流水线

在项目根目录下双击运行：

```
run_ci.bat
```

或者在命令行中：

```bash
# 运行核心测试
python tests/run_tests.py

# 运行边缘情况测试
python tests/test_edge_cases.py

# 运行完整CI检查（推荐）
run_ci.bat
```

### 本地测试包含的检查

| 阶段 | 说明 | 状态 |
|------|------|------|
| 环境检查 | Python和依赖检查 | ✅ |
| 核心测试 | 47个策略功能测试 | ✅ |
| 边缘测试 | 极端情况测试 | ⚠️ |
| 代码质量 | flake8语法检查 | ⚠️ |

---

## 🔗 Git钩子

### 安装pre-commit钩子

```bash
# 方式1: 使用安装脚本（推荐）
scripts\setup_git_hooks.bat

# 方式2: 手动安装
copy scripts\git_hooks\pre-commit.bat .git\hooks\pre-commit
```

### pre-commit钩子功能

每次执行 `git commit` 时会自动：
- 运行完整的策略测试
- 阻止测试失败的代码提交
- 确保代码质量

### 临时跳过钩子

```bash
git commit --no-verify -m "跳过测试的提交"
```

---

## 🌐 GitHub Actions

### 配置说明

GitHub Actions配置已创建在：
```
.github/workflows/ci.yml
```

### 功能特性

- ✅ 多Python版本测试（3.9, 3.10, 3.11, 3.12）
- ✅ 自动运行核心功能测试
- ✅ 自动运行边缘情况测试
- ✅ 代码质量检查（flake8）
- ✅ Pull Request自动检查
- ✅ 手动触发（workflow_dispatch）

### 使用步骤

1. **创建GitHub仓库**
   - 在GitHub上创建新仓库
   
2. **推送代码**
   ```bash
   git remote add origin https://github.com/你的用户名/quantum-trading-system.git
   git branch -M main
   git push -u origin main
   ```

3. **查看CI运行**
   - 访问你的GitHub仓库
   - 点击 "Actions" 标签页
   - 查看CI/CD运行状态

4. **PR检查**
   - 创建Pull Request时会自动运行测试
   - 测试失败会阻止合并（可在仓库设置中配置）

---

## 🦊 GitLab CI

### 配置说明

GitLab CI配置已创建在：
```
.gitlab-ci.yml
```

### 功能特性

- ✅ Python 3.10测试环境
- ✅ pip依赖缓存
- ✅ 多阶段测试流水线
- ✅ 代码质量检查
- ✅ MR自动检查

### 使用步骤

1. **创建GitLab仓库**
   - 在GitLab上创建新项目

2. **推送代码**
   ```bash
   git remote add origin https://gitlab.com/你的用户名/quantum-trading-system.git
   git push -u origin main
   ```

3. **查看CI/CD管道**
   - 访问GitLab项目
   - 点击 "CI/CD" → "Pipelines"

---

## 📁 CI/CD文件结构

```
quantum_trading_system/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions配置
├── .gitlab-ci.yml              # GitLab CI配置
├── .gitignore                  # Git忽略文件
├── run_ci.bat                  # 本地CI脚本
├── scripts/
│   ├── init_repo.bat           # Git仓库初始化脚本
│   ├── setup_git_hooks.bat     # Git钩子安装脚本
│   └── git_hooks/
│       ├── pre-commit          # Unix pre-commit钩子
│       └── pre-commit.bat      # Windows pre-commit钩子
└── CI_README.md                # 本文档
```

---

## ⚙️ CI/CD配置说明

### GitHub Actions工作流程

```
push/pull_request
    ↓
[test] - 多Python版本测试 (3.9-3.12)
    ↓
[edge-cases] - 边缘情况测试
    ↓
[quality-check] - 代码质量检查
```

### GitLab CI工作流程

```
[test] - 策略测试
    ↓
[quality] - 质量检查
```

### 自定义CI配置

#### 修改测试版本（GitHub Actions）

编辑 `.github/workflows/ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']  # 在这里添加/删除版本
```

#### 添加新的测试

在 `tests/` 目录下创建新测试文件，然后在CI配置中添加新步骤。

---

## 🔧 故障排除

### 问题: pre-commit钩子不工作

**解决方案**:
```bash
# 检查钩子是否可执行（Unix）
chmod +x .git/hooks/pre-commit

# Windows: 确保使用.bat文件
copy scripts\git_hooks\pre-commit.bat .git\hooks\pre-commit
```

### 问题: GitHub Actions找不到依赖

**解决方案**:
确保 `requirements.txt` 文件存在并包含所有依赖。

### 问题: 本地测试失败但CI通过

**解决方案**:
检查本地Python版本和依赖版本是否与CI环境一致。

---

## 📊 测试状态指示

| 状态 | 说明 |
|------|------|
| ✅ | 测试通过 |
| ❌ | 测试失败 |
| ⚠️ | 测试有警告 |

---

## 💡 最佳实践

1. **每次提交前运行测试**
   - 使用 `run_ci.bat` 或Git钩子自动运行

2. **保持小的提交**
   - 每次提交专注于一个功能或修复
   - 更容易定位问题

3. **使用Pull Request**
   - 让CI在PR中自动检查代码
   - 代码审查前确保测试通过

4. **更新测试用例**
   - 新增功能时同步更新测试
   - 修复Bug时先写失败测试，再修复

---

## 📞 技术支持

如有问题，请检查：
1. Python版本是否为3.8+
2. 依赖是否完整安装：`pip install -r requirements.txt`
3. 项目目录结构是否正确

---

*文档版本: v1.0*  
*最后更新: 2026-05-20*
