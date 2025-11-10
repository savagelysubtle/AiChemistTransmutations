# 🔴 CRITICAL: Build Failure - File Locking Issue

## Current Status

**Issue:** electron-builder fails with "The process cannot access the file because it is being used by another process"
**File:** `gui/release/1.0.3/win-unpacked/resources/app.asar`
**Severity:** **HIGH** - Blocks all production builds

## Immediate Action Required

### Step 1: Add Windows Defender Exclusions (MUST DO AS ADMIN)

1. **Close Cursor completely**
2. Open PowerShell **as Administrator** (not regular PowerShell!)
3. Navigate to the project:
   ```powershell
   cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui\scripts
   .\add-defender-exclusions.ps1
   ```
4. Verify exclusions were added:
   ```powershell
   Get-MpPreference | Select-Object ExclusionPath
   ```
   You should see paths like `D:\Coding\AiChemistCodex\AiChemistTransmutations\gui\release`

### Step 2: Restart Your Computer

**Yes, really.** Windows Defender exclusions sometimes require a reboot to fully take effect.

### Step 3: Build from Clean PowerShell (Not Cursor Terminal)

After reboot:
1. **Do NOT open Cursor/VS Code**
2. Open PowerShell (regular, not admin)
3. Navigate and build:
   ```powershell
   cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
   .\scripts\build-ultimate.ps1
   ```

This script includes retry logic and will attempt the build 3 times with delays.

## Why This Happens

The file lock occurs because **Windows Defender** (or another background process) is scanning `app.asar` immediately after electron-builder creates it, before electron-builder can modify or package it.

**Common Culprits:**
1. Windows Defender Real-Time Protection (**most likely**)
2. Windows Search Indexer
3. Third-party antivirus (Avast, Norton, McAfee, etc.)
4. Cloud sync services (OneDrive, Dropbox scanning the file)
5. VS Code file watcher

## Alternative Solutions (If Above Doesn't Work)

### Option A: Temporarily Disable Windows Defender

**⚠️ Only do this temporarily for building!**

1. Open Windows Security
2. Virus & threat protection
3. Manage settings
4. Turn off Real-time protection
5. Build immediately:
   ```powershell
   npm run electron:build
   ```
6. **Turn Real-time protection back ON**

### Option B: Move Project to Different Drive

If your project is on a cloud-synced drive (OneDrive), move it:

```powershell
# Move to local drive
xcopy /E /H /C /I D:\Coding\AiChemistCodex C:\Dev\AiChemistCodex
cd C:\Dev\AiChemistCodex\gui
npm run electron:build
```

### Option C: Build in Safe Mode with Networking

1. Restart Windows in Safe Mode with Networking
2. Build the application
3. Restart normally

### Option D: Use WSL2 (Windows Subsystem for Linux)

Build in Linux environment to avoid Windows file locks entirely:

```bash
# In WSL2
cd /mnt/d/Coding/AiChemistCodex/AiChemistTransmutations/gui
npm run electron:build
```

## Verifying the Fix

After implementing solutions, verify:

```powershell
# 1. Check no processes holding files
Get-Process | Where-Object {$_.Path -like "*AiChemist*"}

# 2. Check Windows Defender exclusions
Get-MpPreference | Select-Object ExclusionPath | Where-Object {$_ -like "*AiChemist*"}

# 3. Try build
cd gui
npm run electron:build
```

## Expected Build Output (Success)

```
✓ 1683 modules transformed.
dist/index.html                   1.08 kB │ gzip:  0.53 kB
dist/assets/index-U0Ic9N1i.css   42.32 kB │ gzip:  7.05 kB
dist/assets/index-l-Njcnx-.js   287.03 kB │ gzip: 80.49 kB
✓ built in 3.27s
...
  • packaging       platform=win32 arch=x64 electron=31.7.7 appOutDir=release\1.0.3\win-unpacked
  • building        target=nsis file=release\1.0.3\AiChemist Transmutation Codex Setup 1.0.3.exe
  • building        target=portable file=release\1.0.3\AiChemist Transmutation Codex 1.0.3.exe
```

## Scripts Available

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `build-safe.ps1` | Basic cleanup | First attempt |
| `build-robust.ps1` | Aggressive cleanup | If safe fails |
| `build-ultimate.ps1` | Retry logic | **Use this one** |
| `add-defender-exclusions.ps1` | Add exclusions | **Must run as Admin first** |

## Still Failing?

If all above solutions fail, the issue may be:

###1. Third-Party Antivirus

Check if you have antivirus besides Windows Defender:
- Avast
- Norton
- McAfee
- Kaspersky
- Bitdefender

**Solution:** Add exclusions in that antivirus for the `gui/release` directory.

### 2. Corporate/Group Policy Restrictions

If on a work machine, IT policies may prevent exclusions.

**Solution:** Request IT to add build directory exclusions, or build on personal machine.

### 3. Hardware/Disk Issues

Failing drive can cause file access issues.

**Solution:** Run disk check:
```powershell
chkdsk D: /F /R
```

### 4. Permissions Issues

Your user account may not have full permissions.

**Solution:** Check folder permissions:
```powershell
icacls "D:\Coding\AiChemistCodex\AiChemistTransmutations\gui"
```

## Getting Help

If none of these work:

1. **Gather diagnostic info:**
   ```powershell
   # Check what's locking the file (requires Sysinternals Handle)
   handle.exe app.asar

   # Export Windows Defender exclusions
   Get-MpPreference | Out-File defender-settings.txt

   # List all processes
   Get-Process | Out-File processes.txt
   ```

2. **Contact support with:**
   - Build logs
   - `defender-settings.txt`
   - `processes.txt`
   - Your Windows version
   - Whether you have third-party antivirus

3. **Email:** simpleflowworks@gmail.com
   **Subject:** "electron-builder file lock issue - app.asar"

## Success Checklist

- [ ] Ran `add-defender-exclusions.ps1` as Administrator
- [ ] Verified exclusions were added (`Get-MpPreference`)
- [ ] Restarted computer
- [ ] Closed Cursor/VS Code
- [ ] Ran `build-ultimate.ps1` from clean PowerShell
- [ ] Build succeeded
- [ ] Installer created in `release/1.0.3/`

---

**Last Updated:** November 9, 2025
**Priority:** 🔴 **CRITICAL** - Blocks production releases
**Owner:** @savagelysubtle


