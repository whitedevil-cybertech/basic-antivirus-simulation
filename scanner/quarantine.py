"""Quarantine management: isolate, list, and restore suspicious files.

Each move is recorded in a JSON manifest (``manifest.json``) stored at the
root of the quarantine directory.  The manifest is a list of entry objects:

    [
      {
        "original_path":  "/abs/path/to/bad.exe",
        "quarantine_path": "/abs/quarantine/path/bad.exe",
        "timestamp":       "2026-04-20T18:00:00",
        "hash":            "<sha256-hex>",
        "threat_name":     "Trojan.Generic"
      },
      ...
    ]
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from scanner.utils import validate_existing_path

_MANIFEST_FILENAME = "manifest.json"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_manifest(quarantine_root: Path) -> list[dict]:
    """Return the quarantine manifest list; creates an empty one if absent."""
    manifest_path = quarantine_root / _MANIFEST_FILENAME
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError) as exc:
        logging.warning("Could not read quarantine manifest: %s", exc)
    return []


def _save_manifest(quarantine_root: Path, manifest: list[dict]) -> None:
    """Write the manifest list to disk as formatted JSON."""
    manifest_path = quarantine_root / _MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _unique_destination(destination: Path) -> Path:
    """Append an incrementing counter suffix until the path does not exist."""
    if not destination.exists():
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def quarantine_file(
    file_path: Path,
    quarantine_dir: str | Path,
    scan_root: Path,
    *,
    file_hash: str = "",
    threat_name: str = "Unknown",
) -> Path:
    """Move *file_path* into *quarantine_dir* and record the action.

    The original directory structure (relative to *scan_root*) is preserved
    inside the quarantine directory.  If the file is outside *scan_root* it
    is placed under ``_external/<hash-of-original-path>``.

    Args:
        file_path:     Absolute path of the file to quarantine.
        quarantine_dir: Root quarantine directory (created if absent).
        scan_root:     Root of the original scan (used for relative layout).
        file_hash:     Pre-computed SHA-256 hex digest of the file (optional).
        threat_name:   Human-readable threat identifier for the manifest.

    Returns:
        Absolute path where the file was stored inside the quarantine.

    Raises:
        OSError: If the move fails.
    """
    quarantine_root = Path(quarantine_dir).expanduser().resolve()
    quarantine_root.mkdir(parents=True, exist_ok=True)

    source = file_path.resolve(strict=True)
    root = scan_root.resolve(strict=True)

    try:
        relative = source.relative_to(root)
    except ValueError:
        external_id = hashlib.sha256(source.as_posix().encode("utf-8")).hexdigest()
        relative = Path("_external") / external_id

    destination = _unique_destination(quarantine_root / relative)
    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(destination))

    # Update manifest
    manifest = _load_manifest(quarantine_root)
    manifest.append(
        {
            "original_path": str(source),
            "quarantine_path": str(destination),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "hash": file_hash,
            "threat_name": threat_name,
        }
    )
    _save_manifest(quarantine_root, manifest)

    logging.info("Quarantined %s → %s", source, destination)
    return destination


def list_quarantine(quarantine_dir: str | Path) -> list[dict]:
    """Return all manifest entries for the given quarantine directory.

    Args:
        quarantine_dir: Root quarantine directory.

    Returns:
        List of manifest entry dicts (may be empty).
    """
    quarantine_root = Path(quarantine_dir).expanduser().resolve()
    if not quarantine_root.is_dir():
        return []
    return _load_manifest(quarantine_root)


def restore_file(
    quarantine_dir: str | Path,
    quarantine_path: str | Path,
    *,
    force: bool = False,
) -> Path:
    """Restore a quarantined file to its original location.

    Args:
        quarantine_dir:  Root quarantine directory.
        quarantine_path: Path of the file inside the quarantine to restore.
        force:           When *True*, overwrite an existing file at the
                         original location.

    Returns:
        The path where the file was restored.

    Raises:
        FileNotFoundError: If the quarantined file no longer exists or has no
                           manifest entry.
        FileExistsError:   If the original location is occupied and *force* is
                           *False*.
        OSError:           On any move failure.
    """
    quarantine_root = Path(quarantine_dir).expanduser().resolve()
    source = Path(quarantine_path).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Quarantined file not found: {source}")

    manifest = _load_manifest(quarantine_root)
    entry = next(
        (e for e in manifest if Path(e["quarantine_path"]).resolve() == source),
        None,
    )
    if entry is None:
        raise FileNotFoundError(
            f"No manifest entry found for quarantined file: {source}"
        )

    destination = Path(entry["original_path"])
    if destination.exists() and not force:
        raise FileExistsError(
            f"Restore target already exists (use --force to overwrite): {destination}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))

    # Remove the entry from the manifest
    manifest = [e for e in manifest if Path(e["quarantine_path"]).resolve() != source]
    _save_manifest(quarantine_root, manifest)

    logging.info("Restored %s → %s", source, destination)
    return destination
