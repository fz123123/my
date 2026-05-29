$ErrorActionPreference = "Stop"

# 配置
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "恐慌盘扫描.lnk"
$ScriptPath = "C:\Users\Administrator\Documents\trae_projects\33\恐慌盘扫描.bat"

# 检查目标文件是否存在
if (-not (Test-Path $ScriptPath)) {
    Write-Host "错误: 找不到脚本文件 $ScriptPath" -ForegroundColor Red
    exit 1
}

# 创建快捷方式对象
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)

# 配置快捷方式
$Shortcut.TargetPath = $ScriptPath
$Shortcut.WorkingDirectory = "C:\Users\Administrator\Documents\trae_projects\33"
$Shortcut.Description = "恐慌盘自动扫描工具 - 每日开盘前运行"

# 保存
$Shortcut.Save()

if (Test-Path $ShortcutPath) {
    Write-Host "成功创建桌面快捷方式！" -ForegroundColor Green
    Write-Host "位置: $ShortcutPath" -ForegroundColor Cyan
} else {
    Write-Host "创建失败" -ForegroundColor Red
}
