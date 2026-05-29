# 涨停雷达定时任务使用说明

## 定时任务配置

✅ **任务名称**: LimitUpRadarDaily  
✅ **运行时间**: 每天 09:30（工作日）  
✅ **执行脚本**: auto_radar.py  
✅ **日志输出**: logs/radar_YYYYMMDD.log  

## 功能说明

定时任务会自动执行以下操作：
1. 从新浪财经API获取股票数据
2. 检测涨停股票（涨幅 ≥ 9.8%）
3. 分析涨停股票的风险等级
4. 生成详细的扫描报告到日志文件

## 查看日志

日志文件保存在 `logs` 目录下，每天一个文件：
- 文件命名格式: `radar_20260525.log`
- 可使用命令查看: `Get-Content logs/radar_*.log`

## 管理命令

### 查看任务状态
```powershell
schtasks /Query /TN "LimitUpRadarDaily"
```

### 立即运行任务
```powershell
schtasks /Run /TN "LimitUpRadarDaily"
```

### 删除任务
```powershell
schtasks /Delete /TN "LimitUpRadarDaily" /F
```

### 修改运行时间
```powershell
# 修改为每天下午3点运行
schtasks /Change /TN "LimitUpRadarDaily" /ST 15:00
```

### 修改执行频率
```powershell
# 修改为每周一运行
schtasks /Change /TN "LimitUpRadarDaily" /SC WEEKLY /D MON
```

## 手动测试

### 测试自动扫描脚本
```powershell
python auto_radar.py
```

### 测试交互式界面
```powershell
python main.py
```

## 日志示例

扫描完成后，日志会包含：
- 扫描时间
- 检测到的涨停股票数量
- 涨停股票详细列表（代码、名称、价格、涨幅、换手率、风险等级）
- 风险分布统计
