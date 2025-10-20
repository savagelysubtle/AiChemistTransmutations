# Install MiKTeX automatically
# This script will try multiple methods to install MiKTeX

$ErrorActionPreference = "Continue"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  MiKTeX Installation Script" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$miktexLocations = @(
    "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
    "C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe",
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
)

$existingMiktex = $miktexLocations | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($existingMiktex) {
    Write-Host "✓ MiKTeX appears to be installed already!" -ForegroundColor Green
    Write-Host "  Location: $existingMiktex" -ForegroundColor Gray

    # Test it
    try {
        $parentDir = Split-Path $existingMiktex
        $version = & "$parentDir\miktex.exe" --version 2>$null | Select-Object -First 1
        Write-Host "  Version: $version" -ForegroundColor Gray
    } catch {
        Write-Host "  Warning: Could not get version" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "If you need to update or reinstall, use:" -ForegroundColor Yellow
    Write-Host "  winget upgrade --id=MiKTeX.MiKTeX" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor Yellow
    Write-Host "  choco upgrade miktex" -ForegroundColor White
    exit 0
}

Write-Host "Attempting to install MiKTeX..." -ForegroundColor Yellow
Write-Host ""

# Method 1: Try winget (Windows Package Manager)
Write-Host "[Method 1] Trying winget..." -ForegroundColor Cyan
$wingetAvailable = Get-Command winget -ErrorAction SilentlyContinue

if ($wingetAvailable) {
    Write-Host "  Found winget, installing MiKTeX..." -ForegroundColor Gray
    try {
        winget install --id=MiKTeX.MiKTeX --exact --silent --accept-package-agreements --accept-source-agreements

        # Wait a moment for installation to complete
        Start-Sleep -Seconds 5

        # Check if installed
        $existingMiktex = $miktexLocations | Where-Object { Test-Path $_ } | Select-Object -First 1
        if ($existingMiktex) {
            Write-Host "  ✓ MiKTeX installed successfully via winget!" -ForegroundColor Green
            Write-Host "  Location: $existingMiktex" -ForegroundColor Gray

            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "  1. Restart your GUI" -ForegroundColor White
            Write-Host "  2. MiKTeX will auto-install packages on first use" -ForegroundColor White
            exit 0
        }
    } catch {
        Write-Host "  ✗ winget installation failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ✗ winget not available" -ForegroundColor Red
}

Write-Host ""

# Method 2: Try Chocolatey
Write-Host "[Method 2] Trying Chocolatey..." -ForegroundColor Cyan
$chocoAvailable = Get-Command choco -ErrorAction SilentlyContinue

if ($chocoAvailable) {
    Write-Host "  Found Chocolatey, installing MiKTeX..." -ForegroundColor Gray
    try {
        choco install miktex -y --force

        # Wait a moment for installation to complete
        Start-Sleep -Seconds 5

        # Check if installed
        $existingMiktex = $miktexLocations | Where-Object { Test-Path $_ } | Select-Object -First 1
        if ($existingMiktex) {
            Write-Host "  ✓ MiKTeX installed successfully via Chocolatey!" -ForegroundColor Green
            Write-Host "  Location: $existingMiktex" -ForegroundColor Gray

            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "  1. Restart your GUI" -ForegroundColor White
            Write-Host "  2. MiKTeX will auto-install packages on first use" -ForegroundColor White
            exit 0
        }
    } catch {
        Write-Host "  ✗ Chocolatey installation failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ✗ Chocolatey not available" -ForegroundColor Red
}

Write-Host ""

# Method 3: Manual download (fallback)
Write-Host "[Method 3] Manual Installation Required" -ForegroundColor Yellow
Write-Host ""
Write-Host "Automatic installation failed. Please install manually:" -ForegroundColor White
Write-Host ""
Write-Host "Option A - Direct Download (Recommended):" -ForegroundColor Cyan
Write-Host "  1. Download: https://miktex.org/download" -ForegroundColor White
Write-Host "  2. Run the installer (accept defaults)" -ForegroundColor White
Write-Host "  3. Restart your GUI" -ForegroundColor White
Write-Host ""
Write-Host "Option B - Install Chocolatey first, then retry:" -ForegroundColor Cyan
Write-Host "  1. Install Chocolatey: https://chocolatey.org/install" -ForegroundColor White
Write-Host "  2. Run this script again" -ForegroundColor White
Write-Host ""
Write-Host "Option C - Install winget (if on older Windows):" -ForegroundColor Cyan
Write-Host "  1. Install App Installer from Microsoft Store" -ForegroundColor White
Write-Host "  2. Run this script again" -ForegroundColor White
Write-Host ""

# Try to open the download page
$openBrowser = Read-Host "Open download page in browser? (y/n)"
if ($openBrowser -eq "y") {
    Start-Process "https://miktex.org/download"
    Write-Host "✓ Opening download page in browser..." -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Manual installation required" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan




