"""GUI entry point for antivirus scanner."""

import os
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from basic_antivirus_simulation.gui.main_window import MainWindow
from basic_antivirus_simulation.gui.theme import ThemeManager


def _find_project_root() -> Path:
    """Locate the project root (contains data/)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "data").exists():
            return parent
    return Path.cwd()


def main() -> int:
    """Launch the antivirus GUI application."""
    # Setup logging
    log_dir = Path.home() / ".antivirus" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gui.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Antivirus Scanner GUI")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow(theme=ThemeManager.DARK)
    
    # Initialize panel directories
    project_root = _find_project_root()
    os.chdir(project_root)
    config_dir = Path.home() / ".antivirus"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup quarantine panel
    quarantine_dir = project_root / "data" / "quarantine"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    window.tab_quarantine.set_quarantine_directory(quarantine_dir)
    
    # Setup allowlist panel
    allowlist_file = config_dir / "allowlist.json"
    window.tab_allowlist.set_allowlist_path(allowlist_file)
    
    # Setup analytics panel
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    scan_results_file = logs_dir / "scan_results.log"
    window.tab_analytics.set_scan_results_file(scan_results_file)
    window.tab_analytics.set_quarantine_directory(quarantine_dir)
    
    # Setup settings panel
    config_file = config_dir / "config.json"
    window.tab_settings.set_config_file(config_file)
    window.tab_settings.theme_changed.connect(window._switch_theme)
    
    window.show()
    
    logger.info("Main window displayed")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
