"""Regressions for omitted release files and outputs that alias evidence."""
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from artifacts import atomic_open, output_transaction
from reproduce import reproduce
from followup import run as reproduce_followup
from update_manifest import update
from verify_manifest import inventory, verify


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='patoshi-manifest-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'README.md').write_bytes(b'audit\n')
        (self.root / 'data.bin').write_bytes(b'\x00\x01\x02')
        self.expected = update(self.root)

    def manifest(self, content):
        (self.root / 'SHA256SUMS.txt').write_text(content, encoding='utf-8')

    def line(self, name):
        return self.expected[name] + '  ' + name + '\n'

    def symlink(self, source, link, *, directory=False):
        try:
            link.symlink_to(source, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('Filesystem symlink creation unavailable: ' + str(exc))

    def test_empty_manifest_never_reports_a_successful_zero_file_release(self):
        self.manifest('')
        with self.assertRaisesRegex(ValueError, 'empty'):
            verify(self.root)

    def test_omitted_file_and_duplicate_entry_fail(self):
        self.manifest(self.line('README.md'))
        with self.assertRaisesRegex(ValueError, 'unlisted files'):
            verify(self.root)
        self.manifest(self.line('README.md') * 2 + self.line('data.bin'))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            verify(self.root)

    def test_invalid_digests_and_noncanonical_paths_fail(self):
        for entry in ('0  README.md', 'F' * 64 + '  README.md',
                      self.expected['README.md'] + ' README.md'):
            with self.subTest(entry=entry), self.assertRaisesRegex(ValueError, 'Malformed'):
                self.manifest(entry + '\n')
                verify(self.root)
        for name in ('../README.md', '/README.md', './README.md', 'docs//file',
                     'docs/../README.md', 'docs\\file', 'C:/README.md', ' README.md'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Invalid manifest path'):
                self.manifest('0' * 64 + '  ' + name + '\n')
                verify(self.root)

    def test_missing_or_changed_file_fails(self):
        (self.root / 'data.bin').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
            verify(self.root)
        (self.root / 'data.bin').unlink()
        with self.assertRaisesRegex(ValueError, 'missing files'):
            verify(self.root)

    def test_adding_an_unlisted_file_fails_until_explicitly_reviewed_and_updated(self):
        (self.root / 'analysis.py').write_bytes(b'print("new analysis")\n')
        with self.assertRaisesRegex(ValueError, 'unlisted files'):
            verify(self.root)
        updated = update(self.root)
        self.assertEqual(updated, verify(self.root))
        self.assertEqual(updated['analysis.py'], hashlib.sha256((self.root / 'analysis.py').read_bytes()).hexdigest())

    def test_runtime_outputs_are_excluded_but_a_nested_manifest_is_not(self):
        for relative in ('build/out.json', '.git/HEAD', '.venv/bin/python',
                         '__pycache__/cache.pyc', 'nested/cache.pyo', '.DS_Store'):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'not a release artifact')
        self.assertEqual(set(inventory(self.root)), set(self.expected))
        nested = self.root / 'nested/SHA256SUMS.txt'
        nested.write_bytes(b'independent nested artifact')
        with self.assertRaisesRegex(ValueError, 'nested/SHA256SUMS.txt'):
            verify(self.root)

    def test_manifest_file_and_release_member_symlinks_are_rejected(self):
        original = self.root / 'data.bin'
        alias = self.root / 'linked.bin'
        self.symlink(original, alias)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            inventory(self.root)
        alias.unlink()
        original_manifest = self.root / 'SHA256SUMS.txt'
        saved = original_manifest.read_bytes()
        original_manifest.unlink()
        target = self.root / 'manifest-copy'
        target.write_bytes(saved)
        self.symlink(target, original_manifest)
        with self.assertRaisesRegex(ValueError, 'linked release manifest'):
            verify(self.root)


class OutputArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='patoshi-output-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'checkout'
        self.root.mkdir()
        self.output = self.root / 'build'
        self.output.mkdir()
        self.sentinel = self.root / 'frozen-evidence.txt'
        self.sentinel.write_bytes(b'untouched evidence\n')

    def symlink(self, source, link, *, directory=False):
        try:
            link.symlink_to(source, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('Filesystem symlink creation unavailable: ' + str(exc))

    def test_real_reproduction_rejects_existing_symlink_before_touching_evidence(self):
        self.symlink(self.sentinel, self.output / 'original.csv')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            reproduce(self.output)
        self.assertEqual(self.sentinel.read_bytes(), b'untouched evidence\n')
        self.assertFalse((self.output / 'timestamp_only.csv').exists())

    def test_standalone_followup_rejects_existing_hardlinked_output(self):
        try:
            os.link(self.sentinel, self.output / 'summary.json')
        except (OSError, NotImplementedError) as exc:
            self.skipTest('Filesystem hard-link creation unavailable: ' + str(exc))
        with self.assertRaisesRegex(ValueError, 'hard-linked'):
            reproduce_followup(self.output)
        self.assertEqual(self.sentinel.read_bytes(), b'untouched evidence\n')

    def test_nested_symlink_directory_is_rejected_before_generation(self):
        protected = self.root / 'data'
        protected.mkdir()
        self.symlink(protected, self.output / 'followup', directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            with output_transaction(self.output, root=self.root):
                self.fail('Unsafe output context must not be entered')
        self.assertEqual(list(protected.iterdir()), [])

    def test_failed_calculation_keeps_previous_outputs_and_unrelated_inputs(self):
        (self.output / 'summary.json').write_bytes(b'previous result\n')
        (self.output / 'original.php').write_bytes(b'upstream source\n')
        with self.assertRaisesRegex(RuntimeError, 'deliberate calculation failure'):
            with output_transaction(self.output, root=self.root) as staged:
                (staged / 'summary.json').write_bytes(b'unverified new result\n')
                (staged / 'new.csv').write_bytes(b'unverified rows\n')
                raise RuntimeError('deliberate calculation failure')
        self.assertEqual((self.output / 'summary.json').read_bytes(), b'previous result\n')
        self.assertEqual((self.output / 'original.php').read_bytes(), b'upstream source\n')
        self.assertFalse((self.output / 'new.csv').exists())

    def test_successful_publication_preserves_unrelated_source_and_logs(self):
        (self.output / 'original.php').write_bytes(b'upstream source\n')
        (self.output / 'older.log').write_bytes(b'archived log\n')
        with output_transaction(self.output, root=self.root) as staged:
            (staged / 'summary.json').write_bytes(b'verified result\n')
            (staged / 'nested').mkdir()
            (staged / 'nested/rows.csv').write_bytes(b'verified rows\n')
        self.assertEqual((self.output / 'summary.json').read_bytes(), b'verified result\n')
        self.assertEqual((self.output / 'nested/rows.csv').read_bytes(), b'verified rows\n')
        self.assertEqual((self.output / 'original.php').read_bytes(), b'upstream source\n')
        self.assertEqual((self.output / 'older.log').read_bytes(), b'archived log\n')

    def test_failed_atomic_text_write_does_not_truncate_existing_file(self):
        path = self.output / 'summary.json'
        path.write_bytes(b'previous complete file\n')
        with self.assertRaises(RuntimeError):
            with atomic_open(path) as handle:
                handle.write('incomplete replacement')
                raise RuntimeError('interrupt generation')
        self.assertEqual(path.read_bytes(), b'previous complete file\n')
        self.assertEqual([p.name for p in self.output.iterdir()], ['summary.json'])


if __name__ == '__main__':
    unittest.main()
