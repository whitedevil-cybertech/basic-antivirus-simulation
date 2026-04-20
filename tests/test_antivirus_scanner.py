"""Integration and unit tests for the antivirus scanner modules."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scanner.hashing import hash_file
from scanner.quarantine import list_quarantine, quarantine_file, restore_file
from scanner.report import generate_report
from scanner.scanner import ScanOptions, ScanResult, scan_target
from scanner.signatures import (
    SignatureDatabaseError,
    add_to_allowlist,
    load_allowlist,
    load_signatures,
    save_allowlist,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sig_db(tmp: str, *pairs: tuple[bytes, dict]) -> Path:
    """Write a minimal signatures.json and return its path."""
    data = {hashlib.sha256(content).hexdigest(): meta for content, meta in pairs}
    path = Path(tmp) / "signatures.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

class TestHashFile(unittest.TestCase):
    def test_correct_sha256_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = b"clean-data"
            fp = Path(tmp) / "sample.bin"
            fp.write_bytes(data)
            self.assertEqual(hash_file(fp), hashlib.sha256(data).hexdigest())

    def test_raises_for_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                hash_file(tmp)

    def test_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            hash_file("/nonexistent/path/file.bin")


# ---------------------------------------------------------------------------
# Signatures
# ---------------------------------------------------------------------------

class TestLoadSignatures(unittest.TestCase):
    def test_loads_valid_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            sig_hash = hashlib.sha256(b"evil").hexdigest()
            db = Path(tmp) / "sigs.json"
            db.write_text(
                json.dumps({sig_hash: {"name": "TestVirus", "family": "T", "severity": "High"}}),
                encoding="utf-8",
            )
            sigs = load_signatures(db)
            self.assertIn(sig_hash, sigs)
            self.assertEqual(sigs[sig_hash]["name"], "TestVirus")

    def test_rejects_missing_name_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            sig_hash = hashlib.sha256(b"evil").hexdigest()
            db = Path(tmp) / "sigs.json"
            db.write_text(json.dumps({sig_hash: {"family": "T"}}), encoding="utf-8")
            with self.assertRaises(SignatureDatabaseError):
                load_signatures(db)

    def test_rejects_invalid_hash_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "sigs.json"
            db.write_text(json.dumps({"not-a-hash": {"name": "x"}}), encoding="utf-8")
            with self.assertRaises(SignatureDatabaseError):
                load_signatures(db)

    def test_rejects_non_object_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "sigs.json"
            db.write_text(json.dumps(["hash1", "hash2"]), encoding="utf-8")
            with self.assertRaises(SignatureDatabaseError):
                load_signatures(db)

    def test_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_signatures("/no/such/file.json")


# ---------------------------------------------------------------------------
# Allowlist
# ---------------------------------------------------------------------------

class TestAllowlist(unittest.TestCase):
    def test_load_empty_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            al = Path(tmp) / "allowlist.json"
            al.write_text(json.dumps({"paths": [], "hashes": []}), encoding="utf-8")
            result = load_allowlist(al)
            self.assertEqual(result, {"paths": [], "hashes": []})

    def test_add_path_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            al_path = Path(tmp) / "allowlist.json"
            safe_hash = hashlib.sha256(b"safe").hexdigest()
            add_to_allowlist(al_path, file_path="/tmp/safe.txt", file_hash=safe_hash)
            result = load_allowlist(al_path)
            self.assertIn("/tmp/safe.txt", result["paths"])
            self.assertIn(safe_hash, result["hashes"])

    def test_add_duplicate_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            al_path = Path(tmp) / "allowlist.json"
            safe_hash = hashlib.sha256(b"safe").hexdigest()
            add_to_allowlist(al_path, file_hash=safe_hash)
            add_to_allowlist(al_path, file_hash=safe_hash)
            result = load_allowlist(al_path)
            self.assertEqual(result["hashes"].count(safe_hash), 1)

    def test_save_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            al_path = Path(tmp) / "allowlist.json"
            data = {"paths": ["/a/b"], "hashes": []}
            save_allowlist(al_path, data)
            self.assertEqual(load_allowlist(al_path)["paths"], ["/a/b"])


# ---------------------------------------------------------------------------
# Quarantine
# ---------------------------------------------------------------------------

class TestQuarantine(unittest.TestCase):
    def test_quarantine_moves_file_and_records_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            scan_root = Path(tmp) / "scan"
            scan_root.mkdir()
            qdir = Path(tmp) / "quarantine"
            evil = scan_root / "bad.exe"
            evil.write_bytes(b"malware")
            evil_hash = hashlib.sha256(b"malware").hexdigest()

            dest = quarantine_file(evil, qdir, scan_root, file_hash=evil_hash, threat_name="T.Bad")

            self.assertTrue(dest.exists())
            self.assertFalse(evil.exists())

            entries = list_quarantine(qdir)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["hash"], evil_hash)
            self.assertEqual(entries[0]["threat_name"], "T.Bad")
            self.assertEqual(entries[0]["original_path"], str(evil))

    def test_quarantine_handles_name_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            scan_root = Path(tmp) / "scan"
            scan_root.mkdir()
            qdir = Path(tmp) / "quarantine"

            for i in range(3):
                f = scan_root / f"bad{i}.exe"
                f.write_bytes(b"malware")
                quarantine_file(f, qdir, scan_root)

            entries = list_quarantine(qdir)
            self.assertEqual(len(entries), 3)

    def test_restore_returns_file_to_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            scan_root = Path(tmp) / "scan"
            scan_root.mkdir()
            qdir = Path(tmp) / "quarantine"
            evil = scan_root / "bad.exe"
            evil.write_bytes(b"malware")

            dest = quarantine_file(evil, qdir, scan_root)
            self.assertFalse(evil.exists())

            restore_file(qdir, dest)
            self.assertTrue(evil.exists())
            self.assertFalse(dest.exists())

            # Manifest entry should be removed after restore
            self.assertEqual(list_quarantine(qdir), [])

    def test_restore_raises_if_destination_exists_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            scan_root = Path(tmp) / "scan"
            scan_root.mkdir()
            qdir = Path(tmp) / "quarantine"
            evil = scan_root / "bad.exe"
            evil.write_bytes(b"malware")

            dest = quarantine_file(evil, qdir, scan_root)
            # Re-create the original path so restore would collide.
            evil.write_bytes(b"re-created")

            with self.assertRaises(FileExistsError):
                restore_file(qdir, dest)

    def test_restore_with_force_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            scan_root = Path(tmp) / "scan"
            scan_root.mkdir()
            qdir = Path(tmp) / "quarantine"
            evil = scan_root / "bad.exe"
            evil.write_bytes(b"malware")

            dest = quarantine_file(evil, qdir, scan_root)
            evil.write_bytes(b"re-created")

            restored = restore_file(qdir, dest, force=True)
            self.assertTrue(restored.exists())
            self.assertEqual(restored.read_bytes(), b"malware")


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class TestScanTarget(unittest.TestCase):
    def _setup_scan(self, tmp: str):
        root = Path(tmp) / "scan"
        nested = root / "nested"
        nested.mkdir(parents=True)
        clean = nested / "clean.txt"
        evil = nested / "evil.txt"
        clean.write_bytes(b"safe")
        evil.write_bytes(b"malware")
        return root, clean, evil

    def _make_db(self, tmp: str, content: bytes) -> dict:
        h = hashlib.sha256(content).hexdigest()
        return {h: {"name": "T.Generic", "family": "T", "severity": "High"}}

    def test_detects_malicious_and_quarantines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, clean, evil = self._setup_scan(tmp)
            sigs = self._make_db(tmp, b"malware")
            quarantine = Path(tmp) / "quarantine"

            results = scan_target(root, sigs, quarantine)

            self.assertEqual(len(results), 2)
            malicious = [r for r in results if r.is_malicious]
            self.assertEqual(len(malicious), 1)
            self.assertEqual(malicious[0].threat_name, "T.Generic")
            self.assertIsNotNone(malicious[0].quarantined_to)
            self.assertTrue(malicious[0].quarantined_to.exists())
            self.assertFalse(evil.exists())
            self.assertTrue(clean.exists())

    def test_clean_scan_returns_zero_malicious(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, _ = self._setup_scan(tmp)
            # No signatures → nothing matches
            results = scan_target(root, {})
            self.assertTrue(all(not r.is_malicious for r in results))

    def test_hash_allowlist_skips_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, evil = self._setup_scan(tmp)
            sigs = self._make_db(tmp, b"malware")
            evil_hash = hashlib.sha256(b"malware").hexdigest()
            options = ScanOptions(allowlist_hashes={evil_hash})

            results = scan_target(root, sigs, options=options)
            self.assertTrue(all(not r.is_malicious for r in results))

    def test_path_allowlist_skips_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, evil = self._setup_scan(tmp)
            sigs = self._make_db(tmp, b"malware")
            options = ScanOptions(allowlist_paths={str(evil.resolve())})

            results = scan_target(root, sigs, options=options)
            self.assertTrue(all(not r.is_malicious for r in results))

    def test_extension_filter_excludes_non_matching(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, evil = self._setup_scan(tmp)
            sigs = self._make_db(tmp, b"malware")
            # Only scan .exe files → .txt files are skipped
            options = ScanOptions(allowed_extensions={".exe"})

            results = scan_target(root, sigs, options=options)
            self.assertEqual(results, [])

    def test_excluded_dirs_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, _ = self._setup_scan(tmp)
            sigs = self._make_db(tmp, b"malware")
            options = ScanOptions(excluded_dirs={"nested"})

            results = scan_target(root, sigs, options=options)
            self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class TestGenerateReport(unittest.TestCase):
    def _make_results(self) -> list[ScanResult]:
        return [
            ScanResult(
                path=Path("/scan/evil.exe"),
                sha256="aabbcc" + "0" * 58,
                is_malicious=True,
                threat_name="T.Bad",
                threat_family="Trojan",
                severity="High",
                quarantined_to=Path("/quarantine/evil.exe"),
            ),
            ScanResult(
                path=Path("/scan/clean.txt"),
                sha256="11223344" + "0" * 56,
                is_malicious=False,
            ),
        ]

    def test_report_counts(self):
        results = self._make_results()
        report = generate_report(results)
        self.assertEqual(report["total_files_scanned"], 2)
        self.assertEqual(report["infected_files"], 1)
        self.assertEqual(len(report["detections"]), 1)

    def test_report_detection_fields(self):
        report = generate_report(self._make_results())
        det = report["detections"][0]
        self.assertEqual(det["threat_name"], "T.Bad")
        self.assertEqual(det["severity"], "High")
        self.assertIsNotNone(det["quarantined_to"])

    def test_report_written_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            generate_report(self._make_results(), output_path=out)
            self.assertTrue(out.exists())
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("scan_timestamp", data)
            self.assertEqual(data["infected_files"], 1)


if __name__ == "__main__":
    unittest.main()
