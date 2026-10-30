#!/usr/bin/env python3
"""Explicitly refresh checksums after reviewing intentional project changes."""
import hashlib
from pathlib import Path

from artifacts import write_text
from verify_manifest import MANIFEST, ROOT, inventory, verify


def update(root=ROOT):
    root = Path(root).resolve()
    entries = inventory(root)
    if not entries:
        raise ValueError('Refusing to create an empty release manifest')
    content = ''.join(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + name + '\n'
                      for name, path in entries.items())
    write_text(root / MANIFEST, content)
    return verify(root)


if __name__ == '__main__':
    print(f'Updated {len(update())} release checksums; review the diff before committing.')
