# 涨停先知项目 - 安装和使用指南

## 📦 安装步骤

### 1. 检查Node.js版本
```bash
node --version
# 要求: v14.0.0 或更高版本
```

### 2. 安装依赖
```bash
npm install
```

### 3. 启动开发服务器
```bash
npm run dev
# 或
npx vite --host 0.0.0.0 --port 5173
```

### 4. 访问应用
```
http://localhost:5173
```

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `npm install` | 安装依赖 |
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run preview` | 预览生产版本 |

## 📝 项目配置

### 修改端口
编辑 `vite.config.js`:
```javascript
server: {
  port: 3000,  // 修改为其他端口
  host: '0.0.0.0'
}
```

### 修改股票列表
编辑 `src/services/stockService.js`:
```javascript
const codes = [
  'sh600519',  // 添加股票代码
  'sz000001',
  // ...
]
```

## 🐛 常见问题

### 1. API请求失败
**原因**: 网络问题或API不可用
**解决**: 
- 检查网络连接
- 等待几分钟后重试
- 系统会自动使用模拟数据

### 2. 端口被占用
**解决**:
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# 或使用其他端口
npm run dev -- --port 3000
```

### 3. 构建失败
**解决**:
```bash
# 清除缓存
rm -rf node_modules package-lock.json

# 重新安装
npm install
npm run build
```

## 📚 学习资源

### Vue 3 文档
- 官方文档: https://v3.vuejs.org/
- Composition API: https://v3.vuejs.org/guide/composition-api-introduction.html

### ECharts 文档
- 官方文档: https://echarts.apache.org/zh/index.html

### Vite 文档
- 官方文档: https://vitejs.dev/

## 💡 扩展建议

1. **添加更多股票**: 修改 `stockService.js` 中的股票代码列表
2. **增加技术指标**: 在 `indicators.js` 中添加新指标
3. **优化选股策略**: 修改 `stockSelector.js` 中的评分逻辑
4. **添加用户功能**: 收藏股票、设置提醒等

## 📞 技术支持

如有问题，请检查:
1. 浏览器控制台错误信息
2. 网络请求是否正常
3. API是否可用

---

**⚡ 涨停先知 - 让每一次涨停都不再错过**
