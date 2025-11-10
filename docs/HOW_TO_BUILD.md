# 🚀 How to Build the Electron Application

## ⚠️ IMPORTANT: Close Cursor Before Building!

**The #1 reason builds fail:** Cursor's file watcher locks `app.asar` during the build process.

---

## ✅ Recommended Build Process

### Step 1: Save Your Work
Make sure all your files are saved in Cursor.

### Step 2: Close Cursor
**Close Cursor completely** - don't just close the terminal, close the entire application.

### Step 3: Open PowerShell
Open a **standalone PowerShell window** (not Cursor's integrated terminal):
- Press `Win + X`
- Select "Windows PowerShell" or "Terminal"

### Step 4: Navigate to GUI Directory
```powershell
cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
```

### Step 5: Run the Build
```powershell
.\BUILD_FROM_POWERSHELL.ps1
```

This script will:
- ✅ Check if Cursor is still running (and warn you)
- ✅ Terminate any running app instances
- ✅ Clean old build files
- ✅ Build with retry logic (up to 3 attempts)
- ✅ Show clear success/failure messages

---

## 📦 Build Output

If successful, your installer will be at:
```
gui/release/1.0.3/AiChemist Transmutation Codex Setup 1.0.3.exe
```

---

## 🐛 If Build Still Fails

### 1. Verify Cursor is Closed
```powershell
# Check if Cursor is running
Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
```

If you see output, Cursor is still running. Close it completely.

### 2. Add Windows Defender Exclusions
Run as Administrator:
```powershell
cd scripts
.\add-defender-exclusions.ps1
```

### 3. Restart Your Computer
Sometimes file locks persist. A restart clears everything.

### 4. Manual Build (Advanced)
If you want more control:
```powershell
# Clean everything
Remove-Item -Recurse -Force release -ErrorAction SilentlyContinue

# Build
npm run electron:build
```

---

## 🔧 Alternative Build Methods

### From Cursor Terminal (Not Recommended)
If you **must** build from within Cursor:

1. Run the ultimate build script:
   ```powershell
   .\scripts\build-ultimate.ps1
   ```

2. If it fails with file locking:
   - Close Cursor
   - Follow the recommended process above

### Using VS Code Task (Not Recommended)
The VS Code task "Build: Electron Installer (Safe)" exists but may fail due to file locking. Use the standalone PowerShell method instead.

---

## 📋 Build Checklist

- [ ] All changes saved
- [ ] Cursor/VS Code closed completely
- [ ] PowerShell opened (standalone, not in Cursor)
- [ ] Navigated to `gui/` directory
- [ ] Run `.\BUILD_FROM_POWERSHELL.ps1`
- [ ] Wait for build to complete
- [ ] Check `release/1.0.3/` for installer

---

## 🎯 Why This Works

**The Problem:**
- Cursor monitors all files in the workspace
- When `electron-builder` tries to package, it needs to delete and recreate `app.asar`
- Cursor's file watcher has `app.asar` locked for monitoring
- The build fails with "file in use" error

**The Solution:**
- Closing Cursor releases all file locks
- `electron-builder` can freely delete/recreate files
- Build completes successfully

**Proof:**
- Previous build attempts: **FAILED** (Cursor running)
- Build with Cursor closed: **SUCCESS** ✅

---

## 📚 Additional Documentation

- **Detailed Build Issues:** See [BUILD_ISSUES.md](BUILD_ISSUES.md)
- **Full Build Guide:** See [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **Icon Generation:** See [BUILD_GUIDE.md](BUILD_GUIDE.md#icon-generation)

---

**Last Updated:** November 10, 2025
**Status:** ✅ Working Solution Confirmed


