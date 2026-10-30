#!/usr/bin/env python3
"""Independent source-level audit, written without importing the earlier audit.

Inputs: a JSON array of {height, timestamp, header_hex, block_hash} and a
JSON array of the published Patoshi heights. Header binary input is also
accepted: contiguous 80-byte headers beginning at genesis.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def read_headers(path):
    data = Path(path).read_bytes()
    if path.endswith('.json'):
        blocks = json.loads(data)
        items = [(x['height'], bytes.fromhex(x['header_hex'])) for x in blocks]
        wanted = {x['height']: x for x in blocks}
    else:
        assert len(data) % 80 == 0
        items = [(i // 80, data[i:i+80]) for i in range(0, len(data), 80)]
        wanted = None
    timestamps = {}
    hashes = {}
    previous = bytes(32)
    for h, raw in items:
        assert len(raw) == 80
        digest = hashlib.sha256(hashlib.sha256(raw).digest()).digest()
        assert raw[4:36] == previous, ('broken linkage', h)
        previous = digest
        ntime, bits = struct.unpack_from('<II', raw, 68)
        mantissa, exponent = bits & 0x7fffff, bits >> 24
        target = (mantissa << (8*(exponent-3))) if exponent >= 3 else (mantissa >> (8*(3-exponent)))
        assert int.from_bytes(digest, 'little') <= target, ('invalid PoW', h)
        if wanted:
            assert wanted[h]['timestamp'] == ntime
            assert wanted[h]['block_hash'] == digest[::-1].hex()
        timestamps[h] = ntime
        hashes[h] = digest[::-1].hex()
    return timestamps, hashes


def calculate(timestamps, labels, maximum):
    labels_set = set(labels)
    assert labels == sorted(labels) and len(labels_set) == len(labels)
    events = {'original': [], 'timestamp_only': [], 'stated_rule': []}
    structural_candidates = []
    streak = []
    for height in labels:
        if not streak or height == streak[-1] + 1:
            streak.append(height)
            continue
        if len(streak) > 2:
            b = streak[-1]
            a, c = b-1, b+1
            structural_candidates.append(c)
            if c <= maximum:
                ta, tb, tc = (timestamps[x] for x in (a,b,c))
                row = {'a': a, 'b': b, 'c': c, 'pair_delta': tb-ta, 'child_delta': tc-tb,
                       'published_delta': tc-ta}
                events['original'].append(row)
                if tb < ta + 600:
                    events['timestamp_only'].append(row)
        streak = []

    # A direct scan over every possible C, independent of the run tracker.
    for c in range(2, maximum+1):
        a, b = c-2, c-1
        if a in labels_set and b in labels_set and c not in labels_set:
            ta, tb, tc = (timestamps[x] for x in (a,b,c))
            if tb-ta < 600:
                events['stated_rule'].append({'a': a, 'b': b, 'c': c,
                    'pair_delta': tb-ta, 'child_delta': tc-tb, 'published_delta': tc-ta})

    summary = {}
    for name, rows in events.items():
        key = 'published_delta' if name == 'original' else 'child_delta'
        vals = [x[key] for x in rows]
        summary[name] = {'n': len(rows), 'negative': sum(x < 0 for x in vals),
                         'zero': sum(x == 0 for x in vals),
                         'positive_below_300': sum(0 < x < 300 for x in vals),
                         'less_300': sum(x < 300 for x in vals),
                         'zero_to_299': sum(0 <= x < 300 for x in vals),
                         'at_least_300': sum(x >= 300 for x in vals),
                         'at_300': sum(x == 300 for x in vals),
                         'min_delta': min(vals) if vals else None,
                         'max_delta': max(vals) if vals else None}
    old = {x['c']: x for x in events['original']}
    fixed = {x['c']: x for x in events['timestamp_only']}
    literal = {x['c']: x for x in events['stated_rule']}
    pair_deltas = [timestamps[b]-timestamps[b-1] for b in range(1,maximum+1)
                   if b in labels_set and b-1 in labels_set]
    return {'max_child_height': maximum, 'label_count': len(labels),
            'label_min': min(labels), 'label_max': max(labels),
            'structural_candidates_all': len(structural_candidates),
            'final_unflushed_streak': streak,
            'summary': summary, 'events': events,
            'excluded_by_timestamp_fix': sorted(old.keys()-fixed.keys()),
            'added_by_stated_rule': sorted(literal.keys()-fixed.keys()),
            'patoshi_pair_deltas': {'count': len(pair_deltas),
              'negative': sum(x<0 for x in pair_deltas),
              'less_180': sum(x<180 for x in pair_deltas),
              'less_300': sum(x<300 for x in pair_deltas)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--headers', required=True)
    parser.add_argument('--labels', required=True)
    parser.add_argument('--maximum', type=int)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    times, hashes = read_headers(args.headers)
    limit = args.maximum if args.maximum is not None else max(times)
    result = calculate(times, json.loads(Path(args.labels).read_text()), limit)
    result['header_count_verified'] = len(times)
    result['header_file_sha256'] = hashlib.sha256(Path(args.headers).read_bytes()).hexdigest()
    result['last_verified_hash'] = hashes[max(hashes)]
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k,v in result.items() if k not in
                     ('events','excluded_by_timestamp_fix','added_by_stated_rule')}, indent=2))
