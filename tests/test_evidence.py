"""Regression evidence must remain immutable and disclose the actual sample."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import reproduce
from reporting import (CORE_EVIDENCE_FILES, FOLLOWUP_EVIDENCE_FILES, DISPUTED_LABEL_EVIDENCE_FILES,
                       REPRODUCED_EVIDENCE_FILES, compare_saved_evidence)
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
                compare_saved_evidence(generated, saved, expected_files=('case.csv',))
            (generated / 'case.csv').write_bytes(b'height,delta\n265,630\n')
            with self.assertRaisesRegex(ValueError, 'case.csv'):
                compare_saved_evidence(generated, saved, expected_files=('case.csv',))

    def test_absent_reference_directory_is_not_a_successful_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'directory is missing'):
                compare_saved_evidence(Path(directory) / 'generated',
                                       Path(directory) / 'missing', expected_files=('case.csv',))

    def test_complete_matching_rows_allow_auxiliary_generated_lookup_data(self):
        with tempfile.TemporaryDirectory() as directory:
            saved, generated = (Path(directory) / name for name in ('saved', 'generated'))
            saved.mkdir()
            generated.mkdir()
            for path in (saved / 'case.csv', generated / 'case.csv'):
                path.write_bytes(b'height,delta\n265,71\n')
            (generated / 'headers.json').write_bytes(b'[]\n')
            compare_saved_evidence(generated, saved, expected_files=('case.csv',))

    def test_omitted_frozen_row_file_cannot_disable_its_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            saved = Path(directory) / 'saved'
            saved.mkdir()
            (saved / 'summary.json').write_bytes(b'{}\n')
            with self.assertRaisesRegex(ValueError, 'missing: case.csv'):
                compare_saved_evidence(Path(directory) / 'generated', saved,
                                       expected_files=('summary.json', 'case.csv'))

    def test_unexpected_frozen_row_file_requires_explicit_inventory_change(self):
        with tempfile.TemporaryDirectory() as directory:
            saved = Path(directory) / 'saved'
            saved.mkdir()
            (saved / 'case.csv').write_bytes(b'height,delta\n265,71\n')
            (saved / 'unexpected.csv').write_bytes(b'height,delta\n265,630\n')
            with self.assertRaisesRegex(ValueError, 'unexpected: unexpected.csv'):
                compare_saved_evidence(Path(directory) / 'generated', saved,
                                       expected_files=('case.csv',))

    def test_reference_file_symlink_cannot_redirect_the_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            saved = Path(directory) / 'saved'
            saved.mkdir()
            target = Path(directory) / 'external.csv'
            target.write_bytes(b'height,delta\n265,71\n')
            try:
                (saved / 'case.csv').symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest('Platform does not permit creating a symlink')
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                compare_saved_evidence(Path(directory) / 'generated', saved,
                                       expected_files=('case.csv',))

    def test_reference_directory_symlink_cannot_escape_the_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'external'
            target.mkdir()
            (target / 'case.csv').write_bytes(b'height,delta\n265,71\n')
            saved = Path(directory) / 'saved'
            try:
                saved.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Platform does not permit creating a symlink')
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                compare_saved_evidence(Path(directory) / 'generated', saved,
                                       expected_files=('case.csv',))

    def test_invalid_or_empty_inventory_cannot_create_a_vacuous_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            for names in ((), ('case.csv', 'case.csv'), ('../case.csv',),
                          ('/case.csv',), ('C:/case.csv',), ('case.csv:stream',),
                          ('nested\\case.csv',), ('nested//case.csv',)):
                with self.subTest(names=names), self.assertRaises(ValueError):
                    compare_saved_evidence(Path(directory), Path(directory), expected_files=names)

    def test_fixed_core_and_followup_reference_inventories_are_complete(self):
        expected = set(CORE_EVIDENCE_FILES) | {'followup/' + name for name in FOLLOWUP_EVIDENCE_FILES}
        expected |= {'disputed_labels/' + name for name in DISPUTED_LABEL_EVIDENCE_FILES}
        self.assertEqual(set(REPRODUCED_EVIDENCE_FILES), expected)
        actual = {p.relative_to(ROOT / 'results/reproduced').as_posix()
                  for p in (ROOT / 'results/reproduced').rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
