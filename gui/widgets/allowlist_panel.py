"""Allowlist Panel: Manage whitelisted paths and file hashes."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
    QHeaderView,
    QTabWidget,
    QLineEdit,
    QFileDialog,
)
from PyQt6.QtGui import QColor, QFont

from scanner.signatures import load_allowlist, save_allowlist, add_to_allowlist


class AllowlistPanel(QWidget):
    """UI for managing the allowlist."""

    status_update = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the allowlist panel.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.allowlist_path: Optional[Path] = None
        self.allowlist: dict = {"paths": [], "hashes": []}
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_label = QLabel("Allowlist Management")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.tabs = QTabWidget()

        self.paths_widget = self._create_paths_tab()
        self.hashes_widget = self._create_hashes_tab()

        self.tabs.addTab(self.paths_widget, "Whitelisted Paths")
        self.tabs.addTab(self.hashes_widget, "Whitelisted Hashes")

        layout.addWidget(self.tabs)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def _create_paths_tab(self) -> QWidget:
        """Create the paths tab.

        Returns:
            Paths tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.paths_table = QTableWidget()
        self.paths_table.setColumnCount(2)
        self.paths_table.setHorizontalHeaderLabels(["Path", "Added"])
        self.paths_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.paths_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.paths_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.paths_table.setAlternatingRowColors(True)
        layout.addWidget(self.paths_table)

        button_layout = QHBoxLayout()

        add_path_btn = QPushButton("Add Path")
        add_path_btn.clicked.connect(self._add_path_dialog)
        button_layout.addWidget(add_path_btn)

        browse_path_btn = QPushButton("Browse & Add")
        browse_path_btn.clicked.connect(self._browse_and_add_path)
        button_layout.addWidget(browse_path_btn)

        button_layout.addStretch()

        remove_path_btn = QPushButton("Remove Selected")
        remove_path_btn.setStyleSheet("background-color: #C62828; color: white;")
        remove_path_btn.clicked.connect(self._remove_selected_path)
        button_layout.addWidget(remove_path_btn)

        layout.addLayout(button_layout)
        return tab

    def _create_hashes_tab(self) -> QWidget:
        """Create the hashes tab.

        Returns:
            Hashes tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.hashes_table = QTableWidget()
        self.hashes_table.setColumnCount(2)
        self.hashes_table.setHorizontalHeaderLabels(["SHA-256 Hash", "Added"])
        self.hashes_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.hashes_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.hashes_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.hashes_table.setAlternatingRowColors(True)
        layout.addWidget(self.hashes_table)

        input_layout = QHBoxLayout()
        label = QLabel("Add Hash:")
        self.hash_input = QLineEdit()
        self.hash_input.setPlaceholderText(
            "Paste SHA-256 hash (64 hex characters)"
        )
        add_hash_btn = QPushButton("Add")
        add_hash_btn.clicked.connect(self._add_hash_from_input)
        input_layout.addWidget(label)
        input_layout.addWidget(self.hash_input)
        input_layout.addWidget(add_hash_btn)
        layout.addLayout(input_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        remove_hash_btn = QPushButton("Remove Selected")
        remove_hash_btn.setStyleSheet("background-color: #C62828; color: white;")
        remove_hash_btn.clicked.connect(self._remove_selected_hash)
        button_layout.addWidget(remove_hash_btn)

        layout.addLayout(button_layout)
        return tab

    def _setup_styles(self) -> None:
        """Apply styling to the panel."""
        self.setStyleSheet(
            """
            AllowlistPanel {
                background-color: #f5f5f5;
                padding: 10px;
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
            QLineEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item:selected {
                background-color: #bbdefb;
            }
            """
        )

    def set_allowlist_path(self, allowlist_path: str | Path) -> None:
        """Set the allowlist file path and load entries.

        Args:
            allowlist_path: Path to allowlist.json.
        """
        self.allowlist_path = Path(allowlist_path).expanduser().resolve()
        self._load_allowlist()

    def _load_allowlist(self) -> None:
        """Load and display allowlist entries."""
        if not self.allowlist_path or not self.allowlist_path.exists():
            self.allowlist = {"paths": [], "hashes": []}
        else:
            try:
                self.allowlist = load_allowlist(self.allowlist_path)
            except Exception as e:
                logging.error(f"Failed to load allowlist: {e}")
                self.status_label.setText(f"Error loading allowlist: {e}")
                self.allowlist = {"paths": [], "hashes": []}

        self._refresh_paths_table()
        self._refresh_hashes_table()

    def _refresh_paths_table(self) -> None:
        """Refresh the paths table display."""
        paths = self.allowlist.get("paths", [])
        self.paths_table.setRowCount(len(paths))

        for row, path in enumerate(paths):
            path_item = QTableWidgetItem(path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.paths_table.setItem(row, 0, path_item)

            status_item = QTableWidgetItem("Path")
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setBackground(QColor("#E8F5E9"))
            self.paths_table.setItem(row, 1, status_item)

    def _refresh_hashes_table(self) -> None:
        """Refresh the hashes table display."""
        hashes = self.allowlist.get("hashes", [])
        self.hashes_table.setRowCount(len(hashes))

        for row, hash_val in enumerate(hashes):
            hash_item = QTableWidgetItem(hash_val)
            hash_item.setFlags(hash_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.hashes_table.setItem(row, 0, hash_item)

            status_item = QTableWidgetItem("Hash")
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setBackground(QColor("#E3F2FD"))
            self.hashes_table.setItem(row, 1, status_item)

        self.status_label.setText(
            f"Allowlist: {len(self.allowlist.get('paths', []))} paths, "
            f"{len(self.allowlist.get('hashes', []))} hashes"
        )

    def _add_path_dialog(self) -> None:
        """Show dialog to add a path."""
        path, ok = QLineEdit().text(), False
        label = QLabel("Enter absolute path:")
        input_field = QLineEdit()
        input_field.setPlaceholderText(
            "e.g., /safe/app or C:\\Program Files\\App"
        )

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Add Path to Allowlist")
        dialog.setText("Enter the absolute path to whitelist:")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        input_field = QLineEdit()
        input_field.setPlaceholderText(
            "e.g., /safe/app or C:\\Program Files\\App"
        )
        layout = QVBoxLayout()
        layout.addWidget(input_field)
        dialog.layout().insertLayout(0, layout)

        if dialog.exec() == QMessageBox.StandardButton.Ok:
            path = input_field.text().strip()
            if path:
                self._add_path(path)

    def _browse_and_add_path(self) -> None:
        """Browse for a file or directory to add to allowlist."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Whitelist",
        )

        if path:
            self._add_path(path)

    def _add_path(self, path: str) -> None:
        """Add a path to the allowlist.

        Args:
            path: Path to add.
        """
        try:
            if not self.allowlist_path:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Allowlist path not set",
                )
                return

            add_to_allowlist(self.allowlist_path, file_path=path)
            self._load_allowlist()
            self.status_label.setText(f"Added path: {path}")
        except Exception as e:
            logging.error(f"Failed to add path: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add path:\n{str(e)}",
            )

    def _remove_selected_path(self) -> None:
        """Remove the selected path from allowlist."""
        current_row = self.paths_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a path to remove.",
            )
            return

        path = self.paths_table.item(current_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove '{path}' from allowlist?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if not self.allowlist_path:
                raise ValueError("Allowlist path not set")

            self.allowlist["paths"].remove(path)
            save_allowlist(self.allowlist_path, self.allowlist)
            self._load_allowlist()
            self.status_label.setText(f"Removed path: {path}")
        except Exception as e:
            logging.error(f"Failed to remove path: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to remove path:\n{str(e)}",
            )

    def _add_hash_from_input(self) -> None:
        """Add hash from input field to allowlist."""
        hash_val = self.hash_input.text().strip()

        if not hash_val:
            QMessageBox.warning(
                self,
                "Empty Input",
                "Please enter a SHA-256 hash.",
            )
            return

        self._add_hash(hash_val)
        self.hash_input.clear()

    def _add_hash(self, hash_val: str) -> None:
        """Add a hash to the allowlist.

        Args:
            hash_val: SHA-256 hash to add.
        """
        try:
            if not self.allowlist_path:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Allowlist path not set",
                )
                return

            add_to_allowlist(self.allowlist_path, file_hash=hash_val)
            self._load_allowlist()
            self.status_label.setText(f"Added hash: {hash_val[:16]}...")
        except Exception as e:
            logging.error(f"Failed to add hash: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add hash:\n{str(e)}",
            )

    def _remove_selected_hash(self) -> None:
        """Remove the selected hash from allowlist."""
        current_row = self.hashes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a hash to remove.",
            )
            return

        hash_val = self.hashes_table.item(current_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove '{hash_val[:16]}...' from allowlist?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if not self.allowlist_path:
                raise ValueError("Allowlist path not set")

            self.allowlist["hashes"].remove(hash_val)
            save_allowlist(self.allowlist_path, self.allowlist)
            self._load_allowlist()
            self.status_label.setText(f"Removed hash: {hash_val[:16]}...")
        except Exception as e:
            logging.error(f"Failed to remove hash: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to remove hash:\n{str(e)}",
            )
