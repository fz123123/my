$ErrorActionPreference = "Stop"

$SourceFile = "C:\Users\Administrator\Documents\trae_projects\33\恐慌盘扫描.bat"
$DesktopFile = "$env:USERPROFILE\Desktop\恐慌盘扫描.bat"

if (-not (Test-Path $SourceFile)) {
    Write-Host "ERROR: Source file not found"
    exit 1
}

try {
    Copy-Item -Path $SourceFile -Destination $DesktopFile -Force
    Write-Host "SUCCESS: File copied to desktop"
    Write-Host "Location: $DesktopFile"
} catch {
    Write-Host "ERROR: Failed to copy - $_"
    Write-Host ""
    Write-Host "Please manually copy the file:"
    Write-Host "Source: $SourceFile"
}
