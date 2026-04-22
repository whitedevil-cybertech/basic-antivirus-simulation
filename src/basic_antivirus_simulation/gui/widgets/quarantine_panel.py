"""Quarantine Panel: List, restore, and delete quarantined files."""

from __future__ import annotations

import logging
from datetime import datetime
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
)
from PyQt6.QtGui import QColor, QFont

from basic_antivirus_simulation.scanner.quarantine import list_quarantine, restore_file


class QuarantinePanel(QWidget):
    """UI for managing quarantined files."""

    # Signals
    status_update = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the quarantine panel.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.quarantine_dir: Optional[Path] = None
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_label = QLabel("Quarantined Files")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Original Path",
                "File Hash",
                "Threat Name",
                "Timestamp",
                "Size",
                "Status",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_quarantine_list)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch()

        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.clicked.connect(self._restore_selected)
        self.restore_btn.setStyleSheet("background-color: #2E7D32; color: white;")
        button_layout.addWidget(self.restore_btn)

        self.delete_btn = QPushButton("Delete Permanently")
        self.delete_btn.clicked.connect(self._delete_selected)
        self.delete_btn.setStyleSheet("background-color: #C62828; color: white;")
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def _setup_styles(self) -> None:
        """Apply styling to the panel."""
        self.setStyleSheet(
            """
            QuarantinePanel {
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

    def set_quarantine_directory(self, quarantine_dir: str | Path) -> None:
        """Set the quarantine directory and load files.

        Args:
            quarantine_dir: Path to quarantine directory.
        """
        self.quarantine_dir = Path(quarantine_dir).expanduser().resolve()
        self._refresh_quarantine_list()

    def _refresh_quarantine_list(self) -> None:
        """Refresh the list of quarantined files."""
        if not self.quarantine_dir:
            self.status_label.setText("Quarantine directory not set")
            return

        try:
            manifest = list_quarantine(self.quarantine_dir)
            self.table.setRowCount(len(manifest))

            for row, entry in enumerate(manifest):
                self._populate_row(row, entry)

            self.status_label.setText(
                f"Loaded {len(manifest)} quarantined file(s)"
            )
        except Exception as e:
            logging.error(f"Failed to load quarantine list: {e}")
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load quarantine list:\n{str(e)}",
            )

    def _populate_row(self, row: int, entry: dict) -> None:
        """Populate a table row with quarantine entry data.

        Args:
            row: Row index.
            entry: Manifest entry dict.
        """
        original_path = entry.get("original_path", "Unknown")
        file_hash = entry.get("hash", "N/A")[:16] + "..."
        threat_name = entry.get("threat_name", "Unknown")
        timestamp = entry.get("timestamp", "Unknown")
        quarantine_path = entry.get("quarantine_path", "")

        try:
            if Path(quarantine_path).exists():
                file_size = Path(quarantine_path).stat().st_size
                size_str = self._format_size(file_size)
            else:
                size_str = "N/A"
        except Exception:
            size_str = "N/A"

        try:
            ts_obj = datetime.fromisoformat(timestamp)
            timestamp_str = ts_obj.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            timestamp_str = timestamp

        items = [
            QTableWidgetItem(original_path),
            QTableWidgetItem(file_hash),
            QTableWidgetItem(threat_name),
            QTableWidgetItem(timestamp_str),
            QTableWidgetItem(size_str),
            QTableWidgetItem("Quarantined"),
        ]

        for col, item in enumerate(items):
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if col == 5:
                item.setBackground(QColor("#FFEBEE"))
            self.table.setItem(row, col, item)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size.

        Args:
            size_bytes: Size in bytes.

        Returns:
            Formatted size string.
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _restore_selected(self) -> None:
        """Restore the selected quarantined file."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a file to restore.",
            )
            return

        original_path = self.table.item(current_row, 0).text()
        threat_name = self.table.item(current_row, 2).text()

        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Restore '{original_path}'?\n\nThreat: {threat_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if not self.quarantine_dir:
                raise ValueError("Quarantine directory not set")

            manifest = list_quarantine(self.quarantine_dir)
            entry = manifest[current_row]
            quarantine_path = entry.get("quarantine_path")

            if not quarantine_path:
                raise ValueError("Quarantine path not found in manifest")

            restored_path = restore_file(
                self.quarantine_dir,
                quarantine_path,
                force=False,
            )

            QMessageBox.information(
                self,
                "Success",
                f"File restored to:\n{restored_path}",
            )
            self._refresh_quarantine_list()
        except FileExistsError as e:
            reply = QMessageBox.question(
                self,
                "File Exists",
                f"{str(e)}\n\nForce overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    manifest = list_quarantine(self.quarantine_dir)
                    entry = manifest[current_row]
                    quarantine_path = entry.get("quarantine_path")
                    restored_path = restore_file(
                        self.quarantine_dir,
                        quarantine_path,
                        force=True,
                    )
                    QMessageBox.information(
                        self,
                        "Success",
                        f"File restored to:\n{restored_path}",
                    )
                    self._refresh_quarantine_list()
                except Exception as err:
                    logging.error(f"Restore failed: {err}")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Restore failed:\n{str(err)}",
                    )
        except Exception as e:
            logging.error(f"Restore failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Restore failed:\n{str(e)}",
            )

    def _delete_selected(self) -> None:
        """Delete the selected quarantined file permanently."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a file to delete.",
            )
            return

        original_path = self.table.item(current_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Permanent Deletion",
            f"Permanently delete '{original_path}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if not self.quarantine_dir:
                raise ValueError("Quarantine directory not set")

            manifest = list_quarantine(self.quarantine_dir)
            entry = manifest[current_row]
            quarantine_path = entry.get("quarantine_path")

            if not quarantine_path:
                raise ValueError("Quarantine path not found")

            qpath = Path(quarantine_path)
            if qpath.exists():
                qpath.unlink()
                logging.info(f"Deleted: {quarantine_path}")

            manifest = [
                e for e in manifest
                if e.get("quarantine_path") != quarantine_path
            ]

            import json
            manifest_path = self.quarantine_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2),
                encoding="utf-8",
            )

            QMessageBox.information(
                self,
                "Success",
                "File deleted permanently.",
            )
            self._refresh_quarantine_list()
        except Exception as e:
            logging.error(f"Delete failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Delete failed:\n{str(e)}",
            )
