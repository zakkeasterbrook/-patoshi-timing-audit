#!/usr/bin/env python3
"""Reproduce descriptive timing/nonce comparisons from the frozen original labels.

No miner-identity or causal inference is performed. The independent classification
sensitivity requires its own source snapshot and is not invented when absent.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics

from inputs import HEADER_SHA256, LABEL_SHA256, ROOT, load_inputs, require
from reporting import compare_saved_evidence

NONCE_BAND = frozenset(range(10)) | frozenset(range(19, 59))
PAIR_FIELDS = (
    "a", "b", "a_timestamp", "b_timestamp", "delta_seconds", "label_pair",
    "nonce_byte_a", "nonce_byte_b", "nonce_band_pair", "later_eligible",
)
TRIPLE_FIELDS = (
    "a", "b", "c", "a_timestamp", "b_timestamp", "c_timestamp", "labels",
    "ab_seconds", "bc_seconds", "b_era_start", "ab_band_start", "later_eligible",
)


def later_eligible(heights):
    """Operational sensitivity: all heights >=541; none within 1400..1916."""
    return min(heights) >= 541 and not any(1400 <= h <= 1916 for h in heights)


def stats(values):
    """Disjoint counts keep negative/zero/positive intervals distinguishable."""
    values = list(values)
    n = len(values)
    short = sum(v < 300 for v in values)
    return {
        "cases": n,
        "negative": sum(v < 0 for v in values),
        "zero": sum(v == 0 for v in values),
        "positive_below_300": sum(0 < v < 300 for v in values),
        "zero_to_299": sum(0 <= v < 300 for v in values),
        "below_300_including_negative": short,
        "at_300": sum(v == 300 for v in values),
        "at_least_300": sum(v >= 300 for v in values),
        "below_300_percent": short * 100 / n if n else None,
        "negative_percent": sum(v < 0 for v in values) * 100 / n if n else None,
        "median_seconds": statistics.median(values) if n else None,
        "minimum_seconds": min(values) if n else None,
        "maximum_seconds": max(values) if n else None,
    }


def standardize(ppn, npn):
    """Weight each NPN cell rate by the corresponding PPN cell proportion.

    Only 300<=AB<600 samples enter. Cells use B's height in 10,000-height eras
    and AB's 100-second band. No extrapolation is made across empty NPN cells.
    """
    reference, comparison = {}, {}
    for rows, cells in ((ppn, reference), (npn, comparison)):
        for row in rows:
            require(300 <= row["ab_seconds"] < 600, "Standardization requires 300<=AB<600")
            key = (row["b"] // 10_000 * 10_000, row["ab_seconds"] // 100 * 100)
            cells.setdefault(key, []).append(row["bc_seconds"])
    require(bool(ppn), "Cannot standardize an empty PPN sample")
    adjusted_short, adjusted_negative, rows = 0.0, 0.0, []
    for era, band in sorted(reference):
        key = (era, band)
        require(key in comparison, "NPN has no observations for a PPN adjustment cell")
        p, n = stats(reference[key]), stats(comparison[key])
        weight = p["cases"] / len(ppn)
        adjusted_short += weight * n["below_300_including_negative"] / n["cases"]
        adjusted_negative += weight * n["negative"] / n["cases"]
        rows.append({
            "b_era_start": era, "b_era_end_inclusive": era + 9999,
            "ab_band_start": band, "ab_band_end_inclusive": band + 99,
            "ppn_cases": p["cases"], "ppn_negative": p["negative"],
            "ppn_below_300": p["below_300_including_negative"],
            "npn_cases": n["cases"], "npn_negative": n["negative"],
            "npn_below_300": n["below_300_including_negative"],
            "ppn_weight": weight,
        })
    return {
        "method": "Direct standardization of NPN cell rates to PPN cell proportions",
        "preceding_gap_seconds": "300 <= AB < 600",
        "era_height": "B (the P parent)", "era_width_heights": 10_000,
        "preceding_gap_band_width_seconds": 100,
        "reference_cases": len(ppn), "comparison_cases": len(npn),
        "represented_cells": len(rows),
        "standardized_NPN_below_300_percent": adjusted_short * 100,
        "standardized_NPN_negative_percent": adjusted_negative * 100,
        "PPN_below_300_percent": stats(row["bc_seconds"] for row in ppn)["below_300_percent"],
        "PPN_negative_percent": stats(row["bc_seconds"] for row in ppn)["negative_percent"],
        "pooled_NPN_below_300_percent": stats(row["bc_seconds"] for row in npn)["below_300_percent"],
        "pooled_NPN_negative_percent": stats(row["bc_seconds"] for row in npn)["negative_percent"],
        "interpretation": "Exploratory descriptive comparison; not a causal estimate or significance test",
    }, rows


def analyze(records, labels, payload):
    """Return computed summaries plus every pair and each retained triple group."""
    require(len(payload) == len(records) * 80, "Expected one serialized 80-byte header per record")
    require([r["height"] for r in records] == list(range(len(records))), "Records must be height-contiguous from genesis")
    require(all(type(h) is int and 0 <= h < len(records) for h in labels), "Invalid label height")
    require(len(labels) == len(set(labels)), "Duplicate labels")
    listed = set(labels)
    times = [r["timestamp"] for r in records]
    pair_rows = []
    for b in range(1, len(records)):
        a = b - 1
        byte_a, byte_b = payload[a * 80 + 76], payload[b * 80 + 76]
        pair_rows.append({
            "a": a, "b": b, "a_timestamp": times[a], "b_timestamp": times[b],
            "delta_seconds": times[b] - times[a],
            "label_pair": ("P" if a in listed else "N") + ("P" if b in listed else "N"),
            "nonce_byte_a": byte_a, "nonce_byte_b": byte_b,
            "nonce_band_pair": ("R" if byte_a in NONCE_BAND else "O") + ("R" if byte_b in NONCE_BAND else "O"),
            "later_eligible": later_eligible((a, b)),
        })
    groups = {name: [] for name in (
        "PPN_ab_below_600", "NPN_ab_below_600", "PPN_ab_300_to_599",
        "NPN_ab_300_to_599", "PPN_ab_below_600_later_sensitivity",
    )}
    for c in range(2, len(records)):
        a, b = c - 2, c - 1
        ab, bc = times[b] - times[a], times[c] - times[b]
        if b not in listed or c in listed or ab >= 600:
            continue
        pattern = "PPN" if a in listed else "NPN"
        row = {
            "a": a, "b": b, "c": c, "a_timestamp": times[a],
            "b_timestamp": times[b], "c_timestamp": times[c], "labels": pattern,
            "ab_seconds": ab, "bc_seconds": bc,
            "b_era_start": b // 10_000 * 10_000,
            "ab_band_start": ab // 100 * 100,
            "later_eligible": later_eligible((a, b, c)),
        }
        groups[pattern + "_ab_below_600"].append(row)
        if 300 <= ab:
            groups[pattern + "_ab_300_to_599"].append(row)
        if pattern == "PPN" and row["later_eligible"]:
            groups["PPN_ab_below_600_later_sensitivity"].append(row)
    comparisons = {}
    for name, rows in groups.items():
        comparisons[name] = stats(row["bc_seconds"] for row in rows)
        comparisons[name]["negative_preceding_AB"] = sum(row["ab_seconds"] < 0 for row in rows)
    all_pairs = {key: stats(row["delta_seconds"] for row in pair_rows if row["label_pair"] == key)
                 for key in ("PP", "PN", "NP", "NN")}
    later_pp = [row for row in pair_rows if row["label_pair"] == "PP" and row["later_eligible"]]
    later_stats = stats(row["delta_seconds"] for row in later_pp)
    later_stats["at_least_312"] = sum(row["delta_seconds"] >= 312 for row in later_pp)
    later_stats["below_312_rows"] = [row for row in later_pp if row["delta_seconds"] < 312]
    raw_band = [payload[h * 80 + 76] in NONCE_BAND for h in range(len(records))]
    nonce = {
        "serialized_header_byte_offset": 76,
        "equivalence": "Low byte of the little-endian numeric nonce",
        "inclusive_band": [[0, 9], [19, 58]],
        "listed_inside": sum(raw_band[h] for h in labels),
        "unlisted_inside": sum(raw_band[h] for h in range(len(records)) if h not in listed),
        "unlisted_outside": sum(not raw_band[h] for h in range(len(records)) if h not in listed),
        "all_inside": sum(raw_band),
        "all_inside_percent": sum(raw_band) * 100 / len(records) if records else None,
        "listed_matches_by_serialized_nonce_byte": [
            sum(payload[h * 80 + 76 + offset] in NONCE_BAND for h in labels)
            for offset in range(4)
        ],
        "later_pairs": {
            key: stats(row["delta_seconds"] for row in pair_rows
                       if row["later_eligible"] and row["nonce_band_pair"] == key)
            for key in ("RR", "OO")
        },
        "interpretation": "Descriptive raw-header structure; no ExtraNonce reconstruction or miner identification",
    }
    summary = {
        "header_count": len(records), "label_count": len(labels),
        "comparisons": comparisons, "all_adjacent_pairs": all_pairs,
        "all_PN_pairs": all_pairs["PN"], "later_PP_pairs": later_stats,
        "nonce": nonce,
        "definitions": {
            "P": "Membership in the frozen published list; N is nonmembership",
            "R": "Raw serialized nonce byte at offset 76 inside 0..9 or 19..58; O is outside",
            "following_gap": "Header timestamp(C) - header timestamp(B), in seconds",
            "strict_threshold": "Below 300 includes negative values and excludes exactly 300",
            "later_sensitivity": "Every participating height >=541 and none in 1400..1916 inclusive",
            "scope": "Fixed historical labels; header timestamps are not observed elapsed mining times",
        },
    }
    return summary, pair_rows, groups


def verify_regression_targets(summary):
    """Compare freshly derived results with recovered reports, never force them."""
    targets = {
        "PPN_ab_below_600": (754, 30, 276, 429.5),
        "NPN_ab_below_600": (2780, 55, 1042, 421.5),
        "PPN_ab_300_to_599": (727, 30, 263, 431),
        "NPN_ab_300_to_599": (1192, 35, 445, 436),
        "PPN_ab_below_600_later_sensitivity": (695, 30, 248, None),
    }
    keys = ("cases", "negative", "below_300_including_negative")
    for name, expected in targets.items():
        observed = summary["comparisons"][name]
        require(tuple(observed[k] for k in keys) == expected[:3], "Follow-up regression mismatch: " + name)
        if expected[3] is not None:
            require(observed["median_seconds"] == expected[3], "Median mismatch: " + name)
    require(summary["comparisons"]["NPN_ab_below_600"]["negative_preceding_AB"] == 36, "NPN negative preceding-gap mismatch")
    pairs = summary["all_adjacent_pairs"]
    for name, expected in {"PP": (13053, 0, 139), "PN": (8900, 398, 3215),
                           "NP": (8900, 72, 2497), "NN": (19146, 224, 8238)}.items():
        require(tuple(pairs[name][k] for k in keys) == expected, "Pair regression mismatch: " + name)
    require(sum(p["cases"] for p in pairs.values()) == 49999, "Adjacent pair partition mismatch")
    later = summary["later_PP_pairs"]
    require((later["cases"], later["at_least_312"]) == (12240, 12239), "Later PP count mismatch")
    require([(r["a"], r["b"], r["delta_seconds"]) for r in later["below_312_rows"]] == [(24503, 24504, 65)], "Later PP exception mismatch")
    nonce = summary["nonce"]
    require(tuple(nonce[k] for k in ("listed_inside", "unlisted_inside", "unlisted_outside", "all_inside")) == (21953, 5655, 22392, 27608), "Nonce-band count mismatch")
    require(nonce["listed_matches_by_serialized_nonce_byte"] == [21953, 4309, 4280, 4328], "Nonce-byte-order mismatch")
    for name, expected in {"RR": (16477, 93, 1424, 887), "OO": (12124, 141, 5204, 367)}.items():
        actual = nonce["later_pairs"][name]
        require(tuple(actual[k] for k in keys + ("median_seconds",)) == expected, "Raw-band pair mismatch: " + name)
    adjusted = summary["common_range_standardization"]
    require(adjusted["represented_cells"] == 15, "Adjustment-cell count mismatch")
    require(round(adjusted["standardized_NPN_below_300_percent"], 2) == 37.88, "Standardized short-gap mismatch")
    require(round(adjusted["standardized_NPN_negative_percent"], 2) == 5.56, "Standardized negative-gap mismatch")


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(output_dir=None):
    """Validate frozen inputs, reproduce complete rows, then check recovered totals."""
    output_dir = (Path(output_dir) if output_dir is not None else ROOT / "build/followup").resolve()
    require(output_dir != ROOT and (ROOT not in output_dir.parents or output_dir.is_relative_to(ROOT / 'build')),
            'Write outputs to build/ or outside the checkout; frozen project files must not be overwritten')
    output_dir.mkdir(parents=True, exist_ok=True)
    records, labels, _, _ = load_inputs()
    payload = (ROOT / "data/headers_0_49999.bin").read_bytes()
    summary, pair_rows, groups = analyze(records, labels, payload)
    adjustment, cells = standardize(groups["PPN_ab_300_to_599"], groups["NPN_ab_300_to_599"])
    summary["common_range_standardization"] = adjustment
    summary["input_sha256"] = {"headers": HEADER_SHA256, "canonical_labels": LABEL_SHA256}
    summary["not_reproduced_here"] = {
        "Bitquery_classification_sensitivity": "Requires the separate frozen Bitquery CSV; not supplied in the recovered release package",
        "three_disputed_label_removal": "Exact three heights and historical source were not supplied; no guessed removals applied",
    }
    write_csv(output_dir / "all_adjacent_pairs.csv", pair_rows, PAIR_FIELDS)
    for name, rows in groups.items():
        write_csv(output_dir / (name + ".csv"), rows, TRIPLE_FIELDS)
    write_csv(output_dir / "common_range_adjustment_cells.csv", cells, tuple(cells[0]))
    generated_csv = ["all_adjacent_pairs.csv", "common_range_adjustment_cells.csv"]
    generated_csv.extend(name + ".csv" for name in groups)
    summary["csv_sha256"] = {
        name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest()
        for name in sorted(generated_csv)
    }
    # Preserve genuine computed evidence even when a recovered report disagrees.
    try:
        verify_regression_targets(summary)
    except ValueError as exc:
        summary["status"] = "regression_mismatch"
        summary["regression_error"] = str(exc)
        (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline='\n')
        raise
    summary["status"] = "pass"
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline='\n')
    compare_saved_evidence(output_dir, ROOT / 'results/reproduced/followup')
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build/followup")
    print(json.dumps(run(parser.parse_args().output_dir), indent=2))
