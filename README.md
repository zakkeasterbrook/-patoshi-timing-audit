# Patoshi Timing Audit

**Zakk Easterbrook · Release candidate 1.0.0 · 30 October 2026**

A reproducible correction to the timing test linked from Jameson Lopp’s 2022 article, [*Was Satoshi a Greedy Miner?*](https://blog.lopp.net/was-satoshi-a-greedy-miner/).

**The published program measures the wrong interval and omits eligible sequences. Implementing the stated test produces 276 timestamp gaps below 300 seconds among 754 cases (36.60%), compared with 5 among 1,881 cases (0.27%) from the original program.** The samples differ because the correction changes eligibility as well as the measured interval.

[Understand the finding](docs/plain-english.md) · [Inspect the correction](docs/technical-note.md) · [Verify the evidence](docs/verification.md) · [Review the limitations](docs/context.md)

## See the error in 30 seconds

Three consecutive heights illustrate it:

| Block | Supplied label | Header timestamp (UTC) |
|---|---|---|
| 263 — A | P | 2009-01-13 00:10:21 |
| 264 — B | P | 2009-01-13 00:19:40 |
| 265 — C | N | 2009-01-13 00:20:51 |

A→B is **559 seconds**, so the sequence qualifies. B→C is **71 seconds**. The original program reports **630 seconds**, because it accidentally measures A→C.

The source fetches block B, then reads block A’s time into B’s variable:

```diff
-$patoshiBlock2Time = $patoshiBlock1->get('time');
+$patoshiBlock2Time = $patoshiBlock2->get('time');
```

This also makes the original time filter always true. Two separate run-tracking behaviors omit qualifying sequences, which is why the one-line repair and the complete stated rule have different sample sizes. [See the full explanation.](docs/technical-note.md)

P means “in the supplied classification list”; N means “outside it.” Neither label establishes a person’s identity. This example concerns a 2022 analysis error, not Bitcoin’s original software.

![Computed A–B, B–C and A–C intervals, in seconds; positions are schematic.](docs/figures/interval_example.png)

[Complete example evidence](results/reproduced/example_263_265.json) includes computed block hashes, raw headers and integer timestamps.

## The result

All variants use the same **50,000 Bitcoin headers**, heights **0–49,999**, and the same **21,953 published classifications**.

| Calculation | Selected cases | Negative gaps | All gaps <300 s | Share <300 s |
|---|---:|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 | **0.27%** |
| One timestamp assignment repaired | 400 | 10 | 144 | **36.00%** |
| Stated sequence rule implemented | 754 | 30 | 276 | **36.60%** |

Negative values are included in “All gaps <300 s.” The columns overlap. Each row has its own denominator because eligibility changes. These are differences between miner-supplied header timestamps, not independently measured elapsed mining times. For the original program the emitted interval is C−A; for the corrected variants it is C−B.

![Three versions of the timing test, each with its own denominator and disjoint negative, zero-to-299 and at-least-300-second categories.](docs/figures/timing_test_comparison.png)

The original **1,881 / 1 / 5** counts reproduce the article. Its stated test yields a substantially different result. The separate Patoshi timing and nonce fingerprints remain observable in these inputs; [the context note](docs/context.md) gives checks and their limits.

![Full-data empirical gap distributions, including negatives, with sample sizes, thresholds and a disclosed zoom.](docs/figures/timing_gap_distributions.png)

## Reproduce it

The one-command offline calculation is `python3 reproduce.py`. It also regenerates all original-label follow-up comparisons and complete row exports.

Requires **Python 3.10+**. The numerical audit uses the standard library and runs offline.

```sh
python scripts/verify_manifest.py
python reproduce.py
python scripts/check_direct.py
python -m unittest discover -s tests -v
```

Use `python3` if that is your Python command. Run without `-O` or `PYTHONOPTIMIZE`; disabling validation is explicitly rejected. For the three-block example alone:

```sh
python scripts/demo.py
```

`reproduce.py` validates the input hashes and all 50,000 headers, then compares **every output row and CSV byte** against the recorded native-PHP results. `check_direct.py` uses a second raw-byte implementation without importing the audit calculations. Fresh outputs are written to `build/`. Every retained original-label follow-up row is regenerated too. The command compares complete evidence with [results/reproduced/](results/reproduced/) and refuses to overwrite frozen project files. Zero, positive-below-300 and at-least-300 counts are explicit in the summary.

| Output | Contents |
|---|---|
| `build/summary.json` | Header checks, exact totals and output hashes |
| `build/events.json` | Every selected triple and its intervals |
| `build/original.csv` | Original program’s 1,881 outputs |
| `build/timestamp_only.csv` | One-line repair’s 400 outputs |
| `build/literal_rule.csv` | Stated rule’s 754 outputs |
| `build/direct_check.json` | Second implementation and context checks |
| `build/diagnostics.json` | Fixed-sample and selection decompositions |
| `build/mode_membership.csv` | All selected triples and membership in each mode |
| `build/example_263_265.json` | Verified hashes, serialized headers and minimal-example arithmetic |
| `build/followup/` | Complete comparison triples, all adjacent pairs, adjustment cells and summaries |

### Run the actual PHP

With a PHP 8 CLI installed:

```sh
python scripts/fetch_original_source.py build/original.php
python scripts/verify_source_labels.py --source build/original.php
python scripts/run_native.py --php php --source build/original.php
```

The fetch verifies the pinned source’s size and SHA-256. The native harness executes the original source, the one-line repair and the stated-rule implementation against offline header data. It compares every output byte with Python. [Native fixture instructions](docs/regression-tests.md) cover additional sequence and threshold tests.

For Debian 13 amd64, `bash scripts/setup_php.sh /workspace/tools/php` prepares a signature/checksum-verified rootless runtime; substitute `/workspace/tools/php/bin/php` for `php`. Run all native fixtures with:

```sh
PATOSHI_TEST_PHP=php PATOSHI_TEST_SOURCE="$PWD/build/original.php" \
  python3 -m unittest discover -s tests -v
```

The complete upstream PHP program is fetched separately; it is not relicensed by this project. See [THIRD_PARTY.md](THIRD_PARTY.md).

### Verify the source data again

```sh
python scripts/verify_live_headers.py
```

This optional network check compares a fresh prefix from Electrum’s header archive with all 4,000,000 bundled header bytes. Charts can be rebuilt with `python scripts/plot_results.py` after installing the optional `requirements-figures.txt`. Use `MPLCONFIGDIR=build/matplotlib` if your home directory is read-only.

## What this establishes

The published implementation does not compute the test described in the article. Correcting it removes the reported near-absence of short following-block timestamp gaps from that test.

The result does **not** settle whether a miner paused, manipulated timestamps, or was Satoshi. Other miners can find a block while one miner pauses. This audit does not reconstruct the original extranonce slopes or independently validate the supplied classifications. [Interpretation and context](docs/context.md) explain what survives and what remains open.

## Evidence and review

**Current status:** the three core modes and original-label follow-ups pass local checks, including fresh native PHP 8.4.27 execution. [Hosted Linux, Windows and native PHP checks passed](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41080882699) for implementation commit `dcd4a581041763daa970095a91fc3caa6fac5b6c`, now published on `main`. [Current records](results/current-verification/) are separate from archived package records. A tagged GitHub release is still pending. The package lacks the separate frozen Bitquery CSV and the exact three disputed labels/citation, so those sensitivities remain unverified.

- [Technical note](docs/technical-note.md): exact predicate, source patch and sample differences.
- [Input provenance](docs/provenance.md): source commit, input hashes, archives and anchors.
- [Verification status](docs/verification.md): recorded execution, fresh checks and hosted-CI status.
- [Prior-art search](docs/prior-art.md): sources searched and limits on priority claims.
- [Complete reproduced evidence](results/reproduced/): full events, diagnostics and follow-up rows.
- [Methodology](docs/methodology.md): header validation and descriptive comparison definitions.
- [Expected result tables](results/expected/): complete outputs, ready for inspection.
- [Contributing](CONTRIBUTING.md): report a discrepancy with commands and block heights.
- [Citation](CITATION.cff): author and software metadata; cite the exact commit reviewed.

**External human review and author confirmation are pending.** Separately written implementations are computational cross-checks, not independent peer review. A configured GitHub workflow becomes evidence only after its actual run passes.

Credit: Jameson Lopp for the published article, source and classifications; Sergio Demian Lerner and earlier researchers for the Patoshi research this audit builds on. Newly authored audit code and documentation use the [MIT license](LICENSE), with [third-party scope](THIRD_PARTY.md) stated separately.
