"""Main application window for antivirus scanner."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStatusBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from gui.theme import ThemeManager


class MainWindow(QMainWindow):
    """Main application window with tab-based layout."""

    def __init__(self, theme: str = "dark"):
        """Initialize main window.
        
        Args:
            theme: Either 'dark' or 'light'
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.theme_manager = ThemeManager(theme)
        
        self.setWindowTitle("Antivirus Scanner - Professional Threat Detection")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup UI
        self._setup_ui()
        self._setup_menu()
        self._apply_theme()
        
        self.logger.info("Main window initialized")

    def _setup_ui(self) -> None:
        """Setup the main user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Import all panels
        from gui.widgets.scan_panel import ScanPanel
        from gui.widgets.quarantine_panel import QuarantinePanel
        from gui.widgets.allowlist_panel import AllowlistPanel
        from gui.widgets.settings_panel import SettingsPanel
        
        # Add tabs with actual panels
        self.tab_scan = ScanPanel()
        self.tab_quarantine = QuarantinePanel()
        self.tab_allowlist = AllowlistPanel()
        self.tab_analytics = self._create_empty_tab("Analytics")
        self.tab_settings = SettingsPanel()
        
        self.tabs.addTab(self.tab_scan, "Scan")
        self.tabs.addTab(self.tab_quarantine, "Quarantine")
        self.tabs.addTab(self.tab_allowlist, "Allowlist")
        self.tabs.addTab(self.tab_analytics, "Analytics")
        self.tabs.addTab(self.tab_settings, "Settings")
        
        # Setup status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def _create_empty_tab(self, name: str) -> QWidget:
        """Create an empty tab placeholder."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{name} tab - Coming soon...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget

    def _setup_menu(self) -> None:
        """Setup application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Exit", self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        theme_menu = view_menu.addMenu("Theme")
        theme_menu.addAction("Dark", lambda: self._switch_theme("dark"))
        theme_menu.addAction("Light", lambda: self._switch_theme("light"))
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self._show_about)

    def _apply_theme(self) -> None:
        """Apply the current theme to the application."""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)

    def _switch_theme(self, theme: str) -> None:
        """Switch to a different theme."""
        self.theme_manager.set_theme(theme)
        self._apply_theme()
        self.statusbar.showMessage(f"Theme changed to {theme}")
        self.logger.info(f"Theme switched to {theme}")

    def _show_about(self) -> None:
        """Show about dialog."""
        self.statusbar.showMessage("About - Antivirus Scanner v1.0.0")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.logger.info("Application closing")
        event.accept()
