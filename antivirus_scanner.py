"""Basic signature-based antivirus simulation – compatibility shim.

The core logic now lives in the ``scanner`` package.  This module re-exports
the public symbols that were previously defined here so that existing scripts
that import directly from ``antivirus_scanner`` continue to work.

For new code, prefer importing from the ``scanner`` sub-modules directly:

    from scanner.hashing    import hash_file
    from scanner.signatures import load_signatures, SignatureDatabaseError
    from scanner.scanner    import scan_target, ScanResult, ScanOptions
    from scanner.quarantine import quarantine_file
    from scanner.report     import generate_report
    from scanner.utils      import setup_logging, validate_existing_path
"""

from __future__ import annotations

from scanner.hashing import DEFAULT_CHUNK_SIZE, hash_file
from scanner.quarantine import quarantine_file
from scanner.scanner import ScanOptions, ScanResult, scan_target
from scanner.signatures import SignatureDatabaseError
from scanner.utils import setup_logging, validate_existing_path

__all__ = [
    "DEFAULT_CHUNK_SIZE",
    "hash_file",
    "quarantine_file",
    "ScanOptions",
    "ScanResult",
    "scan_target",
    "SignatureDatabaseError",
    "setup_logging",
    "validate_existing_path",
]
