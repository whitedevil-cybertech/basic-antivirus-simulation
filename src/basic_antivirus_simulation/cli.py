"""Antivirus simulation – command-line entry point.

Commands
--------
scan
    Recursively scan a path for malicious files.

    scan --path <target>
         [--signatures <signatures.json>]
         [--quarantine <dir>]
         [--allowlist  <allowlist.json>]
         [--types      .exe,.dll,...]
         [--exclude    dir1,dir2,...]
         [--report     <report.json>]
         [--log-file   <scan.log>]
         [--verbose]

quarantine list
    Display all entries in the quarantine manifest.

    quarantine list [--quarantine <dir>]

quarantine restore
    Restore a quarantined file to its original location.

    quarantine restore <quarantine-path>
                       [--quarantine <dir>]
                       [--force]

allowlist add
    Add a file path or hash to the persistent allowlist.

    allowlist add [--path <file-path>]
                  [--hash <sha256-hex>]
                  [--allowlist <allowlist.json>]

Exit codes
----------
0   No malicious files detected.
1   One or more malicious files detected.
2   Configuration or runtime error.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

def _find_project_root() -> Path:
    """Locate the project root (contains data/)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "data").exists():
            return parent
    return Path.cwd()


# Default data-file locations (relative to project root if present)
_ROOT = _find_project_root()
_DEFAULT_SIGNATURES = _ROOT / "data" / "signatures.json"
_DEFAULT_ALLOWLIST = _ROOT / "data" / "allowlist.json"
_DEFAULT_QUARANTINE = _ROOT / "data" / "quarantine"
_DEFAULT_LOG_FILE = _ROOT / "logs" / "scan.log"


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="antivirus",
        description="Signature-based antivirus simulation",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── scan ──────────────────────────────────────────────────────────────
    scan_p = subparsers.add_parser("scan", help="Scan a file or directory")
    scan_p.add_argument("--path", required=True, help="File or directory to scan")
    scan_p.add_argument(
        "--signatures",
        default=str(_DEFAULT_SIGNATURES),
        help=f"Signature database JSON (default: {_DEFAULT_SIGNATURES})",
    )
    scan_p.add_argument(
        "--quarantine",
        default=str(_DEFAULT_QUARANTINE),
        help=f"Quarantine directory (default: {_DEFAULT_QUARANTINE})",
    )
    scan_p.add_argument(
        "--allowlist",
        default=str(_DEFAULT_ALLOWLIST),
        help=f"Allowlist JSON file (default: {_DEFAULT_ALLOWLIST})",
    )
    scan_p.add_argument(
        "--types",
        default="",
        help="Comma-separated file extensions to scan, e.g. .exe,.dll (default: all)",
    )
    scan_p.add_argument(
        "--exclude",
        default="",
        help="Comma-separated directory names to skip, e.g. node_modules,.git",
    )
    scan_p.add_argument("--report", help="Write JSON report to this file")
    scan_p.add_argument(
        "--log-file",
        default=str(_DEFAULT_LOG_FILE),
        help=f"Log file path (default: {_DEFAULT_LOG_FILE})",
    )
    scan_p.add_argument("--verbose", action="store_true", help="Enable DEBUG logging")

    # ── quarantine ────────────────────────────────────────────────────────
    quar_p = subparsers.add_parser("quarantine", help="Quarantine management")
    quar_sub = quar_p.add_subparsers(dest="quar_command", required=True)

    # quarantine list
    qlist = quar_sub.add_parser("list", help="List quarantined files")
    qlist.add_argument(
        "--quarantine",
        default=str(_DEFAULT_QUARANTINE),
        help="Quarantine directory",
    )

    # quarantine restore
    qrestore = quar_sub.add_parser("restore", help="Restore a quarantined file")
    qrestore.add_argument(
        "quarantine_path", help="Path of the file inside the quarantine to restore"
    )
    qrestore.add_argument(
        "--quarantine",
        default=str(_DEFAULT_QUARANTINE),
        help="Quarantine directory",
    )
    qrestore.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the original location if it already exists",
    )

    # ── allowlist ─────────────────────────────────────────────────────────
    al_p = subparsers.add_parser("allowlist", help="Allowlist management")
    al_sub = al_p.add_subparsers(dest="al_command", required=True)

    # allowlist add
    al_add = al_sub.add_parser("add", help="Add a path or hash to the allowlist")
    al_add.add_argument("--path", dest="al_path", help="File path to allowlist")
    al_add.add_argument("--hash", dest="al_hash", help="SHA-256 hash to allowlist")
    al_add.add_argument(
        "--allowlist",
        default=str(_DEFAULT_ALLOWLIST),
        help="Allowlist JSON file",
    )

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _cmd_scan(args: argparse.Namespace) -> int:
    """Handle the ``scan`` subcommand."""
    from basic_antivirus_simulation.scanner.report import generate_report, print_summary
    from basic_antivirus_simulation.scanner.scanner import ScanOptions, scan_target
    from basic_antivirus_simulation.scanner.signatures import (
        SignatureDatabaseError,
        load_allowlist,
        load_signatures,
    )
    from basic_antivirus_simulation.scanner.utils import setup_logging

    log_path = Path(args.log_file).expanduser() if args.log_file else None
    setup_logging(log_path, args.verbose)

    try:
        signatures = load_signatures(args.signatures)
    except (FileNotFoundError, SignatureDatabaseError) as exc:
        logging.error("Failed to load signatures: %s", exc)
        return 2

    # Build allowlist
    allowlist_paths: set[str] = set()
    allowlist_hashes: set[str] = set()
    if args.allowlist and Path(args.allowlist).exists():
        try:
            al = load_allowlist(args.allowlist)
            allowlist_paths = set(al.get("paths", []))
            allowlist_hashes = set(al.get("hashes", []))
        except (FileNotFoundError, SignatureDatabaseError) as exc:
            logging.warning("Could not load allowlist (%s), continuing without it.", exc)

    # Build scan options
    allowed_ext: set[str] = set()
    if args.types:
        for ext in args.types.split(","):
            ext = ext.strip()
            if ext and not ext.startswith("."):
                ext = "." + ext
            if ext:
                allowed_ext.add(ext.lower())

    excluded_dirs: set[str] = set()
    if args.exclude:
        excluded_dirs = {d.strip() for d in args.exclude.split(",") if d.strip()}

    options = ScanOptions(
        allowed_extensions=allowed_ext,
        excluded_dirs=excluded_dirs,
        allowlist_paths=allowlist_paths,
        allowlist_hashes=allowlist_hashes,
    )

    try:
        results = scan_target(
            args.path,
            signatures,
            quarantine_dir=args.quarantine if args.quarantine else None,
            options=options,
        )
    except (OSError, ValueError) as exc:
        logging.error("Scan failed: %s", exc)
        return 2

    report = generate_report(results, output_path=args.report)
    print_summary(report)

    return 1 if report["infected_files"] else 0


def _cmd_quarantine_list(args: argparse.Namespace) -> int:
    """Handle ``quarantine list``."""
    from basic_antivirus_simulation.scanner.quarantine import list_quarantine

    entries = list_quarantine(args.quarantine)
    if not entries:
        print("Quarantine is empty.")
        return 0

    print(f"\n{'='*70}")
    print(f"  Quarantine directory: {args.quarantine}")
    print(f"  Total entries: {len(entries)}\n")
    for i, entry in enumerate(entries, 1):
        quarantine_exists = Path(entry.get("quarantine_path", "")).exists()
        status = "present" if quarantine_exists else "MISSING"
        print(
            f"  [{i}] Threat    : {entry.get('threat_name', 'Unknown')}\n"
            f"       Original  : {entry.get('original_path', '')}\n"
            f"       Quarantine: {entry.get('quarantine_path', '')} [{status}]\n"
            f"       Hash      : {entry.get('hash', '')}\n"
            f"       Timestamp : {entry.get('timestamp', '')}\n"
        )
    print("="*70)
    return 0


def _cmd_quarantine_restore(args: argparse.Namespace) -> int:
    """Handle ``quarantine restore``."""
    from basic_antivirus_simulation.scanner.quarantine import restore_file

    try:
        restored = restore_file(
            args.quarantine,
            args.quarantine_path,
            force=args.force,
        )
        print(f"Restored: {args.quarantine_path} → {restored}")
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Restore failed: {exc}", file=sys.stderr)
        return 2


def _cmd_allowlist_add(args: argparse.Namespace) -> int:
    """Handle ``allowlist add``."""
    from basic_antivirus_simulation.scanner.signatures import (
        SignatureDatabaseError,
        add_to_allowlist,
    )

    if not args.al_path and not args.al_hash:
        print("Error: Provide at least one of --path or --hash.", file=sys.stderr)
        return 2

    try:
        add_to_allowlist(
            args.allowlist,
            file_path=args.al_path,
            file_hash=args.al_hash,
        )
        print(f"Allowlist updated: {args.allowlist}")
        return 0
    except (SignatureDatabaseError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Parse arguments and dispatch to the appropriate command handler."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        return _cmd_scan(args)
    if args.command == "quarantine":
        if args.quar_command == "list":
            return _cmd_quarantine_list(args)
        if args.quar_command == "restore":
            return _cmd_quarantine_restore(args)
    if args.command == "allowlist":
        if args.al_command == "add":
            return _cmd_allowlist_add(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
