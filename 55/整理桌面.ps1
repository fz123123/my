# Desktop Organizer Script - Move all files to one folder
$desktopPath = [Environment]::GetFolderPath("Desktop")
$targetFolder = Join-Path $desktopPath "Desktop_Files"

# Create target folder
if (-not (Test-Path $targetFolder)) {
    New-Item -ItemType Directory -Path $targetFolder | Out-Null
    Write-Host "Created folder: $targetFolder"
}

Write-Host "`nMoving desktop files to $targetFolder ..."

# Get all items on desktop (exclude target folder itself)
$items = Get-ChildItem -Path $desktopPath | Where-Object { $_.Name -ne "Desktop_Files" }

foreach ($item in $items) {
    try {
        Move-Item -Path $item.FullName -Destination $targetFolder -Force
        Write-Host "Moved: $($item.Name)"
    }
    catch {
        Write-Host "Cannot move: $($item.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nDesktop organized! All files moved to 'Desktop_Files' folder."
