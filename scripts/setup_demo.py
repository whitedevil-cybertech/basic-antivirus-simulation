#!/usr/bin/env python3
"""Setup demo files for antivirus scanner testing."""

import hashlib
import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

# Create demo directories
examples_dir = project_root / "examples"
examples_dir.mkdir(exist_ok=True)
demo_scan = examples_dir / "demo_scan"
demo_quarantine = examples_dir / "demo_quarantine"
demo_scan.mkdir(parents=True, exist_ok=True)
demo_quarantine.mkdir(parents=True, exist_ok=True)

# Create sample files
clean_doc = demo_scan / "clean_doc.txt"
safe_file = demo_scan / "safe_file.txt"
malware_file = demo_scan / "virus.exe"

clean_doc.write_text("This is a clean document.\n")
safe_file.write_text("This is another safe file.\n")
malware_file.write_text("MALWARE_CODE_HERE")

# Get the hash of the malware file
malware_hash = hashlib.sha256(b"MALWARE_CODE_HERE").hexdigest()

# Create signature database
signatures_json = examples_dir / "malware_signatures.json"
signatures_json.write_text(json.dumps({"signatures": [malware_hash]}, indent=2))

print("✅ Demo setup complete!")
print(f"📁 Created examples/demo_scan/ with 3 test files:")
print(f"   - clean_doc.txt (safe)")
print(f"   - safe_file.txt (safe)")
print(f"   - virus.exe (MALWARE - hash: {malware_hash[:16]}...)")
print(f"\n📋 Created examples/malware_signatures.json with 1 malware signature")
print(f"\n🚀 Ready to scan! Run:")
print(f"   py antivirus_scanner.py examples/demo_scan --signatures examples/malware_signatures.json --quarantine examples/demo_quarantine --log-file logs/scan_results.log --verbose")
