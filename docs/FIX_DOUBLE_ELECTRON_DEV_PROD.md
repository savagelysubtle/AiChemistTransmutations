# Fix: Dev and Non-Dev Electron Apps Launching Together

## Problem

When running "Dev: Full Stack Watch", both a development version and a production version of Electron were launching.

## Root Cause

**Two Electron instances were being launched:**

1. **vite-plugin-electron** - Auto-launched Electron when Vite dev server started
2. **electron:dev script** - Manually launched Electron via our wrapper script

**Result:** Two Electron windows - one from vite-plugin-electron (dev mode) and one from our script (production mode because NODE_ENV wasn't set).

## Fixes Applied

### 1. Disabled vite-plugin-electron Auto-Launch

**File:** `gui/vite.config.ts`

**Before:**
```typescript
{
  entry: 'src/main/main.ts',
  // No onstart - vite-plugin-electron auto-launches Electron
  vite: { ... }
}
```

**After:**
```typescript
{
  entry: 'src/main/main.ts',
  onstart(options) {
    // Don't auto-launch Electron - we'll launch it manually
    console.log('📦 Electron main process built. Launch Electron manually via "npm run electron:dev"');
  },
  vite: { ... }
}
```

**What it does:**
- ✅ vite-plugin-electron builds the Electron main/preload processes
- ✅ But doesn't auto-launch Electron
- ✅ We control Electron launch via our script

### 2. Set NODE_ENV in Electron Wrapper

**File:** `gui/scripts/electron-with-cleanup.js`

**Added:**
```javascript
// Set NODE_ENV to development for dev mode
process.env.NODE_ENV = 'development';

const electron = spawn(electronPath, [guiDir], {
  env: {
    ...process.env,
    NODE_ENV: 'development'  // Explicitly set to development
  }
});
```

**What it does:**
- ✅ Ensures Electron runs in development mode
- ✅ Loads from Vite dev server (http://localhost:3000)
- ✅ Opens DevTools automatically

## How It Works Now

### Process Flow

```
1. Run: bun run dev:fullstack
   ↓
2. Concurrently starts 3 processes:
   ├─ Frontend (vite)
   │  └─ vite-plugin-electron builds main/preload
   │  └─ Does NOT auto-launch Electron ✅
   ├─ Python Watcher (nodemon)
   └─ Electron (electron:dev script)
      └─ Launches Electron with NODE_ENV=development ✅
      └─ Loads from http://localhost:3000 ✅
   ↓
3. Only ONE Electron window opens ✅
```

## Verification

### Before Fix
```
Run: bun run dev:fullstack
Result:
  - Electron window 1 (dev mode, from vite-plugin-electron)
  - Electron window 2 (production mode, from our script)
  ❌ Two windows!
```

### After Fix
```
Run: bun run dev:fullstack
Result:
  - Electron window 1 (dev mode, from our script)
  ✅ Only one window!
```

### Check NODE_ENV

In Electron DevTools console:
```javascript
console.log(process.env.NODE_ENV)
// Should output: "development"
```

### Check Window Source

In Electron DevTools:
- **Dev mode**: Should load from `http://localhost:3000`
- **Production mode**: Would load from `file://` path to `dist/index.html`

## Files Changed

1. **`gui/vite.config.ts`**
   - Added `onstart` callback to prevent auto-launch
   - vite-plugin-electron now only builds, doesn't launch

2. **`gui/scripts/electron-with-cleanup.js`**
   - Set `NODE_ENV=development` explicitly
   - Pass NODE_ENV to Electron process via env

## Additional Benefits

- ✅ **Single source of truth**: Only our script launches Electron
- ✅ **Better control**: We control when Electron starts
- ✅ **Proper cleanup**: Our script handles cleanup properly
- ✅ **Consistent environment**: NODE_ENV always set correctly

## Troubleshooting

### If Electron Still Launches Twice

1. **Check vite.config.ts:**
   ```typescript
   onstart(options) {
     // Should NOT call options.startup()
     // Should just log or do nothing
   }
   ```

2. **Check running processes:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*electron*"}
   ```
   Should see only 1 Electron process

3. **Check NODE_ENV:**
   - In Electron DevTools: `console.log(process.env.NODE_ENV)`
   - Should be "development"

### If Electron Loads Production Files

**Problem**: Electron loads from `dist/index.html` instead of dev server

**Solution**: Check NODE_ENV is set:
```javascript
// In electron-with-cleanup.js
process.env.NODE_ENV = 'development';
```

### If Vite Dev Server Not Found

**Problem**: Electron can't connect to http://localhost:3000

**Solution**:
- Make sure `dev:frontend` is running
- Check Vite port matches (default 3000)
- Check Vite server started before Electron

## Summary

**Problem**: Two Electron apps launching (dev + production)
**Cause**: vite-plugin-electron auto-launch + our script + missing NODE_ENV
**Fix**: Disable auto-launch + set NODE_ENV=development
**Result**: Only one Electron window in dev mode ✅

---

**Status**: ✅ Fixed - Only one Electron window opens in development mode!



















