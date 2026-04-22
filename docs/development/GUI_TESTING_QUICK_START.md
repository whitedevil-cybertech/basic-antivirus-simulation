# How to Test the GUI Visually

## 🎯 Three Ways to Launch

### Option 1: Windows Batch File (EASIEST)
📁 Find and double-click: **`scripts/launch_gui.bat`**

### Option 2: PowerShell Command
```powershell
cd A:\CYBERSECURITY\Skillfied\Project1\basic-antivirus-simulation
python scripts/launch_gui.py
```

### Option 3: Direct GUI Launch
```powershell
cd A:\CYBERSECURITY\Skillfied\Project1\basic-antivirus-simulation
py gui_main.py
```

---

## ✨ What You'll See When It Launches

1. **Welcome Header** - Introduction with feature list
2. **Test Scenarios** - 6 detailed testing scenarios
3. **GUI Window Opens** - Main application window

The GUI will display:
- **5 Tabs**: Scan | Quarantine | Allowlist | Analytics | Settings
- **Menu Bar**: File, View (with Theme), Help
- **Status Bar**: Real-time status messages
- **Professional Dark Theme**: Fully styled and ready

---

## 🧪 Quick Test Flow (5 minutes)

1. **Launch the app** (see above)
2. **Click Scan tab** → Select `a test folder` folder → Click Scan
   - Watch the progress bar
   - See results in table
3. **Click Quarantine tab** → Click Refresh
   - Should be empty (unless you scanned and found malware)
4. **Click Allowlist tab**
   - Add a path or hash
   - Try removing it
   - These persist even after closing!
5. **Click Settings tab**
   - Change theme to "Light"
   - Click "Save Settings"
   - Watch the entire GUI change colors!
6. **Use View menu** → Theme → Dark
   - Switch back to dark theme

---

## 📖 Full Testing Guide

For comprehensive test scenarios, see:
📄 **`VISUAL_TESTING_GUIDE.md`**

This document includes:
- ✅ 8 detailed test scenarios
- ✅ Step-by-step instructions
- ✅ Expected results for each feature
- ✅ Data location reference
- ✅ Success criteria checklist

---

## 🔑 Key Features to Verify

### ✅ Quarantine Panel
- List quarantined files with metadata
- Restore files to original location
- Delete files permanently
- Real-time manifest updates

### ✅ Allowlist Panel  
- Add paths (safe directories)
- Add hashes (safe file signatures)
- Remove entries
- Persistent JSON storage

### ✅ Settings Panel
- Configure file paths (browse dialogs)
- Switch theme (Dark/Light)
- Manage preferences
- Save to config file

### ✅ Main Window
- 5 tabs with smooth switching
- Menu bar (File, View, Help)
- Status bar with messages
- Professional appearance

---

## 🎨 Theme Testing

1. Go to Settings tab
2. Change Theme dropdown from "Dark" to "Light"
3. Click "Save Settings"
4. Watch the entire GUI transform!
5. Change back to "Dark"

Or use the menu: **View → Theme → Light/Dark**

---

## 💾 Persistent Data

After testing, check these locations:

**Allowlist Entries:**
```
C:\Users\[YourUsername]\.antivirus\allowlist.json
```

**Settings/Preferences:**
```
C:\Users\[YourUsername]\.antivirus\config.json
```

**Application Logs:**
```
C:\Users\[YourUsername]\.antivirus\logs\gui.log
```

**Quarantine Manifest:**
```
A:\CYBERSECURITY\Skillfied\Project1\basic-antivirus-simulation\data\quarantine\manifest.json
```

---

## ⚡ What's New in Phase 3

| Feature | Tab | Status |
|---------|-----|--------|
| File Scanning | Scan | ✅ Phase 2 |
| **Quarantine Management** | **Quarantine** | **✅ NEW** |
| **Whitelist Management** | **Allowlist** | **✅ NEW** |
| **Configuration UI** | **Settings** | **✅ NEW** |
| Dashboard (Coming Soon) | Analytics | ⏳ Phase 4 |

---

## 🚀 Next Steps After Testing

1. ✅ Launch GUI and test all features
2. ✅ Verify all components work smoothly
3. ✅ Check persistent storage (config, allowlist)
4. ✅ Test theme switching
5. ✅ Report any issues (if found)
6. ✅ Proceed to Phase 4 (Analytics Dashboard)

---

## ❓ Troubleshooting

### GUI won't start
```bash
# Check Python
python --version

# Install PyQt6
pip install PyQt6

# Try launching again
python scripts/launch_gui.py
```

### ModuleNotFoundError
Make sure you're in the correct directory:
```bash
cd A:\CYBERSECURITY\Skillfied\Project1\basic-antivirus-simulation
python scripts/launch_gui.py
```

### Missing a test folder folder
The GUI will still work, just browse to any folder to scan.

---

## 📊 Testing Checklist

Print this or copy it to track your progress:

```
GUI LAUNCH:
  [ ] Application starts without errors
  [ ] Window displays with all tabs
  [ ] Menu bar is visible
  [ ] Status bar shows "Ready"

SCAN TAB:
  [ ] Can select folder
  [ ] Scan button works
  [ ] Progress bar animates
  [ ] Results display correctly

QUARANTINE TAB:
  [ ] Refresh button works
  [ ] Table displays (even if empty)
  [ ] Buttons enable/disable properly

ALLOWLIST TAB:
  [ ] Both tabs (Paths, Hashes) present
  [ ] Can add entries
  [ ] Can remove entries
  [ ] Data persists after close

SETTINGS TAB:
  [ ] All input fields present
  [ ] Browse buttons open dialogs
  [ ] Theme selector works
  [ ] Save Settings button works

THEME SWITCHING:
  [ ] Light theme displays correctly
  [ ] Dark theme displays correctly
  [ ] Switching is smooth
  [ ] All panels themed consistently

OVERALL:
  [ ] No errors in console
  [ ] No crashes
  [ ] Responsive to clicks
  [ ] Professional appearance
```

---

## 🎉 You're Ready!

Everything is tested, committed to git, and ready for you to explore visually.

**Estimated Testing Time**: 5-10 minutes  
**Difficulty**: Easy - just click around!

Launch the GUI and enjoy the fruits of Phase 3 development! 🚀

If everything works smoothly, Phase 4 (Analytics Dashboard) is next.

---

**Questions?** Check `VISUAL_TESTING_GUIDE.md` for detailed instructions.

**Ready for Phase 4?** Let me know once visual testing is complete!
