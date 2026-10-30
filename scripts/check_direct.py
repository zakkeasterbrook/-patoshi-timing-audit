#!/usr/bin/env python3
"""Second implementation: decode raw bytes and enumerate triples without audit imports.

This checks the stated rule, comparison sequences and surviving pair fingerprints.
It is a numerical cross-check, not external human review or miner attribution.
"""
import csv
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def check():
    payload = (ROOT / 'data/headers_0_49999.bin').read_bytes()
    if len(payload) != 4_000_000 or hashlib.sha256(payload).hexdigest() != 'b9e200ba15c904e05283461469d5582a9580df15ff842436576a7490454b03ec':
        raise ValueError('Header input differs from the pinned dataset')
    labels = json.loads((ROOT / 'data/patoshi_heights.json').read_text())
    if hashlib.sha256(json.dumps(labels, separators=(',', ':')).encode()).hexdigest() != '33c9927845ccd3016fb37bc2b860cfe7a3fea22522c67649d72c6dc50e9ae8e1':
        raise ValueError('Label input differs from the pinned dataset')
    times = [struct.unpack_from('<I', payload, h * 80 + 68)[0] for h in range(50_000)]
    listed = [False] * len(times)
    for h in labels:
        listed[h] = True
    ppn, npn = [], []
    for a in range(len(times) - 2):
        b, c = a + 1, a + 2
        if listed[b] and not listed[c] and times[b] - times[a] < 600:
            (ppn if listed[a] else npn).append([c, times[c] - times[b]])
    with (ROOT / 'results/expected/literal_rule.csv').open(newline='') as f:
        saved = [[int(r['height']), int(r['header_timestamp_delta_seconds'])] for r in csv.DictReader(f)]
    if ppn != saved:
        raise ValueError('Second implementation disagrees with the complete stated-rule CSV')
    def stats(rows):
        values = [r[1] for r in rows]
        return {'cases': len(values), 'negative': sum(v < 0 for v in values),
                'below_300_including_negative': sum(v < 300 for v in values)}
    groups = {key: [] for key in ('PP', 'PN', 'NP', 'NN')}
    later_pp = []
    for b in range(1, len(times)):
        a = b - 1
        key = ('P' if listed[a] else 'N') + ('P' if listed[b] else 'N')
        row = [b, times[b] - times[a]]
        groups[key].append(row)
        if key == 'PP' and a >= 541 and not any(1400 <= h <= 1916 for h in (a, b)):
            later_pp.append(row)
    byte_band = lambda h: payload[h * 80 + 76] in set(range(10)) | set(range(19, 59))
    result = {
        'status': 'pass', 'implementation': 'raw-byte enumeration; no imports from audit modules',
        'stated_rule': stats(ppn), 'NPN_preceding_gap_below_600': stats(npn),
        'all_adjacent_pairs': {key: stats(rows) for key, rows in groups.items()},
        'later_PP_pairs': len(later_pp),
        'later_PP_below_312': [r for r in later_pp if r[1] < 312],
        'listed_inside_coarse_nonce_band': sum(byte_band(h) for h in labels),
        'all_inside_coarse_nonce_band': sum(byte_band(h) for h in range(len(times))),
        'example_263_264_265': {'preceding_gap': times[264]-times[263],
                              'following_gap': times[265]-times[264],
                              'incorrect_combined_gap': times[265]-times[263]},
        'scope': 'Fixed historical labels; descriptive checks only; header timestamps are not observed elapsed times',
    }
    expected = {'cases': 754, 'negative': 30, 'below_300_including_negative': 276}
    if result['stated_rule'] != expected:
        raise ValueError('Unexpected headline totals')
    output = ROOT / 'build/direct_check.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
