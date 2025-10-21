# Fix MiKTeX Configuration Issues
# Run this script in regular PowerShell (not admin)

Write-Host "Fixing MiKTeX Configuration..." -ForegroundColor Cyan

# Initialize MiKTeX databases
Write-Host "Updating file name database..." -ForegroundColor Yellow
initexmf --update-fndb
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ File name database updated" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to update file name database" -ForegroundColor Red
}

# Create font map files
Write-Host "Creating font maps..." -ForegroundColor Yellow
initexmf --mklinks
initexmf --mkmaps
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Font maps created" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create font maps" -ForegroundColor Red
}

# Update package database
Write-Host "Updating package database..." -ForegroundColor Yellow
miktex packages update-package-database
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Package database updated" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to update package database (may need internet)" -ForegroundColor Yellow
}

# Enable auto-install of missing packages
Write-Host "Configuring automatic package installation..." -ForegroundColor Yellow
initexmf --set-config-value "[MPM]AutoInstall=1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Auto-install enabled" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to enable auto-install" -ForegroundColor Red
}

Write-Host "`nMiKTeX configuration complete!" -ForegroundColor Green
Write-Host "Try running your conversion again." -ForegroundColor Cyan
