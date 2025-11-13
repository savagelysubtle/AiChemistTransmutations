# 🚀 Pre-Release Checklist - Gumroad Integration Release

## 📊 **Current Versions**

### Python Package (pyproject.toml)

- **Current:** `0.1.0`
- **Suggested:** `0.2.0` (minor bump for Gumroad integration feature)

### Electron App (gui/package.json)

- **Current:** `1.0.5`
- **Suggested:** `1.1.0` (minor bump for Gumroad integration)

---

## ✅ **Pre-Build Checklist**

### 🔢 **1. Version Bumping**

**Python Package:**

```toml
# pyproject.toml line 7
version = "0.2.0"  # ← Update from 0.1.0
```

**Electron App:**

```json
// gui/package.json line 3
"version": "1.1.0",  // ← Update from 1.0.5
```

**Why these versions?**

- Added major new feature (Gumroad licensing)
- Breaking change from RSA to Gumroad API
- Supabase integration added
- Justifies minor version bump (x.Y.z)

---

### 🔐 **2. Environment Variables**

**Check these files exist and are configured:**

- [ ] `.env` (root) - Contains Supabase credentials
- [ ] `gui/.env` - Contains Supabase credentials
- [ ] Both files in `.gitignore` ✅

**Verify NOT committing:**

```bash
git status
# Should NOT see:
# - .env
# - gui/.env
# - gumroad_license.json
# - *_license.json
```

---

### 🗄️ **3. Supabase Setup**

- [x] Database tables created (`gumroad_licenses`, `license_usage`)
- [x] Row Level Security (RLS) enabled
- [x] Environment variables configured
- [x] Integration tested with real license key
- [x] Can view data in Supabase dashboard

**Test Command:**

```bash
# Verify Supabase connection
python -c "from transmutation_codex.core.licensing import SupabaseBackend; print('✅ Supabase ready!' if SupabaseBackend() else '❌ Failed')"
```

---

### 🔑 **4. Gumroad Product**

- [x] Product created: "AiChemist Transmutation Codex"
- [x] Product ID: `E7oYHqtGSVBBWcpbCFyF-A==`
- [x] License keys enabled ✅
- [x] Price set: $29
- [ ] Product description updated (per-device pricing)
- [ ] Product images/screenshots added
- [ ] Purchase tested with real transaction

**Product ID Locations to Verify:**

```python
# src/transmutation_codex/core/licensing/license_manager.py
PRODUCT_MAPPING = {
    "basic": "E7oYHqtGSVBBWcpbCFyF-A==",  # ✅ Correct
}

# scripts/licensing/gumroad/webhook_server.py
PRODUCT_MAP = {
    "E7oYHqtGSVBBWcpbCFyF-A==": {"type": "basic", "max_activations": 1},  # ✅ Correct
}
```

---

### 🧪 **5. Testing**

**License Activation:**

- [x] Activate with real Gumroad license key
- [x] Verify license stored in `%APPDATA%/AiChemist/gumroad_license.json`
- [x] Verify activation recorded in Supabase
- [x] Machine fingerprint working
- [ ] Deactivation works
- [ ] Reactivation after deactivation works

**Offline Mode:**

- [ ] Test with no internet connection
- [ ] Verify cached license still works
- [ ] Verify error messages are user-friendly

**Trial Mode:**

- [ ] Fresh install shows trial status
- [ ] Trial conversions tracked (limit: 50)
- [ ] Trial expiry enforced

---

### 📝 **6. Documentation**

**Files to Review:**

- [x] `docs/GUMROAD_INTEGRATION_SUCCESS.md` - Setup complete
- [x] `docs/SUPABASE_INTEGRATION_COMPLETE.md` - Supabase guide
- [x] `docs/SUPABASE_QUICK_REFERENCE.md` - SQL queries
- [x] `docs/MULTI_CHANNEL_LICENSING_ARCHITECTURE.md` - Multi-channel
- [ ] `README.md` - Update with licensing info
- [ ] `CHANGELOG.md` - Add v1.1.0 changes

---

### 🏗️ **7. Build Configuration**

**Check electron-builder settings:**

```json
// gui/package.json
{
  "version": "1.1.0", // ← MUST match!
  "build": {
    "appId": "com.aichemist.transmutationcodex", // ✅
    "productName": "AiChemist Transmutation Codex", // ✅
    "directories": {
      "output": "release/${version}" // ← Will create release/1.1.0/
    }
  }
}
```

**Verify output directory will be:**

```
gui/release/1.1.0/
├── AiChemist Transmutation Codex Setup 1.1.0.exe
└── AiChemist Transmutation Codex 1.1.0.exe (portable)
```

---

### 🔨 **8. Build Process**

**Pre-build steps:**

```bash
# 1. Clean old builds
cd gui
rm -rf dist/ dist-electron/ release/

# 2. Install dependencies (if needed)
bun install

# 3. Build Python backend first
cd ..
uv sync
# Build Python distributable if needed

# 4. Build Electron app
cd gui
bun run build
# or
npm run electron:build
```

**Expected build output:**

```
✅ Vite build successful
✅ Electron main process compiled
✅ Electron renderer compiled
✅ Python backend bundled
✅ NSIS installer created
✅ Portable executable created
```

---

### 🧹 **9. Clean Build Environment**

**Remove development artifacts:**

```bash
# Python
rm -rf .venv/ .uv_cache/ __pycache__/ *.pyc
rm -rf dist/ build/ *.egg-info/

# Node
cd gui
rm -rf node_modules/.cache/
rm -rf dist/ dist-electron/

# Temporary files
rm -rf tmp/ temp/ logs/
```

**Keep these:**

- ✅ `.env` files (needed for build)
- ✅ `config/` directory
- ✅ `assets/` directory

---

### 📦 **10. Installer Testing**

**After build completes:**

1. **Test NSIS Installer:**

   ```
   gui/release/1.1.0/AiChemist Transmutation Codex Setup 1.1.0.exe
   ```

   - [ ] Installer launches
   - [ ] Can choose install directory
   - [ ] Desktop shortcut created
   - [ ] Start menu entry created
   - [ ] App launches after install
   - [ ] Icon displays correctly

2. **Test Portable Version:**

   ```
   gui/release/1.1.0/AiChemist Transmutation Codex 1.1.0.exe
   ```

   - [ ] Runs without installation
   - [ ] No admin rights required
   - [ ] Creates data directory in %APPDATA%

3. **Test License Activation:**
   - [ ] Enter Gumroad license key
   - [ ] Activation successful
   - [ ] Check Supabase for activation record
   - [ ] Perform a conversion
   - [ ] Check Supabase for usage log

---

### 🔍 **11. Security Checks**

**Verify secrets are NOT in build:**

```bash
# Extract and search installer
7z x "gui/release/1.1.0/AiChemist Transmutation Codex Setup 1.1.0.exe" -o./extracted/
grep -r "SUPABASE" ./extracted/  # Should find ONLY in .env file
grep -r "sk-" ./extracted/  # Should NOT find service keys
grep -r "private_key" ./extracted/  # Should NOT find private keys
```

**Expected:**

- ✅ `.env` file included (for Supabase URL/anon key)
- ❌ NO service keys in code
- ❌ NO private RSA keys in build
- ❌ NO hardcoded credentials

---

### 📋 **12. Release Notes**

**Create CHANGELOG entry for v1.1.0:**

```markdown
## [1.1.0] - 2025-11-13

### 🎉 Major Features

- **Gumroad Integration**: Native support for Gumroad license keys
- **Supabase Backend**: Online license tracking and usage analytics
- **Multi-Device Support**: Single product, per-device pricing ($29/device)

### ✨ Enhancements

- Real-time license validation via Gumroad API
- Offline license caching (24 hours)
- Machine fingerprinting for activation tracking
- Usage analytics tracked to Supabase
- Graceful offline fallback mode

### 🔧 Changes

- **BREAKING**: Removed RSA-based licensing
- Updated license file format to `gumroad_license.json`
- Environment variables now required for Supabase (optional)

### 🐛 Bug Fixes

- Improved error messages for license failures
- Better handling of network timeouts
- Fixed trial counter persistence

### 📚 Documentation

- Added Gumroad setup guide
- Added Supabase integration guide
- Updated multi-channel architecture docs

### 🔐 Security

- Enhanced .gitignore patterns for sensitive files
- Removed hardcoded credentials
- Secure environment variable handling
```

---

### ⚙️ **13. Version Bump Commands**

**Automatic version bump (recommended):**

```bash
# Python
cd /path/to/project
sed -i 's/version = "0.1.0"/version = "0.2.0"/' pyproject.toml

# Node/Electron
cd gui
npm version minor  # 1.0.5 → 1.1.0
# or manually edit package.json
```

**Manual version bump:**

```bash
# Edit files directly
nano pyproject.toml  # Change line 7: version = "0.2.0"
nano gui/package.json  # Change line 3: "version": "1.1.0"
```

---

### 🚀 **14. Final Build Commands**

```bash
# Full clean build sequence
cd D:\Coding\AiChemistCodex\AiChemistTransmutations

# 1. Update versions first!
# (Edit pyproject.toml and gui/package.json)

# 2. Clean everything
rm -rf gui/dist/ gui/dist-electron/ gui/release/

# 3. Install dependencies
cd gui
bun install

# 4. Build
bun run electron:build

# 5. Verify output
ls -lh release/1.1.0/
```

**Expected files:**

```
release/1.1.0/
├── AiChemist Transmutation Codex Setup 1.1.0.exe  (NSIS installer)
├── AiChemist Transmutation Codex 1.1.0.exe        (Portable)
├── builder-debug.yml
├── builder-effective-config.yaml
└── win-unpacked/ (folder)
```

---

### 📤 **15. Distribution**

**Upload to Gumroad:**

1. Create new "Software" product or update existing
2. Upload both files:
   - NSIS Installer (recommended for most users)
   - Portable version (for advanced users)
3. Update product description with version 1.1.0
4. Test download link

**Update Website:**

- [ ] Update download links
- [ ] Add v1.1.0 to release notes
- [ ] Update screenshots if UI changed

---

## ⚠️ **CRITICAL CHECKS Before Release**

### Must Complete:

1. ✅ Version numbers match in both files
2. ✅ Gumroad product ID is correct
3. ✅ Test license activation with REAL key
4. ✅ Verify Supabase records activation
5. ✅ Test fresh install on clean Windows machine
6. ✅ NO secrets committed to git
7. ✅ Build creates proper installer
8. ✅ Installer works and app launches

### Nice to Have:

- [ ] Code signing certificate (for future)
- [ ] Auto-updater configured (for future)
- [ ] Crash reporting setup (for future)

---

## 🎯 **Quick Command Summary**

```bash
# Version bump
sed -i 's/0.1.0/0.2.0/' pyproject.toml
sed -i 's/"version": "1.0.5"/"version": "1.1.0"/' gui/package.json

# Build
cd gui
rm -rf dist/ dist-electron/ release/
bun install
bun run electron:build

# Test
./release/1.1.0/AiChemist\ Transmutation\ Codex\ Setup\ 1.1.0.exe

# Verify version in app
# Help → About (should show 1.1.0)
```

---

## 📊 **Version Strategy**

### Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (1.x.x): Breaking changes, incompatible API
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.1): Bug fixes, backward compatible

### This Release:

- **0.1.0 → 0.2.0**: Minor bump (new Gumroad feature)
- **1.0.5 → 1.1.0**: Minor bump (new licensing system)

### Future Releases:

- **1.1.x → 1.2.x**: Add new converter or major feature
- **1.x.x → 2.0.0**: Major UI overhaul or breaking changes
- **x.x.5 → x.x.6**: Bug fixes only

---

**Status:** Ready for version bump and build! 🚀

**Last Updated:** November 13, 2025
