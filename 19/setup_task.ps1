# 涨停雷达定时任务配置脚本
# 创建每天早上9:30自动运行的定时任务

$taskName = "涨停雷达每日扫描"
$scriptPath = "C:\Users\Administrator\Documents\trae_projects\19\auto_radar.py"
$pythonPath = "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"
$logDir = "C:\Users\Administrator\Documents\trae_projects\19\logs"

# 创建日志目录（如果不存在）
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

# 检查任务是否已存在，如果存在则删除
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "删除已存在的定时任务..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建定时任务
# 每天早上9:30运行
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At "09:30"

# 以当前用户身份运行
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# 设置任务描述
$description = "涨停雷达每日自动扫描任务 - 检测并记录当日涨停股票"

# 注册任务
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description $description -Force

Write-Host "定时任务创建成功！" -ForegroundColor Green
Write-Host "`n任务详情:" -ForegroundColor Cyan
Write-Host "  任务名称: $taskName"
Write-Host "  运行时间: 每天 09:30"
Write-Host "  执行脚本: $scriptPath"
Write-Host "  日志目录: $logDir"
Write-Host "`n可以使用以下命令查看和管理任务:" -ForegroundColor Yellow
Write-Host "  查看任务: Get-ScheduledTask -TaskName `"$taskName`""
Write-Host "  立即运行: Start-ScheduledTask -TaskName `"$taskName`""
Write-Host "  删除任务: Unregister-ScheduledTask -TaskName `"$taskName`" -Confirm:`$false"
