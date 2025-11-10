<#
.SYNOPSIS
    Build Production Installer for AiChemist Transmutation Codex

.DESCRIPTION
    Simple one-command build script that creates the production installer
    you can sell to customers. Handles all prerequisites and build steps.

.NOTES
    ⚠️ IMPORTANT: Close Cursor/VS Code before running this script!
    
    Run from PowerShell (NOT Cursor terminal):
    1. Save all your work in Cursor
    2. Close Cursor completely
    3. Open PowerShell
    4. cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
    5. .\BUILD_INSTALLER.ps1

.EXAMPLE
    .\BUILD_INSTALLER.ps1
    
    Builds the production installer with all default settings.

.EXAMPLE
    .\BUILD_INSTALLER.ps1 -SkipClean
    
    Builds without cleaning old files (faster for testing).
#>

[CmdletBinding()]
param(
    [switch]$SkipClean = $false,
    [switch]$SkipDependencies = $false
)

$ErrorActionPreference = "Stop"

# ASCII Art Banner
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  AiChemist Transmutation Codex - Production Build" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Cursor/VS Code is running
Write-Host "[1/6] Checking for Cursor/VS Code..." -ForegroundColor Yellow
$cursorProcesses = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
$vscodeProcesses = Get-Process -Name "Code" -ErrorAction SilentlyContinue

if ($cursorProcesses -or $vscodeProcesses) {
    Write-Host ""
    Write-Host "❌ ERROR: Cursor or VS Code is still running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "The IDE's file watcher will lock files during the build." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Save all your work" -ForegroundColor Yellow
    Write-Host "  2. Close Cursor/VS Code completely" -ForegroundColor Yellow
    Write-Host "  3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "  ✓ No IDE detected - Good!" -ForegroundColor Green
Write-Host ""

# Terminate any running app instances
Write-Host "[2/6] Terminating running app instances..." -ForegroundColor Yellow
$processNames = @(
    "AiChemist Transmutation Codex",
    "electron"
)

foreach ($processName in $processNames) {
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue | 
        Where-Object { $_.MainModule.FileName -notlike "*\Cursor\*" }
    
    if ($processes) {
        $processes | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Terminated: $processName" -ForegroundColor Green
    }
}

Start-Sleep -Seconds 2
Write-Host "  ✓ All app instances terminated" -ForegroundColor Green
Write-Host ""

# Clean old build files
if (-not $SkipClean) {
    Write-Host "[3/6] Cleaning old build files..." -ForegroundColor Yellow
    
    $dirsToClean = @("release", "dist", "dist-electron")
    foreach ($dir in $dirsToClean) {
        if (Test-Path $dir) {
            try {
                Remove-Item -Path $dir -Recurse -Force -ErrorAction Stop
                Write-Host "  ✓ Removed: $dir/" -ForegroundColor Green
            } catch {
                Write-Host "  ⚠ Could not remove $dir/ (may be in use)" -ForegroundColor Yellow
            }
        }
    }
    Write-Host "  ✓ Cleanup complete" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[3/6] Skipping cleanup (--SkipClean)" -ForegroundColor Yellow
    Write-Host ""
}

# Install/update dependencies
if (-not $SkipDependencies) {
    Write-Host "[4/6] Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ npm install failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[4/6] Skipping dependencies (--SkipDependencies)" -ForegroundColor Yellow
    Write-Host ""
}

# Build the application
Write-Host "[5/6] Building application..." -ForegroundColor Yellow
Write-Host ""

npm run electron:build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  • File locking - Make sure Cursor/VS Code is completely closed" -ForegroundColor Yellow
    Write-Host "  • Windows Defender - Run: .\build\scripts\add-defender-exclusions.ps1" -ForegroundColor Yellow
    Write-Host "  • Running instances - Check Task Manager for electron.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See BUILD.md for detailed troubleshooting." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "  ✓ Build successful!" -ForegroundColor Green
Write-Host ""

# Find the installer
Write-Host "[6/6] Locating installer..." -ForegroundColor Yellow

$version = (Get-Content package.json | ConvertFrom-Json).version
$installerPath = "release\$version\AiChemist Transmutation Codex Setup $version.exe"

if (Test-Path $installerPath) {
    $fileSize = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  BUILD COMPLETE - PRODUCTION INSTALLER READY!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installer Location:" -ForegroundColor Cyan
    Write-Host "  $installerPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Installer Size:" -ForegroundColor Cyan
    Write-Host "  $fileSize MB" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the installer on a clean machine" -ForegroundColor White
    Write-Host "  2. Verify all features work correctly" -ForegroundColor White
    Write-Host "  3. Upload to your distribution platform" -ForegroundColor White
    Write-Host ""
    Write-Host "Distribution:" -ForegroundColor Cyan
    Write-Host "  • Gumroad: Upload to your product" -ForegroundColor White
    Write-Host "  • Website: Direct download link" -ForegroundColor White
    Write-Host "  • License: Requires valid license key to activate" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "  ⚠ Could not locate installer file" -ForegroundColor Yellow
    Write-Host "  Expected at: $installerPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check the release/ directory manually." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

