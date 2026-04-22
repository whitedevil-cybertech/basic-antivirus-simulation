"""Comprehensive Phase 3 GUI testing suite."""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path for package imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def test_imports():
    """Test all GUI imports."""
    print("=" * 60)
    print("TEST 1: Imports")
    print("=" * 60)
    
    try:
        from basic_antivirus_simulation.gui.widgets.quarantine_panel import QuarantinePanel
        print("[OK] QuarantinePanel imported")
        
        from basic_antivirus_simulation.gui.widgets.allowlist_panel import AllowlistPanel
        print("[OK] AllowlistPanel imported")
        
        from basic_antivirus_simulation.gui.widgets.settings_panel import SettingsPanel
        print("[OK] SettingsPanel imported")
        
        from basic_antivirus_simulation.gui.main_window import MainWindow
        print("[OK] MainWindow imported")
        
        from basic_antivirus_simulation.gui.theme import ThemeManager
        print("[OK] ThemeManager imported")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_integration():
    """Test integration with scanner backend."""
    print("\n" + "=" * 60)
    print("TEST 2: Backend Integration")
    print("=" * 60)
    
    try:
        from basic_antivirus_simulation.scanner.quarantine import (
            list_quarantine,
            restore_file,
        )
        print("[OK] scanner.quarantine module loads")
        
        from basic_antivirus_simulation.scanner.signatures import (
            load_allowlist,
            save_allowlist,
            add_to_allowlist,
        )
        print("[OK] scanner.signatures module loads")
        
        # Test quarantine list with temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = list_quarantine(tmpdir)
            print(f"[OK] list_quarantine works (found {len(manifest)} entries)")
        
        # Test allowlist with temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / "allowlist.json"
            al = {"paths": [], "hashes": []}
            save_allowlist(allowlist_path, al)
            loaded = load_allowlist(allowlist_path)
            print(f"[OK] allowlist save/load works")
        
        return True
    except Exception as e:
        print(f"[FAIL] Backend integration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_widget_instantiation():
    """Test that widgets can be instantiated."""
    print("\n" + "=" * 60)
    print("TEST 3: Widget Instantiation")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from basic_antivirus_simulation.gui.widgets.quarantine_panel import QuarantinePanel
        from basic_antivirus_simulation.gui.widgets.allowlist_panel import AllowlistPanel
        from basic_antivirus_simulation.gui.widgets.settings_panel import SettingsPanel
        
        # Create minimal QApplication for widget testing
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        # Test QuarantinePanel
        qp = QuarantinePanel()
        print("[OK] QuarantinePanel instantiated")
        assert qp.table is not None
        print("[OK] QuarantinePanel has table widget")
        assert qp.restore_btn is not None
        print("[OK] QuarantinePanel has restore button")
        
        # Test AllowlistPanel
        ap = AllowlistPanel()
        print("[OK] AllowlistPanel instantiated")
        assert ap.paths_table is not None
        print("[OK] AllowlistPanel has paths table")
        assert ap.hashes_table is not None
        print("[OK] AllowlistPanel has hashes table")
        
        # Test SettingsPanel
        sp = SettingsPanel()
        print("[OK] SettingsPanel instantiated")
        assert sp.signatures_input is not None
        print("[OK] SettingsPanel has settings inputs")
        assert hasattr(sp, '_save_settings')
        print("[OK] SettingsPanel has save functionality")
        
        return True
    except Exception as e:
        print(f"[FAIL] Widget instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_panel_initialization():
    """Test panel initialization with directories."""
    print("\n" + "=" * 60)
    print("TEST 4: Panel Initialization")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from basic_antivirus_simulation.gui.widgets.quarantine_panel import QuarantinePanel
        from basic_antivirus_simulation.gui.widgets.allowlist_panel import AllowlistPanel
        from basic_antivirus_simulation.gui.widgets.settings_panel import SettingsPanel
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test QuarantinePanel initialization
            qp = QuarantinePanel()
            quarantine_dir = tmpdir / "quarantine"
            quarantine_dir.mkdir()
            qp.set_quarantine_directory(quarantine_dir)
            print("[OK] QuarantinePanel initialized with directory")
            assert qp.table.rowCount() >= 0
            print("[OK] QuarantinePanel table loads without errors")
            
            # Test AllowlistPanel initialization
            ap = AllowlistPanel()
            allowlist_file = tmpdir / "allowlist.json"
            ap.set_allowlist_path(allowlist_file)
            print("[OK] AllowlistPanel initialized with file path")
            assert ap.paths_table.rowCount() == 0
            print("[OK] AllowlistPanel tables load without errors")
            
            # Test SettingsPanel initialization
            sp = SettingsPanel()
            config_file = tmpdir / "config.json"
            sp.set_config_file(config_file)
            print("[OK] SettingsPanel initialized with config file")
            assert sp.get_settings() is not None
            print("[OK] SettingsPanel can read settings")
        
        return True
    except Exception as e:
        print(f"[FAIL] Panel initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signals_and_slots():
    """Test signal/slot connections."""
    print("\n" + "=" * 60)
    print("TEST 5: Signals and Slots")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from basic_antivirus_simulation.gui.widgets.quarantine_panel import QuarantinePanel
        from basic_antivirus_simulation.gui.widgets.allowlist_panel import AllowlistPanel
        from basic_antivirus_simulation.gui.widgets.settings_panel import SettingsPanel
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Test QuarantinePanel signals
        qp = QuarantinePanel()
        assert hasattr(qp, 'status_update')
        print("[OK] QuarantinePanel has status_update signal")
        
        # Test AllowlistPanel signals
        ap = AllowlistPanel()
        assert hasattr(ap, 'status_update')
        print("[OK] AllowlistPanel has status_update signal")
        
        # Test SettingsPanel signals
        sp = SettingsPanel()
        assert hasattr(sp, 'theme_changed')
        print("[OK] SettingsPanel has theme_changed signal")
        assert hasattr(sp, 'settings_saved')
        print("[OK] SettingsPanel has settings_saved signal")
        
        return True
    except Exception as e:
        print(f"[FAIL] Signals/slots error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_style_application():
    """Test stylesheet application."""
    print("\n" + "=" * 60)
    print("TEST 6: Style Application")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from basic_antivirus_simulation.gui.widgets.quarantine_panel import QuarantinePanel
        from basic_antivirus_simulation.gui.widgets.allowlist_panel import AllowlistPanel
        from basic_antivirus_simulation.gui.widgets.settings_panel import SettingsPanel
        from basic_antivirus_simulation.gui.theme import ThemeManager
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Test QuarantinePanel styling
        qp = QuarantinePanel()
        assert qp.styleSheet() != ""
        print("[OK] QuarantinePanel has stylesheet applied")
        
        # Test AllowlistPanel styling
        ap = AllowlistPanel()
        assert ap.styleSheet() != ""
        print("[OK] AllowlistPanel has stylesheet applied")
        
        # Test SettingsPanel styling
        sp = SettingsPanel()
        assert sp.styleSheet() != ""
        print("[OK] SettingsPanel has stylesheet applied")
        
        # Test ThemeManager
        tm = ThemeManager("dark")
        stylesheet = tm.get_stylesheet()
        assert stylesheet != ""
        print("[OK] ThemeManager generates dark theme stylesheet")
        
        tm.set_theme("light")
        stylesheet = tm.get_stylesheet()
        assert stylesheet != ""
        print("[OK] ThemeManager generates light theme stylesheet")
        
        return True
    except Exception as e:
        print(f"[FAIL] Style application error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window_integration():
    """Test main window with all panels."""
    print("\n" + "=" * 60)
    print("TEST 7: Main Window Integration")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from basic_antivirus_simulation.gui.main_window import MainWindow
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        window = MainWindow(theme="dark")
        print("[OK] MainWindow instantiated")
        
        assert hasattr(window, 'tab_scan')
        print("[OK] MainWindow has scan tab")
        
        assert hasattr(window, 'tab_quarantine')
        print("[OK] MainWindow has quarantine tab")
        
        assert hasattr(window, 'tab_allowlist')
        print("[OK] MainWindow has allowlist tab")
        
        assert hasattr(window, 'tab_settings')
        print("[OK] MainWindow has settings tab")
        
        assert hasattr(window, 'tab_analytics')
        print("[OK] MainWindow has analytics tab")
        
        assert window.tabs.count() == 5
        print("[OK] MainWindow has all 5 tabs")
        
        return True
    except Exception as e:
        print(f"[FAIL] Main window integration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n")
    print("*" * 60)
    print("PHASE 3 GUI COMPREHENSIVE TEST SUITE")
    print("*" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Backend Integration", test_backend_integration),
        ("Widget Instantiation", test_widget_instantiation),
        ("Panel Initialization", test_panel_initialization),
        ("Signals and Slots", test_signals_and_slots),
        ("Style Application", test_style_application),
        ("Main Window Integration", test_main_window_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[CRITICAL ERROR in {name}]: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
    
    print(f"\nTotal: {passed}/{total} test groups passed")
    
    if passed == total:
        print("\nAll tests PASSED! GUI is ready for Phase 4.")
        return 0
    else:
        print(f"\n{total - passed} test group(s) FAILED. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
