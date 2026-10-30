"""Deterministic evidence for the interval and selection decompositions."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath

from artifacts import atomic_open, write_text


CORE_EVIDENCE_FILES = (
    'summary.json', 'events.json', 'original.csv', 'timestamp_only.csv',
    'literal_rule.csv', 'diagnostics.json', 'example_263_265.json',
    'mode_membership.csv',
)
FOLLOWUP_EVIDENCE_FILES = (
    'summary.json', 'all_adjacent_pairs.csv',
    'PPN_ab_below_600.csv', 'NPN_ab_below_600.csv',
    'PPN_ab_300_to_599.csv', 'NPN_ab_300_to_599.csv',
    'PPN_ab_below_600_later_sensitivity.csv',
    'common_range_adjustment_cells.csv',
)
DISPUTED_LABEL_EVIDENCE_FILES = ('rows.csv', 'summary.json')
REPRODUCED_EVIDENCE_FILES = CORE_EVIDENCE_FILES + tuple(
    'followup/' + name for name in FOLLOWUP_EVIDENCE_FILES
) + tuple('disputed_labels/' + name for name in DISPUTED_LABEL_EVIDENCE_FILES)


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
        write_text(output / filename, json.dumps(value, indent=2) + '\n')
    by_mode = {mode: {r['c']: r for r in rows} for mode, rows in result['events'].items()}
    heights = sorted(set().union(*(set(rows) for rows in by_mode.values())))
    with atomic_open(output / 'mode_membership.csv', encoding='utf-8', newline='') as handle:
        fields = ['a', 'b', 'c', 'pair_delta', 'child_delta', 'published_delta', *by_mode]
        writer = csv.DictWriter(handle, fields, lineterminator='\n')
        writer.writeheader()
        for c in heights:
            row = next(rows[c] for rows in by_mode.values() if c in rows)
            writer.writerow(dict(row, **{mode: int(c in rows) for mode, rows in by_mode.items()}))
    return diagnostics


def _reject_symlinks(path):
    """Do not read a reference or generated member through redirected paths."""
    for component in (path, *path.absolute().parents):
        if component.is_symlink():
            raise ValueError('Evidence path must not contain symlinks: ' + str(component))


def compare_saved_evidence(output, saved, expected_files=None):
    """Require the complete frozen reference inventory and compare every byte.

    Missing reference files are errors rather than a request to omit a check.
    Production callers select one of the fixed inventories above explicitly.
    Generated directories may also contain RPC lookup data or execution reports;
    these auxiliary outputs are not part of the deterministic reference set.
    """
    output, saved = Path(output), Path(saved)
    if expected_files is None:
        inventories = {'followup': FOLLOWUP_EVIDENCE_FILES, 'disputed_labels': DISPUTED_LABEL_EVIDENCE_FILES}
        expected_files = inventories.get(saved.name, REPRODUCED_EVIDENCE_FILES)
    if isinstance(expected_files, (str, bytes)):
        raise ValueError('Evidence inventory must be a nonempty collection of relative filenames')
    names = tuple(expected_files)
    if not names or not all(isinstance(name, str) for name in names):
        raise ValueError('Evidence inventory must contain relative filename strings')
    if len(set(names)) != len(names):
        raise ValueError('Evidence inventory must be unique')
    for name in names:
        relative = PurePosixPath(name)
        if (relative.is_absolute() or name != relative.as_posix()
                or any(part in ('', '.', '..') for part in name.split('/'))
                or '\\' in name or ':' in name or '\x00' in name):
            raise ValueError('Invalid evidence inventory path: ' + name)
    required = set(names)
    _reject_symlinks(saved)
    if not saved.is_dir():
        raise ValueError('Frozen evidence directory is missing: ' + str(saved))
    observed = set()
    for member in saved.rglob('*'):
        _reject_symlinks(member)
        if member.is_file():
            observed.add(member.relative_to(saved).as_posix())
        elif not member.is_dir():
            raise ValueError('Unsupported frozen evidence entry: ' + str(member))
    missing, unexpected = required - observed, observed - required
    if missing or unexpected:
        raise ValueError('Frozen evidence inventory differs; missing: '
                         + ', '.join(sorted(missing)) + '; unexpected: '
                         + ', '.join(sorted(unexpected)))
    _reject_symlinks(output)
    for name in sorted(required):
        generated = output / name
        _reject_symlinks(generated)
        if not generated.is_file() or generated.read_bytes() != (saved / name).read_bytes():
            raise ValueError('Regenerated evidence differs: ' + name)
