#!/usr/bin/env python3
"""Freshly fetch the pinned 4 MB header prefix without overwriting audit inputs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

from inputs import HEADER_BYTES, HEADER_SHA256, ROOT, require

URL = "https://download.electrum.org/blockchain_headers"


def check(output):
    request = urllib.request.Request(URL, headers={
        "User-Agent": "PatoshiTimingAudit/1.0", "Range": f"bytes=0-{HEADER_BYTES - 1}",
    })
    with urllib.request.urlopen(request, timeout=60) as response:
        status = response.status
        content_range = response.headers.get("Content-Range")
        if status == 206:
            require(content_range is not None and content_range.startswith(f"bytes 0-{HEADER_BYTES - 1}/"), "Unexpected HTTP range")
        else:
            require(status == 200, "Unexpected HTTP status")
        # A server may ignore Range and send 200: read only the known prefix.
        payload = response.read(HEADER_BYTES)
    digest = hashlib.sha256(payload).hexdigest()
    require(len(payload) == HEADER_BYTES, "Incomplete fresh header prefix")
    require(digest == HEADER_SHA256, "Fresh header archive does not match the pinned input")
    require(payload == (ROOT / "data/headers_0_49999.bin").read_bytes(), "Fresh and bundled raw headers differ")
    report = {"status": "pass", "source_url": URL, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": status, "content_range": content_range, "bytes": len(payload), "sha256": digest,
        "fresh_prefix_equals_bundled_headers": True}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/live_header_verification.json")
    print(json.dumps(check(parser.parse_args().output), indent=2))
