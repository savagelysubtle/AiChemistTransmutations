# Add Ghostscript to PATH
# This script finds Ghostscript installation and adds it to your PATH

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Adding Ghostscript to PATH" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Find Ghostscript installation
$gsBasePath = "C:\Program Files\gs"

if (-not (Test-Path $gsBasePath)) {
    Write-Host "✗ Ghostscript not found at: $gsBasePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Ghostscript first:" -ForegroundColor Yellow
    Write-Host "  Download: https://ghostscript.com/releases/gsdnld.html" -ForegroundColor Yellow
    Write-Host "  File: gs10.04.0-win64.exe" -ForegroundColor Yellow
    exit 1
}

# Find the latest version
$gsVersionDirs = Get-ChildItem $gsBasePath -Directory | Where-Object { $_.Name -like "gs*" } | Sort-Object Name -Descending

if ($gsVersionDirs.Count -eq 0) {
    Write-Host "✗ No Ghostscript version directories found in $gsBasePath" -ForegroundColor Red
    exit 1
}

$gsDir = $gsVersionDirs[0].FullName
$gsBinDir = Join-Path $gsDir "bin"
$gsExe = Join-Path $gsBinDir "gswin64c.exe"

if (-not (Test-Path $gsExe)) {
    Write-Host "✗ Ghostscript executable not found at: $gsExe" -ForegroundColor Red
    exit 1
}

Write-Host "Found Ghostscript:" -ForegroundColor Green
Write-Host "  Version Dir: $gsDir" -ForegroundColor Gray
Write-Host "  Bin Dir: $gsBinDir" -ForegroundColor Gray
Write-Host "  Executable: $gsExe" -ForegroundColor Gray
Write-Host ""

# Get current user PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check if already in PATH
if ($currentPath -like "*$gsBinDir*") {
    Write-Host "✓ Ghostscript is already in your PATH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying..." -ForegroundColor Yellow
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
    $gsLocation = Get-Command gswin64c -ErrorAction SilentlyContinue
    if ($gsLocation) {
        Write-Host "✓ gswin64c found at: $($gsLocation.Source)" -ForegroundColor Green
    } else {
        Write-Host "⚠ gswin64c not found in current session PATH" -ForegroundColor Yellow
        Write-Host "  Restart PowerShell or your IDE to refresh PATH" -ForegroundColor Yellow
    }
    exit 0
}

# Add to PATH
Write-Host "Adding Ghostscript to PATH..." -ForegroundColor Yellow

try {
    if ($currentPath) {
        $newPath = $currentPath + ";" + $gsBinDir
    } else {
        $newPath = $gsBinDir
    }

    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

    Write-Host "✓ Successfully added to PATH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Restart your applications to use the new PATH:" -ForegroundColor Yellow
    Write-Host "  1. Close and reopen PowerShell" -ForegroundColor White
    Write-Host "  2. Restart your GUI: cd gui && npm run dev" -ForegroundColor White
    Write-Host "  3. Restart your IDE (VS Code, Cursor, etc.)" -ForegroundColor White
    Write-Host ""
    Write-Host "To verify in a new PowerShell window:" -ForegroundColor Cyan
    Write-Host "  where.exe gswin64c" -ForegroundColor Gray
    Write-Host "  gswin64c --version" -ForegroundColor Gray

} catch {
    Write-Host "✗ Failed to add to PATH: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ✓ Done!" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
