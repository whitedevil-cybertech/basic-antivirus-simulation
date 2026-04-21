"""Settings Panel: Configuration and preferences management."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QGroupBox,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QSpinBox,
)
from PyQt6.QtGui import QFont


class SettingsPanel(QWidget):
    """UI for application settings and configuration."""

    # Signals
    theme_changed = pyqtSignal(str)
    settings_saved = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the settings panel.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.config_file: Optional[Path] = None
        self.settings: dict = self._default_settings()
        self._setup_ui()
        self._setup_styles()

    @staticmethod
    def _default_settings() -> dict:
        """Get default settings.

        Returns:
            Default settings dict.
        """
        return {
            "signatures_db": "malware_signatures.json",
            "quarantine_dir": "data/quarantine",
            "allowlist_file": "data/allowlist.json",
            "log_file": "scan_results.log",
            "theme": "dark",
            "verbose_logging": True,
            "auto_quarantine": True,
            "max_file_size_mb": 100,
        }

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_label = QLabel("Settings & Configuration")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        paths_group = self._create_paths_group()
        layout.addWidget(paths_group)

        options_group = self._create_options_group()
        layout.addWidget(options_group)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #2E7D32; color: white;")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _create_paths_group(self) -> QGroupBox:
        """Create the paths settings group.

        Returns:
            Paths group box.
        """
        group = QGroupBox("File Paths")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Signature Database:"))
        sig_layout = QHBoxLayout()
        self.signatures_input = QLineEdit()
        self.signatures_input.setText(
            self.settings.get("signatures_db", "")
        )
        sig_browse = QPushButton("Browse")
        sig_browse.clicked.connect(self._browse_signatures_db)
        sig_layout.addWidget(self.signatures_input)
        sig_layout.addWidget(sig_browse)
        layout.addLayout(sig_layout)

        layout.addWidget(QLabel("Quarantine Directory:"))
        quar_layout = QHBoxLayout()
        self.quarantine_input = QLineEdit()
        self.quarantine_input.setText(
            self.settings.get("quarantine_dir", "")
        )
        quar_browse = QPushButton("Browse")
        quar_browse.clicked.connect(self._browse_quarantine_dir)
        quar_layout.addWidget(self.quarantine_input)
        quar_layout.addWidget(quar_browse)
        layout.addLayout(quar_layout)

        layout.addWidget(QLabel("Allowlist File:"))
        allow_layout = QHBoxLayout()
        self.allowlist_input = QLineEdit()
        self.allowlist_input.setText(
            self.settings.get("allowlist_file", "")
        )
        allow_browse = QPushButton("Browse")
        allow_browse.clicked.connect(self._browse_allowlist_file)
        allow_layout.addWidget(self.allowlist_input)
        allow_layout.addWidget(allow_browse)
        layout.addLayout(allow_layout)

        layout.addWidget(QLabel("Log File:"))
        log_layout = QHBoxLayout()
        self.log_input = QLineEdit()
        self.log_input.setText(self.settings.get("log_file", ""))
        log_browse = QPushButton("Browse")
        log_browse.clicked.connect(self._browse_log_file)
        log_layout.addWidget(self.log_input)
        log_layout.addWidget(log_browse)
        layout.addLayout(log_layout)

        group.setLayout(layout)
        return group

    def _create_options_group(self) -> QGroupBox:
        """Create the options settings group.

        Returns:
            Options group box.
        """
        group = QGroupBox("Options")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Theme:"))
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = self.settings.get("theme", "dark")
        self.theme_combo.setCurrentText(
            "Dark" if current_theme == "dark" else "Light"
        )
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        self.verbose_check = QCheckBox("Verbose Logging")
        self.verbose_check.setChecked(
            self.settings.get("verbose_logging", True)
        )
        layout.addWidget(self.verbose_check)

        self.auto_quarantine_check = QCheckBox("Auto-Quarantine Threats")
        self.auto_quarantine_check.setChecked(
            self.settings.get("auto_quarantine", True)
        )
        layout.addWidget(self.auto_quarantine_check)

        layout.addWidget(QLabel("Max File Size (MB):"))
        size_layout = QHBoxLayout()
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setMinimum(1)
        self.max_size_spin.setMaximum(10000)
        self.max_size_spin.setValue(
            self.settings.get("max_file_size_mb", 100)
        )
        size_layout.addWidget(self.max_size_spin)
        size_layout.addStretch()
        layout.addLayout(size_layout)

        group.setLayout(layout)
        return group

    def _setup_styles(self) -> None:
        """Apply styling to the panel."""
        self.setStyleSheet(
            """
            SettingsPanel {
                background-color: #f5f5f5;
                padding: 10px;
            }
            QGroupBox {
                font-weight: bold;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
                background-color: #1976d2;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QCheckBox {
                spacing: 8px;
            }
            """
        )

    def set_config_file(self, config_file: str | Path) -> None:
        """Set the configuration file path and load settings.

        Args:
            config_file: Path to config.json.
        """
        self.config_file = Path(config_file).expanduser().resolve()
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from config file."""
        if not self.config_file or not self.config_file.exists():
            self.settings = self._default_settings()
        else:
            try:
                content = self.config_file.read_text(encoding="utf-8")
                loaded = json.loads(content)
                self.settings = {**self._default_settings(), **loaded}
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
                self.settings = self._default_settings()

        self._refresh_ui()

    def _refresh_ui(self) -> None:
        """Refresh UI with current settings."""
        self.signatures_input.setText(
            self.settings.get("signatures_db", "")
        )
        self.quarantine_input.setText(
            self.settings.get("quarantine_dir", "")
        )
        self.allowlist_input.setText(
            self.settings.get("allowlist_file", "")
        )
        self.log_input.setText(self.settings.get("log_file", ""))

        theme = self.settings.get("theme", "dark")
        self.theme_combo.setCurrentText(
            "Dark" if theme == "dark" else "Light"
        )
        self.verbose_check.setChecked(
            self.settings.get("verbose_logging", True)
        )
        self.auto_quarantine_check.setChecked(
            self.settings.get("auto_quarantine", True)
        )
        self.max_size_spin.setValue(
            self.settings.get("max_file_size_mb", 100)
        )

    def _browse_signatures_db(self) -> None:
        """Browse for signature database file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Signature Database",
            filter="JSON Files (*.json)",
        )
        if path:
            self.signatures_input.setText(path)

    def _browse_quarantine_dir(self) -> None:
        """Browse for quarantine directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Quarantine Directory",
        )
        if path:
            self.quarantine_input.setText(path)

    def _browse_allowlist_file(self) -> None:
        """Browse for allowlist file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Allowlist File",
            filter="JSON Files (*.json)",
        )
        if path:
            self.allowlist_input.setText(path)

    def _browse_log_file(self) -> None:
        """Browse for log file."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            filter="Log Files (*.log);;Text Files (*.txt)",
        )
        if path:
            self.log_input.setText(path)

    def _reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings = self._default_settings()
            self._refresh_ui()
            self.status_label.setText("Reset to default settings")

    def _save_settings(self) -> None:
        """Save settings to config file."""
        try:
            self.settings = {
                "signatures_db": self.signatures_input.text(),
                "quarantine_dir": self.quarantine_input.text(),
                "allowlist_file": self.allowlist_input.text(),
                "log_file": self.log_input.text(),
                "theme": "dark" if self.theme_combo.currentText() == "Dark" else "light",
                "verbose_logging": self.verbose_check.isChecked(),
                "auto_quarantine": self.auto_quarantine_check.isChecked(),
                "max_file_size_mb": self.max_size_spin.value(),
            }

            if not self.config_file:
                config_dir = Path.home() / ".antivirus"
                config_dir.mkdir(parents=True, exist_ok=True)
                self.config_file = config_dir / "config.json"

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(
                json.dumps(self.settings, indent=2),
                encoding="utf-8",
            )

            self.status_label.setText(
                f"Settings saved to {self.config_file}"
            )

            if self.theme_combo.currentText() == "Dark":
                self.theme_changed.emit("dark")
            else:
                self.theme_changed.emit("light")

            self.settings_saved.emit(self.settings)

            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully",
            )
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings:\n{str(e)}",
            )

    def get_settings(self) -> dict:
        """Get current settings.

        Returns:
            Settings dict.
        """
        return self.settings.copy()
