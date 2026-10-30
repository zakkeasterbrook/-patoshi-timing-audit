#!/usr/bin/env python3
"""Download the pinned upstream PHP source; refuse unrecognized bytes."""
import argparse
import hashlib
from pathlib import Path
import urllib.request

from inputs import SOURCE_SHA256, SOURCE_URL, require


def fetch(destination):
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "PatoshiTimingAudit/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        source = response.read(125_173)
    require(len(source) == 125_172, "Unexpected original-source size")
    require(hashlib.sha256(source).hexdigest() == SOURCE_SHA256, "Original-source SHA256 mismatch")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source)
    print(f"Verified pinned source: {target} ({len(source)} bytes; SHA256 {SOURCE_SHA256})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    fetch(parser.parse_args().destination)
