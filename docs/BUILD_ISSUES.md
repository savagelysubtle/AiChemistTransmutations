# Build Issues & Solutions

## ⚠️ CRITICAL: Cursor File Watcher Locks Build Files

**CONFIRMED ROOT CAUSE:** Cursor's file watcher locks the `app.asar` file during
builds, preventing `electron-builder` from working.

### ✅ PROVEN SOLUTION: Close Cursor Before Building

The build **WILL WORK** if you close Cursor completely before running it.

**Steps:**

1. **Save all your work in Cursor**
2. **Close Cursor completely** (not just the terminal)
3. Open **standalone PowerShell** (not Cursor terminal)
4. Navigate to the GUI directory:
   ```powershell
   cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
   ```
5. Run the build script:
   ```powershell
   .\BUILD_FROM_POWERSHELL.ps1
   ```

**Why This Works:**

- Cursor monitors files in `release/` directory
- When `electron-builder` tries to delete `app.asar`, Cursor has it locked
- Closing Cursor releases all file locks
- Build completes successfully

### Alternative: Use the Helper Script

We've created `BUILD_FROM_POWERSHELL.ps1` which:

- ✅ Checks if Cursor is running (warns you if it is)
- ✅ Runs the build with retry logic
- ✅ Shows clear success/failure messages

---

## Problem: "The process cannot access the file because it is being used by another process"

This error occurs during `electron-builder` packaging when `app.asar` or other
files in the `release` directory are locked by Windows processes.

### Root Causes

1. **Cursor/VS Code File Watcher** - ⚠️ **PRIMARY CAUSE** - Monitors files and
   locks them
2. **Windows Defender** - Real-time scanning locks files as they're created
3. **Windows Search Indexer** - Indexes new files immediately
4. **Running App Instances** - Previous builds still running
5. **Antivirus Software** - Third-party antivirus scanning build output

### Solutions (In Order of Effectiveness)

#### Solution 1: Close Cursor Completely (MOST EFFECTIVE) ✅

**This is the definitive solution based on successful builds.**

1. Save your work
2. Close Cursor/VS Code completely
3. Run build from standalone PowerShell:
   ```powershell
   cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
   .\BUILD_FROM_POWERSHELL.ps1
   ```

#### Solution 2: Add Windows Defender Exclusions (HELPFUL)

This prevents Windows Defender from scanning build directories in real-time,
eliminating file locks.

**Steps:**

1. Open PowerShell **as Administrator**
2. Navigate to `gui/scripts/`
3. Run:
   ```powershell
   .\add-defender-exclusions.ps1
   ```

This adds exclusions for:

- `gui/node_modules`
- `gui/dist`
- `gui/dist-electron`
- `gui/release`
- `gui/build`
- Project `.venv`
- Project `dist` and `build`

**To remove exclusions later:**

```powershell
.\add-defender-exclusions.ps1 -RemoveExclusions
```

#### Solution 3: VS Code Settings (Already Applied)

The `.vscode/settings.json` file has been updated to exclude build directories
from VS Code's file watcher:

```json
{
  "files.watcherExclude": {
    "**/dist/**": true,
    "**/dist-electron/**": true,
    "**/release/**": true,
    "**/build/**": true,
    "**/gui/release/**": true,
    "**/gui/dist/**": true,
    "**/gui/dist-electron/**": true
  }
}
```

**VS Code must be restarted** for these settings to take effect.

#### Solution 3: Use the Robust Build Script

The `build-robust.ps1` script handles locked files by:

- Terminating all Electron processes
- Aggressively cleaning directories
- Renaming locked directories if needed

**Usage:**

```powershell
cd gui
.\scripts\build-robust.ps1
```

Or use the VS Code task:

- Press `Ctrl+Shift+P`
- Type "Run Task"
- Select "Build: Electron Installer (Safe)"

#### Solution 4: Manual Process Termination

Before building, manually close:

1. All instances of the app
2. VS Code (if watching the project)
3. Any file explorers with `release` directory open

Check Task Manager (`Ctrl+Shift+Esc`) for:

- `electron.exe` processes
- `app-builder.exe` processes

#### Solution 5: Clean Build

Completely remove the release directory before building:

```powershell
# From gui directory
Remove-Item -Path release -Recurse -Force -ErrorAction SilentlyContinue
npm run electron:build
```

### Quick Fix Checklist

Before building, ensure:

- [ ] No app instances running
- [ ] VS Code restarted after settings change
- [ ] Windows Defender exclusions added (run as Admin)
- [ ] No file explorers with release folder open
- [ ] Using `build-robust.ps1` script or VS Code task

### Permanent Solution

**For development machines**, the best permanent solution is:

1. **Add Windows Defender exclusions** (one-time setup as Admin)
2. **Update VS Code settings** (already done, restart VS Code)
3. **Use the robust build script** for all builds

This combination eliminates ~95% of file locking issues.

### Advanced: Using Sysinternals Handle

If file locks persist, use Microsoft's Handle tool to identify what's locking
files:

1. Download
   [Handle.exe](https://docs.microsoft.com/en-us/sysinternals/downloads/handle)
2. Run as Administrator:
   ```powershell
   handle.exe app.asar
   ```
3. This shows which process (PID) has the file open
4. Terminate that process before building

### Build Scripts Reference

| Script                        | Purpose                                   | Runs As Admin? |
| ----------------------------- | ----------------------------------------- | -------------- |
| `build-safe.ps1`              | Basic safe build with process termination | No             |
| `build-robust.ps1`            | Aggressive cleanup, renames locked dirs   | No             |
| `add-defender-exclusions.ps1` | Adds Windows Defender exclusions          | **Yes**        |

### Troubleshooting

**"Access Denied" when adding exclusions:**

- Run PowerShell as Administrator
- Check if you have admin rights on the machine

**Still getting file locks after exclusions:**

1. Verify exclusions were added:
   ```powershell
   Get-MpPreference | Select-Object ExclusionPath
   ```
2. Restart your machine (exclusions may need a reboot)
3. Check for third-party antivirus (Defender exclusions don't affect them)

**Build succeeds but creates "release*old*\*" directories:**

- These are renamed locked directories
- Safe to delete after build completes
- The `build-robust.ps1` script auto-cleans them

### CI/CD Builds

For automated builds (GitHub Actions, etc.), file locking isn't typically an
issue because:

- Fresh environment each build
- No file watchers or antivirus
- No previous app instances

If CI builds fail, check:

- Build scripts are executable
- No parallel builds accessing same files
- Sufficient disk space

### Related Issues

- [electron-builder#4299](https://github.com/electron-userland/electron-builder/issues/4299)
- [Stack Overflow: VS Code Locking Files](https://stackoverflow.com/questions/55774005/)

### Support

If these solutions don't resolve the issue:

1. Check Windows Event Viewer for detailed error logs
2. Run `handle.exe app.asar` to identify the locking process
3. Temporarily disable antivirus and try again
4. Try building from a clean PowerShell session (not VS Code's terminal)

---

**Last Updated:** November 2025 **Author:** @savagelysubtle
