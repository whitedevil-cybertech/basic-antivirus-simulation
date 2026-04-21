"""Analytics Panel: Dashboard with statistics and charts."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QGroupBox,
    QGridLayout,
)
from PyQt6.QtGui import QFont

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class AnalyticsPanel(QWidget):
    """Analytics dashboard with statistics and charts."""

    # Signals
    report_generated = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the analytics panel.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.scan_results_file: Optional[Path] = None
        self.quarantine_dir: Optional[Path] = None
        self.statistics: dict = {}
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Analytics Dashboard")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Statistics Group
        stats_group = self._create_statistics_group()
        layout.addWidget(stats_group)

        # Charts Group
        charts_group = self._create_charts_group()
        layout.addWidget(charts_group)

        # Actions Group
        actions_layout = QHBoxLayout()

        self.generate_report_btn = QPushButton("Generate Report")
        self.generate_report_btn.setStyleSheet(
            "background-color: #1976d2; color: white;"
        )
        self.generate_report_btn.clicked.connect(self._generate_report)
        actions_layout.addWidget(self.generate_report_btn)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        actions_layout.addWidget(self.export_pdf_btn)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        actions_layout.addWidget(self.export_csv_btn)

        actions_layout.addStretch()

        self.clear_stats_btn = QPushButton("Clear Statistics")
        self.clear_stats_btn.setStyleSheet("background-color: #C62828; color: white;")
        self.clear_stats_btn.clicked.connect(self._clear_statistics)
        actions_layout.addWidget(self.clear_stats_btn)

        layout.addLayout(actions_layout)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _create_statistics_group(self) -> QGroupBox:
        """Create statistics display group.

        Returns:
            Statistics group box.
        """
        group = QGroupBox("Statistics")
        layout = QGridLayout()

        # Create statistic labels
        self.total_scans_label = QLabel("Total Scans: 0")
        self.total_files_label = QLabel("Total Files Scanned: 0")
        self.threats_found_label = QLabel("Threats Found: 0")
        self.threat_level_label = QLabel("Current Level: Low")
        self.last_scan_label = QLabel("Last Scan: Never")
        self.avg_duration_label = QLabel("Avg Duration: 0s")

        # Apply bold font
        bold_font = QFont()
        bold_font.setBold(True)
        for label in [
            self.total_scans_label,
            self.total_files_label,
            self.threats_found_label,
            self.threat_level_label,
            self.last_scan_label,
            self.avg_duration_label,
        ]:
            label.setFont(bold_font)

        # Add to grid
        layout.addWidget(self.total_scans_label, 0, 0)
        layout.addWidget(self.total_files_label, 0, 1)
        layout.addWidget(self.threats_found_label, 1, 0)
        layout.addWidget(self.threat_level_label, 1, 1)
        layout.addWidget(self.last_scan_label, 2, 0)
        layout.addWidget(self.avg_duration_label, 2, 1)

        group.setLayout(layout)
        return group

    def _create_charts_group(self) -> QGroupBox:
        """Create charts display group.

        Returns:
            Charts group box.
        """
        group = QGroupBox("Charts")
        layout = QVBoxLayout()

        if HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(10, 4), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
            self._update_charts()
        else:
            no_chart_label = QLabel(
                "Matplotlib not installed. Install with: pip install matplotlib"
            )
            layout.addWidget(no_chart_label)

        group.setLayout(layout)
        return group

    def _setup_styles(self) -> None:
        """Apply styling to the panel."""
        self.setStyleSheet(
            """
            AnalyticsPanel {
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
            QLabel {
                padding: 4px;
            }
            """
        )

    def set_scan_results_file(self, results_file: str | Path) -> None:
        """Set the scan results file path.

        Args:
            results_file: Path to scan results log.
        """
        self.scan_results_file = Path(results_file).expanduser().resolve()
        self._load_statistics()

    def set_quarantine_directory(self, quarantine_dir: str | Path) -> None:
        """Set the quarantine directory path.

        Args:
            quarantine_dir: Path to quarantine directory.
        """
        self.quarantine_dir = Path(quarantine_dir).expanduser().resolve()
        self._load_statistics()

    def _load_statistics(self) -> None:
        """Load statistics from scan results and quarantine."""
        try:
            self.statistics = self._calculate_statistics()
            self._refresh_statistics_display()
            if HAS_MATPLOTLIB:
                self._update_charts()
            self.status_label.setText("Statistics loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load statistics: {e}")
            self.status_label.setText(f"Error loading statistics: {e}")

    def _calculate_statistics(self) -> dict:
        """Calculate statistics from available data.

        Returns:
            Statistics dictionary.
        """
        stats = {
            "total_scans": 0,
            "total_files": 0,
            "total_threats": 0,
            "threats_by_severity": {
                "Critical": 0,
                "High": 0,
                "Medium": 0,
                "Low": 0,
            },
            "threat_families": {},
            "last_scan_date": None,
            "avg_duration": 0.0,
            "scan_history": [],
        }

        # Try to load from scan results file
        if self.scan_results_file and self.scan_results_file.exists():
            try:
                with open(self.scan_results_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Simple parsing of log file
                    lines = content.split("\n")
                    for line in lines:
                        if "files scanned" in line.lower():
                            try:
                                parts = line.split(",")
                                for part in parts:
                                    if "files" in part.lower():
                                        count = int(
                                            "".join(c for c in part if c.isdigit())
                                        )
                                        stats["total_files"] = max(
                                            stats["total_files"], count
                                        )
                            except (ValueError, AttributeError):
                                pass
            except Exception as e:
                logging.debug(f"Could not parse scan results: {e}")

        # Try to load from quarantine manifest
        if self.quarantine_dir:
            try:
                manifest_file = self.quarantine_dir / "manifest.json"
                if manifest_file.exists():
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                        stats["total_threats"] = len(manifest)
                        for entry in manifest:
                            threat_name = entry.get("threat_name", "Unknown")
                            severity = self._get_severity_from_threat(threat_name)
                            stats["threats_by_severity"][severity] += 1
                            family = threat_name.split(".")[0]
                            stats["threat_families"][family] = (
                                stats["threat_families"].get(family, 0) + 1
                            )
            except Exception as e:
                logging.debug(f"Could not load quarantine manifest: {e}")

        # Set current threat level
        if stats["total_threats"] > 0:
            stats["threat_level"] = "High"
        else:
            stats["threat_level"] = "Low"

        stats["total_scans"] = 1 if stats["total_files"] > 0 else 0

        return stats

    @staticmethod
    def _get_severity_from_threat(threat_name: str) -> str:
        """Get severity level from threat name.

        Args:
            threat_name: Name of the threat.

        Returns:
            Severity level (Critical, High, Medium, Low).
        """
        threat_name = threat_name.lower()
        if any(x in threat_name for x in ["trojan", "ransomware", "worm"]):
            return "Critical"
        elif any(x in threat_name for x in ["virus", "spyware"]):
            return "High"
        elif any(x in threat_name for x in ["adware", "pup"]):
            return "Medium"
        else:
            return "Low"

    def _refresh_statistics_display(self) -> None:
        """Refresh the statistics display labels."""
        self.total_scans_label.setText(
            f"Total Scans: {self.statistics.get('total_scans', 0)}"
        )
        self.total_files_label.setText(
            f"Total Files Scanned: {self.statistics.get('total_files', 0)}"
        )
        self.threats_found_label.setText(
            f"Threats Found: {self.statistics.get('total_threats', 0)}"
        )
        self.threat_level_label.setText(
            f"Current Level: {self.statistics.get('threat_level', 'Low')}"
        )
        self.avg_duration_label.setText("Avg Duration: N/A")
        self.last_scan_label.setText(
            f"Last Scan: {self.statistics.get('last_scan_date', 'Never')}"
        )

    def _update_charts(self) -> None:
        """Update the matplotlib charts."""
        if not HAS_MATPLOTLIB:
            return

        self.figure.clear()

        # Create subplots
        ax1 = self.figure.add_subplot(131)  # Threats by severity (pie)
        ax2 = self.figure.add_subplot(132)  # Threat families (bar)
        ax3 = self.figure.add_subplot(133)  # Summary statistics (text)

        # Pie chart: Threats by severity
        severity = self.statistics.get("threats_by_severity", {})
        if any(severity.values()):
            labels = [k for k, v in severity.items() if v > 0]
            sizes = [v for k, v in severity.items() if v > 0]
            colors = ["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"]
            ax1.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                colors=colors[:len(labels)],
                startangle=90,
            )
            ax1.set_title("Threats by Severity")
        else:
            ax1.text(
                0.5,
                0.5,
                "No threats",
                ha="center",
                va="center",
                transform=ax1.transAxes,
            )
            ax1.set_title("Threats by Severity")

        # Bar chart: Top threat families
        families = self.statistics.get("threat_families", {})
        if families:
            top_families = dict(sorted(families.items(), key=lambda x: x[1], reverse=True)[:5])
            ax2.bar(range(len(top_families)), list(top_families.values()))
            ax2.set_xticks(range(len(top_families)))
            ax2.set_xticklabels(list(top_families.keys()), rotation=45, ha="right")
            ax2.set_ylabel("Count")
            ax2.set_title("Top Threat Families")
        else:
            ax2.text(
                0.5,
                0.5,
                "No data",
                ha="center",
                va="center",
                transform=ax2.transAxes,
            )
            ax2.set_title("Top Threat Families")

        # Text summary
        ax3.axis("off")
        summary_text = (
            f"Total Scans: {self.statistics.get('total_scans', 0)}\n"
            f"Files Scanned: {self.statistics.get('total_files', 0)}\n"
            f"Threats Found: {self.statistics.get('total_threats', 0)}\n"
            f"Status: {self.statistics.get('threat_level', 'Low')}"
        )
        ax3.text(
            0.1,
            0.5,
            summary_text,
            fontsize=10,
            verticalalignment="center",
            family="monospace",
        )
        ax3.set_title("Summary")

        self.figure.tight_layout()
        self.canvas.draw()

    def _generate_report(self) -> None:
        """Generate a detailed scan report."""
        try:
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "statistics": self.statistics,
            }
            self.report_generated.emit(report_data)
            self.status_label.setText("Report generated successfully")
            QMessageBox.information(
                self,
                "Success",
                "Report generated. Export options are available.",
            )
        except Exception as e:
            logging.error(f"Report generation failed: {e}")
            self.status_label.setText(f"Report generation failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate report:\n{str(e)}",
            )

    def _export_pdf(self) -> None:
        """Export report as PDF."""
        try:
            from pathlib import Path
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch

            export_path = Path.home() / ".antivirus" / "reports"
            export_path.mkdir(parents=True, exist_ok=True)

            pdf_file = export_path / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

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
            elements.append(
                Paragraph("Antivirus Scanner Report", title_style)
            )

            # Metadata
            elements.append(
                Paragraph(
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 0.3 * inch))

            # Statistics
            elements.append(Paragraph("Statistics", styles["Heading2"]))
            stats_text = (
                f"Total Scans: {self.statistics.get('total_scans', 0)}<br/>"
                f"Files Scanned: {self.statistics.get('total_files', 0)}<br/>"
                f"Threats Found: {self.statistics.get('total_threats', 0)}<br/>"
                f"Current Level: {self.statistics.get('threat_level', 'Low')}"
            )
            elements.append(Paragraph(stats_text, styles["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

            # Build PDF
            doc.build(elements)

            self.status_label.setText(f"PDF exported: {pdf_file}")
            QMessageBox.information(
                self,
                "Success",
                f"Report exported to:\n{pdf_file}",
            )
        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "Reportlab is not installed.\nInstall with: pip install reportlab",
            )
        except Exception as e:
            logging.error(f"PDF export failed: {e}")
            self.status_label.setText(f"PDF export failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export PDF:\n{str(e)}",
            )

    def _export_csv(self) -> None:
        """Export statistics as CSV."""
        try:
            import csv

            export_path = Path.home() / ".antivirus" / "reports"
            export_path.mkdir(parents=True, exist_ok=True)

            csv_file = export_path / f"scan_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Scans", self.statistics.get("total_scans", 0)])
                writer.writerow(
                    ["Total Files Scanned", self.statistics.get("total_files", 0)]
                )
                writer.writerow(
                    ["Threats Found", self.statistics.get("total_threats", 0)]
                )
                writer.writerow(
                    ["Current Level", self.statistics.get("threat_level", "Low")]
                )
                writer.writerow(["Generated At", datetime.now().isoformat()])

            self.status_label.setText(f"CSV exported: {csv_file}")
            QMessageBox.information(
                self,
                "Success",
                f"Statistics exported to:\n{csv_file}",
            )
        except Exception as e:
            logging.error(f"CSV export failed: {e}")
            self.status_label.setText(f"CSV export failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export CSV:\n{str(e)}",
            )

    def _clear_statistics(self) -> None:
        """Clear all statistics with confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Clear all statistics? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.statistics = {
                "total_scans": 0,
                "total_files": 0,
                "total_threats": 0,
                "threats_by_severity": {
                    "Critical": 0,
                    "High": 0,
                    "Medium": 0,
                    "Low": 0,
                },
                "threat_families": {},
                "last_scan_date": None,
                "avg_duration": 0.0,
            }
            self._refresh_statistics_display()
            if HAS_MATPLOTLIB:
                self._update_charts()
            self.status_label.setText("Statistics cleared")

    def get_statistics(self) -> dict:
        """Get current statistics.

        Returns:
            Statistics dictionary.
        """
        return self.statistics.copy()
