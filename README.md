# Patoshi Timing Audit

**Zakk Easterbrook · Reproducing and correcting a published Patoshi timing test**

[![Verify audit](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml)

The script linked from Jameson Lopp’s 2022 article [“Was Satoshi a Greedy Miner?”](https://blog.lopp.net/was-satoshi-a-greedy-miner/) reads the wrong block’s timestamp. This repository reproduces the original output, isolates that assignment error, and independently implements the stated selection rule using the same frozen labels and 50,000 Bitcoin headers.

**Candidate:** [`v1.0.0-rc.1`](https://github.com/zakkeasterbrook/-patoshi-timing-audit/tree/v1.0.0-rc.1), commit [`59d150f`](https://github.com/zakkeasterbrook/-patoshi-timing-audit/commit/59d150f9d95c572f539705561f71f1e248ef2a36) · [Candidate CI passed](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756) · [Current publication status](docs/verification.md)

## The published question and the error

For consecutive blocks A, B, C labelled **P→P→N**, require `tB − tA < 600 seconds` and measure `tC − tB`. P means membership in the supplied label list; N means nonmembership. Neither establishes a miner’s identity.

The source fetches B, then reads A’s response into B’s time variable:

```diff
-$patoshiBlock2Time = $patoshiBlock1->get('time');
+$patoshiBlock2Time = $patoshiBlock2->get('time');
```

That makes the intended timing filter automatically true and reports **C−A instead of C−B**. Separate run-tracking behavior also omits qualifying sequences. The [technical note](docs/technical-note.md) separates these effects.

## A three-block example

| Block | Supplied label | Header timestamp (UTC) |
|---|---|---|
| 263 — A | P | 2009-01-13 00:10:21 |
| 264 — B | P | 2009-01-13 00:19:40 |
| 265 — C | N | 2009-01-13 00:20:51 |

A→B is **559 seconds**, so the sequence qualifies. The intended B→C measurement is **71 seconds**. The original program reports **630 seconds**: 559 + 71.

[Inspect the actual headers, hashes and integer timestamps](results/reproduced/example_263_265.json), or run `python3 scripts/demo.py`. This demonstrates an error in a **2022 analysis program**, not a defect in Bitcoin’s original software.

## Reproduced results

All three calculations use mainnet heights **0–49,999** and the same **21,953 original labels**.

| Calculation | Selected cases | Negative differences | All differences <300 s | Share |
|---|---:|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 | **0.27%** |
| One timestamp assignment repaired | 400 | 10 | 144 | **36.00%** |
| Direct stated rule | 754 | 30 | 276 | **36.60%** |

**Below-300 counts include negative values. Each row has its own denominator because eligibility changes.** The original emits C−A; the corrected modes emit C−B. These are miner-supplied timestamp differences, not independently observed mining durations.

### Hold the sample constant

Keeping the **same original 1,881 cases** and changing only the measured interval raises the below-300 count from **5 to 713 — 37.91%**. The 713 include **121 negative differences**.

This [fixed-sample diagnostic](results/reproduced/diagnostics.json) isolates the measurement error while retaining legacy selection and eligibility. It is separate from the fully implemented stated test, whose main result remains **276 out of 754**.

![Computed proportions of negative, nonnegative-below-300, and at-least-300-second differences, with each sample size.](docs/figures/timing_test_comparison.png)

## What follows

The published near-absence of short following-block timestamp differences **does not survive a correct implementation of the stated test**.

This correction does not identify Satoshi, independently validate the labels, or settle whether a miner paused or manipulated timestamps. Other miners can find a block during one miner’s pause. Broader timing and nonce structure remains observable; the [follow-up note](docs/context.md) preserves those findings and the separately cited disputed-label sensitivity.

## Reproduce offline

Requires **Python 3.10+** and its standard library. From the project root:

```sh
python3 reproduce.py
```

The command validates the frozen inputs and header chain, regenerates every retained result row, and compares complete evidence with the saved references. It needs no Bitcoin node, RPC credentials, live explorer, or plotting packages. Run without Python optimization flags.

The candidate’s [verification record](results/current-verification/quality-pass/run.json) reports **68 local tests with no skips** using PHP. Without PHP, eight native tests explicitly skip. [Hosted checks](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756) passed Linux, Windows, Python 3.10/3.12/3.14, native PHP, and candidate archive construction.

## Review the evidence

- [Reviewer guide](docs/reviewer-guide.md): source inspection, independent questions and reproduction commands.
- [Evidence index](docs/evidence-index.md): complete case tables, schemas, units and sample definitions.
- [Technical note](docs/technical-note.md) and [methodology](docs/methodology.md): exact algorithms and validation scope.
- [Verification and publication status](docs/verification.md): tested snapshot, candidate tag, current limitations and dated history.
- [Provenance](docs/provenance.md) and [prior-art log](docs/prior-art.md): pinned sources, hashes, attribution and bounded priority claims.
- [Portable archives](docs/release-artifacts.md): verified downloads and packaging instructions.
- [Contributing](CONTRIBUTING.md): reproduce a discrepancy or submit an outside review.

**External human review remains pending.** The frozen Bitquery comparison dataset is still unavailable, so that sensitivity is unverified. Header validation does not revalidate transactions or reconstruct historical receiving-node clocks.

Credit: Jameson Lopp for the article, source and classifications; Sergio Demian Lerner and earlier Patoshi researchers for the work this audit builds on. [MIT license](LICENSE) for newly authored material; [third-party scope](THIRD_PARTY.md) and [citation metadata](CITATION.cff) are retained.
