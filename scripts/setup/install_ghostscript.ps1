# Install Ghostscript automatically
# This script will try multiple methods to install Ghostscript

$ErrorActionPreference = "Continue"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Ghostscript Installation Script" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
if (Test-Path "C:\Program Files\gs") {
    Write-Host "✓ Ghostscript appears to be installed already!" -ForegroundColor Green
    Write-Host "  Location: C:\Program Files\gs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Run this to add it to PATH:" -ForegroundColor Yellow
    Write-Host "  .\scripts\add_ghostscript_to_path.ps1" -ForegroundColor White
    exit 0
}

Write-Host "Attempting to install Ghostscript..." -ForegroundColor Yellow
Write-Host ""

# Method 1: Try winget (Windows Package Manager)
Write-Host "[Method 1] Trying winget..." -ForegroundColor Cyan
$wingetAvailable = Get-Command winget -ErrorAction SilentlyContinue

if ($wingetAvailable) {
    Write-Host "  Found winget, installing Ghostscript..." -ForegroundColor Gray
    try {
        winget install --id=Artifex.Ghostscript --exact --silent --accept-package-agreements --accept-source-agreements

        if (Test-Path "C:\Program Files\gs") {
            Write-Host "  ✓ Ghostscript installed successfully via winget!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "  1. Run: .\scripts\add_ghostscript_to_path.ps1" -ForegroundColor White
            Write-Host "  2. Restart your GUI" -ForegroundColor White
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
    Write-Host "  Found Chocolatey, installing Ghostscript..." -ForegroundColor Gray
    try {
        # Uninstall any broken installations first
        choco uninstall ghostscript ghostscript.app -y 2>$null

        # Install the app package which has the actual binaries
        choco install ghostscript.app -y --force

        # Wait a moment for installation to complete
        Start-Sleep -Seconds 3

        if (Test-Path "C:\Program Files\gs") {
            Write-Host "  ✓ Ghostscript installed successfully via Chocolatey!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "  1. Run: .\scripts\add_ghostscript_to_path.ps1" -ForegroundColor White
            Write-Host "  2. Restart your GUI" -ForegroundColor White
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
Write-Host "  1. Download: https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/gs10060w64.exe" -ForegroundColor White
Write-Host "  2. Run the installer (accept defaults)" -ForegroundColor White
Write-Host "  3. Run: .\scripts\add_ghostscript_to_path.ps1" -ForegroundColor White
Write-Host "  4. Restart your GUI" -ForegroundColor White
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
    Start-Process "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/gs10060w64.exe"
    Write-Host "✓ Opening download in browser..." -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Manual installation required" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan
