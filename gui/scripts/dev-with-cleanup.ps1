# =============================================================================
# Electron Development Watcher with Cleanup
# =============================================================================
# This script ensures all watchers stop when Electron closes
# =============================================================================

param(
    [string]$Command = "dev:fullstack"
)

$ErrorActionPreference = "Stop"

# Get the GUI directory
$GuiDir = Split-Path -Parent $PSScriptRoot
Set-Location $GuiDir

Write-Host "🚀 Starting development environment with automatic cleanup..." -ForegroundColor Cyan
Write-Host ""

# Function to cleanup processes
function Stop-AllWatchers {
    Write-Host ""
    Write-Host "🛑 Stopping all watchers..." -ForegroundColor Yellow

    # Stop nodemon processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*nodemon*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue

    # Stop vite processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*vite*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue

    # Stop concurrently processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*concurrently*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue

    Write-Host "✅ All watchers stopped" -ForegroundColor Green
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action {
    Stop-AllWatchers
} | Out-Null

# Handle Ctrl+C
[Console]::TreatControlCAsInput = $false
$null = Register-ObjectEvent -InputObject ([System.Console]) -EventName CancelKeyPress -Action {
    Write-Host ""
    Write-Host "🛑 Interrupted by user" -ForegroundColor Yellow
    Stop-AllWatchers
    exit 0
}

# Start the development command
Write-Host "Running: bun run $Command" -ForegroundColor Cyan
Write-Host ""

try {
    $process = Start-Process -FilePath "bun" -ArgumentList "run", $Command -NoNewWindow -PassThru -Wait

    # When process exits, cleanup
    Stop-AllWatchers

    exit $process.ExitCode
}
catch {
    Write-Host "❌ Error starting development environment: $_" -ForegroundColor Red
    Stop-AllWatchers
    exit 1
}



















