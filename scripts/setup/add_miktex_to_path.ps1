# Add MiKTeX to System PATH
# Run this script as Administrator

Write-Host "Adding MiKTeX to System PATH..." -ForegroundColor Cyan

# Common MiKTeX installation paths
$possiblePaths = @(
    "C:\Program Files\MiKTeX\miktex\bin\x64",
    "C:\Program Files (x86)\MiKTeX\miktex\bin\x64",
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
)

$miktexPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\pdflatex.exe") {
        $miktexPath = $path
        Write-Host "Found MiKTeX at: $path" -ForegroundColor Green
        break
    }
}

if (-not $miktexPath) {
    Write-Host "ERROR: MiKTeX not found in common locations." -ForegroundColor Red
    Write-Host "Please install MiKTeX from: https://miktex.org/download" -ForegroundColor Yellow
    exit 1
}

# Get current system PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)

# Check if already in PATH
if ($currentPath -like "*$miktexPath*") {
    Write-Host "MiKTeX is already in System PATH" -ForegroundColor Yellow
    exit 0
}

# Add to PATH
$newPath = "$currentPath;$miktexPath"
[Environment]::SetEnvironmentVariable("Path", $newPath, [System.EnvironmentVariableTarget]::Machine)

Write-Host "Successfully added MiKTeX to System PATH" -ForegroundColor Green
Write-Host "Please restart your terminal/application for changes to take effect" -ForegroundColor Cyan

# Verify
$updatedPath = [Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
if ($updatedPath -like "*$miktexPath*") {
    Write-Host "Verification: MiKTeX path confirmed in System PATH" -ForegroundColor Green
} else {
    Write-Host "WARNING: Could not verify PATH update" -ForegroundColor Red
}
