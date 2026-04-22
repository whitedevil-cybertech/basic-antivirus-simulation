# basic-antivirus-simulation

Basic signature-based antivirus simulation for educational and ethical defensive use.

## Project structure

```
basic-antivirus-simulation/
│
├── setup.py                   # Package + console scripts
├── gui_requirements.txt       # GUI dependencies
│
├── src/
│   ├── basic_antivirus_simulation/
│   │   ├── cli.py             # CLI entry point
│   │   ├── gui_app.py         # GUI entry point
│   │   ├── gui/               # PyQt6 GUI application
│   │   └── scanner/           # Core scanning backend
│   └── antivirus_scanner.py   # Compatibility module (import-only)
│
├── data/
│   ├── signatures.json        # Signature database (hash → threat metadata)
│   ├── allowlist.json         # Allowlisted paths and hashes
│   └── quarantine/            # Quarantine storage (includes manifest.json)
│
├── logs/
│   ├── scan.log               # Default log output
│   └── scan_results.log       # GUI analytics log
│
├── scripts/
│   ├── launch_gui.py           # GUI visual testing launcher
│   ├── launch_gui.bat          # Windows GUI launcher
│
├── docs/
│   └── development/            # Phase docs + visual testing guides
│
└── tests/
    ├── test_antivirus_scanner.py
    ├── test_gui_phase3.py
    ├── test_gui_phase5.py
    └── test_gui_functional.py
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

### Install (recommended)

```bash
pip install -e .
```

### Scan (CLI)

```bash
antivirus-cli scan --path ./files
antivirus-cli scan --path ./files \
    --signatures data/signatures.json \
    --quarantine data/quarantine \
    --allowlist  data/allowlist.json \
    --types      .exe,.dll \
    --exclude    node_modules,.git \
    --report     report.json \
    --log-file   logs/scan.log \
    --verbose
```

If `antivirus-cli` is not found (PATH not set), use:

```bash
py -m basic_antivirus_simulation.cli scan --path ./files
```

Or use the launcher:

```powershell
scripts\run_cli.bat scan --path .\files
```

### Quarantine management (CLI)

```bash
# List quarantined files
antivirus-cli quarantine list

# Restore a file
antivirus-cli quarantine restore /path/inside/quarantine/bad.exe
antivirus-cli quarantine restore /path/inside/quarantine/bad.exe --force
```

### Allowlist management (CLI)

```bash
# Add a file path
antivirus-cli allowlist add --path /path/to/safe/file.exe

# Add a hash
antivirus-cli allowlist add --hash <sha256-hex>
```

### Launch GUI

```bash
antivirus-gui
```

If `antivirus-gui` is not found (PATH not set), use:

```bash
py -m basic_antivirus_simulation.gui_app
```

Or use the launcher:

```powershell
scripts\run_gui.bat
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
