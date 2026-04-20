"""Shared utilities: path validation and logging setup."""

from __future__ import annotations

import logging
from pathlib import Path


def validate_existing_path(path: str | Path) -> Path:
    """Return a resolved, absolute path that must already exist on disk.

    Raises:
        FileNotFoundError: if the path does not exist.
    """
    return Path(path).expanduser().resolve(strict=True)


def setup_logging(log_file: Path | None = None, verbose: bool = False) -> None:
    """Configure root logger for the scanner.

    Args:
        log_file: Optional path to a file where log entries are appended.
        verbose:  When *True*, sets the log level to DEBUG; otherwise INFO.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
        force=True,
    )
