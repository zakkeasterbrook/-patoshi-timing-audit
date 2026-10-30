#!/usr/bin/env python3
"""Verify that bundled labels equal the integer array in the pinned PHP source.

This command reads an externally retrieved source file; it neither evaluates
PHP nor distributes the upstream program. Fetch the source with
scripts/fetch_original_source.py first.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from inputs import ROOT, SOURCE_COMMIT, SOURCE_SHA256, SOURCE_URL, load_labels, require, validate_labels


def extract_labels(source_text):
    """Parse one literal integer-array assignment without executing source."""
    assignments = re.findall(r"\$patoshiBlocks\s*=\s*array\s*\((.*?)\)\s*;",
                             source_text, re.DOTALL)
    require(len(assignments) == 1, "Expected one literal Patoshi-label array")
    body = assignments[0]
    require(re.fullmatch(r"\s*[0-9]+(?:\s*,\s*[0-9]+)*\s*", body) is not None,
            "Patoshi-label array contains a non-integer literal or malformed separator")
    return validate_labels([int(token.strip()) for token in body.split(",")])


def check(source_path):
    source = Path(source_path).read_bytes()
    require(len(source) == 125_172, "Unexpected original-source size")
    digest = hashlib.sha256(source).hexdigest()
    require(digest == SOURCE_SHA256, "Original-source SHA256 mismatch")
    labels = extract_labels(source.decode("utf-8"))
    require(labels == load_labels(), "Bundled labels differ from the pinned source array")
    return {
        "status": "pass", "source_url": SOURCE_URL, "source_commit": SOURCE_COMMIT,
        "source_sha256": digest, "source_size_bytes": len(source),
        "label_count": len(labels), "minimum_height": min(labels), "maximum_height": max(labels),
        "source_array_equals_bundled_labels_in_order": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "build/original.php")
    parser.add_argument("--output", type=Path, default=ROOT / "build/source_label_verification.json")
    args = parser.parse_args()
    report = check(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
