#!/usr/bin/env python3
"""Show the error with three real headers. Standard library; no network."""
from datetime import datetime, timezone
from pathlib import Path
import json
import struct

root = Path(__file__).resolve().parents[1]
data = (root / 'data/headers_0_49999.bin').read_bytes()
labels = set(json.loads((root / 'data/patoshi_heights.json').read_text()))
times = {}
for h in (263, 264, 265):
    times[h] = struct.unpack_from('<I', data, h * 80 + 68)[0]
    utc = datetime.fromtimestamp(times[h], timezone.utc).isoformat()
    print(f'Block {h}: {"P" if h in labels else "N"}, {utc}')
print(f'Preceding interval: {times[264] - times[263]} seconds (<600, eligible)')
print(f'Correct following interval: {times[265] - times[264]} seconds (<300)')
print(f'Original combined interval: {times[265] - times[263]} seconds (>=300)')
print('The original code also sets the second time equal to the first, so its filter always passes.')
print('P = in the supplied list; N = outside it. These are header timestamp differences.')
