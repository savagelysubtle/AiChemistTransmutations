# 🔍 License Activation Comprehensive Logging Guide

## Overview

I've added detailed logging to both the Electron (TypeScript) and Python sides of the license activation system. This will help you diagnose exactly what's happening when activation fails.

---

## 📊 What Gets Logged

### Electron Side (TypeScript)
Located in: `gui/src/main/main.ts` - `runLicenseCommand()` function

#### Startup Information:
- ✅ Command type (activate, get-status, etc.)
- ✅ Argument count
- ✅ License key preview (first 50 chars)
- ✅ Production vs Development mode detection
- ✅ App path
- ✅ Platform (win32, darwin, linux)
- ✅ Environment variables

#### Path Detection:
- ✅ Python executable path (venv or system)
- ✅ Script/exe existence check
- ✅ File accessibility verification
- ✅ Full command to be executed

#### Execution:
- ✅ Process spawn success/failure
- ✅ Process ID (PID)
- ✅ Real-time stdout chunks
- ✅ Real-time stderr chunks
- ✅ Exit code
- ✅ Full stdout/stderr on completion
- ✅ JSON parsing success/failure

### Python Side (Python)
Located in: `src/transmutation_codex/adapters/bridges/license_bridge.py`

#### Startup Information:
- ✅ Python version
- ✅ Script path
- ✅ Project root
- ✅ sys.path entries
- ✅ Command line arguments
- ✅ Import success/failure

#### Command Handling:
- ✅ Command name
- ✅ License key length and preview
- ✅ Function calls to licensing system
- ✅ Success/failure status
- ✅ Exception details with full traceback
- ✅ JSON output preview

---

## 🔎 Where to Find Logs

### Development Mode

#### Electron Logs (Terminal where you run `npm run dev`):
```
================================================================================
LICENSE COMMAND EXECUTION START
================================================================================
Command: activate
Args count: 1
First 50 chars of first arg: AICHEMIST:T/nUi8R7rx5PJjRsx2YAfUUVgywuCabYKME5dk...
Is Production: false
App Path: D:\...\gui\dist-electron\main
Platform: win32
✓ Development mode detected
  Script path: D:\...\license_bridge.py
  ✓ Using venv Python: D:\...\.venv\Scripts\python.exe
  ✓ Script exists and is accessible
Final command to execute:
  Executable: D:\...\.venv\Scripts\python.exe
  Arguments: license_bridge.py activate AICHEMIST:T/nUi8R7rx...Qgg==:eyJl...9d
--------------------------------------------------------------------------------
Spawning Python process...
✓ Process spawned successfully, PID: 12345
[PYTHON STDOUT]: {"success": true, "status": {...}}
[PYTHON STDERR]: [LICENSE_BRIDGE] INFO: LICENSE BRIDGE STARTED
[PYTHON STDERR]: [LICENSE_BRIDGE] INFO: ✓ Successfully imported licensing functions
...
Process exited with code: 0
✓ Successfully parsed JSON result: {...}
================================================================================
```

#### Python Logs (Same terminal, stderr):
```
[LICENSE_BRIDGE] INFO: ================================================================================
[LICENSE_BRIDGE] INFO: LICENSE BRIDGE STARTED
[LICENSE_BRIDGE] INFO: ================================================================================
[LICENSE_BRIDGE] INFO: Python version: 3.13.x
[LICENSE_BRIDGE] INFO: Script path: D:\...\license_bridge.py
[LICENSE_BRIDGE] INFO: Project root: D:\...\AiChemistTransmutations
[LICENSE_BRIDGE] INFO: Arguments: ['license_bridge.py', 'activate', 'AICHEMIST:...']
[LICENSE_BRIDGE] INFO: ✓ Successfully imported licensing functions
[LICENSE_BRIDGE] INFO: Handling activate command
[LICENSE_BRIDGE] INFO: License key length: 500
[LICENSE_BRIDGE] INFO: License key first 50 chars: AICHEMIST:T/nUi8R7rx5PJjRsx2YAfUUVgywuCabYKME5dk...
[LICENSE_BRIDGE] INFO: Calling activate_license_key()
[LICENSE_BRIDGE] INFO: ✓ Activation successful: {...}
[LICENSE_BRIDGE] INFO: Outputting JSON: {"success": true, "status": {...}}
```

### Production Mode (Installed App)

#### Electron Logs (DevTools Console):
Press `F12` or `Ctrl+Shift+I` to open DevTools, then check Console tab.

Same format as development, but with:
```
✓ Production mode detected
  Python executable: C:\...\resources\python-backend\aichemist_transmutation_codex.exe
  ✓ Executable exists and is accessible
```

#### Python Logs:
These go to **stderr** which Electron captures and logs to console as `[PYTHON STDERR]`.

---

## 🐛 Common Error Patterns & Solutions

### Error Pattern 1: "Python backend not found"
```
✗ Executable not found or not accessible
  Python backend not found at: C:\...\aichemist_transmutation_codex.exe
```

**Cause**: Production build incomplete or wrong path
**Solution**: Rebuild with `npm run build`

---

### Error Pattern 2: "Failed to spawn process"
```
✗ Failed to spawn process: spawn ENOENT
```

**Cause**: Python executable doesn't exist or isn't in PATH
**Solution**:
- Development: Check venv exists (`.venv/Scripts/python.exe`)
- Production: Rebuild installer

---

### Error Pattern 3: "Failed to parse JSON output"
```
✗ Failed to parse JSON output
Raw stdout: (non-JSON text)
```

**Cause**: Python script crashed before outputting JSON
**Solution**: Check `[PYTHON STDERR]` for Python traceback

---

### Error Pattern 4: "License command failed with code 1"
```
✗ Command failed with non-zero exit code
exitCode: 1
stderr: [LICENSE_BRIDGE] ERROR: ✗ Activation failed: Invalid license key
```

**Cause**: License validation failed in Python
**Solution**: Check stderr for specific error (invalid key, expired, etc.)

---

### Error Pattern 5: "Import error"
```
[LICENSE_BRIDGE] ERROR: ✗ Failed to import licensing functions
[LICENSE_BRIDGE] ERROR: Traceback: ModuleNotFoundError: No module named 'transmutation_codex'
```

**Cause**: Python can't find the transmutation_codex package
**Solution**:
- Development: Ensure venv activated and package installed
- Production: Rebuild with PyInstaller

---

## 📝 How to Use Logs for Debugging

### Step 1: Reproduce the Error
1. Open DevTools (F12) if using installed app
2. Try to activate license
3. Note the error message

### Step 2: Find the Failure Point
Look for the first `✗` in the logs:
- Electron logs show where process failed
- Python logs show where activation failed

### Step 3: Check Full Context
- Exit code tells you the error type:
  - `0` = Success
  - `1` = Python caught exception
  - `2` = Python crashed before error handler
  - Other = OS/spawn error

### Step 4: Read the Traceback
If Python side:
```
[LICENSE_BRIDGE] ERROR: Traceback:
  File "...", line X, in activate_license_key
    ...
  ValidationError: Invalid signature
```

This tells you exactly what went wrong.

---

## 🧪 Testing the Logging

### Test 1: Development Mode
```powershell
cd gui
npm run dev

# In the app:
# 1. Click "Enter License"
# 2. Paste your key
# 3. Click Activate
# 4. Check terminal for logs
```

### Test 2: Production Mode
```powershell
# Install the app
gui\release\1.0.1\AiChemist Transmutation Codex Setup 1.0.1.exe

# Run the app
# Press F12 to open DevTools
# Try to activate license
# Check Console tab for logs
```

### Test 3: Command Line (Bypass Electron)
```powershell
# Development
python src/transmutation_codex/adapters/bridges/license_bridge.py activate "YOUR_KEY"

# Production
gui\release\1.0.1\win-unpacked\resources\python-backend\aichemist_transmutation_codex.exe -m transmutation_codex.adapters.bridges.license_bridge activate "YOUR_KEY"
```

---

## 📊 Log Output Examples

### Successful Activation
```
LICENSE COMMAND EXECUTION START
✓ Production mode detected
✓ Executable exists and is accessible
✓ Process spawned successfully, PID: 12345
[PYTHON STDOUT]: {"success": true, "status": {"license_type": "paid", "activated": true, ...}}
Process exited with code: 0
✓ Successfully parsed JSON result
LICENSE COMMAND EXECUTION END
```

### Failed Activation (Invalid Key)
```
LICENSE COMMAND EXECUTION START
✓ Production mode detected
✓ Executable exists and is accessible
✓ Process spawned successfully, PID: 12346
[PYTHON STDERR]: [LICENSE_BRIDGE] ERROR: ✗ Activation failed: Invalid license signature
[PYTHON STDERR]: [LICENSE_BRIDGE] ERROR: Exception type: ValidationError
[PYTHON STDOUT]: {"success": false, "error": "Invalid license signature"}
Process exited with code: 1
✗ Command failed with non-zero exit code
LICENSE COMMAND EXECUTION END
```

---

## 🎯 Quick Debugging Checklist

When activation fails:

- [ ] Check if it's Production or Development mode
- [ ] Verify Python executable exists
- [ ] Check exit code (0=success, 1=validation error, 2=crash)
- [ ] Read first `✗` in logs
- [ ] Check for `[PYTHON STDERR]` errors
- [ ] Look for full traceback
- [ ] Verify license key is complete (not truncated)
- [ ] Check if imports succeeded
- [ ] Verify project root path is correct

---

## 🔧 Files Modified

1. `gui/src/main/main.ts` - Enhanced `runLicenseCommand()` with comprehensive logging
2. `src/transmutation_codex/adapters/bridges/license_bridge.py` - Added startup logging, import verification, and detailed error reporting

---

## ✅ Next Steps

1. **Rebuild the installer**: `cd gui && npm run build`
2. **Test in development**: `npm run dev` and check terminal logs
3. **Test production build**: Install and check DevTools console
4. **Share logs**: If error persists, share the full log output

With this logging, we can pinpoint EXACTLY where and why activation fails! 🎯



















