"""Basic signature-based antivirus simulation."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Set

DEFAULT_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class ScanResult:
    """Represents a single file scan result."""

    path: Path
    sha256: str
    is_malicious: bool
    quarantined_to: Path | None = None


class SignatureDatabaseError(ValueError):
    """Raised when a signature database cannot be parsed safely."""


def setup_logging(log_file: Path | None = None, verbose: bool = False) -> None:
    """Configure scanner logging."""
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def validate_existing_path(path: str | Path) -> Path:
    """Return a resolved path if it exists."""
    resolved = Path(path).expanduser().resolve(strict=True)
    return resolved


def _normalize_hash(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise SignatureDatabaseError(f"Invalid SHA-256 signature entry: {value!r}")
    return normalized


def load_signature_database(signature_db_path: str | Path) -> Set[str]:
    """Load SHA-256 signatures from JSON or text files."""
    path = validate_existing_path(signature_db_path)

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SignatureDatabaseError(f"Unable to read signature database: {path}") from exc

    if path.suffix.lower() == ".json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise SignatureDatabaseError(f"Invalid JSON signature database: {path}") from exc

        if isinstance(data, dict):
            entries = data.get("signatures", [])
        elif isinstance(data, list):
            entries = data
        else:
            raise SignatureDatabaseError("JSON signature database must be a list or dict with 'signatures'.")

        if not isinstance(entries, list):
            raise SignatureDatabaseError("JSON 'signatures' must be a list.")

        return {_normalize_hash(str(entry)) for entry in entries}

    signatures: Set[str] = set()
    for line in content.splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        signatures.add(_normalize_hash(entry))
    return signatures


def hash_file(file_path: str | Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Compute SHA-256 hash of a file using chunked reads."""
    path = validate_existing_path(file_path)
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(target_path: str | Path) -> Iterable[Path]:
    """Yield files under a target path recursively."""
    path = validate_existing_path(target_path)
    if path.is_file():
        yield path
        return

    for root, _, files in os.walk(path):
        root_path = Path(root)
        for file_name in files:
            candidate = root_path / file_name
            try:
                if candidate.is_file():
                    yield candidate.resolve(strict=True)
            except OSError:
                logging.warning("Skipping unreadable path: %s", candidate)


def quarantine_file(file_path: Path, quarantine_dir: str | Path, scan_root: Path) -> Path:
    """Move file to quarantine while preserving relative structure."""
    quarantine_root = Path(quarantine_dir).expanduser().resolve()
    quarantine_root.mkdir(parents=True, exist_ok=True)

    source = file_path.resolve(strict=True)
    root = scan_root.resolve(strict=True)

    try:
        relative = source.relative_to(root)
    except ValueError:
        external_id = hashlib.sha256(source.as_posix().encode("utf-8")).hexdigest()
        relative = Path("_external") / external_id

    destination = quarantine_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)

    counter = 1
    original_destination = destination
    while destination.exists():
        destination = original_destination.with_name(
            f"{original_destination.stem}_{counter}{original_destination.suffix}"
        )
        counter += 1

    shutil.move(str(source), str(destination))
    return destination


def scan_target(
    target_path: str | Path,
    signatures: Set[str],
    quarantine_dir: str | Path | None = None,
) -> list[ScanResult]:
    """Scan a file or directory and return file scan results."""
    root = validate_existing_path(target_path)
    scan_root = root if root.is_dir() else root.parent
    results: list[ScanResult] = []

    for file_path in iter_files(root):
        try:
            file_hash = hash_file(file_path)
        except (OSError, ValueError) as exc:
            logging.warning("Skipping file due to read/hash error: %s (%s)", file_path, exc)
            continue

        is_malicious = file_hash in signatures
        quarantined_to: Path | None = None

        if is_malicious:
            logging.warning("Malicious file detected: %s", file_path)
            if quarantine_dir is not None:
                try:
                    quarantined_to = quarantine_file(file_path, quarantine_dir, scan_root)
                    logging.info("Moved file to quarantine: %s", quarantined_to)
                except OSError as exc:
                    logging.error("Failed to quarantine file %s: %s", file_path, exc)

        results.append(
            ScanResult(
                path=file_path,
                sha256=file_hash,
                is_malicious=is_malicious,
                quarantined_to=quarantined_to,
            )
        )

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Basic signature-based antivirus simulation")
    parser.add_argument("target", help="File or directory to scan")
    parser.add_argument("--signatures", required=True, help="Path to signature database (JSON or text)")
    parser.add_argument("--quarantine", help="Optional quarantine directory")
    parser.add_argument("--log-file", help="Optional log file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        setup_logging(Path(args.log_file).expanduser() if args.log_file else None, args.verbose)
        signatures = load_signature_database(args.signatures)
        results = scan_target(args.target, signatures, args.quarantine)
    except (OSError, ValueError, SignatureDatabaseError) as exc:
        logging.error("Scan failed: %s", exc)
        return 2

    malicious_count = sum(1 for result in results if result.is_malicious)
    logging.info("Scan completed. Total files: %d, malicious: %d", len(results), malicious_count)
    return 1 if malicious_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
