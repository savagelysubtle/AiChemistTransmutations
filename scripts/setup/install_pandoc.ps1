# Install Pandoc automatically
# This script will try multiple methods to install Pandoc

$ErrorActionPreference = "Continue"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Pandoc Installation Script" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$pandocLocations = @(
    "C:\Program Files\Pandoc\pandoc.exe",
    "C:\Program Files (x86)\Pandoc\pandoc.exe",
    "$env:LOCALAPPDATA\Pandoc\pandoc.exe"
)

$existingPandoc = $pandocLocations | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($existingPandoc) {
    Write-Host "✓ Pandoc appears to be installed already!" -ForegroundColor Green
    Write-Host "  Location: $existingPandoc" -ForegroundColor Gray

    # Test it
    try {
        $version = & $existingPandoc --version | Select-Object -First 1
        Write-Host "  Version: $version" -ForegroundColor Gray
    } catch {
        Write-Host "  Warning: Could not get version" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "If you need to update or reinstall, use:" -ForegroundColor Yellow
    Write-Host "  winget upgrade --id=JohnMacFarlane.Pandoc" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor Yellow
    Write-Host "  choco upgrade pandoc" -ForegroundColor White
    exit 0
}

Write-Host "Attempting to install Pandoc..." -ForegroundColor Yellow
Write-Host ""

# Method 1: Try winget (Windows Package Manager)
Write-Host "[Method 1] Trying winget..." -ForegroundColor Cyan
$wingetAvailable = Get-Command winget -ErrorAction SilentlyContinue

if ($wingetAvailable) {
    Write-Host "  Found winget, installing Pandoc..." -ForegroundColor Gray
    try {
        winget install --id=JohnMacFarlane.Pandoc --exact --silent --accept-package-agreements --accept-source-agreements

        # Wait a moment for installation to complete
        Start-Sleep -Seconds 3

        # Check if installed
        $existingPandoc = $pandocLocations | Where-Object { Test-Path $_ } | Select-Object -First 1
        if ($existingPandoc) {
            Write-Host "  ✓ Pandoc installed successfully via winget!" -ForegroundColor Green
            Write-Host "  Location: $existingPandoc" -ForegroundColor Gray

            # Test it
            try {
                $version = & $existingPandoc --version | Select-Object -First 1
                Write-Host "  Version: $version" -ForegroundColor Gray
            } catch {}

            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "  1. Restart your GUI" -ForegroundColor White
            Write-Host "  2. Try MD to DOCX conversion" -ForegroundColor White
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
    Write-Host "  Found Chocolatey, installing Pandoc..." -ForegroundColor Gray
    try {
        choco install pandoc -y --force

        # Wait a moment for installation to complete
        Start-Sleep -Seconds 3

        # Check if installed
        $existingPandoc = $pandocLocations | Where-Object { Test-Path $_ } | Select-Object -First 1
        if ($existingPandoc) {
            Write-Host "  ✓ Pandoc installed successfully via Chocolatey!" -ForegroundColor Green
            Write-Host "  Location: $existingPandoc" -ForegroundColor Gray

            # Test it
            try {
                $version = & $existingPandoc --version | Select-Object -First 1
                Write-Host "  Version: $version" -ForegroundColor Gray
            } catch {}

            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "  1. Restart your GUI" -ForegroundColor White
            Write-Host "  2. Try MD to DOCX conversion" -ForegroundColor White
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
Write-Host "  1. Download: https://github.com/jgm/pandoc/releases/latest/download/pandoc-3.1.11.1-windows-x86_64.msi" -ForegroundColor White
Write-Host "  2. Run the MSI installer (accept defaults)" -ForegroundColor White
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
    Start-Process "https://pandoc.org/installing.html"
    Write-Host "✓ Opening download page in browser..." -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Manual installation required" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan
