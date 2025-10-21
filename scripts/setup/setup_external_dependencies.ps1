# Setup External Dependencies for AiChemist Transmutation Codex
# This script installs and configures all external dependencies

$ErrorActionPreference = "Continue"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  AiChemist Transmutation Codex - External Setup" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  This script should be run as Administrator for best results" -ForegroundColor Yellow
    Write-Host "   Some installations may require elevated privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Function to check if a command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to install via winget
function Install-ViaWinget($packageId, $packageName) {
    Write-Host "Installing $packageName via winget..." -ForegroundColor Yellow
    try {
        winget install --id=$packageId --exact --silent --accept-package-agreements --accept-source-agreements
        return $true
    } catch {
        Write-Host "✗ winget installation failed for $packageName" -ForegroundColor Red
        return $false
    }
}

# Function to install via Chocolatey
function Install-ViaChocolatey($packageName, $packageId = $packageName) {
    Write-Host "Installing $packageName via Chocolatey..." -ForegroundColor Yellow
    try {
        choco install $packageId -y --force
        return $true
    } catch {
        Write-Host "✗ Chocolatey installation failed for $packageName" -ForegroundColor Red
        return $false
    }
}

# Check for package managers
Write-Host "Checking package managers..." -ForegroundColor Cyan
$wingetAvailable = Test-Command "winget"
$chocoAvailable = Test-Command "choco"

Write-Host "winget: $(if ($wingetAvailable) { '✅ Available' } else { '❌ Not available' })" -ForegroundColor $(if ($wingetAvailable) { 'Green' } else { 'Red' })
Write-Host "Chocolatey: $(if ($chocoAvailable) { '✅ Available' } else { '❌ Not available' })" -ForegroundColor $(if ($chocoAvailable) { 'Green' } else { 'Red' })
Write-Host ""

if (-not $wingetAvailable -and -not $chocoAvailable) {
    Write-Host "⚠️  No package managers found. Installing Chocolatey..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $chocoAvailable = Test-Command "choco"
        Write-Host "✅ Chocolatey installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to install Chocolatey: $_" -ForegroundColor Red
        Write-Host "Please install Chocolatey manually: https://chocolatey.org/install" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Define external dependencies
$dependencies = @(
    @{
        Name = "Tesseract OCR"
        WingetId = "UB-Mannheim.TesseractOCR"
        ChocolateyId = "tesseract"
        CheckPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
        Required = $true
        Description = "OCR engine for text extraction from images and PDFs"
    },
    @{
        Name = "Ghostscript"
        WingetId = "Artifex.Ghostscript"
        ChocolateyId = "ghostscript.app"
        CheckPath = "C:\Program Files\gs"
        Required = $true
        Description = "PostScript and PDF interpreter for advanced PDF operations"
    },
    @{
        Name = "MiKTeX"
        WingetId = "MiKTeX.MiKTeX"
        ChocolateyId = "miktex"
        CheckPath = "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
        Required = $false
        Description = "LaTeX distribution for high-quality document typesetting"
    },
    @{
        Name = "Pandoc"
        WingetId = "JohnMacFarlane.Pandoc"
        ChocolateyId = "pandoc"
        CheckPath = "C:\Program Files\Pandoc\pandoc.exe"
        Required = $false
        Description = "Universal document converter"
    },
    @{
        Name = "LibreOffice"
        WingetId = "TheDocumentFoundation.LibreOffice"
        ChocolateyId = "libreoffice"
        CheckPath = "C:\Program Files\LibreOffice\program\soffice.exe"
        Required = $false
        Description = "Office suite for advanced document conversions"
    },
    @{
        Name = "Node.js"
        WingetId = "OpenJS.NodeJS"
        ChocolateyId = "nodejs"
        CheckPath = "C:\Program Files\nodejs\node.exe"
        Required = $true
        Description = "JavaScript runtime for GUI development"
    },
    @{
        Name = "Python"
        WingetId = "Python.Python.3.13"
        ChocolateyId = "python"
        CheckPath = "C:\Program Files\Python313\python.exe"
        Required = $true
        Description = "Python runtime for backend converters"
    }
)

# Install dependencies
Write-Host "Installing external dependencies..." -ForegroundColor Cyan
Write-Host ""

$installed = 0
$failed = 0
$skipped = 0

foreach ($dep in $dependencies) {
    Write-Host "Processing: $($dep.Name)" -ForegroundColor Yellow
    Write-Host "  Description: $($dep.Description)" -ForegroundColor Gray

    # Check if already installed
    if (Test-Path $dep.CheckPath) {
        Write-Host "  ✅ Already installed at: $($dep.CheckPath)" -ForegroundColor Green
        $skipped++
        continue
    }

    # Try installation
    $success = $false

    if ($wingetAvailable) {
        $success = Install-ViaWinget $dep.WingetId $dep.Name
    }

    if (-not $success -and $chocoAvailable) {
        $success = Install-ViaChocolatey $dep.Name $dep.ChocolateyId
    }

    if ($success) {
        Write-Host "  ✅ $($dep.Name) installed successfully!" -ForegroundColor Green
        $installed++
    } else {
        Write-Host "  ❌ Failed to install $($dep.Name)" -ForegroundColor Red
        if ($dep.Required) {
            Write-Host "    ⚠️  This is a REQUIRED dependency!" -ForegroundColor Yellow
        }
        $failed++
    }

    Write-Host ""
}

# Add Tesseract to PATH
Write-Host "Configuring Tesseract OCR..." -ForegroundColor Cyan
if (Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe") {
    $tesseractBinDir = "C:\Program Files\Tesseract-OCR"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($currentPath -notlike "*$tesseractBinDir*") {
        try {
            $newPath = if ($currentPath) { "$currentPath;$tesseractBinDir" } else { $tesseractBinDir }
            [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
            Write-Host "✅ Added Tesseract to PATH" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Failed to add Tesseract to PATH: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✅ Tesseract already in PATH" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Tesseract not found, skipping PATH configuration" -ForegroundColor Yellow
}

# Add Ghostscript to PATH
Write-Host "Configuring Ghostscript..." -ForegroundColor Cyan
if (Test-Path "C:\Program Files\gs") {
    $gsVersionDirs = Get-ChildItem "C:\Program Files\gs" -Directory | Where-Object { $_.Name -like "gs*" } | Sort-Object Name -Descending
    if ($gsVersionDirs.Count -gt 0) {
        $gsBinDir = Join-Path $gsVersionDirs[0].FullName "bin"
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

        if ($currentPath -notlike "*$gsBinDir*") {
            try {
                $newPath = if ($currentPath) { "$currentPath;$gsBinDir" } else { $gsBinDir }
                [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
                Write-Host "✅ Added Ghostscript to PATH" -ForegroundColor Green
            } catch {
                Write-Host "⚠️  Failed to add Ghostscript to PATH: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✅ Ghostscript already in PATH" -ForegroundColor Green
        }
    }
} else {
    Write-Host "⚠️  Ghostscript not found, skipping PATH configuration" -ForegroundColor Yellow
}

Write-Host ""

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
try {
    if (Test-Command "uv") {
        Write-Host "Using UV package manager..." -ForegroundColor Yellow
        Set-Location $PSScriptRoot\..
        uv sync --all-groups
        Write-Host "✅ Python dependencies installed!" -ForegroundColor Green
    } elseif (Test-Command "pip") {
        Write-Host "Using pip package manager..." -ForegroundColor Yellow
        Set-Location $PSScriptRoot\..
        pip install -e ".[dev]"
        Write-Host "✅ Python dependencies installed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No Python package manager found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to install Python dependencies: $_" -ForegroundColor Red
}

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
try {
    if (Test-Path "gui\package.json") {
        Set-Location "gui"
        if (Test-Command "npm") {
            npm install
            Write-Host "✅ Node.js dependencies installed!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  npm not found" -ForegroundColor Yellow
        }
        Set-Location $PSScriptRoot\..
    } else {
        Write-Host "⚠️  GUI package.json not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to install Node.js dependencies: $_" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Installation Summary" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "✅ Installed: $installed" -ForegroundColor Green
Write-Host "⏭️  Skipped: $skipped" -ForegroundColor Yellow
Write-Host "❌ Failed: $failed" -ForegroundColor Red
Write-Host ""

if ($failed -gt 0) {
    Write-Host "⚠️  Some dependencies failed to install!" -ForegroundColor Yellow
    Write-Host "   Check the output above for details" -ForegroundColor Yellow
    Write-Host "   You may need to install them manually" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your terminal/IDE to refresh PATH" -ForegroundColor White
Write-Host "2. Run: python tests/check_deps.py" -ForegroundColor White
Write-Host "3. Run: python tests/check_env.py" -ForegroundColor White
Write-Host "4. Start GUI: cd gui && npm run dev" -ForegroundColor White
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 All external dependencies configured successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Setup completed with some issues. Check failed installations above." -ForegroundColor Yellow
}

Write-Host "=====================================================" -ForegroundColor Cyan
