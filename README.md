# basic-antivirus-simulation

Basic signature-based antivirus simulation for educational and ethical defensive use.

## Features
- SHA-256 file hashing
- Recursive file/directory scanning
- Signature database loading from `.json` or plain text
- Malicious file detection by hash matching
- Optional quarantine directory move
- Logging to console and optional log file

## Signature database formats
- **Text**: one SHA-256 hash per line (`#` comments allowed)
- **JSON**:
  - list format: `["<sha256>", "..."]`
  - object format: `{"signatures": ["<sha256>", "..."]}`

## Usage
```bash
python antivirus_scanner.py /path/to/scan --signatures /path/to/signatures.txt
python antivirus_scanner.py /path/to/scan --signatures /path/to/signatures.json --quarantine /path/to/quarantine --log-file scan.log --verbose
```

Exit codes:
- `0`: no malicious files detected
- `1`: malicious file(s) detected
- `2`: scan/configuration error
