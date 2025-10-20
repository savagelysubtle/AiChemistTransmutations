# Ghostscript Bundling - Update Summary

## What Was Added

Ghostscript is now included alongside Tesseract for production bundling. This is required for OCRmyPDF to function properly.

### Files Modified

1. **`scripts/build_installer.ps1`** - Updated to copy Ghostscript files
   - Detects latest Ghostscript version in `C:\Program Files\gs`
   - Copies executables and DLLs to `build/resources/ghostscript/`
   - Includes Ghostscript LICENSE file
   - Reports bundle size

2. **`src/transmutation_codex/plugins/pdf/to_editable_pdf.py`** - Added Ghostscript detection
   - Added `_get_app_dir()` helper function
   - Added `_get_bundled_ghostscript_path()` function
   - Added `_configure_ghostscript_path()` function
   - Auto-configures Ghostscript PATH at module load time

### Detection Priority (Ghostscript)

```
1. Bundled Ghostscript   📦  (resources/ghostscript/gswin64c.exe)
   ↓ Not found
2. System PATH           🔧  (gswin64c or gs command)
   ↓ Not found
3. Common Locations      📁  (C:\Program Files\gs\gs*\bin\gswin64c.exe)
   ↓ Not found
4. OCRmyPDF Search       🔍  (let OCRmyPDF find it)
   ↓ Not found
5. Error                 ❌  (conversion fails with helpful message)
```

## File Structure After Bundling

```
build/
├── resources/
│   ├── tesseract/
│   │   ├── tesseract.exe
│   │   ├── *.dll
│   │   ├── tessdata/
│   │   │   ├── eng.traineddata
│   │   │   └── osd.traineddata
│   │   └── LICENSE
│   └── ghostscript/           # NEW!
│       ├── gswin64c.exe       # Main executable
│       ├── gsdll64.dll        # Core DLL
│       ├── *.dll              # Other required DLLs
│       └── LICENSE            # AGPL 3.0
└── config/
    └── default_config.yaml
```

## Bundle Size Estimates

| Component | Size | Required |
|-----------|------|----------|
| Tesseract.exe | ~5 MB | ✅ Yes |
| Tesseract DLLs | ~20 MB | ✅ Yes |
| English Language Pack | ~15 MB | ✅ Yes |
| **Ghostscript** | **~30-40 MB** | **✅ Yes** |
| **Total** | **~70-80 MB** | |

## Licensing

### Tesseract

- **License:** Apache 2.0
- **Commercial Use:** ✅ Allowed
- **Redistribution:** ✅ Allowed
- **Requirements:** Include LICENSE file

### Ghostscript

- **License:** AGPL 3.0 (or commercial license)
- **Commercial Use:** ⚠️ Requires commercial license OR AGPL compliance
- **Options:**
  1. Purchase commercial license from Artifex
  2. Make your software AGPL (open source)
  3. Don't bundle - let users install separately

## Current Status (Development)

### Issue

Ghostscript is installed via Chocolatey but not in PATH for the running GUI application.

### Solution

**Restart the GUI application** to pick up the updated PATH with both Tesseract and Ghostscript.

```powershell
# Stop GUI (Ctrl+C)
cd gui
npm run dev
```

### Verification

After restart, check logs for:

```
✅ "Tesseract found in system PATH"
✅ "Ghostscript found in system PATH"
```

Or for bundled (production):

```
✅ "Using bundled Tesseract: ..."
✅ "Using bundled Ghostscript: ..."
```

## Installation Commands (Development)

```powershell
# Install both dependencies
choco install tesseract -y
choco install ghostscript -y

# Restart GUI to pick up PATH changes
cd gui
npm run dev
```

## Production Deployment

```powershell
# 1. Bundle both Tesseract and Ghostscript
.\scripts\build_installer.ps1 -Version "1.0.0"

# Expected output:
# ✓ Copied tesseract.exe
# ✓ Copied Tesseract DLL files
# ✓ Copied tessdata directory
# ℹ Tesseract bundle size: ~40 MB
# ✓ Copied Ghostscript executables and DLLs
# ℹ Ghostscript bundle size: ~35 MB

# 2. Build with PyInstaller
pyinstaller transmutation_codex.spec --clean

# 3. Create installer
iscc installer.iss
```

## Benefits of Bundling Ghostscript

### For Users

- ✅ No manual Ghostscript installation
- ✅ PDF to Editable conversion works immediately
- ✅ Zero configuration required
- ✅ Works offline

### For You

- ✅ Consistent Ghostscript version
- ✅ No "missing dependency" errors
- ✅ Professional user experience
- ✅ Controlled testing environment

### Trade-offs

- ⚠️ Larger installer size (~70-80MB vs ~40-60MB)
- ⚠️ AGPL licensing considerations
- ✅ But: Much better user experience!

## Alternative Approach (No Bundling)

If you prefer not to bundle Ghostscript due to licensing:

1. **Detect but don't bundle:**
   - Keep the detection code
   - Don't include in `build_installer.ps1`
   - Show helpful error message with install instructions

2. **User installs separately:**

   ```
   Error: Ghostscript not found
   Install with: choco install ghostscript
   Or download from: https://ghostscript.com/
   ```

3. **Update documentation:**
   - List Ghostscript as a system requirement
   - Provide installation instructions
   - Explain it's needed for PDF to Editable conversion

## Recommendation

**For Commercial Software:**

- Purchase Ghostscript commercial license (~$10K/year for unlimited distribution)
- Or don't bundle Ghostscript - let users install it separately
- Tesseract bundling alone is still very valuable!

**For Open Source:**

- Bundle both Tesseract and Ghostscript
- Include AGPL license file
- Full zero-config experience for users

## Next Steps

1. **Immediate (Development):**
   - Restart GUI to pick up Ghost script PATH
   - Test PDF to Editable conversion
   - Verify both Tesseract and Ghostscript are detected

2. **Before Production:**
   - Decide on Ghostscript licensing approach
   - Test bundling with `build_installer.ps1`
   - Verify bundle size is acceptable
   - Test on clean Windows machine

3. **Documentation:**
   - Update README with Ghostscript requirement
   - Document licensing decisions
   - Provide installation instructions (if not bundling)

---

**Status:** ✅ Code complete - Ghostscript detection and bundling ready!
**Action Required:** Restart GUI to test in development



