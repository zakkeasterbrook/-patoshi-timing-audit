#!/usr/bin/env python3
"""Verify the release's recorded file checksums. No network or dependencies."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
count = 0
for line in (ROOT / 'SHA256SUMS.txt').read_text().splitlines():
    digest, name = line.split('  ', 1)
    path = (ROOT / name).resolve()
    if ROOT not in path.parents or not path.is_file():
        raise ValueError('Invalid or missing manifest path: ' + name)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Checksum mismatch: ' + name)
    count += 1
print(f'PASS: {count} release file checksums match.')
