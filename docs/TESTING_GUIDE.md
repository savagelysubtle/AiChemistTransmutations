# Testing Guide - Installation & License Activation

**Purpose:** Verify the complete application works before public launch
**Time Required:** 30-45 minutes
**Status:** Ready to test

---

## 🧪 Test Environment Setup

### What You Need

- Clean Windows 10 or 11 machine (or VM)
- Internet connection
- ~500 MB free disk space
- Your built installer (176 MB)

### Optional But Recommended

- Virtual Machine (VMware, VirtualBox, Hyper-V)
- Fresh Windows installation
- No dev tools installed

---

## 📋 Test Checklist

### Part 1: Installation Test (15 min)

**1.1 Copy Installer**

```powershell
# Copy from build location to test machine
# Source: gui\release\1.0.0\AiChemist Transmutation Codex Setup 1.0.0.exe
# Destination: Desktop or Downloads folder
```

**1.2 Run Installer**

- [ ] Double-click installer
- [ ] Windows SmartScreen appears (expected - no code signing yet)
- [ ] Click "More info" → "Run anyway"
- [ ] Installer window opens
- [ ] Accept license agreement
- [ ] Choose installation directory (default: `C:\Program Files\AiChemist Transmutation Codex`)
- [ ] Check "Create desktop shortcut"
- [ ] Check "Create Start menu shortcut"
- [ ] Click "Install"
- [ ] Installation progress completes
- [ ] Click "Finish" (and optionally "Launch")

**1.3 Verify Installation**

- [ ] Desktop shortcut created
- [ ] Start menu entry exists
- [ ] Installation folder contains files

  ```powershell
  cd "C:\Program Files\AiChemist Transmutation Codex"
  dir
  # Should see: AiChemist Transmutation Codex.exe
  # And resources folder with python-backend
  ```

**1.4 First Launch**

- [ ] Double-click desktop shortcut (or Start menu)
- [ ] Application window opens
- [ ] GUI loads without errors
- [ ] Trial status shows: "Trial: 50 conversions remaining"
- [ ] Main conversion interface visible

**Expected Result:** ✅ App installs and launches successfully in trial mode

---

### Part 2: License Activation Test (15 min)

**2.1 Generate Dev License**

```powershell
cd D:\Coding\AiChemistCodex\AiChemistTransmutations
python scripts/licensing/generate_dev_license.py

# Output: DEV_LICENSE.txt created with license key
```

**2.2 Copy License Key**

```powershell
# Open DEV_LICENSE.txt
# Copy the license key (format: long string with dashes)
```

**2.3 Activate in App**

- [ ] Open installed app
- [ ] Click "Upgrade" or "Activate License" button
- [ ] License dialog appears
- [ ] Paste license key
- [ ] Click "Activate"
- [ ] Wait for validation (~2-5 seconds)

**2.4 Verify Activation**

- [ ] Success message appears
- [ ] Trial badge changes to "Licensed" or "Pro"
- [ ] Conversion limit removed
- [ ] All features unlocked
- [ ] App doesn't require activation on next launch

**2.5 Restart Test**

- [ ] Close app completely
- [ ] Reopen from shortcut
- [ ] License still active (no trial mode)
- [ ] No re-activation required

**Expected Result:** ✅ License activates and persists across restarts

---

### Part 3: Core Functionality Test (15 min)

**3.1 PDF to Markdown**

- [ ] Click "Select File" or drag & drop
- [ ] Choose a PDF file (any PDF)
- [ ] Select conversion type: "PDF to Markdown"
- [ ] Click "Convert"
- [ ] Progress bar shows
- [ ] Conversion completes
- [ ] Output file created
- [ ] Open output - verify readable Markdown

**3.2 Markdown to PDF**

- [ ] Create or use a test .md file
- [ ] Select conversion type: "Markdown to PDF"
- [ ] Add some conversion options (optional)
- [ ] Click "Convert"
- [ ] Output PDF created
- [ ] Open output - verify looks correct

**3.3 Batch Conversion**

- [ ] Click "Batch Mode" or "Add Multiple Files"
- [ ] Select 3-5 files of same type
- [ ] Choose conversion type
- [ ] Click "Convert All"
- [ ] All files convert successfully
- [ ] Check conversion log

**3.4 PDF Merge (if available)**

- [ ] Select 2-3 PDF files
- [ ] Click "Merge PDFs"
- [ ] Output merged PDF created
- [ ] Verify all pages included

**3.5 Dependency Check**

- [ ] Open Settings or Help menu
- [ ] Find "Check Dependencies"
- [ ] Run dependency check
- [ ] Review results (some may be missing - that's OK)

**Expected Result:** ✅ All core conversions work as expected

---

### Part 4: Error Handling Test (5 min)

**4.1 Invalid File**

- [ ] Try to convert a corrupt or wrong format file
- [ ] App shows appropriate error message
- [ ] App doesn't crash

**4.2 Invalid License**

- [ ] Uninstall and reinstall app
- [ ] Try activating with random string
- [ ] App shows "Invalid license" message
- [ ] Allows retry

**4.3 Missing Output Path**

- [ ] Start conversion without selecting output
- [ ] App uses default location or asks for one

**Expected Result:** ✅ Errors handled gracefully without crashes

---

### Part 5: Uninstallation Test (5 min)

**5.1 Uninstall**

- [ ] Open Windows Settings → Apps
- [ ] Find "AiChemist Transmutation Codex"
- [ ] Click "Uninstall"
- [ ] Uninstaller runs
- [ ] Choose to keep or remove settings

**5.2 Verify Removal**

- [ ] Installation folder deleted
- [ ] Desktop shortcut removed
- [ ] Start menu entry removed
- [ ] (Optional) User data preserved in AppData

**Expected Result:** ✅ Clean uninstallation

---

## 📊 Test Results Template

Copy this to track your testing:

```markdown
## Test Results - [Date]

### Installation
- [ ] ✅ Installer runs
- [ ] ✅ Installation completes
- [ ] ✅ Shortcuts created
- [ ] ✅ App launches
- [ ] ✅ Trial mode active

### License Activation
- [ ] ✅ Dev license generated
- [ ] ✅ License activates
- [ ] ✅ Full unlock confirmed
- [ ] ✅ License persists

### Core Features
- [ ] ✅ PDF → Markdown works
- [ ] ✅ Markdown → PDF works
- [ ] ✅ Batch conversion works
- [ ] ✅ PDF merge works (if available)
- [ ] ✅ Dependency check works

### Error Handling
- [ ] ✅ Invalid files handled
- [ ] ✅ Invalid license handled
- [ ] ✅ No crashes observed

### Uninstallation
- [ ] ✅ Uninstaller works
- [ ] ✅ Files removed
- [ ] ✅ Shortcuts removed

### Issues Found
- Issue 1: [Description]
- Issue 2: [Description]

### Notes
- [Any additional observations]
```

---

## 🐛 Common Issues & Solutions

### Installer Won't Run

**Problem:** Double-clicking does nothing
**Solution:** Right-click → "Run as administrator"

### SmartScreen Blocks

**Problem:** Windows prevents installation
**Solution:** Click "More info" → "Run anyway" (normal without code signing)

### App Won't Launch

**Problem:** Nothing happens after install
**Solution:**

1. Check Start Menu instead of shortcut
2. Look for error in Event Viewer
3. Check `%APPDATA%\AiChemist\logs\`

### License Won't Activate

**Problem:** "Invalid license" error
**Solution:**

1. Check internet connection
2. Verify license key copied completely
3. Try regenerating dev license
4. Check Supabase is running

### Conversion Fails

**Problem:** "Conversion failed" error
**Solution:**

1. Run dependency check
2. Install missing tools (Tesseract, etc.)
3. Try different file
4. Check file isn't corrupted

---

## ✅ Success Criteria

**Installation:** ✅

- Installs without errors
- Creates shortcuts
- Launches successfully

**License:** ✅

- Activates with valid key
- Shows full unlock
- Persists across restarts

**Functionality:** ✅

- Converts documents successfully
- Handles errors gracefully
- Doesn't crash

**Uninstall:** ✅

- Removes cleanly
- No leftover files (except user data)

---

## 📝 Next Steps After Testing

**If All Tests Pass:**

1. ✅ Mark application as "Production Ready"
2. ✅ Proceed with Gumroad setup
3. ✅ Prepare marketing materials
4. ✅ Set launch date

**If Issues Found:**

1. Document each issue clearly
2. Prioritize (critical, high, medium, low)
3. Fix critical issues first
4. Retest after fixes
5. Repeat until all pass

---

## 🎯 Testing Best Practices

1. **Use Clean Machine** - No dev tools, fresh Windows
2. **Test Like a User** - Don't use workarounds
3. **Document Everything** - Screenshots, errors, steps
4. **Test Edge Cases** - Large files, special characters, etc.
5. **Check Logs** - Look in `%APPDATA%\AiChemist\logs\`

---

## 📞 Support During Testing

**If you encounter issues:**

1. Check `%APPDATA%\AiChemist\logs\python\` for error logs
2. Try uninstall and reinstall
3. Test on different Windows version
4. Check antivirus isn't interfering

**For license issues:**

1. Verify Supabase connection
2. Check public key in app matches private key
3. Regenerate license if needed

---

**Ready to test?** Follow this guide step-by-step and document your results!

**After successful testing:** Move on to Gumroad setup (`docs/GUMROAD_COMPLETE_SETUP.md`)
