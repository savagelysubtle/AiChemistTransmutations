# Bundling Tesseract for Production Deployment

This guide explains how to bundle Tesseract OCR with your AiChemist Transmutation Codex installer for a seamless end-user experience.

## Overview

Bundling Tesseract ensures:

- ✅ No manual installation required by end users
- ✅ Consistent Tesseract version across all installations
- ✅ Controlled, tested environment
- ✅ Works offline (no internet required)
- ✅ Professional user experience

## Licensing Considerations

**Tesseract OCR License:** Apache License 2.0

✅ **You CAN:**

- Distribute Tesseract with your commercial application
- Modify and redistribute Tesseract
- Use Tesseract in proprietary software

✅ **You MUST:**

- Include a copy of the Apache 2.0 license
- State any significant changes you made to Tesseract
- Include NOTICE file if one exists

📄 **Include these files in your installer:**

- `LICENSE` - Apache 2.0 license text
- `NOTICE` - Attribution file
- `README` - Tesseract documentation

## Directory Structure

Recommended bundled structure:

```
YourApp/
├── bin/
│   └── transmutation_codex.exe       # Your main application
├── resources/
│   ├── tesseract/
│   │   ├── tesseract.exe              # Tesseract executable
│   │   ├── tessdata/                  # Language data files
│   │   │   ├── eng.traineddata        # English
│   │   │   ├── osd.traineddata        # Orientation/script detection
│   │   │   └── ...                    # Additional languages
│   │   ├── LICENSE                    # Apache 2.0 license
│   │   └── NOTICE                     # Attribution
│   └── ghostscript/                   # Optional: for OCRmyPDF
│       └── ...
├── config/
│   └── default_config.yaml            # Auto-configured paths
└── logs/
```

## Implementation Steps

### Step 1: Download Tesseract

**Option A: Use Chocolatey to Extract Files**

```powershell
# Install to a temporary location
choco install tesseract --install-directory="C:\TesseractBuild"

# Copy files to your build directory
Copy-Item "C:\TesseractBuild\Tesseract-OCR\*" -Destination "build\resources\tesseract\" -Recurse
```

**Option B: Download Installer and Extract**

```powershell
# Download from https://github.com/UB-Mannheim/tesseract/wiki
# Install to temporary location
# Extract files

$sourceDir = "C:\Program Files\Tesseract-OCR"
$targetDir = "build\resources\tesseract"

# Copy essential files
Copy-Item "$sourceDir\tesseract.exe" -Destination $targetDir
Copy-Item "$sourceDir\tessdata" -Destination $targetDir -Recurse
Copy-Item "$sourceDir\*.dll" -Destination $targetDir  # Required DLLs
```

### Step 2: Update Configuration System

Modify `_configure_tesseract_path()` to check bundled location first:

```python
def _configure_tesseract_path() -> None:
    """Configure Tesseract PATH dynamically."""

    # 1. Check bundled Tesseract FIRST
    bundled_path = _get_bundled_tesseract_path()
    if bundled_path and bundled_path.exists():
        tesseract_dir = str(bundled_path.parent)
        if tesseract_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = tesseract_dir + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"Using bundled Tesseract: {tesseract_dir}")
            return

    # 2. Check if tesseract is already in PATH
    if shutil.which("tesseract"):
        logger.debug("Tesseract found in system PATH")
        return

    # 3. Check user configuration
    # ... rest of existing code


def _get_bundled_tesseract_path() -> Path | None:
    """Get path to bundled Tesseract executable.

    Returns:
        Path to bundled tesseract.exe or None if not found
    """
    try:
        # Get application directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            app_dir = Path(sys._MEIPASS)
        else:
            # Running as script (development)
            app_dir = Path(__file__).parent.parent.parent.parent

        # Check relative to application
        possible_locations = [
            app_dir / "resources" / "tesseract" / "tesseract.exe",
            app_dir / "bin" / "tesseract" / "tesseract.exe",
            app_dir / "tesseract" / "tesseract.exe",
        ]

        for path in possible_locations:
            if path.exists():
                logger.debug(f"Found bundled Tesseract at: {path}")
                return path

        return None
    except Exception as e:
        logger.debug(f"Could not locate bundled Tesseract: {e}")
        return None
```

### Step 3: Update Your Installer Script

**Example: Using Inno Setup (Windows)**

```innosetup
[Setup]
AppName=AiChemist Transmutation Codex
AppVersion=1.0.0
DefaultDirName={pf}\AiChemist
DefaultGroupName=AiChemist

[Files]
; Main application
Source: "dist\transmutation_codex.exe"; DestDir: "{app}\bin"

; Bundled Tesseract
Source: "resources\tesseract\*"; DestDir: "{app}\resources\tesseract"; Flags: recursesubdirs

; Configuration
Source: "config\default_config.yaml"; DestDir: "{app}\config"

; Licenses
Source: "resources\tesseract\LICENSE"; DestDir: "{app}\licenses"; DestName: "TESSERACT_LICENSE.txt"

[Icons]
Name: "{group}\AiChemist Transmutation Codex"; Filename: "{app}\bin\transmutation_codex.exe"

[Run]
; Optional: Verify Tesseract after installation
Filename: "{app}\resources\tesseract\tesseract.exe"; Parameters: "--version"; Flags: runhidden; StatusMsg: "Verifying Tesseract installation..."
```

**Example: Using NSIS (Windows)**

```nsis
!define APP_NAME "AiChemist Transmutation Codex"
!define APP_VERSION "1.0.0"

InstallDir "$PROGRAMFILES\${APP_NAME}"

Section "MainSection" SEC01
  ; Application files
  SetOutPath "$INSTDIR\bin"
  File "dist\transmutation_codex.exe"

  ; Bundled Tesseract
  SetOutPath "$INSTDIR\resources\tesseract"
  File /r "resources\tesseract\*.*"

  ; Configuration
  SetOutPath "$INSTDIR\config"
  File "config\default_config.yaml"

  ; Licenses
  SetOutPath "$INSTDIR\licenses"
  File /oname=TESSERACT_LICENSE.txt "resources\tesseract\LICENSE"
SectionEnd
```

### Step 4: Add to PyInstaller Spec (if using PyInstaller)

```python
# transmutation_codex.spec

a = Analysis(
    ['src/transmutation_codex/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle Tesseract
        ('resources/tesseract', 'resources/tesseract'),
        # Bundle config
        ('config/default_config.yaml', 'config'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transmutation_codex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transmutation_codex',
)
```

## File Size Optimization

Tesseract with English language pack is ~60MB. To reduce size:

### Include Only Required Languages

```powershell
# Only include English
Copy-Item "$sourceDir\tessdata\eng.traineddata" -Destination "$targetDir\tessdata\"
Copy-Item "$sourceDir\tessdata\osd.traineddata" -Destination "$targetDir\tessdata\"
```

### Use Fast Models (Smaller Size)

Tesseract offers "fast" models that are smaller but less accurate:

- `eng.traineddata` - Best quality (~15MB)
- `eng_fast.traineddata` - Fast version (~5MB)

### Optional: Download on Demand

For very size-conscious deployments:

1. Bundle only `tesseract.exe` and `eng.traineddata`
2. Offer additional languages as optional downloads
3. Download on first use

## Testing Your Bundle

### Test Checklist

```python
# test_bundled_tesseract.py

import os
import subprocess
from pathlib import Path

def test_bundled_tesseract():
    """Test that bundled Tesseract works correctly."""

    # 1. Check executable exists
    app_dir = Path(__file__).parent.parent
    tesseract_path = app_dir / "resources" / "tesseract" / "tesseract.exe"
    assert tesseract_path.exists(), "Tesseract executable not found"

    # 2. Check tessdata exists
    tessdata_dir = tesseract_path.parent / "tessdata"
    assert tessdata_dir.exists(), "tessdata directory not found"
    assert (tessdata_dir / "eng.traineddata").exists(), "English language pack not found"

    # 3. Verify Tesseract runs
    result = subprocess.run(
        [str(tesseract_path), "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Tesseract failed to run: {result.stderr}"
    assert "tesseract" in result.stdout.lower(), "Invalid Tesseract output"

    # 4. Test actual OCR
    from transmutation_codex.plugins.pdf.to_editable_pdf import convert_pdf_to_editable

    # Use a test PDF
    test_pdf = Path("tests/test_files/sample_scanned.pdf")
    output_pdf = Path("tests/test_files/output_editable.pdf")

    result = convert_pdf_to_editable(test_pdf, output_pdf)
    assert result.exists(), "Conversion failed"

    print("✅ All bundled Tesseract tests passed!")

if __name__ == "__main__":
    test_bundled_tesseract()
```

### Manual Testing

1. **Clean install on test machine**
   - No Tesseract installed
   - No PATH modifications
   - Fresh Windows installation

2. **Run your installer**

3. **Launch application**

4. **Test PDF to Editable conversion**
   - Check logs for: "Using bundled Tesseract"
   - Verify conversion succeeds

5. **Test with system Tesseract**
   - Install Tesseract separately
   - Verify app still uses bundled version (priority)

## Build Automation Script

```powershell
# build_installer.ps1

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = "dist"
)

Write-Host "Building AiChemist Transmutation Codex v$Version" -ForegroundColor Green

# Step 1: Clean previous builds
Write-Host "`n[1/6] Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "build/resources/tesseract" -Force | Out-Null

# Step 2: Copy Tesseract files
Write-Host "[2/6] Copying Tesseract files..." -ForegroundColor Yellow
$tesseractSource = "C:\Program Files\Tesseract-OCR"
if (Test-Path $tesseractSource) {
    Copy-Item "$tesseractSource\tesseract.exe" -Destination "build/resources/tesseract/"
    Copy-Item "$tesseractSource\*.dll" -Destination "build/resources/tesseract/"
    Copy-Item "$tesseractSource\tessdata" -Destination "build/resources/tesseract/" -Recurse
    Copy-Item "$tesseractSource\LICENSE" -Destination "build/resources/tesseract/"
    Write-Host "  ✓ Tesseract files copied" -ForegroundColor Green
} else {
    Write-Host "  ✗ Tesseract not found at $tesseractSource" -ForegroundColor Red
    exit 1
}

# Step 3: Build Python application
Write-Host "[3/6] Building Python application..." -ForegroundColor Yellow
pyinstaller transmutation_codex.spec --clean

# Step 4: Copy bundled resources
Write-Host "[4/6] Copying bundled resources..." -ForegroundColor Yellow
Copy-Item "build/resources" -Destination "dist/transmutation_codex/" -Recurse -Force

# Step 5: Create installer
Write-Host "[5/6] Creating installer..." -ForegroundColor Yellow
iscc installer.iss /DAppVersion=$Version

# Step 6: Sign installer (optional)
Write-Host "[6/6] Signing installer..." -ForegroundColor Yellow
# signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com "dist/AiChemistSetup_$Version.exe"

Write-Host "`n✅ Build complete! Installer: dist/AiChemistSetup_$Version.exe" -ForegroundColor Green
```

## User Documentation

Include in your README/User Guide:

```markdown
## System Requirements

- Windows 10 or later (64-bit)
- 500MB free disk space
- Internet connection (for initial download only)

**Note:** Tesseract OCR is included with the application.
No separate installation required!

## Installation

1. Download `AiChemistSetup.exe`
2. Run the installer
3. Follow the installation wizard
4. Launch AiChemist Transmutation Codex

## Features

- PDF to Editable PDF (OCR included)
- PDF to Markdown with OCR
- And more...
```

## Support & Troubleshooting

Add to your support documentation:

### "Tesseract Not Found" Error

This should never happen with bundled installation. If it does:

1. Verify installation directory contains: `resources/tesseract/tesseract.exe`
2. Check logs: `logs/python/app_session_*.log`
3. Reinstall application

### Performance Optimization

Users can install additional language packs in: `<InstallDir>/resources/tesseract/tessdata/`

Download from: <https://github.com/tesseract-ocr/tessdata>

## Summary

**Bundling Checklist:**

- ✅ Tesseract executable
- ✅ Required DLLs
- ✅ tessdata directory (English at minimum)
- ✅ LICENSE and NOTICE files
- ✅ Modified `_configure_tesseract_path()` to check bundled location first
- ✅ PyInstaller/Installer script updated
- ✅ Automated build script
- ✅ Test on clean machine
- ✅ User documentation updated

**Benefits:**

- Zero-configuration for end users
- Consistent environment across all installations
- Works offline
- Professional user experience
- Full control over Tesseract version

**Next Steps:**

1. Implement `_get_bundled_tesseract_path()` function
2. Update installer scripts
3. Test on clean Windows machine
4. Update user documentation
5. Build and distribute!
