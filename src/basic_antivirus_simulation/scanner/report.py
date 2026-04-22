"""Structured JSON report generation for scan results."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from basic_antivirus_simulation.scanner.scanner import ScanResult


def generate_report(
    results: list[ScanResult],
    output_path: str | Path | None = None,
) -> dict:
    """Build a structured scan report and optionally write it to disk.

    Report structure::

        {
          "scan_timestamp": "<ISO-8601>",
          "total_files_scanned": <int>,
          "infected_files": <int>,
          "detections": [
            {
              "file_path":   "<str>",
              "hash":        "<sha256-hex>",
              "threat_name": "<str>",
              "severity":    "<str>",
              "quarantined_to": "<str | null>"
            },
            ...
          ]
        }

    Args:
        results:     List of :class:`~scanner.scanner.ScanResult` objects
                     returned by :func:`~scanner.scanner.scan_target`.
        output_path: Optional filesystem path where the report is saved as
                     pretty-printed JSON.  Intermediate directories are
                     created automatically.

    Returns:
        The report as a plain Python dictionary.
    """
    detections = [
        {
            "file_path": str(result.path),
            "hash": result.sha256,
            "threat_name": result.threat_name,
            "severity": result.severity,
            "quarantined_to": str(result.quarantined_to)
            if result.quarantined_to
            else None,
        }
        for result in results
        if result.is_malicious
    ]

    report = {
        "scan_timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "total_files_scanned": len(results),
        "infected_files": len(detections),
        "detections": detections,
    }

    if output_path is not None:
        dest = Path(output_path).expanduser().resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logging.info("Report written to %s", dest)

    return report


def print_summary(report: dict) -> None:
    """Print a human-readable scan summary to stdout.

    Args:
        report: Dict produced by :func:`generate_report`.
    """
    total = report.get("total_files_scanned", 0)
    infected = report.get("infected_files", 0)
    timestamp = report.get("scan_timestamp", "")
    print(f"\n{'='*60}")
    print(f"  Scan completed at : {timestamp}")
    print(f"  Files scanned     : {total}")
    print(f"  Malicious files   : {infected}")
    if report.get("detections"):
        print("\n  Detections:")
        for det in report["detections"]:
            quarantine_info = (
                f"  → quarantined: {det['quarantined_to']}"
                if det.get("quarantined_to")
                else ""
            )
            print(
                f"    • {det['file_path']}\n"
                f"      [{det['threat_name']} | severity: {det['severity']}]"
                f"{quarantine_info}"
            )
    print(f"{'='*60}\n")
