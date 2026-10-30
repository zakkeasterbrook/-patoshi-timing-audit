"""Portable source archives must reflect the committed, verified tree exactly."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_release import build
from verify_manifest import verify


class ReleaseArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'source'
        self.root.mkdir()
        (self.root / 'README.md').write_bytes(b'A research fixture.\n')
        (self.root / '.gitignore').write_bytes(b'build/\n')
        # Match the real repository's LF contract even when Git's Windows
        # autocrlf setting would otherwise transform exported text bytes.
        (self.root / '.gitattributes').write_bytes(b'* text=auto eol=lf\n')
        manifest = ''.join(sha256((self.root / name).read_bytes()).hexdigest() + '  ' + name + '\n'
                           for name in ('.gitattributes', '.gitignore', 'README.md'))
        (self.root / 'SHA256SUMS.txt').write_text(manifest, encoding='ascii', newline='\n')
        self.git('init', '--quiet')
        self.git('config', 'core.autocrlf', 'true')
        self.git('add', '.')
        self.git('-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '--quiet', '-m', 'Frozen test tree')

    def git(self, *arguments):
        return subprocess.run(['git', *arguments], cwd=self.root, check=True, capture_output=True).stdout

    def test_same_commit_produces_identical_bytes_and_traceable_files(self):
        first = build('1.0.0-rc.1', self.root / 'build/one', root=self.root)
        second = build('1.0.0-rc.1', self.root / 'build/two', root=self.root)
        a, b = (self.root / 'build' / directory / first['archive'] for directory in ('one', 'two'))
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(first, second)
        with zipfile.ZipFile(a) as archive:
            names = archive.namelist()
            self.assertEqual(names, sorted(names))
            self.assertFalse(any('/.git/' in name or '/build/' in name for name in names))
            metadata = json.loads(archive.read('RELEASE_MANIFEST.json'))
            self.assertEqual(metadata['git_commit'], self.git('rev-parse', 'HEAD').decode().strip())
            for name, record in metadata['files'].items():
                payload = archive.read('patoshi-timing-audit/' + name)
                self.assertEqual(sha256(payload).hexdigest(), record['sha256'])
                self.assertEqual(len(payload), record['bytes'])
            self.assertTrue(all(item.date_time == (1980, 1, 1, 0, 0, 0) for item in archive.infolist()))
            extracted = Path(self.temporary.name) / 'extracted'
            archive.extractall(extracted)
            self.assertEqual(set(verify(extracted / 'patoshi-timing-audit')), {'.gitattributes', '.gitignore', 'README.md'})

    def test_dirty_or_untracked_content_cannot_be_packaged_as_a_commit(self):
        (self.root / 'README.md').write_text('Uncommitted edit.\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'clean, committed'):
            build('1.0.0', root=self.root)
        self.git('checkout', '--', 'README.md')
        (self.root / 'unreviewed.txt').write_text('Untracked.\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'clean, committed'):
            build('1.0.0', root=self.root)

    def test_version_cannot_escape_or_change_artifact_paths(self):
        for version in ('../1.0.0', 'v1.0.0', '1.0.0/extra', '', '1.0.0\n'):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, 'semantic version'):
                build(version, root=self.root)


if __name__ == '__main__':
    unittest.main()
