# VS Code Build Tasks Documentation

## Overview

This document describes all available build tasks configured in `.vscode/tasks.json` for the AiChemist Transmutation Codex project.

## How to Use

### Running Tasks

1. **Keyboard Shortcut**: Press `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (Mac)
2. **Command Palette**: Press `Ctrl+Shift+P`, type "Tasks: Run Task", select your task
3. **Menu**: Terminal → Run Task

### Default Build Task

The default build task (runs with `Ctrl+Shift+B`) is **"Build: Full Application"** which builds everything.

## Available Tasks

### 🏗️ Build Tasks

#### `Build: Full Application` ⭐ (Default)
**What it does**: Builds the complete application including Python backend and Electron installer

**Dependencies**:
- Build: Python Backend
- Build: Electron Installer

**Use when**: Creating a complete release build

**Output**:
- Python wheel in `dist/`
- Electron installer in `gui/release/X.X.X/`

---

#### `Build: Python Backend`
**What it does**: Builds the Python backend wheel package using UV

**Command**: `uv build --wheel --out-dir dist`

**Use when**:
- You've changed Python code
- Need to update the backend for GUI integration

**Output**: `dist/aichemist_transmutation_codex-X.X.X-py3-none-any.whl`

---

#### `Build: Electron Installer`
**What it does**: Builds the complete Electron installer with GUI and Python backend

**Command**: `bun run electron:build` (in `gui/` directory)

**Steps performed**:
1. Builds React app with Vite
2. Builds Electron main/preload processes
3. Packages Python backend
4. Creates NSIS installer
5. Creates portable executable

**Use when**: Creating the final installer for distribution

**Output** (in `gui/release/X.X.X/`):
- `AiChemist Transmutation Codex Setup X.X.X.exe` (Installer)
- `AiChemist Transmutation Codex X.X.X.exe` (Portable)
- `latest.yml` (Update metadata)
- `win-unpacked/` (Unpacked files)

---

#### `Build: GUI Only (Development)`
**What it does**: Builds only the React frontend for development

**Command**: `bun run build` (in `gui/` directory)

**Use when**:
- Testing frontend changes
- Quick build without Electron packaging

**Output**: `gui/dist/` (static assets)

---

#### `Package: Python Standalone`
**What it does**: Creates a standalone Python executable using PyInstaller

**Command**: `pyinstaller --onefile --name=aichemist_transmutation_codex src/transmutation_codex/adapters/cli/main.py`

**Use when**:
- Need standalone CLI tool
- Testing Python packaging

**Output**: `dist/aichemist_transmutation_codex.exe`

**Note**: Requires PyInstaller: `pip install pyinstaller`

---

### 🧹 Clean Tasks

#### `Clean: All Build Artifacts`
**What it does**: Removes all build artifacts from both Python and GUI

**Dependencies**:
- Clean: Python Build
- Clean: GUI Build

**Use when**: Starting fresh or troubleshooting build issues

---

#### `Clean: Python Build`
**What it does**: Removes Python build artifacts

**Removes**:
- `dist/`
- `build/`
- `*.egg-info/`
- `.pytest_cache/`
- `__pycache__/`

---

#### `Clean: GUI Build`
**What it does**: Removes GUI build artifacts

**Removes** (from `gui/`):
- `dist/`
- `dist-electron/`
- `release/`

---

### 🧪 Test Tasks

#### `Test: Run All Tests`
**What it does**: Runs all Python tests with coverage

**Command**: `pytest -v --cov=transmutation_codex --cov-report=html`

**Use when**: Before committing changes

**Output**:
- Test results in terminal
- Coverage report in `htmlcov/index.html`

---

#### `Test: Unit Tests Only`
**What it does**: Runs only unit tests (faster)

**Command**: `pytest -v -m unit`

**Use when**: Quick validation of code changes

---

### 🔍 Lint Tasks

#### `Lint: Python (Ruff)`
**What it does**: Checks Python code for style and errors

**Command**: `ruff check src`

**Use when**: Before committing Python changes

**Fix issues**: Run `ruff check src --fix` in terminal

---

#### `Lint: GUI (ESLint)`
**What it does**: Checks TypeScript/React code for style and errors

**Command**: `bun run lint` (in `gui/` directory)

**Use when**: Before committing GUI changes

---

### 📦 Install Tasks

#### `Install: All Dependencies`
**What it does**: Installs all Python and GUI dependencies

**Dependencies**:
- Install: Python Dependencies
- Install: GUI Dependencies

**Use when**:
- Setting up project for first time
- After pulling updates with dependency changes

---

#### `Install: Python Dependencies`
**What it does**: Installs Python dependencies using UV

**Command**: `uv sync --all-groups`

**Installs**:
- Core dependencies
- Development dependencies
- Test dependencies
- Documentation dependencies

---

#### `Install: GUI Dependencies`
**What it does**: Installs GUI dependencies using Bun

**Command**: `bun install` (in `gui/` directory)

**Installs**: All packages from `gui/package.json`

---

### 🚀 Development Tasks

#### `Dev: Start GUI`
**What it does**: Starts Vite development server for GUI

**Command**: `bun run dev` (in `gui/` directory)

**Use when**: Developing React components

**Opens**: http://localhost:5173 (or similar)

**Note**: Runs in background, use terminal to stop

---

#### `Dev: Start Electron`
**What it does**: Starts Electron in development mode

**Command**: `bun run electron:dev` (in `gui/` directory)

**Use when**: Testing full Electron app with hot reload

**Note**: Runs in background

---

## Common Workflows

### 🏁 First Time Setup

```
1. Install: All Dependencies
2. Build: Full Application
3. Test: Run All Tests
```

### 📝 Daily Development

```
1. Dev: Start Electron    (for GUI development)
   OR
   Test: Unit Tests Only   (for Python development)
2. Make changes
3. Lint: Python/GUI
4. Test: Run All Tests
5. Build: Full Application (before committing)
```

### 🚢 Creating a Release

```
1. Clean: All Build Artifacts
2. Install: All Dependencies
3. Lint: Python (Ruff)
4. Lint: GUI (ESLint)
5. Test: Run All Tests
6. Build: Full Application
7. Test installer manually
```

### 🐛 Troubleshooting Builds

```
1. Clean: All Build Artifacts
2. Install: All Dependencies
3. Build: Python Backend    (test Python separately)
4. Build: GUI Only          (test GUI separately)
5. Build: Electron Installer (final package)
```

## Task Groups

Tasks are organized into these groups:

| Group | Tasks |
|-------|-------|
| **build** | Build and lint tasks |
| **test** | Testing tasks |
| **none** | Install and clean tasks |

## Keyboard Shortcuts

- **`Ctrl+Shift+B`**: Run default build task (Build: Full Application)
- **`Ctrl+Shift+T`**: Run last task
- **`Ctrl+Shift+P` → "Tasks: Run Task"**: Show all tasks

## Task Output

### Where to Find Output

- **Terminal Panel**: Shows command output
- **Problems Panel** (`Ctrl+Shift+M`): Shows linter errors
- **Build artifacts**: See each task's output section

### Build Output Locations

```
project-root/
├── dist/                          # Python wheels
├── gui/
│   ├── dist/                      # React build
│   ├── dist-electron/             # Electron build
│   └── release/
│       └── X.X.X/                 # Installers
│           ├── AiChemist Transmutation Codex Setup X.X.X.exe
│           ├── AiChemist Transmutation Codex X.X.X.exe (portable)
│           ├── latest.yml
│           └── win-unpacked/
└── htmlcov/                       # Test coverage reports
```

## Customizing Tasks

To modify tasks, edit `.vscode/tasks.json`:

```json
{
  "label": "Your Task Name",
  "type": "shell",
  "command": "your-command",
  "args": ["arg1", "arg2"],
  "options": {
    "cwd": "${workspaceFolder}/subdirectory"
  },
  "group": "build",
  "presentation": {
    "reveal": "always",
    "panel": "shared"
  }
}
```

## Task Variables

Available VS Code variables:

- `${workspaceFolder}`: Project root directory
- `${file}`: Current file path
- `${fileBasename}`: Current filename
- `${fileDirname}`: Current file's directory

## Troubleshooting

### Task Not Found

**Problem**: "Task 'X' not found"

**Solution**:
1. Check `.vscode/tasks.json` exists
2. Reload VS Code: `Ctrl+Shift+P` → "Reload Window"

### Build Fails

**Problem**: Build task fails with errors

**Solutions**:
1. Run `Clean: All Build Artifacts`
2. Run `Install: All Dependencies`
3. Check terminal output for specific errors
4. Ensure all tools are installed (UV, Bun, Python)

### Permission Errors

**Problem**: "Access denied" or permission errors

**Solutions**:
1. Close running application
2. Run VS Code as administrator (if needed)
3. Check antivirus isn't blocking files

### Python Command Not Found

**Problem**: `uv` or `pytest` not found

**Solution**:
1. Ensure Python environment is activated
2. Run `Install: Python Dependencies`
3. Add Python/UV to PATH

### Bun Command Not Found

**Problem**: `bun` not found

**Solution**:
1. Install Bun: https://bun.sh/
2. Restart terminal/VS Code
3. Verify: `bun --version`

## Performance Tips

1. **Parallel Builds**: Build Python and GUI separately for faster iteration
2. **Incremental Builds**: Use specific build tasks instead of full build
3. **Skip Tests**: During development, run tests separately
4. **Clean Selectively**: Clean only what you need (Python or GUI)

## CI/CD Integration

These tasks can be automated in CI/CD:

```bash
# GitHub Actions / Azure Pipelines
- Run: Install Dependencies
- Run: Lint Python
- Run: Lint GUI
- Run: Test All
- Run: Build Full Application
```

## Additional Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **Bun Documentation**: https://bun.sh/docs
- **Electron Builder**: https://www.electron.build/
- **VS Code Tasks**: https://code.visualstudio.com/docs/editor/tasks

---

**Last Updated**: November 2025
**VS Code Version**: 1.80+
**Project Version**: 1.0.2

