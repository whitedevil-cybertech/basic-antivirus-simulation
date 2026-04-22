# Visual Testing Guide - Phase 3 GUI

## 🚀 Quick Start

### Option 1: Windows (Easiest)
Double-click: `scripts/launch_gui.bat`

### Option 2: Command Line
```bash
python scripts/launch_gui.py
```

### Option 3: Direct Python
```bash
antivirus-gui
```

---

## 📋 Test Scenarios

### 1️⃣ SCAN PANEL (Phase 2 Review)

**What to Test:**
- ✅ Scan functionality with demo files
- ✅ Progress bar during scan
- ✅ Results table display
- ✅ File status indicators

**Steps:**
1. Click "Scan" tab
2. Click "Browse" button
3. Select `a test folder` folder
4. Review file count (should show 2-3 files)
5. Click "Scan" button
6. Watch progress bar update
7. Review results table (File Path, Status, Threat, Severity, Quarantined To)
8. Verify "Scan completed" message in status bar

**Expected Result:**
- Files listed in table
- Status shows "Clean" or "Malicious"
- Progress bar completes
- No errors in status label

---

### 2️⃣ QUARANTINE PANEL (Phase 3 - NEW)

**What to Test:**
- ✅ Quarantine file listing
- ✅ File restoration
- ✅ File deletion
- ✅ Manifest synchronization

**Steps:**
1. Click "Quarantine" tab
2. Click "Refresh" button
3. Observe table (6 columns: Original Path, File Hash, Threat Name, Timestamp, Size, Status)

**If quarantine is empty:**
- This is normal if no malicious files detected
- Test restore/delete with a test folder if needed

**If quarantine has files:**
1. Select a file in the table
2. Click "Restore Selected"
3. Confirm in dialog
4. Verify success message
5. Click "Refresh" to confirm file is gone
6. Try deleting a file (red button, "Delete Permanently")
7. Confirm deletion
8. Verify file removed

**Expected Result:**
- Files displayed with all metadata
- Buttons work (enable when row selected)
- Confirmation dialogs appear
- Status messages update
- Table refreshes after operations

---

### 3️⃣ ALLOWLIST PANEL (Phase 3 - NEW)

**What to Test:**
- ✅ Path whitelisting
- ✅ Hash whitelisting
- ✅ Add/Remove functionality
- ✅ Two-tab interface
- ✅ Persistent storage

**Paths Tab:**
1. Click "Allowlist" tab
2. Click "Whitelisted Paths" tab
3. Click "Add Path" button
4. Enter a safe directory (e.g., `C:\Program Files\Chrome`)
5. Verify path appears in table
6. Click "Browse & Add" to select a different directory
7. Select a folder from dialog
8. Verify added to table
9. Select an entry and click "Remove Selected"
10. Confirm removal
11. Close app and reopen
12. Check if paths are still there (persistence test)

**Hashes Tab:**
1. Click "Whitelisted Hashes" tab
2. In "Add Hash" field, enter a test hash:
   `d41d8cd98f00b204e9800998ecf8427e` (MD5 of empty file - 32 chars, will fail)
3. Click "Add" - should show error (not valid SHA-256)
4. Enter a 64-character hex string:
   `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (SHA-256)
5. Click "Add"
6. Verify hash appears in table
7. Select and remove it
8. Test persistence by closing/reopening app

**Expected Result:**
- Both tabs work independently
- Paths and hashes stored separately
- Add/Remove operations work
- Tables update immediately
- Data persists after closing app
- Stored in `~/.antivirus/allowlist.json`

---

### 4️⃣ SETTINGS PANEL (Phase 3 - NEW)

**What to Test:**
- ✅ File path configuration
- ✅ Browser dialogs
- ✅ Theme switching
- ✅ Preferences storage
- ✅ Reset to defaults

**Paths Configuration:**
1. Click "Settings" tab
2. Observe Paths section:
   - Signature Database: `data/signatures.json`
   - Quarantine Directory: `data/quarantine`
   - Allowlist File: `data/allowlist.json`
   - Log File: `logs/scan_results.log`

3. Click each "Browse" button
   - File dialogs should open
   - Select a location (don't change, just test)
   - Dialog should close

**Options Configuration:**
1. Observe Options section:
   - Theme selector (Dark/Light dropdown)
   - Verbose Logging (checkbox - should be checked)
   - Auto-Quarantine (checkbox - should be checked)
   - Max File Size (spinner - 100 MB default)

2. Toggle "Verbose Logging" checkbox
3. Toggle "Auto-Quarantine" checkbox
4. Change Max File Size to 50 MB
5. Select different theme in dropdown ("Light")
6. Click "Save Settings"
7. Verify success message
8. Check file: `~/.antivirus/config.json`
   - Should contain your settings

**Theme Testing:**
1. Select "Light" theme in Settings
2. Click "Save Settings"
3. Observe entire GUI changing to light colors
4. Select "Dark" in Settings
5. Click "Save Settings"
6. Observe return to dark theme

**Reset Testing:**
1. Click "Reset to Defaults"
2. Confirm in dialog
3. All values should reset to original
4. Theme should return to "Dark"

**Expected Result:**
- All inputs work smoothly
- File dialogs open/close properly
- Theme switching is smooth and complete
- Settings save to config file
- Settings persist after app restart
- Reset clears all changes

---

### 5️⃣ THEME SWITCHING (Global)

**What to Test:**
- ✅ Menu-based theme switching
- ✅ Settings-based theme switching
- ✅ Consistency across all panels
- ✅ Persistence

**Via Menu:**
1. Click "View" menu
2. Click "Theme" submenu
3. Click "Light"
4. Observe all panels changing to light theme
5. Click "View" → "Theme" → "Dark"
6. Observe return to dark theme

**Via Settings Tab:**
1. Go to Settings tab
2. Change Theme dropdown
3. Click "Save Settings"
4. Verify change applies immediately

**Visual Verification:**
- Background colors change
- Text colors change readably
- Buttons maintain contrast
- Tables remain readable
- All panels styled consistently

**Expected Result:**
- Theme switching is instant
- No visual glitches
- All UI elements properly themed
- Changes persist

---

### 6️⃣ TAB NAVIGATION

**What to Test:**
- ✅ Tab switching smoothness
- ✅ Tab content loads correctly
- ✅ Tab state preservation

**Steps:**
1. Click each tab in order: Scan → Quarantine → Allowlist → Analytics → Settings
2. Go back in reverse order: Settings → Analytics → Allowlist → Quarantine → Scan
3. Rapidly click between tabs
4. Verify no crashes or lag

**Expected Result:**
- Smooth tab transitions
- Content loads immediately
- No data loss
- Analytics tab shows "Coming soon..." placeholder

---

### 7️⃣ MENU BAR

**What to Test:**
- ✅ File menu
- ✅ View menu with themes
- ✅ Help menu

**Steps:**
1. Click "File" menu → "Exit"
   - Application should close
   - (Or close and relaunch)

2. Click "View" menu
   - Should show "Theme" submenu
   - Theme options visible

3. Click "Help" menu → "About"
   - Should show status message

**Expected Result:**
- Menu items responsive
- Submenu displays properly
- Exit closes application

---

### 8️⃣ WINDOW FUNCTIONALITY

**What to Test:**
- ✅ Resize behavior
- ✅ Responsive layout
- ✅ Status bar messages
- ✅ Window title

**Steps:**
1. Verify window title: "Antivirus Scanner - Professional Threat Detection"
2. Drag window edges to resize
3. Make window larger - layout should expand
4. Make window smaller - content should adapt
5. Double-click title bar to maximize
6. Observe status bar at bottom with messages

**Expected Result:**
- Window responsive to resize
- Content flows properly
- Status bar always visible
- No text cutoff
- Professional appearance maintained

---

## 📊 Test Checklist

| Component | Test | Status |
|-----------|------|--------|
| **Scan Panel** | File scanning | [ ] |
| | Progress tracking | [ ] |
| | Results display | [ ] |
| **Quarantine Panel** | List files | [ ] |
| | Restore files | [ ] |
| | Delete files | [ ] |
| **Allowlist Panel** | Add paths | [ ] |
| | Remove paths | [ ] |
| | Add hashes | [ ] |
| | Remove hashes | [ ] |
| | Persistence | [ ] |
| **Settings Panel** | Path browsing | [ ] |
| | Theme switching | [ ] |
| | Preferences save | [ ] |
| | Reset defaults | [ ] |
| **Global** | Tab navigation | [ ] |
| | Menu bar | [ ] |
| | Window resize | [ ] |
| | Status messages | [ ] |

---

## 🔍 What to Look For

### Good Signs ✅
- GUI launches without errors
- All tabs load content immediately
- Buttons respond to clicks
- Dialog boxes appear and close properly
- Status messages display correctly
- Theme switching is smooth
- No console errors (if running from terminal)
- Settings persist across restarts

### Issues to Report ⚠️
- Blank tabs or missing content
- Buttons that don't work
- Crashes or freezing
- Slow performance
- Misaligned text or buttons
- Colors not applying properly
- Console errors (Python traceback)

---

## 💾 Data Locations

After testing, check these files:

| Data | Location | Purpose |
|------|----------|---------|
| Quarantine | `data/quarantine/manifest.json` | List of quarantined files |
| Allowlist | `~/.antivirus/allowlist.json` | Whitelisted paths and hashes |
| Settings | `~/.antivirus/config.json` | User preferences |
| Logs | `~/.antivirus/logs/gui.log` | Application logs |

On Windows:
- `~/.antivirus/` = `C:\Users\[YourUsername]\.antivirus\`

---

## 🎯 Success Criteria

✅ All tests pass → Phase 3 is VALIDATED → Ready for Phase 4

**If any issues found:**
1. Note the exact steps to reproduce
2. Screenshot if possible
3. Check console output for errors
4. Report in detail

---

## 📞 Need Help?

Check the following if something doesn't work:

1. **PyQt6 not installed?**
   ```bash
   pip install PyQt6
   ```

2. **ModuleNotFoundError?**
   ```bash
   cd A:\CYBERSECURITY\Skillfied\Project1\basic-antivirus-simulation
   python scripts/launch_gui.py
   ```

3. **Looking for demo files?**
   - Check `a test folder/` folder for test files

4. **Want to see logs?**
   - Check `~/.antivirus/logs/gui.log`

---

## 🎉 You're Ready!

Enjoy testing the GUI! This is the culmination of Phase 1, Phase 2, and Phase 3 work.

After visual testing confirms everything works, Phase 4 (Analytics Dashboard) can begin.

Good luck! 🚀
