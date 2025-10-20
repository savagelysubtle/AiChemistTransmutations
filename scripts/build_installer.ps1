# Build Installer Script for AiChemist Transmutation Codex
# This script automates the process of building a production installer with bundled Tesseract

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = "dist",
    [switch]$SkipTests = $false,
    [switch]$SkipSign = $true
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  AiChemist Transmutation Codex Installer Builder" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean previous builds
Write-Host "[1/7] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
    Write-Host "  ✓ Removed build directory" -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Path "dist" -Recurse -Force
    Write-Host "  ✓ Removed dist directory" -ForegroundColor Green
}

# Create build directories
New-Item -ItemType Directory -Path "build/resources/tesseract" -Force | Out-Null
New-Item -ItemType Directory -Path "build/resources/ghostscript" -Force | Out-Null
New-Item -ItemType Directory -Path "build/resources/pandoc" -Force | Out-Null
New-Item -ItemType Directory -Path "build/installers" -Force | Out-Null
Write-Host "  ✓ Created build directories" -ForegroundColor Green

# Download Ghostscript installer if not present
Write-Host "`n  Checking for Ghostscript installer..." -ForegroundColor Yellow
$gsInstallerPath = "build\installers\gs10.04.0-win64.exe"
$gsInstallerUrl = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10040/gs10.04.0-win64.exe"

if (-not (Test-Path $gsInstallerPath)) {
    Write-Host "  Downloading Ghostscript installer (~40 MB)..." -ForegroundColor Yellow
    try {
        # Use .NET WebClient for better progress feedback
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($gsInstallerUrl, $gsInstallerPath)
        Write-Host "  ✓ Downloaded Ghostscript installer" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to download Ghostscript installer: $_" -ForegroundColor Red
        Write-Host "  Please download manually from: $gsInstallerUrl" -ForegroundColor Yellow
        Write-Host "  Save to: $gsInstallerPath" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "  ✓ Ghostscript installer already present" -ForegroundColor Green
}

# Download Pandoc installer if not present
Write-Host "`n  Checking for Pandoc installer..." -ForegroundColor Yellow
$pandocInstallerPath = "build\installers\pandoc-3.1.11.1-windows-x86_64.msi"
$pandocInstallerUrl = "https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-windows-x86_64.msi"

if (-not (Test-Path $pandocInstallerPath)) {
    Write-Host "  Downloading Pandoc installer (~30 MB)..." -ForegroundColor Yellow
    try {
        # Use .NET WebClient for better progress feedback
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($pandocInstallerUrl, $pandocInstallerPath)
        Write-Host "  ✓ Downloaded Pandoc installer" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to download Pandoc installer: $_" -ForegroundColor Red
        Write-Host "  Please download manually from: $pandocInstallerUrl" -ForegroundColor Yellow
        Write-Host "  Save to: $pandocInstallerPath" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "  ✓ Pandoc installer already present" -ForegroundColor Green
}

# Download MiKTeX installer if not present
Write-Host "`n  Checking for MiKTeX installer..." -ForegroundColor Yellow
$miktexInstallerPath = "build\installers\miktexsetup-x64.exe"
$miktexInstallerUrl = "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/miktexsetup-5.9-x64.exe"

if (-not (Test-Path $miktexInstallerPath)) {
    Write-Host "  Downloading MiKTeX installer (~10 MB)..." -ForegroundColor Yellow
    try {
        # Use .NET WebClient for better progress feedback
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($miktexInstallerUrl, $miktexInstallerPath)
        Write-Host "  ✓ Downloaded MiKTeX installer" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to download MiKTeX installer: $_" -ForegroundColor Red
        Write-Host "  Please download manually from: https://miktex.org/download" -ForegroundColor Yellow
        Write-Host "  Save to: $miktexInstallerPath" -ForegroundColor Yellow
        Write-Host "  Note: MiKTeX is optional for advanced PDF generation" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  ✓ MiKTeX installer already present" -ForegroundColor Green
}

# Step 2: Run tests (optional)
if (-not $SkipTests) {
    Write-Host "`n[2/7] Running tests..." -ForegroundColor Yellow
    try {
        uv run pytest tests/unit/ -v --tb=short
        Write-Host "  ✓ Tests passed" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Tests failed" -ForegroundColor Red
        Write-Host "  Continue anyway? (y/n): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        if ($response -ne "y") {
            exit 1
        }
    }
}
else {
    Write-Host "`n[2/7] Skipping tests..." -ForegroundColor Yellow
}

# Step 3: Copy Tesseract files
Write-Host "`n[3/7] Copying Tesseract files..." -ForegroundColor Yellow
$tesseractSource = "C:\Program Files\Tesseract-OCR"
$tesseractTargetDir = "build\resources\tesseract"

if (Test-Path $tesseractSource) {
    # Copy essential files
    Copy-Item "$tesseractSource\tesseract.exe" -Destination $tesseractTargetDir
    Write-Host "  ✓ Copied tesseract.exe" -ForegroundColor Green

    # Copy DLLs
    Get-ChildItem "$tesseractSource\*.dll" | Copy-Item -Destination $tesseractTargetDir
    Write-Host "  ✓ Copied Tesseract DLL files" -ForegroundColor Green

    # Copy tessdata (language packs)
    Copy-Item "$tesseractSource\tessdata" -Destination $tesseractTargetDir -Recurse
    Write-Host "  ✓ Copied tessdata directory" -ForegroundColor Green

    # Copy license files
    if (Test-Path "$tesseractSource\LICENSE") {
        Copy-Item "$tesseractSource\LICENSE" -Destination "$tesseractTargetDir\LICENSE"
        Write-Host "  ✓ Copied Tesseract LICENSE" -ForegroundColor Green
    }

    # Calculate size
    $tesseractSize = (Get-ChildItem -Path $tesseractTargetDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  ℹ Tesseract bundle size: $($tesseractSize.ToString('F2')) MB" -ForegroundColor Cyan
}
else {
    Write-Host "  ✗ Tesseract not found at $tesseractSource" -ForegroundColor Red
    Write-Host "  Please install Tesseract: choco install tesseract" -ForegroundColor Yellow
    exit 1
}

# Copy Ghostscript files
Write-Host "`n  Copying Ghostscript files..." -ForegroundColor Yellow
$ghostscriptSource = Get-ChildItem "C:\Program Files\gs" -Directory | Sort-Object Name -Descending | Select-Object -First 1
$ghostscriptTargetDir = "build\resources\ghostscript"
New-Item -ItemType Directory -Path $ghostscriptTargetDir -Force | Out-Null

if ($ghostscriptSource -and (Test-Path $ghostscriptSource.FullName)) {
    $gsExePath = Join-Path $ghostscriptSource.FullName "bin"

    # Copy Ghostscript executables and DLLs
    if (Test-Path $gsExePath) {
        Copy-Item "$gsExePath\*" -Destination $ghostscriptTargetDir -Recurse -Force
        Write-Host "  ✓ Copied Ghostscript executables and DLLs" -ForegroundColor Green

        # Copy license
        $gsLicense = Join-Path $ghostscriptSource.FullName "LICENSE"
        if (Test-Path $gsLicense) {
            Copy-Item $gsLicense -Destination "$ghostscriptTargetDir\LICENSE"
            Write-Host "  ✓ Copied Ghostscript LICENSE" -ForegroundColor Green
        }

        # Calculate size
        $ghostscriptSize = (Get-ChildItem -Path $ghostscriptTargetDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  ℹ Ghostscript bundle size: $($ghostscriptSize.ToString('F2')) MB" -ForegroundColor Cyan
    }
    else {
        Write-Host "  ✗ Ghostscript bin directory not found" -ForegroundColor Red
        Write-Host "  Please install Ghostscript: choco install ghostscript" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "  ✗ Ghostscript not found in C:\Program Files\gs" -ForegroundColor Red
    Write-Host "  Please install Ghostscript: choco install ghostscript" -ForegroundColor Yellow
    exit 1
}

# Copy Pandoc files
Write-Host "`n  Copying Pandoc files..." -ForegroundColor Yellow
$pandocLocations = @(
    "C:\Program Files\Pandoc",
    "C:\Program Files (x86)\Pandoc",
    "$env:LOCALAPPDATA\Pandoc"
)

$pandocSource = $pandocLocations | Where-Object { Test-Path $_ } | Select-Object -First 1
$pandocTargetDir = "build\resources\pandoc"
New-Item -ItemType Directory -Path $pandocTargetDir -Force | Out-Null

if ($pandocSource) {
    # Copy Pandoc executable
    if (Test-Path "$pandocSource\pandoc.exe") {
        Copy-Item "$pandocSource\pandoc.exe" -Destination $pandocTargetDir
        Write-Host "  ✓ Copied pandoc.exe" -ForegroundColor Green
    }

    # Copy any DLLs if present
    Get-ChildItem "$pandocSource\*.dll" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination $pandocTargetDir
    }

    # Copy data directory if it exists
    if (Test-Path "$pandocSource\data") {
        Copy-Item "$pandocSource\data" -Destination $pandocTargetDir -Recurse -Force
        Write-Host "  ✓ Copied Pandoc data directory" -ForegroundColor Green
    }

    # Copy license/copyright files
    Get-ChildItem "$pandocSource\*" -Include "COPYRIGHT*","LICENSE*","COPYING*" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "$pandocTargetDir\$($_.Name)"
    }
    Write-Host "  ✓ Copied Pandoc license files" -ForegroundColor Green

    # Calculate size
    $pandocSize = (Get-ChildItem -Path $pandocTargetDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  ℹ Pandoc bundle size: $($pandocSize.ToString('F2')) MB" -ForegroundColor Cyan
}
else {
    Write-Host "  ✗ Pandoc not found in expected locations" -ForegroundColor Red
    Write-Host "  Please install Pandoc: choco install pandoc" -ForegroundColor Yellow
    Write-Host "  Or run: .\scripts\install_pandoc.ps1" -ForegroundColor Yellow
    exit 1
}

# Step 4: Build Python application with PyInstaller (if using PyInstaller)
Write-Host "`n[4/7] Building Python application..." -ForegroundColor Yellow
# Uncomment this if you're using PyInstaller
# if (Test-Path "transmutation_codex.spec") {
#     pyinstaller transmutation_codex.spec --clean
#     Write-Host "  ✓ PyInstaller build complete" -ForegroundColor Green
# }
# else {
#     Write-Host "  ⚠ PyInstaller spec file not found - skipping" -ForegroundColor Yellow
# }
Write-Host "  ⚠ PyInstaller build skipped (not configured yet)" -ForegroundColor Yellow
Write-Host "  ℹ This step will be enabled when you create a .spec file" -ForegroundColor Cyan

# Step 5: Copy configuration files
Write-Host "`n[5/7] Copying configuration files..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "build/config" -Force | Out-Null
Copy-Item "config/default_config.yaml" -Destination "build/config/"
Write-Host "  ✓ Copied default_config.yaml" -ForegroundColor Green

# Step 6: Create installer (if using Inno Setup or NSIS)
Write-Host "`n[6/7] Creating installer..." -ForegroundColor Yellow
# Uncomment when you have an installer script
# if (Test-Path "installer.iss") {
#     iscc installer.iss /DAppVersion=$Version
#     Write-Host "  ✓ Installer created" -ForegroundColor Green
# }
# else {
#     Write-Host "  ⚠ Installer script not found - skipping" -ForegroundColor Yellow
# }
Write-Host "  ⚠ Installer creation skipped (not configured yet)" -ForegroundColor Yellow
Write-Host "  ℹ You can use Inno Setup or NSIS for Windows installers" -ForegroundColor Cyan

# Step 7: Sign installer (optional)
if (-not $SkipSign) {
    Write-Host "`n[7/7] Signing installer..." -ForegroundColor Yellow
    # Uncomment and configure when you have a code signing certificate
    # $installerPath = "dist\AiChemistSetup_$Version.exe"
    # if (Test-Path $installerPath) {
    #     signtool sign /f "path\to\cert.pfx" /p "password" /t "http://timestamp.digicert.com" $installerPath
    #     Write-Host "  ✓ Installer signed" -ForegroundColor Green
    # }
    Write-Host "  ⚠ Code signing skipped (not configured)" -ForegroundColor Yellow
}
else {
    Write-Host "`n[7/7] Skipping code signing..." -ForegroundColor Yellow
}

# Summary
Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "  Build Summary" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ✓ Build directory: build/" -ForegroundColor Green
Write-Host "  ✓ Tesseract bundled: build/resources/tesseract/" -ForegroundColor Green
Write-Host "  ✓ Configuration: build/config/" -ForegroundColor Green

# Next steps
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test bundled Tesseract detection:" -ForegroundColor White
Write-Host "     python -c `"from transmutation_codex.plugins.pdf.to_editable_pdf import _get_bundled_tesseract_path; print(_get_bundled_tesseract_path())`"" -ForegroundColor Gray
Write-Host "  2. Create PyInstaller spec file (transmutation_codex.spec)" -ForegroundColor White
Write-Host "  3. Create installer script (installer.iss or installer.nsi)" -ForegroundColor White
Write-Host "  4. Test on clean Windows machine" -ForegroundColor White
Write-Host ""
Write-Host "✅ Build preparation complete!" -ForegroundColor Green
Write-Host "   See docs/BUNDLING_TESSERACT.md for detailed instructions" -ForegroundColor Gray
Write-Host ""

