# Evidence index and data dictionary

All main-analysis heights refer to Bitcoin mainnet, **0–49,999 inclusive**.
Order is by height, never by timestamp. All differences are signed seconds
between miner-supplied header timestamps. A negative value is retained, and
`<300` excludes exactly 300.

`results/reproduced/` contains committed reference evidence; `python3 reproduce.py`
stages regeneration, requires the complete fixed reference inventory, and
compares the bytes before publishing outputs in `build/`. Missing reference
files fail validation. Output paths containing symbolic links or hard-linked
files are rejected; publication is atomic per file, not across the complete
directory. Treat the records as inspectable outputs, not inputs to the numerical calculation.
[Result provenance](../results/README.md) distinguishes these files from the
preserved package execution logs.

## Inputs and authentication

| Path | Contract |
|---|---|
| [`data/headers_0_49999.bin`](../data/headers_0_49999.bin) | Exactly 4,000,000 bytes: 50,000 serialized 80-byte headers, beginning at genesis. Header `h` occupies `[80*h, 80*(h+1))`. Timestamp offset 68 is little-endian uint32 Unix seconds; compact target and nonce begin at offsets 72 and 76. |
| [`data/patoshi_heights.json`](../data/patoshi_heights.json) | Sorted array of 21,953 unique integer heights. P means membership; N means absence in this audit universe. Its canonical-content hash differs from the pretty-printed file byte hash. |
| [`provenance/label_provenance.json`](../provenance/label_provenance.json) | Source identity and fixed-label provenance. Verify the original array with `scripts/verify_source_labels.py` after a pinned source fetch. |
| [`provenance/independent_explorer_anchors.json`](../provenance/independent_explorer_anchors.json) | Ten saved observations covering five heights against two explorers. Offline agreement with these records is not a fresh network query. |

The [methodology](methodology.md) specifies genesis, hash byte order, links,
targets, proof of work, retargets and median-time-past checks. Input digests
and retrieval scope are documented in [provenance](provenance.md).

## Core outputs

All paths in the following table are under `results/reproduced/`; fresh
counterparts are written under `build/`.

| File | Granularity and interpretation |
|---|---|
| [`original.csv`](../results/reproduced/original.csv) | 1,881 legacy-selected child heights; emitted difference is C-minus-A. |
| [`timestamp_only.csv`](../results/reproduced/timestamp_only.csv) | 400 child heights after changing only the defective timestamp assignment; emitted difference is C-minus-B. |
| [`literal_rule.csv`](../results/reproduced/literal_rule.csv) | 754 adjacent PPN triples with AB `<600`; emitted difference is C-minus-B. |
| [`events.json`](../results/reproduced/events.json) | Every selected triple for each mode, summaries, excluded/added child-height sets, and final legacy tracker state. |
| [`mode_membership.csv`](../results/reproduced/mode_membership.csv) | Union of selected triples with all intervals and inclusion flags for the three modes. A missing mode flag is represented by `0`, not by deleting the case. |
| [`diagnostics.json`](../results/reproduced/diagnostics.json) | Fixed-sample interval correction, selection decomposition, original negative case, exactly-300 cases, interval identity and final tracker. |
| [`example_263_265.json`](../results/reproduced/example_263_265.json) | Complete minimal-example headers, hashes, integer/UTC timestamps, labels and computed differences. |
| [`summary.json`](../results/reproduced/summary.json) | Input digests, validation scope/counts, mode summaries, CSV digests and explicit pending follow-ups. |

The three compact core CSVs have exactly two columns:

| Column | Type and meaning |
|---|---|
| `height` | Integer child height C. A = C−2 and B = C−1. |
| `header_timestamp_delta_seconds` | Signed integer seconds: C−A in `original.csv`, C−B in the other two files. |

Event records and `mode_membership.csv` use these common fields:

| Field | Definition |
|---|---|
| `a`, `b`, `c` | Consecutive integer block heights A, B, C. |
| `pair_delta` | `timestamp(B) - timestamp(A)` in signed seconds. |
| `child_delta` | `timestamp(C) - timestamp(B)` in signed seconds. |
| `published_delta` | `timestamp(C) - timestamp(A)` in signed seconds, equal to `pair_delta + child_delta`. |
| `original`, `timestamp_only`, `stated_rule` | CSV-only integer flags `0`/`1` for membership in each mode. In JSON, mode membership is represented by the separate `events` arrays. |

Mode summaries distinguish `negative`, `zero`, `positive_below_300`, and
`at_least_300`. These disjoint counts sum to `n`. `less_300` includes the first
three categories; `zero_to_299` combines the middle two; `at_300` is a subset
of `at_least_300`. Rates must use the mode's own `n`.

## Follow-up triples

These five files share the same schema, under `results/reproduced/followup/`:

| File | Rows | Selection |
|---|---:|---|
| [`PPN_ab_below_600.csv`](../results/reproduced/followup/PPN_ab_below_600.csv) | 754 | PPN and AB `<600`; negative AB is permitted. |
| [`NPN_ab_below_600.csv`](../results/reproduced/followup/NPN_ab_below_600.csv) | 2,780 | NPN and AB `<600`; negative AB is permitted. |
| [`PPN_ab_300_to_599.csv`](../results/reproduced/followup/PPN_ab_300_to_599.csv) | 727 | PPN and `300 ≤ AB <600`. |
| [`NPN_ab_300_to_599.csv`](../results/reproduced/followup/NPN_ab_300_to_599.csv) | 1,192 | NPN and `300 ≤ AB <600`. |
| [`PPN_ab_below_600_later_sensitivity.csv`](../results/reproduced/followup/PPN_ab_below_600_later_sensitivity.csv) | 695 | First PPN selection with the later-period sensitivity applied to the whole triple. |

`a`, `b`, `c` are the consecutive heights. `a_timestamp`, `b_timestamp`, and
`c_timestamp` are integer Unix seconds decoded from the headers. `labels`
is `PPN` or `NPN`. `ab_seconds` and `bc_seconds` are signed preceding and
following differences. `b_era_start` is `10000 * floor(b/10000)`;
`ab_band_start` is `100 * floor(ab_seconds/100)`, including negative bands
where present. `later_eligible` is the CSV string `True` or `False`.

The later-period flag requires every participating height to be at least 541
and no height to fall in 1,400–1,916 inclusive. It is an operational sensitivity
choice, not an empirically established change point.

## All adjacent pairs and nonce groups

[`all_adjacent_pairs.csv`](../results/reproduced/followup/all_adjacent_pairs.csv)
has **49,999 rows**, one for each pair `(a, b)` with `b = a + 1`. It retains
every pair, including those excluded from a later-period diagnostic.

| Column | Type and meaning |
|---|---|
| `a`, `b` | Integer parent and child heights. These are two-block pair names, not the three-block A/B/C roles. |
| `a_timestamp`, `b_timestamp` | Integer Unix seconds. |
| `delta_seconds` | Signed `b_timestamp - a_timestamp`. |
| `label_pair` | One of `PP`, `PN`, `NP`, `NN`, using the fixed original list. |
| `nonce_byte_a`, `nonce_byte_b` | Integers 0–255 from each serialized header's byte at offset 76. |
| `nonce_band_pair` | One of `RR`, `RO`, `OR`, `OO`. R means byte value 0–9 or 19–58 inclusive; O is its complement. |
| `later_eligible` | CSV string `True`/`False` after applying the pair version of the later-period exclusions. |

The first serialized nonce byte is the low byte of the little-endian numeric
nonce. Pair grouping by this byte does not use P/N labels, but related features
may have informed the original classifications. It therefore does not
independently validate them or establish miner identity.

## Descriptive adjustment cells

[`common_range_adjustment_cells.csv`](../results/reproduced/followup/common_range_adjustment_cells.csv)
contains all **15 cells** in the common AB range. `b_era_start` and
`b_era_end_inclusive` identify a 10,000-height era of parent B;
`ab_band_start` and `ab_band_end_inclusive` identify a 100-second band.

`ppn_cases`, `npn_cases` are integer cell denominators. The respective
`*_negative` and `*_below_300` columns count following BC differences; the
below-300 count includes negatives. `ppn_weight` is a unitless fraction:
`ppn_cases / total common-range PPN cases`.

Reconstruct the standardized short-gap fraction as
`sum(ppn_weight * npn_below_300 / npn_cases)`; use `npn_negative` for the
negative-gap fraction. Multiply by 100 for a percentage. This weights NPN
cell rates to PPN composition. It is a descriptive calculation, not a causal
estimate or a significance test. The parent-B era definition is an explicit
reconstruction because the earlier follow-up script was not supplied.

[`followup/summary.json`](../results/reproduced/followup/summary.json) groups the
comparison statistics, pair partition, later-period diagnostics, nonce counts,
standardization, definitions, input/output digests and missing analyses.
Its `below_300_including_negative` field corresponds to core `less_300`;
`cases` corresponds to core `n`. `median_seconds` is the ordinary sample median.

## Disputed-label sensitivity

[`provenance/disputed_labels.json`](../provenance/disputed_labels.json) records
the exact public source comments for positive heights **24,504, 35,573 and
35,599**, including authors, comment times, URLs and inference limits. These
identities were recovered from the prior-art record and the cited discussion.
They are not labels chosen to force a numerical target. Historical co-spend
and ExtraNonce assertions remain source assertions; this audit does not
independently revalidate those claims.

[`disputed_labels/rows.csv`](../results/reproduced/disputed_labels/rows.csv)
contains **753 rows** selected after removing only the three positive labels
from a separate copy of the list. The primary labels remain unchanged.
N in this sensitivity means absence from the revised list, including the
three removed heights. The same consecutive PPN selection and strict AB
`<600` criterion apply; BC is the emitted difference.

| Columns | Type and meaning |
|---|---|
| `a`, `b`, `c` | Consecutive integer heights. |
| `a_timestamp`, `b_timestamp`, `c_timestamp` | Integer Unix seconds decoded from the frozen headers. |
| `a_block_hash`, `b_block_hash`, `c_block_hash` | Conventional displayed 64-character hexadecimal header hashes. |
| `ab_seconds`, `bc_seconds` | Signed preceding and following timestamp differences. |
| `original_labels` | Three-character label string using the original frozen positive set. |
| `sensitivity_labels` | Three-character label string using the set after the three removals; selected rows satisfy `PPN`. |

[`disputed_labels/summary.json`](../results/reproduced/disputed_labels/summary.json)
contains both `original_stated_rule` and `sensitivity` statistics, original and
revised label counts, exact removed heights, added/removed case child heights,
definitions, input digests, source-record path and the CSV digest. Its
statistics use the same disjoint categories as the other follow-up summaries.

The revised result is **753 cases, 30 negative and 276 below 300 seconds
(36.65%)**; the primary direct result is 754 cases, 30 negative and 276 below
300 (36.60%). Below-300 counts include negatives, and the denominators differ.
Only child height 24,505 leaves the sample; no cases enter. This measures
classification sensitivity, not the validity of the historical criticisms.

## Portable candidate identity

`scripts/build_release.py` accepts a version such as `1.0.0-rc.1` and requires
a clean, committed checkout with exact manifested-file coverage. It reads
committed blobs, verifies their digests and writes these generated artifacts
under `build/release/`:

| Artifact | Contract |
|---|---|
| `Patoshi_Timing_Audit_v<version>.zip` | Complete manifested source tree under `patoshi-timing-audit/`, plus generated `RELEASE_MANIFEST.json`. Members are sorted with fixed 1980-01-01 container timestamps and `ZIP_STORED` compression mode. |
| `SHA256SUMS.txt` | Archive byte digest and filename. This generated artifact checksum is separate from the repository-root source-file manifest of the same name. |
| `release.json` | Packaging status, version, exact Git commit, archive name/size/digest, source-file count, generated metadata name and explicit GitHub-release-creation flag. |

Inside the archive, `RELEASE_MANIFEST.json` records `format_version`, project,
repository, version, exact `git_commit`, source commit time, packaging and
verification scopes, and a `files` mapping of source names to `sha256` and
`bytes`. Source commit time and fixed ZIP container timestamps are not claims
about public release time. This generated manifest is not an additional input
to the source-file checksum inventory.

Archive construction verifies byte identity and completeness, not a new
scientific execution or native-PHP run. The configured CI packaging job depends
on offline/native verification. Consult the actual run for its execution state;
an archive or uploaded CI artifact does not establish a tagged GitHub Release.

## Execution records and unverified inputs

[`results/current-verification/`](../results/current-verification/) contains
command/runtime logs and observed publication records. Earlier
`results/local-verification/` and `results/release-verification/` are preserved
archive evidence for their own snapshots; folder names alone do not establish
fresh execution or a GitHub release. Check exact commits and outcomes in
[verification status](verification.md).

[`provenance/pending_inputs.json`](../provenance/pending_inputs.json) identifies
the missing frozen Bitquery CSV. That classification-sensitivity calculation
is not completed here. Its reported source checksum is an unverified
acquisition target, not a verified local input.
Any future high-grade Bitquery analysis must preserve medium/low positives as
unknown and use explicitly negative source rows as N; genesis is unclassified.
