"""Core file scanning logic with allowlist and filter support."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from basic_antivirus_simulation.scanner.hashing import hash_file
from basic_antivirus_simulation.scanner.quarantine import quarantine_file
from basic_antivirus_simulation.scanner.signatures import SignatureDB
from basic_antivirus_simulation.scanner.utils import validate_existing_path


@dataclass(frozen=True)
class ScanResult:
    """Represents the scan outcome for a single file.

    Attributes:
        path:            Absolute path of the scanned file.
        sha256:          SHA-256 hex digest of the file contents.
        is_malicious:    *True* if the hash matched a signature.
        threat_name:     Human-readable threat name (empty for clean files).
        threat_family:   Malware family string (empty for clean files).
        severity:        Threat severity string (empty for clean files).
        quarantined_to:  Destination inside quarantine, or *None*.
    """

    path: Path
    sha256: str
    is_malicious: bool
    threat_name: str = ""
    threat_family: str = ""
    severity: str = ""
    quarantined_to: Path | None = None


@dataclass
class ScanOptions:
    """Controls which files are included in or excluded from a scan.

    Attributes:
        allowed_extensions: When non-empty, only files whose suffix (lowercased)
                            is in this set are hashed.  E.g. ``{".exe", ".dll"}``.
        excluded_dirs:      Directory *names* (not paths) to skip entirely
                            during recursion.  E.g. ``{"node_modules", ".git"}``.
        allowlist_paths:    Set of absolute path strings that are never flagged.
        allowlist_hashes:   Set of SHA-256 hex digests that are never flagged.
    """

    allowed_extensions: set[str] = field(default_factory=set)
    excluded_dirs: set[str] = field(default_factory=set)
    allowlist_paths: set[str] = field(default_factory=set)
    allowlist_hashes: set[str] = field(default_factory=set)


def _iter_files(target_path: Path, options: ScanOptions) -> list[Path]:
    """Yield resolved file paths under *target_path* respecting *options*.

    Args:
        target_path: File or directory to traverse.
        options:     Active scan options.

    Returns:
        Ordered list of absolute Path objects.
    """
    if target_path.is_file():
        return [target_path]

    collected: list[Path] = []
    for root, dirs, files in os.walk(target_path):
        # Prune excluded directory names in-place so os.walk won't descend.
        if options.excluded_dirs:
            dirs[:] = [d for d in dirs if d not in options.excluded_dirs]

        root_path = Path(root)
        for file_name in files:
            candidate = root_path / file_name

            # Extension filter
            if options.allowed_extensions:
                if candidate.suffix.lower() not in options.allowed_extensions:
                    logging.debug("Skipping (extension filter): %s", candidate)
                    continue

            try:
                resolved = candidate.resolve(strict=True)
                if resolved.is_file():
                    collected.append(resolved)
            except OSError:
                logging.warning("Skipping unreadable path: %s", candidate)

    return collected


def scan_target(
    target_path: str | Path,
    signatures: SignatureDB,
    quarantine_dir: str | Path | None = None,
    options: ScanOptions | None = None,
) -> list[ScanResult]:
    """Scan a file or directory tree and return per-file results.

    For every file visited:

    1. If its absolute path is in the allowlist → mark clean and continue.
    2. Compute SHA-256 hash.
    3. If the hash is in the allowlist → mark clean and continue.
    4. Look up the hash in *signatures*.
    5. If malicious and *quarantine_dir* is set → move the file there.

    Args:
        target_path:    File or directory to scan.
        signatures:     Loaded signature database (hash → metadata dict).
        quarantine_dir: Optional directory to move malicious files into.
        options:        Optional :class:`ScanOptions` controlling filters and
                        allowlists.

    Returns:
        List of :class:`ScanResult` instances (one per file visited).
    """
    if options is None:
        options = ScanOptions()

    root = validate_existing_path(target_path)
    scan_root = root if root.is_dir() else root.parent

    logging.info("Scan started: %s", root)
    files = _iter_files(root, options)
    results: list[ScanResult] = []

    for file_path in files:
        logging.debug("Scanning: %s", file_path)

        # --- Path-based allowlist check ---
        if str(file_path) in options.allowlist_paths:
            logging.debug("Skipping (allowlist path): %s", file_path)
            results.append(
                ScanResult(path=file_path, sha256="", is_malicious=False)
            )
            continue

        # --- Hash the file ---
        try:
            file_hash = hash_file(file_path)
        except (OSError, ValueError) as exc:
            logging.warning("Skipping file due to read error: %s (%s)", file_path, exc)
            continue

        # --- Hash-based allowlist check ---
        if file_hash in options.allowlist_hashes:
            logging.debug("Skipping (allowlist hash): %s", file_path)
            results.append(
                ScanResult(path=file_path, sha256=file_hash, is_malicious=False)
            )
            continue

        # --- Signature match ---
        meta = signatures.get(file_hash)
        is_malicious = meta is not None
        threat_name = ""
        threat_family = ""
        severity = ""
        quarantined_to: Path | None = None

        if is_malicious:
            threat_name = meta.get("name", "Unknown")  # type: ignore[union-attr]
            threat_family = meta.get("family", "")
            severity = meta.get("severity", "")
            logging.warning(
                "Malicious file detected: %s [%s / %s / %s]",
                file_path,
                threat_name,
                threat_family,
                severity,
            )
            if quarantine_dir is not None:
                try:
                    quarantined_to = quarantine_file(
                        file_path,
                        quarantine_dir,
                        scan_root,
                        file_hash=file_hash,
                        threat_name=threat_name,
                    )
                except OSError as exc:
                    logging.error(
                        "Failed to quarantine %s: %s", file_path, exc
                    )

        results.append(
            ScanResult(
                path=file_path,
                sha256=file_hash,
                is_malicious=is_malicious,
                threat_name=threat_name,
                threat_family=threat_family,
                severity=severity,
                quarantined_to=quarantined_to,
            )
        )

    logging.info(
        "Scan finished: %d file(s) scanned, %d malicious",
        len(results),
        sum(1 for r in results if r.is_malicious),
    )
    return results
