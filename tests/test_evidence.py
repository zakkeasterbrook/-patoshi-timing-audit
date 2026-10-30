"""Regression evidence must remain immutable and disclose the actual sample."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import reproduce
from reporting import compare_saved_evidence
from followup import run as reproduce_followup


class EvidenceTests(unittest.TestCase):
    def test_protected_evidence_cannot_be_an_output_destination(self):
        for destination in (ROOT, ROOT / 'results/reproduced', ROOT / 'data'):
            with self.subTest(destination=destination), self.assertRaisesRegex(ValueError, 'frozen project files'):
                reproduce(destination)

    def test_standalone_followup_cannot_overwrite_frozen_evidence(self):
        with self.assertRaisesRegex(ValueError, 'frozen project files'):
            reproduce_followup(ROOT / 'results/reproduced/followup')

    def test_missing_or_changed_regenerated_rows_fail_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            saved = Path(directory) / 'saved'
            generated = Path(directory) / 'generated'
            saved.mkdir()
            generated.mkdir()
            (saved / 'case.csv').write_bytes(b'height,delta\n265,71\n')
            with self.assertRaisesRegex(ValueError, 'case.csv'):
                compare_saved_evidence(generated, saved)
            (generated / 'case.csv').write_bytes(b'height,delta\n265,630\n')
            with self.assertRaisesRegex(ValueError, 'case.csv'):
                compare_saved_evidence(generated, saved)


if __name__ == '__main__':
    unittest.main()
