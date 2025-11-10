# VS Code Tasks - Quick Reference

## 🚀 Most Used Tasks

### Build Everything
**Keyboard**: `Ctrl+Shift+B`
**Task**: `Build: Full Application`
**Output**: Complete installer in `gui/release/X.X.X/`

### Start Development
**Task**: `Dev: Start Electron`
**Use**: Opens Electron app with hot reload

### Run Tests
**Task**: `Test: Run All Tests`
**Output**: Test results + coverage report

### Clean Build
**Task**: `Clean: All Build Artifacts`
**Use**: Fresh start for builds

---

## 📋 All Tasks List

| Task Name | What It Does | When To Use |
|-----------|--------------|-------------|
| **Build: Full Application** ⭐ | Builds Python + Electron installer | Release builds |
| **Build: Python Backend** | Builds Python wheel | After Python changes |
| **Build: Electron Installer** | Creates installer | Final packaging |
| **Build: GUI Only** | Builds React app | Frontend testing |
| **Package: Python Standalone** | PyInstaller executable | CLI tool |
| **Clean: All Build Artifacts** | Removes all builds | Fresh start |
| **Clean: Python Build** | Removes Python artifacts | Python clean |
| **Clean: GUI Build** | Removes GUI artifacts | GUI clean |
| **Test: Run All Tests** | All tests + coverage | Before commit |
| **Test: Unit Tests Only** | Fast unit tests | Quick validation |
| **Lint: Python (Ruff)** | Check Python code | Before commit |
| **Lint: GUI (ESLint)** | Check TypeScript/React | Before commit |
| **Install: All Dependencies** | Install everything | First setup |
| **Install: Python Dependencies** | UV install | Python deps |
| **Install: GUI Dependencies** | Bun install | GUI deps |
| **Dev: Start GUI** | Vite dev server | Frontend dev |
| **Dev: Start Electron** | Electron dev mode | Full app dev |

---

## 📁 Build Output Locations

```
dist/                  → Python wheels
gui/dist/              → React build
gui/dist-electron/     → Electron build
gui/release/X.X.X/     → Final installers
  ├── AiChemist Transmutation Codex Setup X.X.X.exe  (Installer)
  ├── AiChemist Transmutation Codex X.X.X.exe        (Portable)
  ├── latest.yml                                      (Updates)
  └── win-unpacked/                                   (Debug)
```

---

## 🎯 Common Workflows

### First Time Setup
```
1. Install: All Dependencies
2. Build: Full Application
3. Test: Run All Tests
```

### Daily Development
```
1. Dev: Start Electron
2. Make changes
3. Lint + Test
4. Commit
```

### Create Release
```
1. Clean: All Build Artifacts
2. Install: All Dependencies
3. Lint: Python + GUI
4. Test: Run All Tests
5. Build: Full Application
6. Test installer manually
```

---

## ⌨️ Keyboard Shortcuts

- `Ctrl+Shift+B` - Run default build (Build: Full Application)
- `Ctrl+Shift+P` → "Tasks: Run Task" - Show all tasks
- `Ctrl+Shift+T` - Rerun last task

---

## 🐛 Quick Fixes

**Build fails?**
1. Run "Clean: All Build Artifacts"
2. Run "Install: All Dependencies"
3. Try again

**Python not found?**
- Check UV is installed: `uv --version`
- Run "Install: Python Dependencies"

**Bun not found?**
- Install Bun: https://bun.sh/
- Restart VS Code

**Permission errors?**
- Close running application
- Run VS Code as admin (if needed)

---

**Full Documentation**: See `docs/VSCODE_TASKS.md`

