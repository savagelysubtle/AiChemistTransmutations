# Automatic PATH Configuration for Bundled Executables

## Overview

The AiChemist Transmutation Codex production builds automatically configure the system PATH to include bundled Tesseract and Ghostscript executables. This ensures OCR and PDF processing work immediately without any manual configuration.

## How It Works

### 1. **Runtime Hook (`scripts/runtime_hook_paths.py`)**

When the frozen application starts, PyInstaller executes the runtime hook **before** your main application code runs. This hook:

1. Detects if running as a frozen executable (production) or script (development)
2. Locates bundled executables in `resources/tesseract/` and `resources/ghostscript/`
3. Prepends these directories to the `PATH` environment variable
4. Verifies executables are accessible

**Key Benefits:**

- ✅ Automatic - no user interaction required
- ✅ Works immediately on first run
- ✅ Cross-platform compatible (Windows, Linux, macOS)
- ✅ Does not modify system PATH (only process environment)

### 2. **Module-Level Detection (Fallback)**

Each converter module (`to_editable_pdf.py`, etc.) also has detection logic that runs when the module is imported:

- `_configure_tesseract_path()` - Detects and adds Tesseract to PATH
- `_configure_ghostscript_path()` - Detects and adds Ghostscript to PATH

**Detection Priority:**

1. Check for bundled executable (production)
2. Check system PATH (already installed)
3. Check user configuration (`config/default_config.yaml`)
4. Check common installation directories
5. Log warning if not found

## Cross-Platform Support

### Windows

- **Tesseract:** `resources/tesseract/tesseract.exe`
- **Ghostscript:** `resources/ghostscript/gswin64c.exe`
- **PATH Separator:** `;` (semicolon)

### Linux

- **Tesseract:** `resources/tesseract/tesseract`
- **Ghostscript:** `resources/ghostscript/gs`
- **PATH Separator:** `:` (colon)
- **Important:** Ensure executables have execute permissions (`chmod +x`)

### macOS

- **Tesseract:** `resources/tesseract/tesseract`
- **Ghostscript:** `resources/ghostscript/gs`
- **PATH Separator:** `:` (colon)
- **Note:** May need code signing for Gatekeeper compatibility

## Build Process

### Windows (`scripts/build_installer.ps1`)

```powershell
# Copies executables from system installation
.\scripts\build_installer.ps1 -Version "1.0.0"
```

**What it does:**

1. Copies `C:\Program Files\Tesseract-OCR\*` → `build/resources/tesseract/`
2. Copies `C:\Program Files\gs\*` → `build/resources/ghostscript/`
3. Builds with PyInstaller (includes runtime hook)
4. Creates Inno Setup installer

### Linux/macOS (`scripts/build_installer.sh`)

```bash
# Copies executables from system installation
./scripts/build_installer.sh 1.0.0
```

**What it does:**

1. Detects Tesseract location (`/usr/bin`, `/usr/local/bin`, Homebrew)
2. Detects Ghostscript location
3. Copies executables and shared libraries
4. Builds with PyInstaller (includes runtime hook)
5. Creates `.tar.gz` archive (Linux) or `.app` bundle (macOS)

## Verification

### Development Mode

When running as a script, you'll see debug messages:

```
[Runtime Hook] No bundled executables found (development mode?)
```

This is normal - development uses system-installed executables.

### Production Mode

When running the frozen executable, you should see:

```
[Runtime Hook] Found bundled Tesseract at: C:\...\resources\tesseract
[Runtime Hook] Found bundled Ghostscript at: C:\...\resources\ghostscript
[Runtime Hook] Added 2 director(ies) to PATH
[Runtime Hook] ✓ tesseract.exe is accessible in PATH
[Runtime Hook] ✓ gswin64c.exe is accessible in PATH
```

### Manual Verification

After building and running the executable:

**Windows PowerShell:**

```powershell
# Check if Tesseract is in PATH
$env:PATH -split ';' | Select-String "tesseract"

# Check if Ghostscript is in PATH
$env:PATH -split ';' | Select-String "ghostscript"

# Verify executables work
tesseract --version
gswin64c --version
```

**Linux/macOS Bash:**

```bash
# Check if Tesseract is in PATH
echo $PATH | tr ':' '\n' | grep tesseract

# Check if Ghostscript is in PATH
echo $PATH | tr ':' '\n' | grep ghostscript

# Verify executables work
tesseract --version
gs --version
```

## Troubleshooting

### Issue: "Tesseract not found" in production

**Cause:** Bundled files weren't copied during build

**Solution:**

1. Verify `build/resources/tesseract/` contains files before building
2. Check PyInstaller output for warnings
3. Ensure `transmutation_codex.spec` includes data files correctly

### Issue: "Permission denied" on Linux/macOS

**Cause:** Executable permissions not set

**Solution:**

```bash
chmod +x dist/aichemist_transmutation_codex/resources/tesseract/tesseract
chmod +x dist/aichemist_transmutation_codex/resources/ghostscript/gs
```

Or add to build script:

```bash
chmod +x build/resources/tesseract/tesseract
chmod +x build/resources/ghostscript/gs
```

### Issue: Runtime hook not executing

**Cause:** PyInstaller spec file not configured correctly

**Solution:**
Verify `transmutation_codex.spec` contains:

```python
runtime_hooks=['scripts/runtime_hook_paths.py']
```

### Issue: PATH changes not persisting between runs

**Expected behavior!** The PATH modification only affects the current process, not the system PATH. This is intentional for security and portability.

## Architecture Diagram

```
Application Startup
       ↓
PyInstaller Loader
       ↓
Runtime Hook (scripts/runtime_hook_paths.py)
   ├─→ Detect frozen executable
   ├─→ Find bundled resources/
   ├─→ Modify process PATH
   └─→ Verify executables
       ↓
Main Application Code
       ↓
Import converter modules
   ├─→ to_editable_pdf.py
   │   ├─→ _configure_tesseract_path()
   │   └─→ _configure_ghostscript_path()
   └─→ Other converters...
       ↓
Converters use subprocess.run()
   ├─→ Finds tesseract in PATH ✅
   └─→ Finds gswin64c/gs in PATH ✅
```

## Security Considerations

### PATH Injection Safety

**Safe:**

- PATH is modified **only for the current process**
- Does not affect system PATH or other applications
- Changes are lost when the application exits

**Not Safe For:**

- Modifying global system PATH (requires admin/root)
- Persisting changes across reboots
- Affecting other running applications

### Executable Verification

The runtime hook verifies executables are accessible:

```python
import shutil
if shutil.which('tesseract.exe'):
    print("✓ Tesseract accessible")
```

This ensures:

- Executables exist in PATH
- Executables are properly named
- No broken symlinks or missing files

## Performance Impact

**Minimal overhead:**

- Runtime hook executes **once** at startup (~10-50ms)
- PATH modification is in-memory only
- No disk I/O after initial detection
- No impact on application runtime

## Testing

### Test Bundled Executables (Before Distribution)

```bash
# Build the application
./scripts/build_installer.ps1

# Run the executable
./dist/aichemist_transmutation_codex/aichemist_transmutation_codex.exe

# Check logs for PATH configuration messages
cat logs/python/app_session_*.log | grep "Runtime Hook"
```

### Unit Test the Runtime Hook

Create `tests/test_runtime_hook.py`:

```python
import sys
import os
from pathlib import Path
from unittest.mock import patch

def test_runtime_hook_frozen():
    """Test runtime hook when running as frozen executable"""
    with patch.object(sys, 'frozen', True, create=True):
        with patch.object(sys, '_MEIPASS', '/fake/app/dir', create=True):
            # Import the runtime hook
            import scripts.runtime_hook_paths as hook

            # Verify PATH was modified (if bundled resources exist)
            assert 'resources' in os.environ.get('PATH', '')
```

## Best Practices

1. **Always test on clean machines** - verify no system Tesseract/Ghostscript
2. **Include verification in installer** - Inno Setup `[Run]` section
3. **Log PATH modifications** - helps debugging user issues
4. **Handle missing executables gracefully** - show helpful error messages
5. **Document licensing** - especially for Ghostscript (AGPL)

## Alternatives Considered

### ❌ System PATH Modification

**Rejected:** Requires admin privileges, affects other apps, security risk

### ❌ Wrapper Scripts

**Rejected:** Platform-specific, adds complexity, harder to maintain

### ✅ Runtime Hook + Module Detection (Chosen)

**Advantages:** Automatic, safe, cross-platform, no admin required

---

**Summary:** The automatic PATH configuration ensures bundled Tesseract and Ghostscript work immediately in production builds, with zero user configuration required. It's safe, fast, cross-platform, and transparent to end users.



