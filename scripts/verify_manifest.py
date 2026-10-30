#!/usr/bin/env python3
"""Verify exact release-file coverage and SHA-256 digests without dependencies."""
import hashlib
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat

from artifacts import is_link

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'SHA256SUMS.txt'
EXCLUDED_DIRECTORIES = frozenset({'.git', 'build', '__pycache__', '.venv'})


def _valid_name(name):
    path = PurePosixPath(name)
    if (not name or name.strip() != name or '\\' in name or path.is_absolute()
            or PureWindowsPath(name).drive or path.as_posix() != name
            or any(part in ('.', '..') for part in path.parts)
            or re.search(r'[\x00-\x1f\x7f]', name)):
        raise ValueError('Invalid manifest path: ' + repr(name))
    return name


def inventory(root=ROOT):
    """Return every publishable regular file; reject links and special files."""
    root = Path(root).resolve()
    result = {}
    def failed_walk(error):
        raise ValueError('Cannot inventory release files: ' + str(error)) from error
    for parent, directories, files in os.walk(root, followlinks=False, onerror=failed_walk):
        parent = Path(parent)
        directories[:] = [name for name in directories if name not in EXCLUDED_DIRECTORIES]
        for name in directories:
            path = parent / name
            if is_link(path):
                raise ValueError('Symlink directory is not a release artifact: ' + str(path.relative_to(root)))
        for name in files:
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if relative == MANIFEST or name == '.DS_Store' or path.suffix in ('.pyc', '.pyo'):
                continue
            _valid_name(relative)
            if is_link(path) or not stat.S_ISREG(path.stat().st_mode):
                raise ValueError('Release artifact must be a regular file: ' + relative)
            result[relative] = path
    return dict(sorted(result.items()))


def verify(root=ROOT):
    """Return verified path/digest pairs, failing on empty or omitted entries."""
    root = Path(root).resolve()
    manifest = root / MANIFEST
    if is_link(manifest) or not manifest.is_file():
        raise ValueError('Missing or linked release manifest: ' + MANIFEST)
    expected = {}
    for number, line in enumerate(manifest.read_text(encoding='utf-8').splitlines(), 1):
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None:
            raise ValueError('Malformed manifest line: ' + str(number))
        digest, name = match.groups()
        _valid_name(name)
        if name in expected:
            raise ValueError('Duplicate manifest path: ' + name)
        expected[name] = digest
    if not expected:
        raise ValueError('Release manifest is empty')
    actual = inventory(root)
    missing = sorted(set(expected) - set(actual))
    omitted = sorted(set(actual) - set(expected))
    if missing or omitted:
        raise ValueError('Manifest coverage mismatch; missing files: ' + repr(missing)
                         + '; unlisted files: ' + repr(omitted))
    for name, path in actual.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected[name]:
            raise ValueError('Checksum mismatch: ' + name)
    return expected


if __name__ == '__main__':
    entries = verify()
    print(f'PASS: {len(entries)} release file checksums match with exact artifact coverage.')
