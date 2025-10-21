# Build Script Templates

This file contains the PowerShell build scripts that need to be manually created due to workspace restrictions.

## File 1: scripts/build/build_msix.ps1

```powershell
# Build MSIX package for Microsoft Store
# Usage: .\build_msix.ps1 [-Version "1.0.0.0"] [-Architecture "x64"]

param(
    [string]$Version = "1.0.0.0",
    [string]$Architecture = "x64",
    [switch]$SkipBuild,
    [switch]$Sign,
    [string]$CertPath = "",
    [string]$CertPassword = ""
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AiChemist MSIX Build Script" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for required tools
Write-Host "Checking for required tools..." -ForegroundColor Yellow

# Find makeappx.exe
$MakeAppxPath = Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter "makeappx.exe" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -like "*\x64\makeappx.exe" } |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $MakeAppxPath) {
    Write-Host "ERROR: makeappx.exe not found. Please install Windows SDK." -ForegroundColor Red
    Write-Host "Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found makeappx.exe: $MakeAppxPath" -ForegroundColor Green

# Find signtool.exe if signing
if ($Sign) {
    $SignToolPath = Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like "*\x64\signtool.exe" } |
        Select-Object -First 1 -ExpandProperty FullName

    if (-not $SignToolPath) {
        Write-Host "ERROR: signtool.exe not found. Cannot sign package." -ForegroundColor Red
        exit 1
    }
    Write-Host "Found signtool.exe: $SignToolPath" -ForegroundColor Green
}

# Build with PyInstaller first (unless skipped)
if (-not $SkipBuild) {
    Write-Host "`nBuilding application with PyInstaller..." -ForegroundColor Yellow
    pyinstaller transmutation_codex.spec --clean

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: PyInstaller build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "PyInstaller build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nSkipping PyInstaller build (using existing build)" -ForegroundColor Yellow
}

# Verify dist directory exists
if (-not (Test-Path "dist\aichemist_transmutation_codex")) {
    Write-Host "ERROR: dist\aichemist_transmutation_codex not found!" -ForegroundColor Red
    Write-Host "Please run PyInstaller first or remove -SkipBuild flag." -ForegroundColor Yellow
    exit 1
}

# Create MSIX staging directory
$StagingDir = "build\msix_staging"
Write-Host "`nPreparing MSIX staging directory..." -ForegroundColor Yellow
if (Test-Path $StagingDir) {
    Remove-Item -Path $StagingDir -Recurse -Force
}
New-Item -Path $StagingDir -ItemType Directory | Out-Null

# Copy application files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Path "dist\aichemist_transmutation_codex\*" -Destination $StagingDir -Recurse

# Copy MSIX manifest
Write-Host "Copying MSIX manifest..." -ForegroundColor Yellow
Copy-Item -Path "build\msix\AppxManifest.xml" -Destination $StagingDir

# Copy assets
Write-Host "Copying assets..." -ForegroundColor Yellow
if (Test-Path "build\msix\Assets") {
    Copy-Item -Path "build\msix\Assets" -Destination "$StagingDir\Assets" -Recurse
} else {
    Write-Host "WARNING: No assets found in build\msix\Assets" -ForegroundColor Yellow
    Write-Host "MSIX build will fail without required asset files." -ForegroundColor Yellow
    Write-Host "Please add: StoreLogo.png, Square*.png, SplashScreen.png" -ForegroundColor Yellow
}

# Update version in manifest
Write-Host "Updating version in manifest to $Version..." -ForegroundColor Yellow
$ManifestPath = "$StagingDir\AppxManifest.xml"
$ManifestContent = Get-Content $ManifestPath -Raw
$ManifestContent = $ManifestContent -replace 'Version="1\.0\.0\.0"', "Version=`"$Version`""
$ManifestContent | Set-Content $ManifestPath -Encoding UTF8

# Create MSIX package
$OutputPath = "dist\AiChemistCodex_${Version}_${Architecture}.msix"
Write-Host "`nCreating MSIX package..." -ForegroundColor Yellow
& $MakeAppxPath pack /d $StagingDir /p $OutputPath /o

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: MSIX packaging failed!" -ForegroundColor Red
    exit 1
}

Write-Host "MSIX package created successfully!" -ForegroundColor Green
Write-Host "Output: $OutputPath" -ForegroundColor Cyan

# Sign package if requested
if ($Sign) {
    Write-Host "`nSigning MSIX package..." -ForegroundColor Yellow

    if (-not $CertPath) {
        Write-Host "ERROR: Certificate path not specified. Use -CertPath parameter." -ForegroundColor Red
        exit 1
    }

    if (-not (Test-Path $CertPath)) {
        Write-Host "ERROR: Certificate not found: $CertPath" -ForegroundColor Red
        exit 1
    }

    if ($CertPassword) {
        & $SignToolPath sign /fd SHA256 /f $CertPath /p $CertPassword $OutputPath
    } else {
        & $SignToolPath sign /fd SHA256 /f $CertPath $OutputPath
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Signing failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host "Package signed successfully!" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "MSIX Package: $OutputPath" -ForegroundColor Cyan
Write-Host "Package Size: $((Get-Item $OutputPath).Length / 1MB) MB" -ForegroundColor Cyan
Write-Host ""

if (-not $Sign) {
    Write-Host "NOTE: Package is not signed. To sign, use:" -ForegroundColor Yellow
    Write-Host "  .\build_msix.ps1 -Sign -CertPath <path> [-CertPassword <password>]" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test the MSIX package locally" -ForegroundColor White
Write-Host "  2. Sign with a trusted certificate for production" -ForegroundColor White
Write-Host "  3. Submit to Microsoft Store Partner Center" -ForegroundColor White
```

## File 2: scripts/build/build_direct_installer.ps1

```powershell
# Build direct download installer with Inno Setup
# Usage: .\build_direct_installer.ps1 [-Version "1.0.0"]

param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AiChemist Direct Installer Build" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find Inno Setup compiler
$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $InnoSetupPath)) {
    Write-Host "ERROR: Inno Setup not found at $InnoSetupPath" -ForegroundColor Red
    Write-Host "Please install Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Inno Setup: $InnoSetupPath" -ForegroundColor Green

# 1. Build Python backend with PyInstaller
Write-Host "`n1. Building Python backend..." -ForegroundColor Yellow
pyinstaller transmutation_codex.spec --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed!" -ForegroundColor Red
    exit 1
}

# 2. Build Electron GUI
Write-Host "`n2. Building Electron GUI..." -ForegroundColor Yellow
Push-Location gui

# Set production environment
$env:NODE_ENV = "production"
$env:DEV_MODE = "false"

npm run build
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "ERROR: GUI build failed!" -ForegroundColor Red
    exit 1
}

npm run electron:build
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "ERROR: Electron build failed!" -ForegroundColor Red
    exit 1
}

Pop-Location

# 3. Verify external dependencies (optional)
Write-Host "`n3. Checking external dependencies..." -ForegroundColor Yellow
Write-Host "NOTE: External dependencies should be downloaded separately" -ForegroundColor Yellow
Write-Host "Run setup_external_dependencies.ps1 if not already done" -ForegroundColor Yellow

# 4. Create installer with Inno Setup
Write-Host "`n4. Creating installer with Inno Setup..." -ForegroundColor Yellow

# Create output directory
$OutputDir = "dist\installer"
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory | Out-Null
}

# Build installer
& $InnoSetupPath installer.iss /DMyAppVersion=$Version /O$OutputDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Inno Setup build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find the created installer
$Installer = Get-ChildItem -Path $OutputDir -Filter "AiChemistSetup*.exe" | Select-Object -First 1

if ($Installer) {
    Write-Host "Installer: $($Installer.FullName)" -ForegroundColor Cyan
    Write-Host "Size: $([math]::Round($Installer.Length / 1MB, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "WARNING: Installer not found in $OutputDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test installer on clean Windows machine" -ForegroundColor White
Write-Host "  2. Sign with code signing certificate" -ForegroundColor White
Write-Host "  3. Upload to download server (GitHub Releases, S3, etc.)" -ForegroundColor White
Write-Host "  4. Update website with download link" -ForegroundColor White
```

## Instructions

1. **Create the files manually:**

   ```powershell
   # Navigate to project root
   cd D:\Coding\AiChemistCodex\AiChemistTransmutations

   # Create build_msix.ps1
   New-Item -Path "scripts\build\build_msix.ps1" -ItemType File
   # Copy content from above into the file

   # Create build_direct_installer.ps1
   New-Item -Path "scripts\build\build_direct_installer.ps1" -ItemType File
   # Copy content from above into the file
   ```

2. **Set execution policy (if needed):**

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Test the scripts:**

   ```powershell
   # Test MSIX build
   .\scripts\build\build_msix.ps1 -Version "1.0.0.0"

   # Test direct installer build
   .\scripts\build\build_direct_installer.ps1 -Version "1.0.0"
   ```

## Notes

- These scripts assume you have:
  - Windows SDK installed (for makeappx.exe and signtool.exe)
  - Inno Setup 6 installed
  - PyInstaller installed (`pip install pyinstaller`)
  - Node.js and npm installed

- The scripts will automatically:
  - Build Python backend with PyInstaller
  - Build Electron GUI
  - Package into MSIX or Inno Setup installer
  - Sign (if certificate provided)

- For production builds, always sign your installers with a valid code signing certificate.
