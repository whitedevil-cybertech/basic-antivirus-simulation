"""Scan panel widget for file/directory scanning."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QColor

from basic_antivirus_simulation.scanner.scanner import scan_target, ScanOptions
from basic_antivirus_simulation.scanner.signatures import load_signatures
from basic_antivirus_simulation.gui.dialogs.scan_dialog import ScanOptionsDialog


class ScanWorker(QThread):
    """Worker thread for background file scanning."""

    # Signals
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    result = pyqtSignal(list)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        target_path: str,
        signatures_path: str,
        quarantine_dir: Optional[str] = None,
        options: Optional[ScanOptions] = None,
    ):
        """Initialize scan worker.
        
        Args:
            target_path: Path to scan
            signatures_path: Path to signature database
            quarantine_dir: Optional quarantine directory
            options: ScanOptions for filtering
        """
        super().__init__()
        self.target_path = target_path
        self.signatures_path = signatures_path
        self.quarantine_dir = quarantine_dir
        self.options = options or ScanOptions()
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        """Run the scan in background."""
        try:
            self.status_update.emit("Loading signatures...")
            self.progress.emit(10)

            # Load signatures
            signatures = load_signatures(self.signatures_path)
            self.logger.info(f"Loaded {len(signatures)} signatures")

            self.status_update.emit("Scanning files...")
            self.progress.emit(25)

            # Perform scan
            results = scan_target(
                self.target_path,
                signatures,
                quarantine_dir=self.quarantine_dir,
                options=self.options,
            )

            self.status_update.emit("Processing results...")
            self.progress.emit(90)

            # Emit results
            self.result.emit(results)
            self.progress.emit(100)
            self.status_update.emit("Scan completed successfully")

        except Exception as e:
            self.logger.error(f"Scan error: {e}")
            self.error.emit(str(e))
            self.progress.emit(0)
        finally:
            self.finished.emit()


class ScanPanel(QWidget):
    """Panel for scanning files and directories."""

    def __init__(self, parent=None):
        """Initialize scan panel."""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.scan_worker: Optional[ScanWorker] = None
        self.scan_results: list = []
        self.scan_options: dict = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the scan panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ═════════════════════════════════════════════════════════════
        # Input Section
        # ═════════════════════════════════════════════════════════════
        input_group = QGroupBox("Scan Target")
        input_layout = QHBoxLayout(input_group)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Select a file or directory to scan...")
        input_layout.addWidget(QLabel("Path:"), 0)
        input_layout.addWidget(self.target_input, 1)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_target)
        input_layout.addWidget(self.browse_btn, 0)

        layout.addWidget(input_group)

        # ═════════════════════════════════════════════════════════════
        # Options Section
        # ═════════════════════════════════════════════════════════════
        options_group = QGroupBox("Scan Options")
        options_layout = QHBoxLayout(options_group)

        self.sig_input = QLineEdit()
        self.sig_input.setPlaceholderText("Path to signature database (JSON or TXT)")
        options_layout.addWidget(QLabel("Signatures:"), 0)
        options_layout.addWidget(self.sig_input, 1)

        self.sig_browse_btn = QPushButton("Browse...")
        self.sig_browse_btn.clicked.connect(self._browse_signatures)
        options_layout.addWidget(self.sig_browse_btn, 0)

        self.quarantine_input = QLineEdit()
        self.quarantine_input.setPlaceholderText("Optional quarantine directory")
        options_layout.addWidget(QLabel("Quarantine:"), 0)
        options_layout.addWidget(self.quarantine_input, 1)

        self.quarantine_btn = QPushButton("Browse...")
        self.quarantine_btn.clicked.connect(self._browse_quarantine)
        options_layout.addWidget(self.quarantine_btn, 0)

        layout.addWidget(options_group)

        # ═════════════════════════════════════════════════════════════
        # Control Section
        # ═════════════════════════════════════════════════════════════
        control_layout = QHBoxLayout()

        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.clicked.connect(self._start_scan)
        control_layout.addWidget(self.scan_btn)

        self.stop_btn = QPushButton("Stop Scan")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_scan)
        control_layout.addWidget(self.stop_btn)

        self.advanced_btn = QPushButton("Advanced Options")
        self.advanced_btn.setMinimumHeight(40)
        self.advanced_btn.clicked.connect(self._show_advanced)
        control_layout.addWidget(self.advanced_btn)

        layout.addLayout(control_layout)

        # ═════════════════════════════════════════════════════════════
        # Progress Section
        # ═════════════════════════════════════════════════════════════
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to scan")
        self.status_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(self.status_label)

        # ═════════════════════════════════════════════════════════════
        # Results Section
        # ═════════════════════════════════════════════════════════════
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout(results_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "File Path",
            "Status",
            "Threat",
            "Severity",
            "Quarantined To",
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.results_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        results_layout.addWidget(self.results_table)

        layout.addWidget(results_group)

        # ═════════════════════════════════════════════════════════════
        # Summary Section
        # ═════════════════════════════════════════════════════════════
        summary_layout = QHBoxLayout()

        self.summary_label = QLabel("No scan performed yet")
        self.summary_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()

        layout.addLayout(summary_layout)

    def _browse_target(self) -> None:
        """Browse for target file or directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if path:
            self.target_input.setText(path)
            self.logger.info(f"Selected target: {path}")

    def _browse_signatures(self) -> None:
        """Browse for signature database."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Signature Database",
            "",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)",
        )
        if path:
            self.sig_input.setText(path)
            self.logger.info(f"Selected signatures: {path}")

    def _browse_quarantine(self) -> None:
        """Browse for quarantine directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Quarantine Directory")
        if path:
            self.quarantine_input.setText(path)
            self.logger.info(f"Selected quarantine: {path}")

    def _start_scan(self) -> None:
        """Start the scan process."""
        target = self.target_input.text().strip()
        signatures = self.sig_input.text().strip()

        # Input validation
        try:
            if not target:
                self.status_label.setText("Error: Please select a target directory")
                QMessageBox.warning(self, "Input Required", "Please select a target directory to scan.")
                self.logger.warning("Scan attempted without target")
                return

            if not signatures:
                self.status_label.setText("Error: Please select a signature database")
                QMessageBox.warning(self, "Input Required", "Please select a signature database.")
                self.logger.warning("Scan attempted without signatures")
                return

            # Path validation
            target_path = Path(target)
            if not target_path.exists():
                self.status_label.setText(f"Error: Target path not found: {target}")
                QMessageBox.critical(self, "Path Not Found", f"Target path does not exist:\n{target}")
                self.logger.error(f"Target path not found: {target}")
                return

            if not target_path.is_dir() and not target_path.is_file():
                self.status_label.setText(f"Error: Invalid target path: {target}")
                QMessageBox.critical(self, "Invalid Path", f"Target is neither a file nor directory:\n{target}")
                self.logger.error(f"Invalid target path: {target}")
                return

            sig_path = Path(signatures)
            if not sig_path.exists():
                self.status_label.setText(f"Error: Signature file not found: {signatures}")
                QMessageBox.critical(self, "Signature File Not Found", f"Signature database not found:\n{signatures}")
                self.logger.error(f"Signature file not found: {signatures}")
                return

            if not sig_path.is_file():
                self.status_label.setText(f"Error: Signature path is not a file: {signatures}")
                QMessageBox.critical(self, "Invalid Signature File", f"Signature path must be a file:\n{signatures}")
                self.logger.error(f"Signature path is not a file: {signatures}")
                return

            # Quarantine directory validation
            quarantine = self.quarantine_input.text().strip() or None
            if quarantine:
                quarantine_path = Path(quarantine)
                if quarantine_path.exists() and not quarantine_path.is_dir():
                    self.status_label.setText(f"Error: Quarantine path is not a directory: {quarantine}")
                    QMessageBox.critical(self, "Invalid Quarantine Path", 
                                       f"Quarantine path must be a directory:\n{quarantine}")
                    self.logger.error(f"Quarantine path is not a directory: {quarantine}")
                    return

            # Clear previous results
            self.results_table.setRowCount(0)
            self.scan_results = []

            # Setup worker thread
            self.scan_worker = ScanWorker(target, signatures, quarantine)

            # Connect signals
            self.scan_worker.progress.connect(self._on_progress)
            self.scan_worker.status_update.connect(self._on_status_update)
            self.scan_worker.result.connect(self._on_scan_result)
            self.scan_worker.error.connect(self._on_scan_error)
            self.scan_worker.finished.connect(self._on_scan_finished)

            # Update UI
            self.scan_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.browse_btn.setEnabled(False)
            self.sig_browse_btn.setEnabled(False)

            # Start scanning
            self.scan_worker.start()
            self.logger.info(f"Scan started: {target}")
            self.status_label.setText("Initializing scan...")

        except Exception as e:
            error_msg = str(e)
            self.status_label.setText(f"Error: {error_msg}")
            QMessageBox.critical(self, "Scan Error", f"Failed to start scan:\n{error_msg}")
            self.logger.error(f"Exception during scan start: {e}", exc_info=True)

    def _stop_scan(self) -> None:
        """Stop the current scan."""
        if self.scan_worker:
            self.scan_worker.quit()
            self.scan_worker.wait()
            self.status_label.setText("Scan stopped by user")
            self._reset_ui()
            self.logger.info("Scan stopped")

    def _show_advanced(self) -> None:
        """Show advanced options dialog."""
        dialog = ScanOptionsDialog(self)
        dialog.set_options(self.scan_options)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.scan_options = dialog.get_options()
            self.status_label.setText(f"Advanced options configured")
            self.logger.info(f"Advanced options updated: {self.scan_options}")

    def _on_progress(self, value: int) -> None:
        """Handle progress update."""
        self.progress_bar.setValue(value)

    def _on_status_update(self, message: str) -> None:
        """Handle status update."""
        self.status_label.setText(message)
        self.logger.debug(f"Status: {message}")

    def _on_scan_result(self, results: list) -> None:
        """Handle scan results."""
        self.scan_results = results
        self._display_results(results)
        self.logger.info(f"Scan completed: {len(results)} files scanned")

    def _on_scan_error(self, error: str) -> None:
        """Handle scan error with user-friendly message."""
        self.status_label.setText(f"Error: {error}")
        self.logger.error(f"Scan error: {error}")
        self._reset_ui()
        
        # Show user-friendly error message
        error_details = error.split(":")[-1].strip() if ":" in error else error
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n\n{error_details}\n\nPlease check the paths and try again.")

    def _on_scan_finished(self) -> None:
        """Handle scan finished."""
        self._reset_ui()

    def _reset_ui(self) -> None:
        """Reset UI to ready state."""
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.browse_btn.setEnabled(True)
        self.sig_browse_btn.setEnabled(True)

    def _display_results(self, results: list) -> None:
        """Display scan results in table."""
        self.results_table.setRowCount(len(results))

        malicious_count = 0
        clean_count = 0

        for row, result in enumerate(results):
            status = "Malicious" if result.is_malicious else "Clean"
            if result.is_malicious:
                malicious_count += 1
            else:
                clean_count += 1

            # File path
            path_item = QTableWidgetItem(str(result.path))
            self.results_table.setItem(row, 0, path_item)

            # Status
            status_item = QTableWidgetItem(status)
            if result.is_malicious:
                status_item.setBackground(QColor("#da3633"))
                status_item.setForeground(QColor("#ffffff"))
            else:
                status_item.setBackground(QColor("#238636"))
                status_item.setForeground(QColor("#ffffff"))
            self.results_table.setItem(row, 1, status_item)

            # Threat name
            threat_item = QTableWidgetItem(result.threat_name or "-")
            self.results_table.setItem(row, 2, threat_item)

            # Severity
            severity_item = QTableWidgetItem(result.severity or "-")
            self.results_table.setItem(row, 3, severity_item)

            # Quarantined to
            quarantine_item = QTableWidgetItem(str(result.quarantined_to) if result.quarantined_to else "-")
            self.results_table.setItem(row, 4, quarantine_item)

        # Update summary
        total = len(results)
        summary = f"Scan Results: {total} files scanned | {malicious_count} malicious | {clean_count} clean"
        self.summary_label.setText(summary)
