# Watcher Cleanup Documentation

## Overview

The development environment now includes automatic cleanup that ensures all watchers (Python, Frontend) stop when the Electron app closes.

## 🔄 How It Works

### Automatic Cleanup Mechanism

When you run `bun run dev:fullstack`, the system uses **concurrently** with special flags:

```json
"dev:fullstack": "concurrently --kill-others --kill-others-on-fail ..."
```

**Key Flags:**
- `--kill-others`: When one process exits, kill all others
- `--kill-others-on-fail`: When one process fails, kill all others

### Process Flow

```
User runs: bun run dev:fullstack
    ↓
Concurrently starts 3 processes:
  ├─ Frontend (Vite)
  ├─ Python Watcher (Nodemon)
  └─ Electron (via electron-with-cleanup.js)
    ↓
User closes Electron window
    ↓
electron-with-cleanup.js detects exit
    ↓
Exits with code 0
    ↓
Concurrently sees Electron process exit
    ↓
--kill-others flag triggers
    ↓
Kills Frontend and Python watcher
    ↓
All processes stopped ✅
```

## 📋 Cleanup Methods

### Method 1: Concurrently Flags (Primary)

**In `package.json`:**
```json
"dev:fullstack": "concurrently --kill-others --kill-others-on-fail ..."
```

**How it works:**
- When Electron process exits → Concurrently kills other processes
- When any process fails → Concurrently kills all processes
- Clean, automatic cleanup

### Method 2: Electron Wrapper Script (Secondary)

**File:** `gui/scripts/electron-with-cleanup.js`

**What it does:**
- Wraps Electron process
- Detects when Electron closes
- Exits cleanly to trigger concurrently cleanup
- Handles Ctrl+C gracefully

**Features:**
- ✅ Detects window close
- ✅ Handles SIGINT (Ctrl+C)
- ✅ Handles SIGTERM
- ✅ Prevents duplicate cleanup
- ✅ Clean exit codes

### Method 3: VS Code Task Cleanup (Tertiary)

**VS Code tasks** are configured as `isBackground: true` which means:
- VS Code monitors the process
- When you stop the task (Ctrl+C), it kills the process tree
- All child processes are terminated

## 🎯 Usage

### Normal Development

```bash
cd gui
bun run dev:fullstack
```

**To stop:**
- Close Electron window → All watchers stop automatically
- OR Press `Ctrl+C` in terminal → All processes stop

### VS Code Task

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select: **"Dev: Full Stack Watch"**
4. To stop: Press `Ctrl+C` or stop the task

**VS Code will:**
- Kill the main process
- Kill all child processes (watchers)
- Clean up properly

## 🔍 Verification

### Check if Watchers Stop

**Before closing Electron:**
```powershell
# Check running processes
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Select-Object ProcessName, Id
```

**After closing Electron:**
```powershell
# Should see no nodemon/vite processes
Get-Process | Where-Object {$_.ProcessName -like "*node*"}
```

### Expected Behavior

**✅ Good (Clean Exit):**
```
[Electron] Electron window closed
[Electron] Stopping all watchers...
[Frontend] Process killed
[Python] Process killed
All processes stopped
```

**❌ Bad (Watchers Still Running):**
```
[Electron] Electron window closed
[Frontend] Still running... (BAD!)
[Python] Still running... (BAD!)
```

## 🐛 Troubleshooting

### Watchers Don't Stop

**Problem**: After closing Electron, nodemon/vite still running

**Solutions:**

1. **Check concurrently flags:**
   ```json
   "dev:fullstack": "concurrently --kill-others ..."
   ```
   Make sure `--kill-others` is present

2. **Check Electron wrapper:**
   ```bash
   # Test Electron wrapper directly
   node gui/scripts/electron-with-cleanup.js
   ```
   Should exit when Electron closes

3. **Manual cleanup:**
   ```powershell
   # Kill all node processes (nuclear option)
   Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

### VS Code Task Doesn't Stop

**Problem**: Stopping VS Code task doesn't kill watchers

**Solution:**
- Make sure task has `isBackground: true`
- Use "Terminate Task" from command palette
- Or manually kill processes (see above)

### Multiple Instances Running

**Problem**: Multiple dev servers running

**Solution:**
```powershell
# Find and kill all dev processes
Get-Process | Where-Object {
    $_.CommandLine -like "*vite*" -or
    $_.CommandLine -like "*nodemon*" -or
    $_.CommandLine -like "*concurrently*"
} | Stop-Process -Force
```

## 📊 Process Tree

When running `dev:fullstack`:

```
concurrently (main process)
├─ Frontend (Vite dev server)
│  └─ node vite
├─ Python Watcher (Nodemon)
│  └─ node nodemon
└─ Electron (electron-with-cleanup.js)
   └─ electron.exe
```

**When Electron closes:**
```
concurrently detects Electron exit
→ Kills Frontend (Vite)
→ Kills Python Watcher (Nodemon)
→ Exits concurrently
→ All processes stopped ✅
```

## 🎁 Benefits

### Before (No Cleanup)
- Close Electron → Watchers keep running
- Multiple instances accumulate
- Port conflicts
- High CPU usage
- Manual cleanup needed

### After (With Cleanup)
- Close Electron → All watchers stop automatically
- No orphaned processes
- No port conflicts
- Clean system
- One command to stop everything

## 🔧 Advanced Configuration

### Custom Cleanup Script

If you need custom cleanup logic, edit `gui/scripts/electron-with-cleanup.js`:

```javascript
electron.on('exit', (code) => {
  // Add custom cleanup here
  console.log('Running custom cleanup...');

  // Your cleanup code

  process.exit(code || 0);
});
```

### Adjust Concurrently Behavior

Edit `package.json`:

```json
{
  "dev:fullstack": "concurrently
    --kill-others
    --kill-others-on-fail
    --success first
    --raw
    ..."
}
```

**Flags:**
- `--kill-others`: Kill others when one exits
- `--kill-others-on-fail`: Kill others on failure
- `--success first`: Exit when first process succeeds
- `--raw`: Raw output (no prefix)

## 📝 Summary

**What Happens:**
1. Start: `bun run dev:fullstack`
2. Three processes start (Frontend, Python, Electron)
3. Close Electron window
4. Electron wrapper detects exit
5. Concurrently kills other processes
6. All processes stopped ✅

**Key Files:**
- `gui/package.json` - Concurrently configuration
- `gui/scripts/electron-with-cleanup.js` - Electron wrapper
- `.vscode/tasks.json` - VS Code task configuration

**Commands:**
```bash
# Start with cleanup
bun run dev:fullstack

# Stop (close Electron or Ctrl+C)
# All watchers stop automatically
```

---

**Last Updated**: November 2025
**Status**: Production Ready ✅



















