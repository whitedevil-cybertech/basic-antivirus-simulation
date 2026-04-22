"""Signature database and allowlist loading/management.

Signature database format (JSON):

    {
        "<sha256-hex>": {
            "name":     "Trojan.Generic",
            "family":   "Trojan",
            "severity": "High"
        },
        ...
    }

Allowlist format (JSON):

    {
        "paths":  ["/absolute/path/to/safe/file"],
        "hashes": ["<sha256-hex>", ...]
    }
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict

from basic_antivirus_simulation.scanner.utils import validate_existing_path

# A valid SHA-256 hex digest is exactly 64 lowercase hex characters.
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Type alias: hash → threat metadata dict
SignatureDB = Dict[str, dict]


class SignatureDatabaseError(ValueError):
    """Raised when a signature database file cannot be loaded or parsed."""


def _validate_hash(value: str) -> str:
    """Normalise and validate a hex hash string.

    Args:
        value: Raw hash string from a database or allowlist.

    Returns:
        Lowercase, stripped 64-character hex string.

    Raises:
        SignatureDatabaseError: If the value is not a valid SHA-256 digest.
    """
    normalised = value.strip().lower()
    if not _SHA256_RE.match(normalised):
        raise SignatureDatabaseError(f"Invalid SHA-256 hash entry: {value!r}")
    return normalised


def load_signatures(signature_db_path: str | Path) -> SignatureDB:
    """Load a JSON signature database from *signature_db_path*.

    The file must be valid JSON whose top-level value is an object where every
    key is a SHA-256 hex digest and every value is a dict containing at least
    a ``"name"`` field.  Extra fields (``"family"``, ``"severity"``, …) are
    preserved as-is.

    Args:
        signature_db_path: Path to ``signatures.json``.

    Returns:
        Mapping of normalised hash → threat metadata dict.

    Raises:
        SignatureDatabaseError: On parse or validation errors.
        FileNotFoundError: If the path does not exist.
    """
    path = validate_existing_path(signature_db_path)
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SignatureDatabaseError(f"Cannot read signature database: {path}") from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise SignatureDatabaseError(f"Invalid JSON in signature database: {path}") from exc

    if not isinstance(data, dict):
        raise SignatureDatabaseError(
            f"Signature database must be a JSON object (got {type(data).__name__}): {path}"
        )

    result: SignatureDB = {}
    for raw_hash, meta in data.items():
        normalised = _validate_hash(raw_hash)
        if not isinstance(meta, dict):
            raise SignatureDatabaseError(
                f"Metadata for hash {raw_hash!r} must be a JSON object."
            )
        if "name" not in meta:
            raise SignatureDatabaseError(
                f"Metadata for hash {raw_hash!r} is missing required 'name' field."
            )
        result[normalised] = meta

    logging.debug("Loaded %d signature(s) from %s", len(result), path)
    return result


def load_allowlist(allowlist_path: str | Path) -> dict:
    """Load the allowlist JSON file.

    Returns a dict with keys ``"paths"`` (list of str) and ``"hashes"``
    (list of normalised hex strings).  Missing keys default to empty lists.

    Args:
        allowlist_path: Path to ``allowlist.json``.

    Raises:
        SignatureDatabaseError: On parse errors.
        FileNotFoundError: If the path does not exist.
    """
    path = validate_existing_path(allowlist_path)
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SignatureDatabaseError(f"Cannot read allowlist: {path}") from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise SignatureDatabaseError(f"Invalid JSON in allowlist: {path}") from exc

    if not isinstance(data, dict):
        raise SignatureDatabaseError("Allowlist must be a JSON object.")

    paths: list[str] = [str(p) for p in data.get("paths", [])]
    raw_hashes: list = data.get("hashes", [])
    hashes: list[str] = [_validate_hash(str(h)) for h in raw_hashes]

    return {"paths": paths, "hashes": hashes}


def save_allowlist(allowlist_path: str | Path, allowlist: dict) -> None:
    """Persist *allowlist* to *allowlist_path* as formatted JSON.

    Args:
        allowlist_path: Destination file path.
        allowlist:      Dict with ``"paths"`` and ``"hashes"`` keys.
    """
    path = Path(allowlist_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(allowlist, indent=2), encoding="utf-8")
    logging.debug("Saved allowlist to %s", path)


def add_to_allowlist(
    allowlist_path: str | Path,
    *,
    file_path: str | None = None,
    file_hash: str | None = None,
) -> None:
    """Add a path or hash entry to the persistent allowlist file.

    The file is created with empty lists if it does not yet exist.

    Args:
        allowlist_path: Path to ``allowlist.json``.
        file_path:      Absolute path string to add to the ``"paths"`` list.
        file_hash:      SHA-256 hex string to add to the ``"hashes"`` list.

    Raises:
        ValueError: If neither *file_path* nor *file_hash* is supplied.
        SignatureDatabaseError: On hash validation failure.
    """
    if file_path is None and file_hash is None:
        raise ValueError("Provide at least one of file_path or file_hash.")

    al_path = Path(allowlist_path).expanduser().resolve()
    if al_path.exists():
        allowlist = load_allowlist(al_path)
    else:
        allowlist = {"paths": [], "hashes": []}

    if file_path is not None:
        resolved = str(Path(file_path).expanduser().resolve())
        if resolved not in allowlist["paths"]:
            allowlist["paths"].append(resolved)
            logging.info("Added path to allowlist: %s", resolved)
        else:
            logging.info("Path already in allowlist: %s", resolved)

    if file_hash is not None:
        normalised = _validate_hash(file_hash)
        if normalised not in allowlist["hashes"]:
            allowlist["hashes"].append(normalised)
            logging.info("Added hash to allowlist: %s", normalised)
        else:
            logging.info("Hash already in allowlist: %s", normalised)

    save_allowlist(al_path, allowlist)
