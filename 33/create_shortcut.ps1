$ErrorActionPreference = "Stop"

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "panic_scanner.lnk"

# 使用8.3短文件名格式访问中文路径
Add-Type -AssemblyName Microsoft.VisualBasic
$ShortPath = [Microsoft.VisualBasic.FileIO.FileSystem]::GetFileInfo("C:\Users\Administrator\Documents\trae_projects\33\恐慌盘扫描.bat").FullName

if (-not (Test-Path $ShortPath)) {
    Write-Host "ERROR: Script file not found at $ShortPath"
    exit 1
}

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)

$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c ""$ShortPath"""
$Shortcut.WorkingDirectory = "C:\Users\Administrator\Documents\trae_projects\33"
$Shortcut.Description = "Panic Stock Scanner"

$Shortcut.Save()

if (Test-Path $ShortcutPath) {
    Write-Host "SUCCESS: Desktop shortcut created"
    Write-Host "Location: $ShortcutPath"
} else {
    Write-Host "ERROR: Failed to create shortcut"
}
