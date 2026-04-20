import hashlib
import tempfile
import unittest
from pathlib import Path

from antivirus_scanner import (
    SignatureDatabaseError,
    hash_file,
    load_signature_database,
    scan_target,
)


class AntivirusScannerTests(unittest.TestCase):
    def test_hash_file_uses_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "sample.bin"
            data = b"clean-data"
            file_path.write_bytes(data)

            expected_hash = hashlib.sha256(data).hexdigest()
            self.assertEqual(hash_file(file_path), expected_hash)

    def test_load_signature_database_supports_text_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            signature = hashlib.sha256(b"evil").hexdigest()
            text_db = Path(tmp) / "sigs.txt"
            json_db = Path(tmp) / "sigs.json"

            text_db.write_text(f"# comment\n{signature}\n", encoding="utf-8")
            json_db.write_text(f'{{"signatures": ["{signature}"]}}', encoding="utf-8")

            self.assertEqual(load_signature_database(text_db), {signature})
            self.assertEqual(load_signature_database(json_db), {signature})

    def test_load_signature_database_rejects_invalid_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "invalid.txt"
            db.write_text("not-a-hash\n", encoding="utf-8")

            with self.assertRaises(SignatureDatabaseError):
                load_signature_database(db)

    def test_scan_target_detects_and_quarantines_malicious_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "scan"
            quarantine = Path(tmp) / "quarantine"
            nested = root / "nested"
            nested.mkdir(parents=True)

            clean_file = nested / "clean.txt"
            evil_file = nested / "evil.txt"
            clean_file.write_bytes(b"safe")
            evil_file.write_bytes(b"malware")

            evil_hash = hashlib.sha256(b"malware").hexdigest()
            results = scan_target(root, {evil_hash}, quarantine)

            self.assertEqual(len(results), 2)
            malicious_results = [result for result in results if result.is_malicious]
            self.assertEqual(len(malicious_results), 1)
            self.assertIsNotNone(malicious_results[0].quarantined_to)

            quarantined_path = malicious_results[0].quarantined_to
            self.assertIsNotNone(quarantined_path)
            self.assertTrue(Path(quarantined_path).exists())
            self.assertFalse(evil_file.exists())
            self.assertTrue(clean_file.exists())


if __name__ == "__main__":
    unittest.main()
