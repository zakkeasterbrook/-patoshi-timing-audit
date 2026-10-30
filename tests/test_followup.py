"""Scientific regression checks for fixed-label descriptive follow-up comparisons."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import followup


class FollowupTests(unittest.TestCase):
    def test_disjoint_outcome_categories_and_median(self):
        observed = followup.stats([-1, 0, 299, 300])
        self.assertEqual([observed[key] for key in (
            "negative", "zero", "positive_below_300", "at_least_300")], [1, 1, 1, 1])
        self.assertEqual(observed["below_300_including_negative"], 3)
        self.assertEqual(observed["median_seconds"], 149.5)

    def test_height_exclusions_apply_to_every_participating_height(self):
        for heights in ((540, 541), (1399, 1400), (1916, 1917), (1398, 1399, 1400)):
            with self.subTest(heights=heights):
                self.assertFalse(followup.later_eligible(heights))
        for heights in ((541, 542), (1398, 1399), (1917, 1918, 1919)):
            with self.subTest(heights=heights):
                self.assertTrue(followup.later_eligible(heights))

    def test_negative_preceding_gap_is_retained_and_600_is_excluded(self):
        def analyze(times):
            records = [{"height": h, "timestamp": t} for h, t in enumerate(times)]
            return followup.analyze(records, [1], bytes(80 * len(times)))[2]
        negative = analyze([1000, 999, 1298])
        self.assertEqual(negative["NPN_ab_below_600"][0]["ab_seconds"], -1)
        self.assertEqual(negative["NPN_ab_below_600"][0]["bc_seconds"], 299)
        self.assertEqual(negative["NPN_ab_300_to_599"], [])
        self.assertEqual(len(analyze([1000, 1599, 1899])["NPN_ab_below_600"]), 1)
        self.assertEqual(analyze([1000, 1600, 1899])["NPN_ab_below_600"], [])

    def test_standardization_weights_the_reference_distribution(self):
        def row(b, ab, bc):
            return {"b": b, "ab_seconds": ab, "bc_seconds": bc}
        ppn = [row(500, 300, 500), row(10500, 400, -1), row(10501, 400, 600)]
        npn = [row(500, 300, 299), row(501, 300, 600), row(10500, 400, -1)]
        summary, cells = followup.standardize(ppn, npn)
        self.assertAlmostEqual(summary["standardized_NPN_below_300_percent"], 100 * (1 / 3 * 1 / 2 + 2 / 3))
        self.assertAlmostEqual(summary["standardized_NPN_negative_percent"], 100 * 2 / 3)
        self.assertEqual([(r["b_era_start"], r["ab_band_start"]) for r in cells], [(0, 300), (10000, 400)])
        with self.assertRaisesRegex(ValueError, "no observations"):
            followup.standardize(ppn, npn[:2])

    def test_full_frozen_input_reproduces_rows_and_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            summary = followup.run(directory)
            output = Path(directory)
            self.assertEqual(summary["status"], "pass")
            self.assertEqual(summary["all_PN_pairs"]["cases"], 8900)
            with (output / "all_adjacent_pairs.csv").open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 49999)
            self.assertEqual([int(r["b"]) for r in rows], list(range(1, 50000)))
            with (output / "PPN_ab_below_600.csv").open(newline="") as handle:
                followup_rows = [(int(r["c"]), int(r["bc_seconds"])) for r in csv.DictReader(handle)]
            with (ROOT / "results/expected/literal_rule.csv").open(newline="") as handle:
                expected_rows = [(int(r["height"]), int(r["header_timestamp_delta_seconds"])) for r in csv.DictReader(handle)]
            self.assertEqual(followup_rows, expected_rows)
            with (output / "summary.json").open() as handle:
                self.assertEqual(json.load(handle), summary)
            previous_hashes = summary["csv_sha256"]
            repeated = followup.run(directory)
            self.assertEqual(previous_hashes, repeated["csv_sha256"])


if __name__ == "__main__":
    unittest.main()
