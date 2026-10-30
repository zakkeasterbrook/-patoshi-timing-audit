# Numerical evidence and execution records

The result files preserve individual observations as well as totals. All main
heights refer to Bitcoin mainnet 0–49,999 inclusive. Signed differences use
miner-supplied header timestamps; negative values remain included in strict
below-300 counts.

| Directory or file | Evidence |
|---|---|
| `expected/` | Frozen ordered core CSVs preserved from the supplied research package |
| `reproduced/` | Complete deterministic rows and summaries regenerated from verified frozen inputs |
| `current-verification/` | Retained local command logs, runtime reports and dated publication observations |
| `local-verification/`, `release-verification/` | Earlier package execution records for their own source snapshots |
| `status.json` | Release evidence index and analytical scope |

`python3 reproduce.py` regenerates the complete required reference inventory
under `build/` and compares its bytes with `reproduced/`. Missing or unexpected
reference files fail validation. The saved reference files are not calculation
inputs and are never used as an output destination.

Every one of the 49,999 adjacent pairs is retained in
`reproduced/followup/all_adjacent_pairs.csv`. Its label, nonce-band and
`later_eligible` columns reconstruct the pair comparisons without discarding
excluded cases. Comparison triples and all fifteen descriptive adjustment
cells are exported separately.

`reproduced/disputed_labels/` contains the source-supported sensitivity
removing 24,504; 35,573; and 35,599 from a copy of the list. Its 753 rows form
a separate sample. The original labels and main results are unchanged.
Historical criticisms of those labels remain source assertions.

The [data dictionary](../docs/evidence-index.md) defines every field and unit.
The [verification document](../docs/verification.md) distinguishes current
release checks from dated execution records. The
[analysis-scope record](../provenance/analysis_scope.json) specifies analyses
and identity claims that this release does not establish.
