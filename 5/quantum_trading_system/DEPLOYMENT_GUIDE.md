
# 🚀 量子量化平台 Pro - 部署指南

## 一、项目概览

恭喜！您已经拥有了一个**完整的企业级量化交易平台**，包含：

✅ **技术基础**
- 风控引擎（止损止盈、仓位管理、风险熔断）
- 数据引擎（多数据源、历史数据库）
- 策略引擎（4大经典策略）
- 回测引擎（Monte Carlo、敏感性分析）

✅ **产品功能**
- Streamlit Web界面
- 专业Dashboard（Plotly可视化）
- 回测报告生成系统

✅ **商业化模块**
- 订阅管理系统（4个版本）
- 用户认证系统
- 运营数据分析

---

## 二、快速启动

### Windows 用户

**方法1：双击启动（最简单）**

```
双击文件：启动平台.bat
```

**方法2：命令行启动**

```bash
# 进入项目目录
cd c:\Users\Administrator\Documents\trae_projects\5\quantum_trading_system

# 安装依赖
pip install -r requirements.txt

# 启动Web界面
streamlit run web_app.py

# 或启动命令行版本
python main.py
```

**方法3：启动用户中心**

```bash
streamlit run user_center.py
```

### Linux/Mac 用户

```bash
# 进入项目目录
cd quantum_trading_system

# 安装依赖
pip install -r requirements.txt

# 启动Web界面
streamlit run web_app.py --server.headless false

# 或启动命令行版本
python main.py
```

---

## 三、访问地址

启动后，浏览器会自动打开：

- **Web界面**: http://localhost:8501
- **用户中心**: http://localhost:8501/user_center.py
- **命令行**: 终端界面

---

## 四、功能测试

### 4.1 测试策略回测

1. 打开 Web 界面
2. 选择 "📈 策略回测"
3. 输入标的：`000001.SZ`（平安银行）
4. 选择策略：`均线交叉`
5. 点击 "开始回测"
6. 查看结果和图表

### 4.2 测试策略优化

1. 选择 "🔍 策略优化"
2. 输入标的：`000001.SZ`
3. 选择策略：`均线交叉`
4. 设置参数范围
5. 点击 "开始优化"
6. 查看最优参数

### 4.3 测试策略组合

1. 选择 "📊 策略组合"
2. 勾选多个策略
3. 设置权重
4. 点击 "分析组合"
5. 查看组合表现

### 4.4 测试实时监控

1. 选择 "💹 实时监控"
2. 选择监控标的
3. 设置刷新间隔
4. 点击 "开始监控"
5. 查看实时信号

### 4.5 测试用户系统

1. 启动：`streamlit run user_center.py`
2. 测试注册功能
3. 测试登录功能
4. 查看订阅计划
5. 测试用户中心

---

## 五、系统配置

### 5.1 修改配置文件

编辑 `config.py`：

```python
# 风控参数
'risk_control': {
    'stop_loss_default': 0.05,      # 5%止损
    'take_profit_default': 0.10,     # 10%止盈
    'max_drawdown': 0.15            # 15%最大回撤
}

# 交易参数
'trading': {
    'initial_capital': 100000,      # 初始资金
    'fee_rate': 0.0004,            # 万4手续费
    'slippage': 0.0005             # 万5滑点
}

# 监控标的
'watchlist': [
    '000001.SZ',
    '000002.SZ',
    '600000.SH',
    '600519.SH',
    'BTCUSDT',
    'ETHUSDT'
]
```

### 5.2 修改订阅价格

编辑 `business/subscription_manager.py`：

```python
plans = {
    'free': {'price': 0},
    'basic': {'price': 99},      # 修改价格
    'pro': {'price': 299},
    'enterprise': {'price': 999}
}
```

---

## 六、数据管理

### 6.1 查看数据状态

在 Web 界面的 "⚙️ 系统设置" 中查看：
- 股票记录数
- 加密货币记录数
- 缓存大小

### 6.2 手动备份

```bash
# 命令行版本
进入菜单 [4] 数据管理
选择 [2] 立即备份

# 自动备份
系统每24小时自动备份一次
```

### 6.3 恢复备份

```bash
进入菜单 [4] 数据管理
选择 [3] 恢复备份
选择要恢复的备份编号
```

---

## 七、常见问题

### 问题1：数据获取失败

**原因**：网络问题或API限制

**解决方法**：
1. 检查网络连接
2. 使用代理（如需要）
3. 等待几分钟后重试
4. 系统会自动使用模拟数据

### 问题2：回测结果为0

**原因**：数据不足或策略参数不当

**解决方法**：
1. 确保数据量 > 60天
2. 调整策略参数
3. 更换标的

### 问题3：Web界面无法启动

**原因**：端口被占用或依赖缺失

**解决方法**：
```bash
# 检查端口
netstat -ano | findstr 8501

# 杀死进程
taskkill /PID <进程ID> /F

# 或使用其他端口
streamlit run web_app.py --server.port 8502
```

---

## 八、商业化部署

### 8.1 本地部署

适合：个人使用、小团队

```bash
# 直接运行
streamlit run web_app.py
```

### 8.2 云服务器部署

适合：商业运营

**推荐配置**：
- CPU: 2核+
- 内存: 4GB+
- 带宽: 5Mbps+
- 系统: Ubuntu 20.04 / Windows Server

**部署步骤**：

1. 安装 Python 3.8+
2. 安装依赖：`pip install -r requirements.txt`
3. 配置防火墙：开放端口 8501
4. 使用 nohup 后台运行：
   ```bash
   nohup streamlit run web_app.py --server.port 8501 &
   ```

### 8.3 Docker 部署（推荐）

适合：生产环境

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "web_app.py", "--server.address", "0.0.0.0"]
```

```bash
# 构建镜像
docker build -t quantum-quant-pro .

# 运行容器
docker run -d -p 8501:8501 quantum-quant-pro
```

---

## 九、下一步建议

### 短期（1-2周）
1. ✅ 完成本部署指南
2. ✅ 测试所有功能
3. ✅ 调整参数和配置
4. ⬜ 添加更多策略
5. ⬜ 优化界面设计

### 中期（1-3月）
1. ⬜ 接入实盘交易API
2. ⬜ 开发移动端App
3. ⬜ 建立用户社区
4. ⬜ 开始小规模推广

### 长期（3-6月）
1. ⬜ 申请相关资质
2. ⬜ 建立运营团队
3. ⬜ 扩大用户规模
4. ⬜ 实现盈利目标

---

## 十、技术支持

- 📧 邮箱: support@quantumquant.com
- 📖 文档: https://docs.quantumquant.com
- 💬 客服: 开发中
- 📊 状态: https://status.quantumquant.com

---

## 十一、版本信息

- **项目版本**: v3.0 Pro
- **发布日期**: 2024
- **作者**: QuantumQuant Team
- **许可证**: MIT

---

## 十二、致谢

感谢您选择 **量子量化平台 Pro**！

这个平台凝聚了：
- ✅ 专业的量化交易知识
- ✅ 丰富的软件开发经验
- ✅ 完整的产品设计思路
- ✅ 商业化的运营思维

希望这个平台能帮助您在量化投资的道路上走得更远！

**祝您投资顺利，收益丰厚！** 🚀💰

---

**© 2024 量子量化平台 Pro | QuantumQuant Pro**

**Powered by Quantum Technology**
