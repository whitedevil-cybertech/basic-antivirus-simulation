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
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

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
        from gui.widgets.analytics_panel import AnalyticsPanel
        from gui.widgets.settings_panel import SettingsPanel
        
        # Add tabs with actual panels
        self.tab_scan = ScanPanel()
        self.tab_quarantine = QuarantinePanel()
        self.tab_allowlist = AllowlistPanel()
        self.tab_analytics = AnalyticsPanel()
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
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()

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

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for common actions."""
        # Ctrl+S: Start scan
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self._trigger_scan())
        
        # Ctrl+Q: Quit application
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        
        # Ctrl+H: Go to Quarantine tab
        QShortcut(QKeySequence("Ctrl+H"), self, lambda: self.tabs.setCurrentIndex(1))
        
        # Ctrl+W: Go to Allowlist tab
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.tabs.setCurrentIndex(2))
        
        # Ctrl+A: Go to Analytics tab
        QShortcut(QKeySequence("Ctrl+A"), self, lambda: self.tabs.setCurrentIndex(3))
        
        # Ctrl+E: Go to Settings tab
        QShortcut(QKeySequence("Ctrl+E"), self, lambda: self.tabs.setCurrentIndex(4))
        
        # Ctrl+T: Switch theme
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_theme)
        
        # F1: Show help
        QShortcut(QKeySequence("F1"), self, self._show_help)
        
        self.logger.info("Keyboard shortcuts initialized")

    def _trigger_scan(self) -> None:
        """Trigger scan from keyboard shortcut."""
        self.tabs.setCurrentIndex(0)  # Go to Scan tab
        self.statusbar.showMessage("Scan tab active - click 'Start Scan' or press Ctrl+S again")

    def _toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        current = self.theme_manager.current_theme
        new_theme = "light" if current == "dark" else "dark"
        self._switch_theme(new_theme)

    def _show_help(self) -> None:
        """Show keyboard shortcuts help."""
        help_text = """
Keyboard Shortcuts:

Ctrl+S  - Go to Scan tab (then click Start Scan button)
Ctrl+Q  - Quit application
Ctrl+H  - Go to Quarantine tab
Ctrl+W  - Go to Allowlist tab
Ctrl+A  - Go to Analytics tab
Ctrl+E  - Go to Settings tab
Ctrl+T  - Toggle between dark/light theme
F1      - Show this help

Tab     - Move between controls in current panel
Enter   - Activate focused button
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text.strip())

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.logger.info("Application closing")
        event.accept()
