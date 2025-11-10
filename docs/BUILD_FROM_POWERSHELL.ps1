<#
.SYNOPSIS
    Build Electron Installer WITHOUT Cursor/VS Code running

.DESCRIPTION
    This script is designed to be run from a standalone PowerShell window,
    NOT from within Cursor/VS Code terminal. Cursor's file watcher locks
    the app.asar file and prevents electron-builder from working.

.NOTES
    CRITICAL: Close Cursor/VS Code BEFORE running this script!

    Run from PowerShell (NOT Cursor terminal):
    1. Close Cursor completely
    2. Open PowerShell as Administrator
    3. cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
    4. .\BUILD_FROM_POWERSHELL.ps1
#>

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  BUILD FROM STANDALONE POWERSHELL" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Cursor is running
$cursorProcesses = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
if ($cursorProcesses) {
    Write-Host "❌ ERROR: Cursor is still running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Cursor's file watcher will lock the app.asar file." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Close Cursor completely" -ForegroundColor Yellow
    Write-Host "  2. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✓ Cursor is not running - Good!" -ForegroundColor Green
Write-Host ""

# Run the ultimate build script
Write-Host "Running build script..." -ForegroundColor Cyan
& .\scripts\build-ultimate.ps1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESS!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installer location: release\1.0.3\" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "If file locking persists, try:" -ForegroundColor Yellow
    Write-Host "  1. Restart your computer" -ForegroundColor Yellow
    Write-Host "  2. Add Windows Defender exclusions (requires admin):" -ForegroundColor Yellow
    Write-Host "     .\scripts\add-defender-exclusions.ps1" -ForegroundColor Yellow
    Write-Host ""
}


