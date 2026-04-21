"""Report Dialog: Detailed scan report with export options."""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtGui import QFont

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ReportDialog(QDialog):
    """Dialog for viewing and exporting detailed scan reports."""

    def __init__(
        self,
        statistics: dict,
        quarantine_dir: Optional[Path] = None,
        parent: Optional[QDialog] = None,
    ):
        """Initialize report dialog.

        Args:
            statistics: Statistics dictionary from analytics panel.
            quarantine_dir: Path to quarantine directory (for manifest).
            parent: Parent widget.
        """
        super().__init__(parent)
        self.statistics = statistics
        self.quarantine_dir = quarantine_dir
        self.scan_history = []

        self.setWindowTitle("Scan Report")
        self.setGeometry(100, 100, 900, 600)

        self._load_scan_history()
        self._setup_ui()
        self._setup_styles()

    def _load_scan_history(self) -> None:
        """Load scan history from quarantine manifest."""
        if not self.quarantine_dir:
            return

        try:
            manifest_file = self.quarantine_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    self.scan_history = manifest
        except Exception as e:
            logging.error(f"Failed to load scan history: {e}")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Scan Report")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Summary Section
        summary_group_layout = QVBoxLayout()
        summary_label = QLabel("Summary")
        summary_font = QFont()
        summary_font.setBold(True)
        summary_label.setFont(summary_font)
        summary_group_layout.addWidget(summary_label)

        summary_text = (
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total Scans: {self.statistics.get('total_scans', 0)}\n"
            f"Files Scanned: {self.statistics.get('total_files', 0)}\n"
            f"Threats Found: {self.statistics.get('total_threats', 0)}\n"
            f"Current Level: {self.statistics.get('threat_level', 'Low')}"
        )
        self.summary_text = QTextEdit()
        self.summary_text.setText(summary_text)
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(120)
        summary_group_layout.addWidget(self.summary_text)

        layout.addLayout(summary_group_layout)

        # Quarantine History Section
        history_label = QLabel("Quarantine History")
        history_font = QFont()
        history_font.setBold(True)
        history_label.setFont(history_font)
        layout.addWidget(history_label)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Timestamp", "Original Path", "Threat Name", "File Hash"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.history_table.setAlternatingRowColors(True)

        # Populate history table
        self.history_table.setRowCount(len(self.scan_history))
        for row, entry in enumerate(self.scan_history):
            timestamp = entry.get("timestamp", "Unknown")
            original_path = entry.get("original_path", "Unknown")
            threat_name = entry.get("threat_name", "Unknown")
            file_hash = entry.get("hash", "N/A")[:16] + "..."

            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.history_table.setItem(row, 1, QTableWidgetItem(original_path))
            self.history_table.setItem(row, 2, QTableWidgetItem(threat_name))
            self.history_table.setItem(row, 3, QTableWidgetItem(file_hash))

        layout.addWidget(self.history_table)

        # Buttons
        button_layout = QHBoxLayout()

        self.export_pdf_btn = QPushButton("Export as PDF")
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        button_layout.addWidget(self.export_pdf_btn)

        self.export_csv_btn = QPushButton("Export as CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        button_layout.addWidget(self.export_csv_btn)

        self.print_btn = QPushButton("Print")
        self.print_btn.clicked.connect(self._print_report)
        button_layout.addWidget(self.print_btn)

        self.copy_btn = QPushButton("Copy Summary")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #757575; color: white;")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _setup_styles(self) -> None:
        """Apply styling."""
        self.setStyleSheet(
            """
            ReportDialog {
                background-color: #f5f5f5;
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
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                padding: 8px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            """
        )

    def _export_pdf(self) -> None:
        """Export report as PDF."""
        if not HAS_REPORTLAB:
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "Reportlab is not installed.\nInstall with: pip install reportlab",
            )
            return

        try:
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

            export_path = Path.home() / ".antivirus" / "reports"
            export_path.mkdir(parents=True, exist_ok=True)

            pdf_file = (
                export_path
                / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            doc = SimpleDocTemplate(str(pdf_file), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor="#1976d2",
                spaceAfter=30,
            )
            elements.append(Paragraph("Antivirus Scanner - Scan Report", title_style))

            # Generated date
            elements.append(
                Paragraph(
                    f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 0.2 * inch))

            # Summary Section
            elements.append(Paragraph("Summary", styles["Heading2"]))
            summary_data = [
                ["Metric", "Value"],
                ["Total Scans", str(self.statistics.get("total_scans", 0))],
                ["Files Scanned", str(self.statistics.get("total_files", 0))],
                ["Threats Found", str(self.statistics.get("total_threats", 0))],
                ["Current Level", str(self.statistics.get("threat_level", "Low"))],
            ]

            summary_table = Table(summary_data)
            summary_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ])
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3 * inch))

            # History Section
            if self.scan_history:
                elements.append(Paragraph("Quarantine History", styles["Heading2"]))

                history_data = [["Timestamp", "Original Path", "Threat Name", "Hash"]]
                for entry in self.scan_history:
                    history_data.append([
                        entry.get("timestamp", "Unknown")[:19],
                        entry.get("original_path", "Unknown")[-50:],
                        entry.get("threat_name", "Unknown"),
                        entry.get("hash", "N/A")[:16],
                    ])

                history_table = Table(history_data)
                history_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ])
                )
                elements.append(history_table)

            # Build PDF
            doc.build(elements)

            QMessageBox.information(
                self,
                "Success",
                f"Report exported to:\n{pdf_file}",
            )
        except Exception as e:
            logging.error(f"PDF export failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export PDF:\n{str(e)}",
            )

    def _export_csv(self) -> None:
        """Export report as CSV."""
        try:
            export_path = Path.home() / ".antivirus" / "reports"
            export_path.mkdir(parents=True, exist_ok=True)

            csv_file = (
                export_path
                / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(["Antivirus Scanner - Scan Report"])
                writer.writerow([f"Generated: {datetime.now().isoformat()}"])
                writer.writerow([])

                # Summary
                writer.writerow(["Summary"])
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Scans", self.statistics.get("total_scans", 0)])
                writer.writerow(
                    ["Files Scanned", self.statistics.get("total_files", 0)]
                )
                writer.writerow(
                    ["Threats Found", self.statistics.get("total_threats", 0)]
                )
                writer.writerow(
                    ["Current Level", self.statistics.get("threat_level", "Low")]
                )
                writer.writerow([])

                # History
                if self.scan_history:
                    writer.writerow(["Quarantine History"])
                    writer.writerow(["Timestamp", "Original Path", "Threat Name", "Hash"])
                    for entry in self.scan_history:
                        writer.writerow([
                            entry.get("timestamp", "Unknown"),
                            entry.get("original_path", "Unknown"),
                            entry.get("threat_name", "Unknown"),
                            entry.get("hash", "N/A"),
                        ])

            QMessageBox.information(
                self,
                "Success",
                f"Report exported to:\n{csv_file}",
            )
        except Exception as e:
            logging.error(f"CSV export failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export CSV:\n{str(e)}",
            )

    def _print_report(self) -> None:
        """Print the report."""
        try:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

            printer = QPrinter()
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Simple print - just print the summary for now
                painter = printer.paintEngine()
                self.summary_text.document().print(printer)
                QMessageBox.information(self, "Success", "Report sent to printer")
        except ImportError:
            QMessageBox.warning(
                self,
                "Not Available",
                "Print functionality requires Qt print support",
            )
        except Exception as e:
            logging.error(f"Print failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to print report:\n{str(e)}",
            )

    def _copy_to_clipboard(self) -> None:
        """Copy report summary to clipboard."""
        try:
            from PyQt6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            clipboard.setText(self.summary_text.toPlainText())
            QMessageBox.information(
                self,
                "Success",
                "Report summary copied to clipboard",
            )
        except Exception as e:
            logging.error(f"Clipboard copy failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to copy to clipboard:\n{str(e)}",
            )
