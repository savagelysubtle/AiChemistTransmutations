# Fix: Double Electron Launch Issue

## Problem

When running "Dev: Full Stack Watch" via VS Code (Ctrl+Shift+P), two Electron apps were launching instead of one.

## Root Causes

1. **Incorrect path in wrapper script**: `path.join(__dirname, '.')` was pointing to wrong directory
2. **Shell mode enabled**: `shell: true` in spawn options could cause double launching
3. **No single instance lock**: Electron app didn't prevent multiple instances

## Fixes Applied

### 1. Fixed Electron Wrapper Script (`gui/scripts/electron-with-cleanup.js`)

**Before:**
```javascript
const electron = spawn(electronPath, [path.join(__dirname, '.'), ...process.argv.slice(2)], {
  stdio: 'inherit',
  shell: true  // ❌ Could cause double launching
});
```

**After:**
```javascript
const guiDir = path.join(__dirname, '..');  // ✅ Correct path to gui directory

const electron = spawn(electronPath, [guiDir], {
  stdio: 'inherit',
  shell: false,  // ✅ Prevents double launching
  windowsHide: false,
  detached: false
});
```

**Changes:**
- ✅ Fixed path: `path.join(__dirname, '..')` instead of `path.join(__dirname, '.')`
- ✅ Removed extra args: Only pass GUI directory, no `...process.argv.slice(2)`
- ✅ Disabled shell: `shell: false` prevents shell from spawning extra processes
- ✅ Added better error handling and cleanup

### 2. Added Single Instance Lock (`gui/src/main/main.ts`)

**Added:**
```typescript
// Prevent multiple instances of the app
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  console.log('Another instance is already running. Exiting...');
  app.quit();
} else {
  // Handle second instance attempts
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}
```

**What it does:**
- ✅ Prevents multiple Electron windows from opening
- ✅ If second instance attempted, focuses existing window instead
- ✅ Ensures only one app instance runs at a time

## Testing

### Before Fix
```
Run: Ctrl+Shift+P → "Dev: Full Stack Watch"
Result: 2 Electron windows open ❌
```

### After Fix
```
Run: Ctrl+Shift+P → "Dev: Full Stack Watch"
Result: 1 Electron window opens ✅
```

## Verification

To verify the fix works:

1. **Start the task:**
   - Press `Ctrl+Shift+P`
   - Select "Dev: Full Stack Watch"

2. **Check processes:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*electron*"} | Select-Object ProcessName, Id
   ```
   Should see: **Only 1 Electron process** ✅

3. **Check windows:**
   - Should see: **Only 1 Electron window** ✅

4. **Try to launch again:**
   - If you try to run the task again while it's running
   - Should see: Existing window focuses (doesn't open second) ✅

## Files Changed

1. **`gui/scripts/electron-with-cleanup.js`**
   - Fixed path resolution
   - Disabled shell mode
   - Improved error handling

2. **`gui/src/main/main.ts`**
   - Added single instance lock
   - Added second-instance handler

## Additional Improvements

- ✅ Better process tracking with `electron.pid` checks
- ✅ Improved cleanup on exit
- ✅ Better error messages
- ✅ Prevents duplicate cleanup calls

## Summary

**Problem**: Two Electron apps launching
**Cause**: Wrong path + shell mode + no instance lock
**Fix**: Correct path + no shell + single instance lock
**Result**: Only one Electron app launches ✅

---

**Status**: ✅ Fixed - Only one Electron window opens now!



















