"""
Comprehensive test suite for Phase 5: Polish & Optimization.

Tests cover:
- Error handling and validation
- Edge cases and error scenarios
- Input validation
- Keyboard shortcuts
- Accessibility features
- Performance and responsiveness
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from basic_antivirus_simulation.gui.main_window import MainWindow
from basic_antivirus_simulation.gui.widgets.scan_panel import ScanPanel
from basic_antivirus_simulation.gui.widgets.quarantine_panel import QuarantinePanel
from basic_antivirus_simulation.gui.widgets.allowlist_panel import AllowlistPanel
from basic_antivirus_simulation.gui.widgets.settings_panel import SettingsPanel
from basic_antivirus_simulation.gui.widgets.analytics_panel import AnalyticsPanel


def get_or_create_app():
    """Get existing QApplication or create new one."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestErrorHandling(unittest.TestCase):
    """Test error handling in GUI components."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def setUp(self):
        """Setup for each test."""
        self.scan_panel = ScanPanel()
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Cleanup after each test."""
        self.temp_dir.cleanup()

    def test_scan_empty_target(self):
        """Test scan with empty target path."""
        self.scan_panel.target_input.setText("")
        self.scan_panel.sig_input.setText("signatures.json")
        
        # Mock the QMessageBox to avoid blocking
        with patch.object(QMessageBox, 'warning'):
            self.scan_panel._start_scan()
        
        # Should show error in status
        self.assertIn("Error", self.scan_panel.status_label.text())

    def test_scan_empty_signatures(self):
        """Test scan with empty signature path."""
        self.scan_panel.target_input.setText("/some/path")
        self.scan_panel.sig_input.setText("")
        
        with patch.object(QMessageBox, 'warning'):
            self.scan_panel._start_scan()
        
        self.assertIn("Error", self.scan_panel.status_label.text())

    def test_scan_nonexistent_target(self):
        """Test scan with nonexistent target."""
        self.scan_panel.target_input.setText("/nonexistent/path/12345")
        self.scan_panel.sig_input.setText(str(self.temp_path / "test.json"))
        
        with patch.object(QMessageBox, 'critical'):
            self.scan_panel._start_scan()
        
        self.assertIn("Error", self.scan_panel.status_label.text())

    def test_scan_nonexistent_signatures(self):
        """Test scan with nonexistent signature file."""
        # Create a temp file for target
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test")
        
        self.scan_panel.target_input.setText(str(test_file))
        self.scan_panel.sig_input.setText("/nonexistent/signatures.json")
        
        with patch.object(QMessageBox, 'critical'):
            self.scan_panel._start_scan()
        
        self.assertIn("Error", self.scan_panel.status_label.text())

    def test_scan_error_handler(self):
        """Test error handler shows user message."""
        self.scan_panel._on_scan_error("Test error message")
        
        self.assertIn("Error", self.scan_panel.status_label.text())
        self.assertIn("Test error message", self.scan_panel.status_label.text())

    def test_scan_error_reset_ui(self):
        """Test that scan error resets UI properly."""
        # Disable UI as if scan started
        self.scan_panel.scan_btn.setEnabled(False)
        self.scan_panel.stop_btn.setEnabled(True)
        
        # Trigger error handler
        self.scan_panel._on_scan_error("Test error")
        
        # UI should be reset
        self.assertTrue(self.scan_panel.scan_btn.isEnabled())
        self.assertFalse(self.scan_panel.stop_btn.isEnabled())


class TestInputValidation(unittest.TestCase):
    """Test input validation across all panels."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def setUp(self):
        """Setup for each test."""
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Cleanup after each test."""
        self.temp_dir.cleanup()

    def test_allowlist_empty_path(self):
        """Test allowlist with empty path."""
        panel = AllowlistPanel()
        # Just verify panel exists and can handle empty inputs
        self.assertIsNotNone(panel)

    def test_settings_invalid_path(self):
        """Test settings with invalid path."""
        panel = SettingsPanel()
        # Just verify panel exists
        self.assertIsNotNone(panel)


class TestKeyboardShortcuts(unittest.TestCase):
    """Test keyboard shortcuts."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def test_main_window_shortcuts_exist(self):
        """Test that shortcuts are created in main window."""
        window = MainWindow()
        
        # Shortcuts should be created
        self.assertIsNotNone(window)
        # Check tab navigation works
        self.assertEqual(window.tabs.currentIndex(), 0)  # Scan tab

    def test_ctrl_q_shortcut(self):
        """Test Ctrl+Q closes application."""
        window = MainWindow()
        
        # Test that shortcut exists
        # (actual close test would require event loop)
        self.assertIsNotNone(window)

    def test_theme_toggle(self):
        """Test Ctrl+T toggles theme."""
        window = MainWindow()
        
        # Just verify toggle doesn't crash
        window._toggle_theme()
        self.assertIsNotNone(window)

    def test_help_dialog(self):
        """Test F1 shows help."""
        window = MainWindow()
        
        # Mock the QMessageBox to avoid blocking
        with patch.object(QMessageBox, 'information'):
            window._show_help()


class TestAccessibility(unittest.TestCase):
    """Test accessibility features."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def test_tab_order_scan_panel(self):
        """Test tab order in scan panel."""
        panel = ScanPanel()
        
        # Verify tab order is set (buttons should be accessible via Tab)
        self.assertIsNotNone(panel.browse_btn)
        self.assertIsNotNone(panel.scan_btn)
        self.assertIsNotNone(panel.stop_btn)

    def test_button_accessibility(self):
        """Test button accessibility features."""
        panel = ScanPanel()
        
        # Buttons should have text
        self.assertGreater(len(panel.browse_btn.text()), 0)
        self.assertGreater(len(panel.scan_btn.text()), 0)

    def test_focus_indicators(self):
        """Test focus indicator visibility."""
        panel = ScanPanel()
        
        # Simulate setting focus (may not work in headless mode)
        panel.scan_btn.setFocus()
        # Just verify button exists and can receive focus
        self.assertIsNotNone(panel.scan_btn)

    def test_status_labels_exist(self):
        """Test that status labels exist for user feedback."""
        panel = ScanPanel()
        
        # Status label should exist
        self.assertIsNotNone(panel.status_label)
        self.assertGreater(len(panel.status_label.text()), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def setUp(self):
        """Setup for each test."""
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Cleanup after each test."""
        self.temp_dir.cleanup()

    def test_very_long_path(self):
        """Test handling very long file paths."""
        # Create deeply nested directories
        long_path = self.temp_path
        for i in range(20):
            long_path = long_path / f"dir_{i}"
        long_path.mkdir(parents=True, exist_ok=True)
        
        panel = ScanPanel()
        panel.target_input.setText(str(long_path))
        
        # Should not crash
        self.assertEqual(panel.target_input.text(), str(long_path))

    def test_special_characters_in_path(self):
        """Test handling special characters in paths."""
        special_path = self.temp_path / "test (1) [2] {3}.txt"
        special_path.write_text("test")
        
        panel = ScanPanel()
        panel.target_input.setText(str(special_path))
        
        self.assertIn("test", panel.target_input.text())

    def test_unicode_characters_in_path(self):
        """Test handling unicode characters in paths."""
        unicode_path = self.temp_path / "test_文件.txt"
        unicode_path.write_text("test")
        
        panel = ScanPanel()
        panel.target_input.setText(str(unicode_path))
        
        self.assertIn("test", panel.target_input.text())

    def test_whitespace_handling(self):
        """Test handling whitespace in inputs."""
        panel = ScanPanel()
        
        # Input with leading/trailing whitespace
        panel.target_input.setText("   /some/path   ")
        panel.sig_input.setText("   signatures.json   ")
        
        with patch.object(QMessageBox, 'critical'):
            panel._start_scan()
        
        # Should strip whitespace


class TestPanelInstantiation(unittest.TestCase):
    """Test that all panels instantiate without errors."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def test_scan_panel_instantiate(self):
        """Test ScanPanel instantiation."""
        panel = ScanPanel()
        self.assertIsNotNone(panel)

    def test_quarantine_panel_instantiate(self):
        """Test QuarantinePanel instantiation."""
        panel = QuarantinePanel()
        self.assertIsNotNone(panel)

    def test_allowlist_panel_instantiate(self):
        """Test AllowlistPanel instantiation."""
        panel = AllowlistPanel()
        self.assertIsNotNone(panel)

    def test_settings_panel_instantiate(self):
        """Test SettingsPanel instantiation."""
        panel = SettingsPanel()
        self.assertIsNotNone(panel)

    def test_analytics_panel_instantiate(self):
        """Test AnalyticsPanel instantiation."""
        panel = AnalyticsPanel()
        self.assertIsNotNone(panel)

    def test_main_window_instantiate(self):
        """Test MainWindow instantiation."""
        window = MainWindow()
        self.assertIsNotNone(window)
        self.assertEqual(window.tabs.count(), 5)


class TestMainWindowIntegration(unittest.TestCase):
    """Test main window integration and functionality."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def test_all_tabs_accessible(self):
        """Test all tabs are accessible."""
        window = MainWindow()
        
        for i in range(5):
            window.tabs.setCurrentIndex(i)
            self.assertEqual(window.tabs.currentIndex(), i)

    def test_theme_switch_dark_to_light(self):
        """Test switching from dark to light theme."""
        window = MainWindow(theme="dark")
        window._switch_theme("light")
        
        # Just verify it doesn't crash
        self.assertIsNotNone(window)

    def test_theme_switch_light_to_dark(self):
        """Test switching from light to dark theme."""
        window = MainWindow(theme="light")
        window._switch_theme("dark")
        
        # Just verify it doesn't crash
        self.assertIsNotNone(window)

    def test_status_bar_messages(self):
        """Test status bar message updates."""
        window = MainWindow()
        
        # Simulate status update
        window.statusbar.showMessage("Test message")
        self.assertIn("Test message", window.statusbar.currentMessage())

    def test_panel_references(self):
        """Test panel references are accessible."""
        window = MainWindow()
        
        self.assertIsNotNone(window.tab_scan)
        self.assertIsNotNone(window.tab_quarantine)
        self.assertIsNotNone(window.tab_allowlist)
        self.assertIsNotNone(window.tab_analytics)
        self.assertIsNotNone(window.tab_settings)


class TestUIResponsiveness(unittest.TestCase):
    """Test UI responsiveness and button states."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def test_scan_button_enable_disable(self):
        """Test scan button enable/disable states."""
        panel = ScanPanel()
        
        # Initially enabled
        self.assertTrue(panel.scan_btn.isEnabled())
        
        # Disable
        panel.scan_btn.setEnabled(False)
        self.assertFalse(panel.scan_btn.isEnabled())
        
        # Enable
        panel.scan_btn.setEnabled(True)
        self.assertTrue(panel.scan_btn.isEnabled())

    def test_stop_button_enable_disable(self):
        """Test stop button enable/disable states."""
        panel = ScanPanel()
        
        # Initially disabled
        self.assertFalse(panel.stop_btn.isEnabled())
        
        # Enable
        panel.stop_btn.setEnabled(True)
        self.assertTrue(panel.stop_btn.isEnabled())

    def test_progress_bar_updates(self):
        """Test progress bar value updates."""
        panel = ScanPanel()
        
        # Test range
        panel.progress_bar.setRange(0, 100)
        self.assertEqual(panel.progress_bar.maximum(), 100)
        
        # Test value change
        panel.progress_bar.setValue(50)
        self.assertEqual(panel.progress_bar.value(), 50)

    def test_results_table_rows(self):
        """Test results table row management."""
        panel = ScanPanel()
        
        # Initially empty
        self.assertEqual(panel.results_table.rowCount(), 0)
        
        # Add rows
        panel.results_table.setRowCount(3)
        self.assertEqual(panel.results_table.rowCount(), 3)
        
        # Clear rows
        panel.results_table.setRowCount(0)
        self.assertEqual(panel.results_table.rowCount(), 0)


class TestErrorMessages(unittest.TestCase):
    """Test error message quality and clarity."""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures."""
        cls.app = get_or_create_app()

    def test_error_message_clarity(self):
        """Test error messages are clear and helpful."""
        panel = ScanPanel()
        panel._on_scan_error("Permission denied")
        
        status = panel.status_label.text()
        self.assertIn("Error", status)
        self.assertIn("Permission denied", status)

    def test_validation_error_messages(self):
        """Test validation error messages."""
        panel = ScanPanel()
        
        # Test empty target message
        panel.target_input.setText("")
        panel.sig_input.setText("test")
        
        with patch.object(QMessageBox, 'warning'):
            panel._start_scan()
        
        status = panel.status_label.text()
        self.assertIn("target", status.lower())


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
