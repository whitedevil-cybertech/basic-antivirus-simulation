"""SHA-256 file hashing utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path

from scanner.utils import validate_existing_path

DEFAULT_CHUNK_SIZE: int = 1024 * 1024  # 1 MiB


def hash_file(file_path: str | Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Compute the SHA-256 hex digest of *file_path* using chunked reads.

    Args:
        file_path:  Path to the file to hash.
        chunk_size: Number of bytes to read per iteration (default 1 MiB).

    Returns:
        Lowercase hexadecimal SHA-256 digest string.

    Raises:
        ValueError:  If the path does not point to a regular file.
        OSError:     If the file cannot be opened or read.
        FileNotFoundError: If the path does not exist.
    """
    path = validate_existing_path(file_path)
    if not path.is_file():
        raise ValueError(f"Path is not a regular file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as fobj:
        for chunk in iter(lambda: fobj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
