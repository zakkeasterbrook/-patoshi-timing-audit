#!/usr/bin/env python3
"""Verify all 50,000 headers and reproduce each timing-test output offline."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from inputs import HEADER_SHA256, LABEL_SHA256, load_inputs, require
from timing import calculate
from reporting import write_evidence, compare_saved_evidence, REPRODUCED_EVIDENCE_FILES
from artifacts import output_transaction, write_bytes, write_text
from followup import run as reproduce_followup
from disputed_labels import run as reproduce_disputed_labels

VERSIONS = {
    "original": ("original.csv", "published_delta"),
    "timestamp_only": ("timestamp_only.csv", "child_delta"),
    "stated_rule": ("literal_rule.csv", "child_delta"),
}
EXPECTED = {
    "original": (1881, 1, 5, 4),
    "timestamp_only": (400, 10, 144, 134),
    "stated_rule": (754, 30, 276, 246),
}


def reproduce(output_dir):
    with output_transaction(output_dir, root=ROOT) as output_dir:
        records, labels, retargets, anchors = load_inputs()
        times = {r["height"]: r["timestamp"] for r in records}
        result = calculate(times, labels, 49_999)
        csv_checksums = {}
        for version, (filename, delta_key) in VERSIONS.items():
            rows = [(row["c"], row[delta_key]) for row in result["events"][version]]
            expected_path = ROOT / "results/expected" / filename
            with expected_path.open(encoding="utf-8", newline="") as handle:
                saved = list(csv.reader(handle))
            require(saved[0] == ["height", "header_timestamp_delta_seconds"], "Unexpected CSV header")
            require(rows == [(int(h), int(d)) for h, d in saved[1:]], "Saved native-PHP rows differ: " + version)
            summary = result["summary"][version]
            observed = tuple(summary[k] for k in ("n", "negative", "less_300", "zero_to_299"))
            require(observed == EXPECTED[version], "Headline-count mismatch: " + version)
            csv_text = "height,header_timestamp_delta_seconds\n" + "".join(f"{h},{d}\n" for h, d in rows)
            csv_bytes = csv_text.encode("ascii")
            require(csv_bytes == expected_path.read_bytes(), "Expected CSV bytes differ: " + version)
            write_bytes(output_dir / filename, csv_bytes)
            csv_checksums[filename] = hashlib.sha256(csv_bytes).hexdigest()
        require(result["final_unflushed_streak"] == [], "Final-flush effect differs from the audited input")
        diagnostics = write_evidence(output_dir, records, labels, result)
        require(diagnostics['original_sample_measured_C_minus_B'] == {
            'cases': 1881, 'negative': 121, 'below_300_including_negative': 713,
        }, 'Fixed-sample interval decomposition differs')
        require(diagnostics['removed_by_filter'] == 1481 and diagnostics['added_by_direct_selection'] == 354,
                'Selection decomposition differs')
        # Rebuild the RPC adapter's input from verified binary headers every run.
        write_text(output_dir / "headers_0_49999.json",
            json.dumps(records, separators=(",", ":")) + "\n", encoding="utf-8"
        )
        write_text(output_dir / "events.json",json.dumps(result, indent=2) + "\n", encoding="utf-8")
        followup = reproduce_followup(output_dir / 'followup')
        disputed = reproduce_disputed_labels(output_dir / 'disputed_labels')
        summary = {
            "status": "pass",
            "header_count": len(records),
            "height_range_inclusive": [0, 49_999],
            "raw_header_sha256": HEADER_SHA256,
            "canonical_classification_list_sha256": LABEL_SHA256,
            "retarget_boundaries_verified": len(retargets),
            "recorded_external_anchor_observations_matched": len(anchors),
            "header_validation": ["known mainnet genesis", "hash linkage", "declared proof of work", "difficulty transitions", "median time past"],
            "saved_native_php_outputs_match_every_python_row": True,
            "csv_sha256": csv_checksums,
            "counts": result["summary"],
            "no_final_flush_effect_on_this_dataset": True,
            "followup_status": followup['status'],
            "followup_summary": "followup/summary.json",
            "disputed_label_sensitivity_status": disputed['status'],
            "disputed_label_sensitivity_summary": "disputed_labels/summary.json",
            "unverified_followups": followup['not_reproduced_here'],
            "scope": "Fixed published labels; no independent attribution of miner identity",
        }
        write_text(output_dir / "summary.json",json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        compare_saved_evidence(output_dir, ROOT / 'results/reproduced', expected_files=REPRODUCED_EVIDENCE_FILES)
        return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build")
    args = parser.parse_args()
    print(json.dumps(reproduce(args.output_dir), indent=2))
