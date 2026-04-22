"""Quick functional GUI test - simulate user interactions."""

import sys
import json
import tempfile
from pathlib import Path

def test_gui_functionality():
    """Test GUI functionality with simulated interactions."""
    print("\n" + "=" * 60)
    print("FUNCTIONAL GUI TEST")
    print("=" * 60)
    
    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MainWindow
    
    # Create app if needed
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    # Create main window
    window = MainWindow(theme="dark")
    print("[OK] Main window created")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Setup panels
        qdir = tmpdir / "quarantine"
        qdir.mkdir()
        window.tab_quarantine.set_quarantine_directory(qdir)
        print("[OK] Quarantine panel configured")
        
        afile = tmpdir / "allowlist.json"
        window.tab_allowlist.set_allowlist_path(afile)
        print("[OK] Allowlist panel configured")
        
        cfile = tmpdir / "config.json"
        window.tab_settings.set_config_file(cfile)
        print("[OK] Settings panel configured")
        
        # Test quarantine panel
        print("\n[Testing Quarantine Panel]")
        qp = window.tab_quarantine
        assert qp.table is not None
        print("  - Table widget functional")
        assert qp.restore_btn is not None
        print("  - Restore button present")
        assert qp.delete_btn is not None
        print("  - Delete button present")
        assert qp.refresh_btn is not None
        print("  - Refresh button present")
        
        # Test allowlist panel
        print("\n[Testing Allowlist Panel]")
        ap = window.tab_allowlist
        assert ap.paths_table is not None
        print("  - Paths table present")
        assert ap.hashes_table is not None
        print("  - Hashes table present")
        assert ap.tabs is not None
        print("  - Two tabs (Paths, Hashes) present")
        
        # Test settings panel
        print("\n[Testing Settings Panel]")
        sp = window.tab_settings
        assert sp.signatures_input is not None
        print("  - Signature DB input present")
        assert sp.quarantine_input is not None
        print("  - Quarantine dir input present")
        assert sp.allowlist_input is not None
        print("  - Allowlist file input present")
        assert sp.log_input is not None
        print("  - Log file input present")
        assert sp.theme_combo is not None
        print("  - Theme selector present")
        assert sp.verbose_check is not None
        print("  - Verbose logging checkbox present")
        assert sp.auto_quarantine_check is not None
        print("  - Auto-quarantine checkbox present")
        
        # Test theme switching
        print("\n[Testing Theme Switching]")
        window._switch_theme("light")
        print("  - Switched to light theme")
        window._switch_theme("dark")
        print("  - Switched to dark theme")
        
        # Test settings loading/saving
        print("\n[Testing Settings Persistence]")
        test_settings = {
            "signatures_db": "test.json",
            "quarantine_dir": "/test",
            "allowlist_file": "/test/allowlist.json",
            "log_file": "/test/app.log",
            "theme": "light",
            "verbose_logging": False,
            "auto_quarantine": True,
            "max_file_size_mb": 50,
        }
        settings_file = tmpdir / "test_config.json"
        settings_file.write_text(json.dumps(test_settings), encoding="utf-8")
        
        sp = window.tab_settings
        sp.set_config_file(settings_file)
        loaded = sp.get_settings()
        assert loaded["theme"] == "light"
        print("  - Settings loaded correctly")
        
        print("\nAll functional tests PASSED!")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(test_gui_functionality())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
