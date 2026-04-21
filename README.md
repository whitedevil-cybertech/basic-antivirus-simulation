# basic-antivirus-simulation

Basic signature-based antivirus simulation for educational and ethical defensive use.

## Project structure

```
basic-antivirus-simulation/
│
├── main.py                    # CLI entry point
├── antivirus_scanner.py       # Backward-compatibility shim
│
├── scanner/
│   ├── __init__.py
│   ├── hashing.py             # SHA-256 file hashing
│   ├── signatures.py          # Signature DB + allowlist loading/management
│   ├── quarantine.py          # Quarantine, restore, manifest
│   ├── scanner.py             # Core scan logic + ScanOptions/ScanResult
│   ├── report.py              # JSON report generation
│   └── utils.py               # Logging setup, path validation
│
├── data/
│   ├── signatures.json        # Signature database (hash → threat metadata)
│   ├── allowlist.json         # Allowlisted paths and hashes
│   └── quarantine/            # Quarantine storage (includes manifest.json)
│
├── logs/
│   └── scan.log               # Default log output
│
└── tests/
    └── test_antivirus_scanner.py
```

## Signature database format

```json
{
  "<sha256-hex>": {
    "name":     "Trojan.Generic",
    "family":   "Trojan",
    "severity": "High"
  }
}
```

## Allowlist format

```json
{
  "paths":  ["/absolute/path/to/safe/file"],
  "hashes": ["<sha256-hex>"]
}
```

## Features

- SHA-256 file hashing with chunked reads (large-file safe)
- Recursive directory scanning
- Signature-based detection (hash → threat name / family / severity)
- Allowlist support (skip by file path or hash)
- File type and directory exclusion filters
- Quarantine with manifest (original path, hash, timestamp, threat name)
- Restore quarantined files to their original location
- Structured JSON report generation
- Logging to console and optional log file
- Modular architecture

## Usage

### Scan

```bash
python main.py scan --path ./files
python main.py scan --path ./files \
    --signatures data/signatures.json \
    --quarantine data/quarantine \
    --allowlist  data/allowlist.json \
    --types      .exe,.dll \
    --exclude    node_modules,.git \
    --report     report.json \
    --log-file   logs/scan.log \
    --verbose
```

### Quarantine management

```bash
# List quarantined files
python main.py quarantine list

# Restore a file
python main.py quarantine restore /path/inside/quarantine/bad.exe
python main.py quarantine restore /path/inside/quarantine/bad.exe --force
```

### Allowlist management

```bash
# Add a file path
python main.py allowlist add --path /path/to/safe/file.exe

# Add a hash
python main.py allowlist add --hash <sha256-hex>
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | No malicious files detected |
| `1`  | One or more malicious files detected |
| `2`  | Configuration or runtime error |

## Running tests

```bash
python -m pytest tests/
# or
python -m unittest discover -s tests
```
