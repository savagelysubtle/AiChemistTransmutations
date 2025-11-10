# First Build - Pre-Flight Checklist

**Date:** October 22, 2025
**Build Target:** Windows Executable (Python Backend)

---

## ✅ Pre-Build Checklist

### Environment Setup

- [ ] Python 3.13+ installed
- [ ] UV package manager installed
- [ ] Node.js 18+ installed (for GUI later)
- [ ] All dependencies synced (`uv sync --all-groups`)
- [ ] Virtual environment activated

### External Dependencies

- [ ] Tesseract OCR installed
- [ ] Ghostscript installed
- [ ] Pandoc installed
- [ ] Dependencies findable by `prepare_dependencies.py`

### Configuration

- [ ] `config/default_config.yaml` present
- [ ] `config/production_config.yaml` present
- [ ] No hardcoded secrets in code

### Build Scripts Ready

- [ ] `scripts/prepare_dependencies.py` exists
- [ ] `scripts/runtime_hook_paths.py` exists
- [ ] `transmutation_codex.spec` present (or will be auto-generated)

---

## 🚀 Build Steps

### Step 1: Sync Dependencies

```powershell
# From project root
uv sync --all-groups
```

### Step 2: Prepare External Dependencies

```powershell
python scripts/prepare_dependencies.py --platform windows
```

This will:

- Locate Tesseract, Ghostscript, Pandoc
- Copy them to `build/resources/`
- Prepare for bundling

### Step 3: Build Python Backend

```powershell
# Clean previous builds
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue

# Run PyInstaller
uv run pyinstaller transmutation_codex.spec --clean --noconfirm
```

If `transmutation_codex.spec` doesn't exist, PyInstaller will create a basic one. You can then customize it.

### Step 4: Test the Executable

```powershell
# Navigate to the built executable
cd dist\transmutation_codex

# Test basic functionality
.\transmutation_codex.exe --help

# Test a simple conversion (if you have a test file)
.\transmutation_codex.exe --type md2pdf --input test.md --output test.pdf
```

---

## 🔍 Troubleshooting

### Issue: PyInstaller not found

**Solution:** Install it: `uv add --dev pyinstaller`

### Issue: External dependencies not found

**Solution:**

1. Verify they're installed and in PATH
2. Run `python scripts/check_premium_dependencies.py`
3. Manually specify paths in `prepare_dependencies.py` if needed

### Issue: Import errors in built exe

**Solution:**

1. Add missing packages to `hiddenimports` in `.spec` file
2. Rebuild with `--clean` flag

### Issue: "Module not found" at runtime

**Solution:**

1. Check `runtime_hook_paths.py` is working
2. Verify `datas` section in `.spec` includes all config files
3. Add to `datas`: `('config/*.yaml', 'config')`

---

## 📊 Expected Output

After successful build:

```
dist/
└── transmutation_codex/
    ├── transmutation_codex.exe  (main executable)
    ├── config/                   (configuration files)
    ├── resources/                (Tesseract, Ghostscript, Pandoc)
    └── _internal/                (Python libraries and dependencies)
```

**Size:** ~150-250 MB (depending on dependencies)

---

## ✨ Next Steps After Successful Build

1. **Test thoroughly** - Try multiple conversion types
2. **Package with GUI** - Build the Electron frontend
3. **Create installer** - Use NSIS or electron-builder
4. **Sign the executable** - Get code signing certificate

---

## 🎯 Full Build Command (All-in-One)

```powershell
# Complete build from scratch
uv sync --all-groups
python scripts/prepare_dependencies.py --platform windows
Remove-Item -Path "build","dist" -Recurse -Force -ErrorAction SilentlyContinue
uv run pyinstaller transmutation_codex.spec --clean --noconfirm

# Test
cd dist\transmutation_codex
.\transmutation_codex.exe --help
```

---

**Ready to build!** 🚀
