# Review the audit from claim to bytes

The main claim is narrow: the published program does not compute its stated
three-block timing statistic. This guide separates verification of that code
correction from questions about miner classification or historical behavior.

## Start with a clean checkout

Record the full commit being reviewed, then run from the repository root with
Python 3.10 or newer:

```sh
git rev-parse HEAD
python3 scripts/verify_manifest.py
python3 reproduce.py
python3 scripts/check_direct.py
python3 -m unittest discover -s tests -v
```

`reproduce.py` uses frozen local inputs, stages fresh evidence, compares the
complete required reference inventory, and publishes outputs to `build/` only
after successful validation. Missing reference files fail instead of silently
reducing the comparison. Output paths containing symbolic links or hard-linked
files are rejected. Each published file is replaced atomically; publication
of the whole directory is not claimed to be one atomic filesystem operation.
A count match alone is insufficient: the ordered core CSV bytes and retained
pair/triple evidence must also agree.
Core reproduction does not need a Bitcoin node, credentials, a live explorer,
or plotting dependencies. Run without Python optimization flags. The test
runner reports native tests as skipped unless their prerequisites are set.

Use the [evidence index](evidence-index.md) to inspect the files and fields
behind each reported result.

## Questions to answer independently

| Review question | Evidence and decisive check |
|---|---|
| Are these the documented inputs? | Inspect [data provenance](provenance.md), verify the frozen digests, and review `scripts/verify_headers.py`. The main input contains exactly 50,000 consecutive 80-byte mainnet headers. |
| Is the classification list the published one? | Fetch the pinned source, then run `scripts/verify_source_labels.py`. It checks the source size/digest before comparing every extracted height in order. Source acquisition is separate from offline reproduction. |
| Does the original source exhibit the defect? | Inspect the immutable source and [minimal patch](../provenance/timestamp_fix.patch). B is fetched, but B's time variable reads A's response. Review native execution and adapter tests rather than relying only on Python emulation. |
| Does the direct rule implement the stated predicate? | For height-adjacent A, B, C, require labels PPN and `tB - tA < 600`; emit `tC - tB`. Inspect `scripts/timing.py` and the separately written raw-byte enumeration in `scripts/check_direct.py`. |
| Are interval and selection effects separated? | Use `diagnostics.json`, `mode_membership.csv`, and all three core CSVs. The assignment-only version retains the legacy sequence tracker; the direct rule changes sequence selection too. |
| Do the follow-up tables follow from their stated groups? | Recount the exported triples, all adjacent pairs, and adjustment cells. Check the parent-B era definition and operational later-period exclusions in [methodology](methodology.md). |
| Is classification sensitivity separate from the primary correction? | Inspect [the cited disputed-label provenance](../provenance/disputed_labels.json), then trace the primary and revised selections in `results/reproduced/disputed_labels/`. The original 21,953-label input remains unchanged. |

These computations are cross-checks written separately; they are not external
human peer review. Verify their assumptions and shared inputs as well as their
agreement.

## Trace a case before reading aggregate percentages

Run:

```sh
python3 scripts/demo.py
```

Then inspect
[`example_263_265.json`](../results/reproduced/example_263_265.json). It contains
the three integer timestamps, computed hashes, serialized headers, fixed labels,
and UTC displays. For height `h`, the corresponding header is the 80-byte slice
`[80*h, 80*(h+1))` of `data/headers_0_49999.bin`.

Find child height 265 in each core CSV and in `mode_membership.csv`. The
preceding difference is 559 seconds. The intended following difference is 71;
the published interval is 630. Check the identity `AC = AB + BC` from the
timestamps instead of treating the displayed arithmetic as an input.

For boundaries and diagnostic cases, inspect child heights 9,656 and 24,143.
Exactly 300 seconds does not enter a strict below-300 count. The original
negative case at 24,143 fails the intended preceding-gap filter; it is not
evidence that the corrected sample must contain that same case.

## Recount without mixing samples

For each mode, use its own denominator and its emitted interval. The original
mode reports C-minus-A; the corrected modes report C-minus-B. The summary's
disjoint categories are negative, zero, positive below 300, and at least 300.
Their sum must equal the selected count. The below-300 total overlaps these
categories: it includes negative and zero values and excludes exactly 300.

Keep these comparisons distinct:

1. Changing only the interval on the original fixed sample.
2. Applying the intended preceding-gap filter to legacy-selected cases.
3. Enumerating all qualifying adjacent PPN triples directly.

The complete rows allow disagreements in selection to be located even when
aggregate totals happen to agree.

## Trace the disputed-label sensitivity separately

The existing prior-art log and a fresh inspection of
[discussion 465](https://github.com/janoside/btc-rpc-explorer/discussions/465)
identify disputed positive labels **24,504, 35,573 and 35,599**. Review the exact
comments and their inference limits in
[`provenance/disputed_labels.json`](../provenance/disputed_labels.json).
The historical criticisms are source assertions, not newly validated miner
attributions or transaction revalidation.

`scripts/disputed_labels.py` removes only these heights from a separate label
set, treats them as N for that sensitivity, and independently enumerates the
same direct PPN rule. The primary list and its results remain unchanged.
The sensitivity yields **753 cases, 30 negative differences and 276 below
300 seconds (36.65%)**. Its denominator differs from the primary direct rule's
754; both below-300 totals include negatives.

Trace child height 24,505 in `results/reproduced/literal_rule.csv` and confirm
it is absent from `results/reproduced/disputed_labels/rows.csv`. The sensitivity
summary records that single removed child height and no added cases. Inspect
the remaining rows' hashes, timestamps and both label strings rather than
inferring equivalence from unchanged negative/short-gap totals.

## Fresh PHP execution

With a trusted PHP 8 CLI available, the following commands freshly execute the
pinned source. The environment assignments shown here use POSIX shell syntax:

```sh
python3 scripts/fetch_original_source.py build/original.php
python3 scripts/verify_source_labels.py --source build/original.php
python3 scripts/run_native.py --php php --source build/original.php
PATOSHI_TEST_PHP=php PATOSHI_TEST_SOURCE="$PWD/build/original.php" \
  python3 -m unittest discover -s tests -v
```

Substitute the actual interpreter path when needed. Inspect the resulting
runtime report, CSV-byte agreement, adapter lookup tests and synthetic
sequence/threshold fixtures. Reading an archived PHP report is a different
check from executing PHP now. The offline adapter does not reconstruct the
author's complete 2022 runtime or Bitcoin Core environment.

## What remains outside this result

P and N describe membership in one supplied list, not established identities.
The follow-up comparisons are descriptive; their groups are not randomized,
and the adjustment is not a causal estimate. Nonce-byte grouping does not
reconstruct ExtraNonce slopes or independently validate the attribution list.

Header validation does not revalidate transactions, scripts, or historical
receiving-node clocks. Header timestamps are not independently measured mining
durations. Short following gaps can coexist with a miner's pause.

The separate Bitquery frozen CSV is still required for that pending
classification sensitivity. See
[`pending_inputs.json`](../provenance/pending_inputs.json). Its reported
targets are not fresh results in this repository.

For execution freshness and publication, consult [verification status](verification.md)
and the actual hosted run for the commit reviewed. Archived package logs,
current local execution, hosted CI, and a tagged release establish different
things. Report a discrepancy with its commit, command, runtime, case heights,
expected predicate and observed result as described in [CONTRIBUTING.md](../CONTRIBUTING.md).

## Inspect a portable candidate

From a clean, committed checkout, build a candidate with:

```sh
python3 scripts/build_release.py --version 1.0.0-rc.1
```

The builder requires the complete source-file inventory and SHA-256 manifest
to match the committed Git tree. It produces a sorted `ZIP_STORED` archive,
checksum file and packaging report under `build/release/`; the archive contains
`RELEASE_MANIFEST.json` with the exact commit and source-file digests. Fixed
1980 container timestamps are reproducibility constants, not publication dates.
Changing the version or commit changes the artifact identity.

The configured CI matrix covers Python 3.10, 3.12 and 3.14 on Linux and Python
3.12 on Windows. Its candidate-packaging job depends on both offline and native
verification jobs. Inspect the actual outcome for the reviewed commit; workflow
configuration alone does not establish that these new jobs have run. Building
an archive verifies artifact identity and does not independently rerun the
scientific analysis or create a GitHub Release.
