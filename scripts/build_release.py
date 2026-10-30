#!/usr/bin/env python3
"""Build a byte-reproducible candidate archive from a clean, verified Git commit.

This verifies artifact identity, not a new scientific or native-PHP execution.
The CI packaging job requires the offline and native verification jobs first.
"""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import stat
import subprocess
import zipfile

from artifacts import output_transaction, write_bytes, write_text
from verify_manifest import ROOT, verify

VERSION = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?')
EXTRA_MANIFEST = 'RELEASE_MANIFEST.json'


def git(root, *arguments):
    return subprocess.run(['git', *arguments], cwd=root, check=True, capture_output=True).stdout


def build(version, output_dir=None, *, root=ROOT):
    """Archive exactly the committed, manifested files with stable ZIP metadata."""
    if not isinstance(version, str) or VERSION.fullmatch(version) is None:
        raise ValueError('Version must be a safe semantic version, such as 1.0.0-rc.1')
    root = Path(root).resolve()
    output_dir = Path(output_dir) if output_dir is not None else root / 'build/release'
    top = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if top != root:
        raise ValueError('Build from the actual Git checkout root')
    if git(root, 'status', '--porcelain=v1', '--untracked-files=normal').strip():
        raise ValueError('Release packaging requires a clean, committed checkout')
    commit = git(root, 'rev-parse', 'HEAD^{commit}').decode().strip()
    expected = verify(root)
    expected['SHA256SUMS.txt'] = sha256((root / 'SHA256SUMS.txt').read_bytes()).hexdigest()
    if EXTRA_MANIFEST in expected:
        raise ValueError('Reserved generated release-manifest filename is already tracked')

    # Read committed blobs, not arbitrary local copies, ignored files or .git.
    with zipfile.ZipFile(BytesIO(git(root, 'archive', '--format=zip', commit))) as source:
        members = {item.filename: item for item in source.infolist() if not item.is_dir()}
        if set(members) != set(expected):
            raise ValueError('Committed Git tree and verified release inventory differ')
        files = {name: source.read(name) for name in sorted(members)}
        for name, payload in files.items():
            if sha256(payload).hexdigest() != expected[name]:
                raise ValueError('Committed blob differs from verified worktree: ' + name)
        modes = {name: (members[name].external_attr >> 16) & 0o777 for name in members}
    metadata = {
        'format_version': 1,
        'project': 'Patoshi Timing Audit',
        'repository': 'https://github.com/zakkeasterbrook/-patoshi-timing-audit',
        'version': version,
        'git_commit': commit,
        'source_root': 'patoshi-timing-audit',
        'source_commit_utc': git(root, 'show', '-s', '--format=%cI', commit).decode().strip(),
        'packaging': 'ZIP_STORED; sorted members; fixed 1980-01-01 container timestamps; regular-file modes',
        'timestamp_scope': 'Container timestamps are format constants, not publication dates',
        'verification_scope': 'Clean Git tree, complete file inventory and SHA-256 identity; scientific execution is verified separately',
        'files': {name: {'sha256': expected[name], 'bytes': len(files[name])} for name in sorted(files)},
    }
    archive_members = {'patoshi-timing-audit/' + name: content for name, content in files.items()}
    archive_modes = {'patoshi-timing-audit/' + name: mode for name, mode in modes.items()}
    # Keep generated metadata outside the exact source tree: its own manifest
    # must still verify unchanged after extraction, with no circular hashes.
    archive_members[EXTRA_MANIFEST] = (json.dumps(metadata, indent=2, sort_keys=True) + '\n').encode('utf-8')
    archive_modes[EXTRA_MANIFEST] = 0o644
    payload = BytesIO()
    with zipfile.ZipFile(payload, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(archive_members):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | (archive_modes[name] or 0o644)) << 16
            archive.writestr(entry, archive_members[name])
    archive_bytes = payload.getvalue()
    filename = 'Patoshi_Timing_Audit_v' + version + '.zip'
    digest = sha256(archive_bytes).hexdigest()
    report = {
        'status': 'pass', 'version': version, 'git_commit': commit,
        'archive': filename, 'bytes': len(archive_bytes), 'sha256': digest,
        'source_files': len(expected), 'generated_metadata': EXTRA_MANIFEST,
        'github_release_created': False,
    }
    with output_transaction(output_dir, root=root) as staged:
        write_bytes(staged / filename, archive_bytes)
        write_text(staged / 'SHA256SUMS.txt', digest + '  ' + filename + '\n', encoding='ascii')
        write_text(staged / 'release.json', json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='1.0.0-rc.1')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/release')
    args = parser.parse_args()
    print(json.dumps(build(args.version, args.output_dir), indent=2))
