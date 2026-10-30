"""Source-identified label removals must stay separate from primary results."""
import copy
import csv
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import disputed_labels
from inputs import load_inputs


class DisputedLabelTests(unittest.TestCase):
    def test_source_identified_removals_reproduce_every_retained_primary_case(self):
        records, labels, _, _ = load_inputs()
        original_labels = list(labels)
        summary, rows = disputed_labels.analyze(records, labels)
        disputed_labels.verify_regression_targets(summary)
        self.assertEqual(labels, original_labels)
        self.assertEqual(summary['removed_positive_heights'], [24504, 35573, 35599])
        self.assertEqual(summary['sensitivity_label_count'], 21950)
        self.assertEqual(summary['original_stated_rule']['cases'], 754)
        with (ROOT / 'results/expected/literal_rule.csv').open(newline='') as handle:
            primary = [(int(r['height']), int(r['header_timestamp_delta_seconds'])) for r in csv.DictReader(handle)]
        expected = [(height, delta) for height, delta in primary if height != 24505]
        self.assertEqual([(r['c'], r['bc_seconds']) for r in rows], expected)
        self.assertEqual([r['c'] for r in rows], sorted({r['c'] for r in rows}))
        for row in rows:
            self.assertEqual((row['b'], row['c']), (row['a'] + 1, row['a'] + 2))
            self.assertEqual(row['sensitivity_labels'], 'PPN')
            self.assertLess(row['ab_seconds'], 600)
            self.assertEqual(row['c_block_hash'], records[row['c']]['block_hash'])

    def test_removal_can_create_a_negative_label_without_mutating_primary_data(self):
        records = [{'height': h, 'timestamp': t, 'block_hash': f'{h:064x}'}
                   for h, t in enumerate([0, 599, 898])]
        labels = [0, 1, 2]
        before = copy.deepcopy(records)
        summary, rows = disputed_labels.analyze(records, labels, removed_heights=[2])
        self.assertEqual(summary['original_stated_rule']['cases'], 0)
        self.assertEqual(summary['added_case_child_heights'], [2])
        self.assertEqual(rows[0]['original_labels'], 'PPP')
        self.assertEqual(rows[0]['sensitivity_labels'], 'PPN')
        self.assertEqual(rows[0]['bc_seconds'], 299)
        self.assertEqual(records, before)
        self.assertEqual(labels, [0, 1, 2])

    def test_strict_filter_negative_preceding_gap_and_outcome_boundaries(self):
        def analyze(ab, bc):
            times = [1000, 1000 + ab, 1000 + ab + bc]
            records = [{'height': h, 'timestamp': t, 'block_hash': f'{h:064x}'} for h, t in enumerate(times)]
            return disputed_labels.analyze(records, [0, 1, 2], removed_heights=[2])
        self.assertEqual(analyze(600, -1)[1], [])
        self.assertEqual(len(analyze(599, 300)[1]), 1)
        self.assertEqual(analyze(-1, 299)[1][0]['ab_seconds'], -1)
        for delta, expected in [(-1, (1, 0, 0, 0)), (0, (0, 1, 0, 0)),
                                (299, (0, 0, 1, 0)), (300, (0, 0, 0, 1))]:
            with self.subTest(delta=delta):
                summary, _ = analyze(599, delta)
                self.assertEqual(tuple(summary['sensitivity'][key] for key in
                    ('negative', 'zero', 'positive_below_300', 'at_least_300')), expected)

    def test_unknown_or_duplicate_removed_labels_fail_visibly(self):
        records = [{'height': h, 'timestamp': h, 'block_hash': f'{h:064x}'} for h in range(3)]
        for removals in ([3], [1, 1], [2, 1], [True]):
            with self.subTest(removals=removals), self.assertRaises(ValueError):
                disputed_labels.analyze(records, [0, 1, 2], removed_heights=removals)

    def test_standalone_cannot_overwrite_frozen_evidence(self):
        with self.assertRaisesRegex(ValueError, 'frozen project files'):
            disputed_labels.run(ROOT / 'results/reproduced/disputed_labels')


if __name__ == '__main__':
    unittest.main()
