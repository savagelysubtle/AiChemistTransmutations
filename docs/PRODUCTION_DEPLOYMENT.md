# Production Deployment Quick Start

This guide helps you quickly deploy AiChemist Transmutation Codex with bundled Tesseract for end users.

## Prerequisites

- Windows 10 or later (64-bit)
- Python 3.13+ with UV
- Tesseract OCR installed (for bundling)
- PyInstaller (install: `uv add --dev pyinstaller`)
- Inno Setup (download from: <https://jrsoftware.org/isinfo.php>)

## 5-Minute Deployment

### 1. Prepare Tesseract Bundle

```powershell
# Run the automated build script
.\scripts\build_installer.ps1 -Version "1.0.0"
```

This script will:

- ✅ Clean previous builds
- ✅ Copy Tesseract files to `build/resources/tesseract/`
- ✅ Bundle configuration files
- ✅ Prepare for PyInstaller

### 2. Build Standalone Executable

```powershell
# Build with PyInstaller
pyinstaller transmutation_codex.spec --clean
```

Output: `dist/aichemist_transmutation_codex/` (standalone folder)

### 3. Create Windows Installer

```powershell
# Compile with Inno Setup
iscc installer.iss
```

Output: `dist/installer/AiChemistSetup_1.0.0.exe`

### 4. Test on Clean Machine

- Copy installer to test machine (no Tesseract installed)
- Run installer
- Launch application
- Test PDF to Editable conversion
- Check logs for: "Using bundled Tesseract"

## What Gets Bundled?

| Component | Size | Required |
|-----------|------|----------|
| Tesseract.exe | ~5MB | ✅ Yes |
| DLLs | ~20MB | ✅ Yes |
| English Language Pack | ~15MB | ✅ Yes |
| Additional Languages | ~15MB each | ⚠️ Optional |
| **Total** | **~40-60MB** | |

## File Structure After Installation

```
C:\Program Files\AiChemist\
├── aichemist_transmutation_codex.exe
├── resources\
│   └── tesseract\
│       ├── tesseract.exe
│       ├── *.dll
│       ├── tessdata\
│       │   ├── eng.traineddata
│       │   └── osd.traineddata
│       └── LICENSE
├── config\
│   └── default_config.yaml
├── licenses\
│   └── TESSERACT_LICENSE.txt
└── logs\
```

## Verification Checklist

Before distributing:

- [ ] Run bundled Tesseract test: `uv run python tests/test_bundled_tesseract.py`
- [ ] Test all converters (PDF↔MD, PDF→HTML, PDF→Editable, etc.)
- [ ] Check log files for Tesseract detection messages
- [ ] Test on Windows 10 and Windows 11
- [ ] Test on machine without Tesseract installed
- [ ] Verify installer includes LICENSE files
- [ ] Test uninstaller

## Configuration Options

Users can customize Tesseract location via `config/default_config.yaml`:

```yaml
environment:
  tesseract_path: "C:\\Custom\\Path\\tesseract.exe"
```

## Troubleshooting

### Build Script Fails

**Problem:** `Tesseract not found at C:\Program Files\Tesseract-OCR`

**Solution:** Update `$tesseractSource` in `scripts/build_installer.ps1` to your Tesseract installation path.

### PyInstaller Import Errors

**Problem:** `ModuleNotFoundError` during build

**Solution:** Add missing modules to `hiddenimports` in `transmutation_codex.spec`.

### Bundled Tesseract Not Found

**Problem:** Application doesn't detect bundled Tesseract

**Solution:** Check `_get_bundled_tesseract_path()` search paths match your installer structure.

### Large Installer Size

**Problem:** Installer is > 100MB

**Solution:**

- Remove unnecessary language packs from `tessdata/`
- Use `eng.traineddata` only (~15MB)
- Consider using `eng_fast.traineddata` (~5MB, less accurate)

## Advanced Options

### Custom Installer Icon

Edit `installer.iss`:

```ini
SetupIconFile=resources\icon.ico
```

### Code Signing

Edit `scripts/build_installer.ps1`:

```powershell
signtool sign /f "cert.pfx" /p "password" /t "http://timestamp.digicert.com" $installerPath
```

### Environment Variables

For enterprise deployments, set system-wide Tesseract path:

```powershell
[System.Environment]::SetEnvironmentVariable("TESSERACT_PATH", "C:\Tesseract\tesseract.exe", "Machine")
```

## Distribution

### Direct Download

- Upload `AiChemistSetup_1.0.0.exe` to your website
- Provide SHA256 checksum
- Include installation instructions

### Auto-Updates

Consider implementing:

- GitHub Releases for version tracking
- Electron auto-updater for GUI updates
- Update notification system

### Licensing

Remember to:

- Include Tesseract's Apache 2.0 license
- Add attribution in your About dialog
- Document any modifications to Tesseract

## Support Resources

- **Installation Issues:** `docs/TESSERACT_CONFIGURATION.md`
- **Bundling Details:** `docs/BUNDLING_TESSERACT.md`
- **Build Errors:** Check `build_installer.ps1` logs
- **Test Suite:** `tests/test_bundled_tesseract.py`

## Production Checklist

Before release:

- [ ] Update version numbers in all files
- [ ] Generate fresh GUID for `installer.iss`
- [ ] Update publisher information
- [ ] Test installer on multiple machines
- [ ] Create backup of signing certificate
- [ ] Document system requirements
- [ ] Prepare release notes
- [ ] Set up support channels

## Quick Commands Reference

```powershell
# Build everything
.\scripts\build_installer.ps1 -Version "1.0.0"
pyinstaller transmutation_codex.spec --clean
iscc installer.iss

# Test
uv run python tests/test_bundled_tesseract.py

# Verify Tesseract
tesseract --version

# Check bundled detection
python -c "from transmutation_codex.plugins.pdf.to_editable_pdf import _get_bundled_tesseract_path; print(_get_bundled_tesseract_path())"
```

---

**Ready to deploy?** Follow steps 1-4 above, then distribute your installer! 🚀



