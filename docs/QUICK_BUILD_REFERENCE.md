# ⚡ Quick Build Reference Card

## 🎯 The 3-Step Build Process

```powershell
# 1️⃣ Close Cursor/VS Code

# 2️⃣ Open PowerShell and navigate
cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui

# 3️⃣ Build
npm run electron:build
```

## 🔧 Common Commands

| Task | Command |
|------|---------|
| **Build installer** | `npm run electron:build` |
| **Generate icons** | `npm run generate-all-icons` |
| **Clean build** | `Remove-Item release -Recurse -Force` |
| **Full rebuild** | `npm run electron:build` |

## 📍 Build Output Location

```
gui/release/1.0.3/
├── AiChemist Transmutation Codex Setup 1.0.3.exe  ← NSIS Installer
├── AiChemist Transmutation Codex 1.0.3.exe        ← Portable
└── win-unpacked/                                   ← Unpacked files
```

## ❗ If Build Fails

**Most Common:** File locked by Cursor
- **Fix:** Close Cursor, build from PowerShell

**Missing Icons:**
```powershell
npm run generate-all-icons
npm run electron:build
```

**Still failing:**
See `BUILD_ISSUES.md` or `BUILD_FAILURE_ACTION_PLAN.md`

## ✅ Success Indicators

```
✓ 1683 modules transformed
✓ built in 3.27s
✓ packaging platform=win32 arch=x64
✓ building target=nsis
✓ building target=portable
```

## 📚 Full Documentation

- **BUILD_GUIDE.md** - Complete build guide
- **BUILD_ISSUES.md** - Troubleshooting
- **BUILD_SUCCESS_SUMMARY.md** - Full success report
- **ICON_FIX_COMPLETE.md** - Icon documentation

---

**Remember:** Close Cursor before building! 🔥
