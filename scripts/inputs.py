"""Pinned inputs shared by the offline and native-PHP reproduction commands."""
import hashlib
import json
from pathlib import Path

from verify_headers import verify

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "66ee906b28ca13269d6f71d63f848973a1b747a2"
SOURCE_URL = (
    "https://raw.githubusercontent.com/jlopp/bitcoin-utils/"
    + SOURCE_COMMIT + "/findNonPatoshiDeltasAfterFastPatoshiBlocks.php"
)
SOURCE_SHA256 = "104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119"
HEADER_SHA256 = "b9e200ba15c904e05283461469d5582a9580df15ff842436576a7490454b03ec"
LABEL_SHA256 = "33c9927845ccd3016fb37bc2b860cfe7a3fea22522c67649d72c6dc50e9ae8e1"
HEADER_BYTES = 50_000 * 80


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_labels(labels, maximum_height=49_999):
    """Validate height labels without coercing booleans, strings or floats.

    Keep source ordering explicit: sorting or deduplicating malformed input
    would conceal a changed classification list before its digest is checked.
    """
    require(isinstance(labels, list), "Classification list must be a JSON array")
    require(all(type(height) is int for height in labels),
            "Classification heights must be integers, not booleans or other types")
    require(all(0 <= height <= maximum_height for height in labels),
            "Classification height outside the audited range")
    require(len(labels) == len(set(labels)), "Duplicate classification height")
    require(labels == sorted(labels), "Classification heights must be in increasing order")
    return labels


def load_labels(path=None):
    path = ROOT / "data/patoshi_heights.json" if path is None else Path(path)
    labels = validate_labels(json.loads(path.read_text(encoding="utf-8")))
    canonical = json.dumps(labels, separators=(",", ":")).encode("ascii")
    require(hashlib.sha256(canonical).hexdigest() == LABEL_SHA256, "Classification-list SHA256 mismatch")
    require(len(labels) == 21_953, "Unexpected classification-list size")
    return labels


def load_inputs():
    # The historical header verifier deliberately uses assertions. Never allow
    # a Python optimization flag to disable its checks silently.
    require(__debug__, "Run without -O or PYTHONOPTIMIZE; header checks require assertions")
    payload = (ROOT / "data/headers_0_49999.bin").read_bytes()
    require(len(payload) == HEADER_BYTES, "Unexpected raw-header length")
    require(hashlib.sha256(payload).hexdigest() == HEADER_SHA256, "Raw-header SHA256 mismatch")
    records, retargets = verify(payload)
    labels = load_labels()
    anchors = json.loads((ROOT / "provenance/independent_explorer_anchors.json").read_text(encoding="utf-8"))
    require(len(anchors) == 10, "Expected ten recorded explorer anchor observations")
    for anchor in anchors:
        record = records[anchor["height"]]
        require(anchor["header_hex"] == record["header_hex"], "Recorded anchor header differs")
        require(anchor["block_hash"] == record["block_hash"], "Recorded anchor hash differs")
    return records, labels, retargets, anchors
