"""
GUI Visual Testing Guide and Launcher

Run this script to launch the Antivirus Scanner GUI for visual testing.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
src_root = project_root / "src"
sys.path.insert(0, str(src_root))

def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("ANTIVIRUS SCANNER GUI - VISUAL TESTING")
    print("="*70)
    print("\nThis will launch the complete GUI with all Phase 3 components.")
    print("\nFeatures to test:")
    print("  1. Scan Panel (Phase 2) - Scan directories")
    print("  2. Quarantine Panel (Phase 3) - Manage quarantined files")
    print("  3. Allowlist Panel (Phase 3) - Whitelist paths and hashes")
    print("  4. Settings Panel (Phase 3) - Configure application")
    print("  5. Theme Switching - Dark/Light mode")
    print("\n" + "="*70 + "\n")

def print_test_scenarios():
    """Print suggested test scenarios."""
    print("\nSUGGESTED TEST SCENARIOS:")
    print("-" * 70)
    
    scenarios = [
        ("Scan Panel", [
            "1. Go to Scan tab",
            "2. Click 'Browse' and select a folder to scan",
            "3. Click 'Scan' button",
            "4. Observe real-time progress",
            "5. Review results table"
        ]),
        ("Quarantine Panel", [
            "1. Go to Quarantine tab",
            "2. Click 'Refresh' to load quarantined files (if any)",
            "3. If files exist: select one and try 'Restore' or 'Delete'",
            "4. Test confirmation dialogs"
        ]),
        ("Allowlist Panel", [
            "1. Go to Allowlist tab",
            "2. Switch to 'Whitelisted Paths' tab",
            "3. Click 'Add Path' and enter a path (e.g., C:\\safe)",
            "4. Click 'Browse & Add' to select a directory",
            "5. Try removing an entry",
            "6. Switch to 'Whitelisted Hashes' tab",
            "7. Try adding a hash",
            "8. Check persistent storage in ~/.antivirus/allowlist.json"
        ]),
        ("Settings Panel", [
            "1. Go to Settings tab",
            "2. Review all path configurations",
            "3. Click 'Browse' buttons to test file dialogs",
            "4. Toggle 'Verbose Logging' checkbox",
            "5. Toggle 'Auto-Quarantine' checkbox",
            "6. Adjust 'Max File Size'",
            "7. Click 'Save Settings'",
            "8. Check ~/.antivirus/config.json for persistence"
        ]),
        ("Theme Switching", [
            "1. Open View menu → Theme → Light",
            "2. Observe all panels switching to light theme",
            "3. Open View menu → Theme → Dark",
            "4. Verify dark theme applied everywhere"
        ]),
        ("Overall UI", [
            "1. Click between tabs - verify smooth transitions",
            "2. Test window resize - verify responsive layout",
            "3. Check status bar messages",
            "4. Verify button hover effects",
            "5. Test menu bar (File, View, Help)"
        ])
    ]
    
    for category, steps in scenarios:
        print(f"\n{category}:")
        for step in steps:
            print(f"  {step}")
    
    print("\n" + "-" * 70)

def print_important_notes():
    """Print important notes."""
    print("\nIMPORTANT NOTES:")
    print("-" * 70)
    notes = [
        "Select any folder you want to scan during testing",
        "Quarantine data stored in data/quarantine/",
        "Allowlist saved to ~/.antivirus/allowlist.json",
        "Settings saved to ~/.antivirus/config.json",
        "Log files created in ~/.antivirus/logs/gui.log",
        "Close the window to stop the application",
        "No data will be lost during testing"
    ]
    for note in notes:
        print(f"  • {note}")
    print()

def main():
    """Launch the GUI application."""
    print_header()
    print_test_scenarios()
    print_important_notes()
    
    print("\nLaunching GUI...\n")
    print("="*70)
    
    try:
        os.chdir(project_root)
        from PyQt6.QtWidgets import QApplication
        from basic_antivirus_simulation.gui_app import main as gui_main
        
        # Launch the GUI
        return gui_main()
        
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("\nPlease install PyQt6:")
        print("  pip install PyQt6")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
