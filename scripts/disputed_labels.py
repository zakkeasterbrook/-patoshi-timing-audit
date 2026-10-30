#!/usr/bin/env python3
"""Reproduce the explicitly cited three-label sensitivity without changing P.

The historical label criticisms are source assertions, not newly validated
miner attributions. This module independently scans consecutive heights and
keeps the original-list calculation separate from the sensitivity calculation.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics

from artifacts import atomic_open, output_transaction, write_text
from inputs import HEADER_SHA256, LABEL_SHA256, ROOT, load_inputs, require, validate_labels
from reporting import compare_saved_evidence, DISPUTED_LABEL_EVIDENCE_FILES

DISPUTED_HEIGHTS = (24_504, 35_573, 35_599)
FIELDS = (
    'a', 'b', 'c', 'a_timestamp', 'b_timestamp', 'c_timestamp',
    'a_block_hash', 'b_block_hash', 'c_block_hash', 'ab_seconds', 'bc_seconds',
    'original_labels', 'sensitivity_labels',
)


def _enumerate(records, original, selected):
    rows = []
    for c in range(2, len(records)):
        a, b = c - 2, c - 1
        if a not in selected or b not in selected or c in selected:
            continue
        ta, tb, tc = (records[h]['timestamp'] for h in (a, b, c))
        if tb - ta >= 600:
            continue
        rows.append({
            'a': a, 'b': b, 'c': c,
            'a_timestamp': ta, 'b_timestamp': tb, 'c_timestamp': tc,
            'a_block_hash': records[a]['block_hash'],
            'b_block_hash': records[b]['block_hash'],
            'c_block_hash': records[c]['block_hash'],
            'ab_seconds': tb - ta, 'bc_seconds': tc - tb,
            'original_labels': ''.join('P' if h in original else 'N' for h in (a, b, c)),
            'sensitivity_labels': ''.join('P' if h in selected else 'N' for h in (a, b, c)),
        })
    return rows


def _stats(rows):
    values = [r['bc_seconds'] for r in rows]
    n = len(values)
    below = sum(d < 300 for d in values)
    return {
        'cases': n, 'negative': sum(d < 0 for d in values),
        'zero': sum(d == 0 for d in values),
        'positive_below_300': sum(0 < d < 300 for d in values),
        'zero_to_299': sum(0 <= d < 300 for d in values),
        'below_300_including_negative': below,
        'at_300': sum(d == 300 for d in values),
        'at_least_300': sum(d >= 300 for d in values),
        'below_300_percent': below * 100 / n if n else None,
        'median_seconds': statistics.median(values) if values else None,
    }


def analyze(records, labels, *, removed_heights=DISPUTED_HEIGHTS):
    """Return independent direct-rule results and complete sensitivity rows.

    ``removed_heights`` permits small synthetic boundary tests; the public CLI
    always uses the fixed three heights supported by the provenance record.
    All primary labels and records are read without mutation.
    """
    require(bool(records), 'Expected header records')
    require([r['height'] for r in records] == list(range(len(records))),
            'Header records must be consecutive from genesis')
    require(all(type(r['timestamp']) is int for r in records), 'Timestamps must be integers')
    validate_labels(labels, len(records) - 1)
    removals = list(removed_heights)
    require(removals == sorted(set(removals)) and all(type(h) is int for h in removals),
            'Removed labels must be unique sorted integer heights')
    original = set(labels)
    require(set(removals) <= original, 'A disputed positive label is absent from the original list')
    revised = original - set(removals)
    primary_rows = _enumerate(records, original, original)
    rows = _enumerate(records, original, revised)
    primary_heights = {r['c'] for r in primary_rows}
    sensitivity_heights = {r['c'] for r in rows}
    summary = {
        'original_label_count': len(original), 'sensitivity_label_count': len(revised),
        'removed_positive_heights': removals,
        'original_stated_rule': _stats(primary_rows), 'sensitivity': _stats(rows),
        'removed_case_child_heights': sorted(primary_heights - sensitivity_heights),
        'added_case_child_heights': sorted(sensitivity_heights - primary_heights),
        'source_record': 'provenance/disputed_labels.json' if removals == list(DISPUTED_HEIGHTS) else None,
        'definitions': {
            'P_primary': 'Membership in the unchanged frozen published list',
            'P_sensitivity': 'Membership after removing only the named positive heights',
            'N_sensitivity': 'Nonmembership in the revised list, including removed positives',
            'selection': 'Consecutive PPN heights with timestamp(B)-timestamp(A) <600 seconds; no nonnegative lower bound',
            'outcome': 'timestamp(C)-timestamp(B), in seconds; strict below300 includes negatives and excludes exactly300',
            'scope': 'Classification sensitivity; not independent validation of historical label criticisms or miner identity',
        },
    }
    return summary, rows


def verify_regression_targets(summary):
    measured = summary['sensitivity']
    require(tuple(measured[k] for k in ('cases', 'negative', 'below_300_including_negative')) == (753, 30, 276),
            'Disputed-label sensitivity differs from the recovered report')
    require(summary['removed_case_child_heights'] == [24_505] and summary['added_case_child_heights'] == [],
            'Disputed-label selection differences changed')


def write_outputs(directory, summary, rows):
    """Write reviewed computed evidence to a staging directory deterministically."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with atomic_open(directory / 'rows.csv', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    summary = dict(summary)
    summary['csv_sha256'] = hashlib.sha256((directory / 'rows.csv').read_bytes()).hexdigest()
    write_text(directory / 'summary.json', json.dumps(summary, indent=2) + '\n')
    return summary


def run(output_dir=None):
    output_dir = Path(output_dir) if output_dir is not None else ROOT / 'build/disputed_labels'
    with output_transaction(output_dir, root=ROOT) as staged:
        records, labels, _, _ = load_inputs()
        provenance = json.loads((ROOT / 'provenance/disputed_labels.json').read_text(encoding='utf-8'))
        require(provenance['disputed_heights'] == list(DISPUTED_HEIGHTS), 'Disputed-label provenance differs')
        summary, rows = analyze(records, labels)
        summary['input_sha256'] = {'headers': HEADER_SHA256, 'canonical_primary_labels': LABEL_SHA256}
        verify_regression_targets(summary)
        summary['status'] = 'pass'
        summary = write_outputs(staged, summary, rows)
        compare_saved_evidence(staged, ROOT / 'results/reproduced/disputed_labels', DISPUTED_LABEL_EVIDENCE_FILES)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/disputed_labels')
    print(json.dumps(run(parser.parse_args().output_dir), indent=2))
