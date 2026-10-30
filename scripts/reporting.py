"""Deterministic evidence for the interval and selection decompositions."""
import csv
from datetime import datetime, timezone
import json


def write_evidence(output, records, labels, result):
    labels = set(labels)
    original = result['events']['original']
    corrected_intervals = [r['child_delta'] for r in original]
    ab = [r['pair_delta'] for r in original]
    diagnostics = {
        'original_sample_measured_C_minus_B': {
            'cases': len(original),
            'negative': sum(d < 0 for d in corrected_intervals),
            'below_300_including_negative': sum(d < 300 for d in corrected_intervals),
        },
        'legacy_preceding_interval_seconds': {'min': min(ab), 'max': max(ab)},
        'removed_by_filter': len(result['excluded_by_timestamp_fix']),
        'added_by_direct_selection': len(result['added_by_stated_rule']),
        'original_negative_cases': [r for r in original if r['published_delta'] < 0],
        'exactly_300_child_heights': {
            mode: [r['c'] for r in rows if r['child_delta'] == 300]
            for mode, rows in result['events'].items() if mode != 'original'
        },
        'interval_identity_holds_every_original_case': all(
            r['published_delta'] == r['child_delta'] + r['pair_delta'] for r in original
        ),
        'final_legacy_tracker': result['final_unflushed_streak'],
    }
    example = {
        'blocks': [dict(records[h], label='P' if h in labels else 'N',
                        timestamp_utc=datetime.fromtimestamp(records[h]['timestamp'], timezone.utc).isoformat())
                   for h in (263, 264, 265)],
        'preceding_gap_seconds': records[264]['timestamp'] - records[263]['timestamp'],
        'intended_following_gap_seconds': records[265]['timestamp'] - records[264]['timestamp'],
        'published_gap_seconds': records[265]['timestamp'] - records[263]['timestamp'],
        'header_byte_range': 'For height h, data/headers_0_49999.bin bytes [80*h, 80*(h+1)).',
    }
    for filename, value in [('diagnostics.json', diagnostics), ('example_263_265.json', example)]:
        (output / filename).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')
    by_mode = {mode: {r['c']: r for r in rows} for mode, rows in result['events'].items()}
    heights = sorted(set().union(*(set(rows) for rows in by_mode.values())))
    with (output / 'mode_membership.csv').open('w', encoding='utf-8', newline='') as handle:
        fields = ['a', 'b', 'c', 'pair_delta', 'child_delta', 'published_delta', *by_mode]
        writer = csv.DictWriter(handle, fields, lineterminator='\n')
        writer.writeheader()
        for c in heights:
            row = next(rows[c] for rows in by_mode.values() if c in rows)
            writer.writerow(dict(row, **{mode: int(c in rows) for mode, rows in by_mode.items()}))
    return diagnostics


def compare_saved_evidence(output, saved):
    """Never replace archived rows when regenerating; compare the full evidence."""
    if not saved.exists():
        return
    for expected in sorted(saved.rglob('*')):
        if expected.is_file():
            relative = expected.relative_to(saved)
            generated = output / relative
            if not generated.is_file() or generated.read_bytes() != expected.read_bytes():
                raise ValueError('Regenerated evidence differs: ' + str(relative))
