"""Advanced scan options dialog."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QGroupBox,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt


class ScanOptionsDialog(QDialog):
    """Dialog for advanced scan options."""

    def __init__(self, parent=None):
        """Initialize the options dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.options = {
            "file_types": "",
            "exclude_dirs": "",
            "recursive": True,
            "follow_symlinks": False,
        }
        self._setup_ui()
        self.setWindowTitle("Advanced Scan Options")
        self.setGeometry(100, 100, 500, 400)

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # File Types Section
        file_types_group = QGroupBox("File Types")
        file_types_layout = QVBoxLayout(file_types_group)

        file_types_label = QLabel(
            "Scan only specific file types (e.g., .exe,.dll,.zip)\nLeave empty to scan all files:"
        )
        file_types_layout.addWidget(file_types_label)

        self.file_types_input = QLineEdit()
        self.file_types_input.setPlaceholderText(".exe,.dll,.zip")
        file_types_layout.addWidget(self.file_types_input)

        layout.addWidget(file_types_group)

        # Exclusions Section
        exclusions_group = QGroupBox("Exclusions")
        exclusions_layout = QVBoxLayout(exclusions_group)

        exclude_dirs_label = QLabel(
            "Skip specific directories (e.g., System32,ProgramFiles)\nUse comma-separated directory names:"
        )
        exclusions_layout.addWidget(exclude_dirs_label)

        self.exclude_dirs_input = QLineEdit()
        self.exclude_dirs_input.setPlaceholderText("System32,AppData,node_modules")
        exclusions_layout.addWidget(self.exclude_dirs_input)

        layout.addWidget(exclusions_group)

        # Scan Behavior Section
        behavior_group = QGroupBox("Scan Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        self.recursive_check = QCheckBox("Scan subdirectories recursively")
        self.recursive_check.setChecked(True)
        behavior_layout.addWidget(self.recursive_check)

        self.symlinks_check = QCheckBox("Follow symbolic links")
        self.symlinks_check.setChecked(False)
        behavior_layout.addWidget(self.symlinks_check)

        layout.addWidget(behavior_group)

        # Button Section
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def get_options(self) -> dict:
        """Get the selected options.
        
        Returns:
            Dictionary of scan options
        """
        return {
            "file_types": self.file_types_input.text().strip(),
            "exclude_dirs": self.exclude_dirs_input.text().strip(),
            "recursive": self.recursive_check.isChecked(),
            "follow_symlinks": self.symlinks_check.isChecked(),
        }

    def set_options(self, options: dict) -> None:
        """Set the options in the dialog.
        
        Args:
            options: Dictionary of options to set
        """
        if "file_types" in options:
            self.file_types_input.setText(options["file_types"])
        if "exclude_dirs" in options:
            self.exclude_dirs_input.setText(options["exclude_dirs"])
        if "recursive" in options:
            self.recursive_check.setChecked(options["recursive"])
        if "follow_symlinks" in options:
            self.symlinks_check.setChecked(options["follow_symlinks"])
