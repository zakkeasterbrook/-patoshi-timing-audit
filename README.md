# Patoshi Timing Audit

**Zakk Easterbrook · Reproducing and correcting a published Bitcoin timing test**

[![Verify audit](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml)

The timing script linked from Jameson Lopp’s 2022 article [“Was Satoshi a Greedy Miner?”](https://blog.lopp.net/was-satoshi-a-greedy-miner/) reads the wrong block’s timestamp. This audit reproduces its output, isolates the measurement error, and implements the test described in the article.

**Lopp’s published script reports 5 differences below 300 seconds out of 1,881 cases (0.27%). Implementing the stated test gives 276 out of 754 (36.60%).**

Both use the **same 50,000 Bitcoin headers and 21,953 original labels**. Below-300 counts include negative values; the selected samples have different denominators.

![Published script: 5 of 1,881 below 300 seconds; one assignment repaired: 144 of 400; direct stated rule: 276 of 754. Bars separate negative, nonnegative-below-300 and at-least-300-second differences.](docs/figures/timing_test_comparison.png)

## How this differs from the published script

The article’s test concerns three consecutive blocks: two in the supplied Patoshi label set (**P**), followed by one outside it (**N**). Require the second timestamp minus the first to be **<600 seconds**, then measure the difference from the **second block to the third**.

This repository keeps the labels fixed and separates three calculations:

| Calculation | What it does | Differences below 300 s |
|---|---|---:|
| **Published script** | Preserves the wrong timestamp assignment and original sequence tracker. | **5 / 1,881 — 0.27%** |
| **One assignment repaired** | Reads the second block’s time, restoring the intended interval and timing filter; keeps the original sequence tracker. | **144 / 400 — 36.00%** |
| **Direct stated rule** | Enumerates every adjacent P→P→N triple, applies the stated timing filter, and measures the second-to-third interval. | **276 / 754 — 36.60%** |

The below-300 totals include **1, 10 and 30 negative differences**, respectively. The samples change because eligibility and sequence selection change. These are miner-supplied **header timestamp differences**, not independently measured mining durations.

[Inspect the exact algorithms and complete per-case differences.](docs/technical-note.md)

## See the mistake: 71 seconds reported as 630

Blocks **263→264→265** give a small, directly checkable example. The first two are labelled P; the third is N.

The preceding gap is **559 seconds**, so the example passes the under-600-second condition. The intended following gap is **71 seconds**. The published program instead adds the preceding gap and reports **630 seconds**.

![Real headers at heights 263, 264 and 265: the intended second-to-third difference is 71 seconds, while the published first-to-third difference is 630 seconds.](docs/figures/interval_example.png)

The script fetches the second block, B, then reads the first block, A, into B’s time variable:

```diff
-$patoshiBlock2Time = $patoshiBlock1->get('time');
+$patoshiBlock2Time = $patoshiBlock2->get('time');
```

The original assignment makes the timing filter automatically true and reports **C−A in place of the intended C−B**. Separate tracker behavior also omits eligible sequences, explaining the difference between the one-line repair and the direct rule.

[Check the actual headers, hashes and integer timestamps](results/reproduced/example_263_265.json), or run `python3 scripts/demo.py`. The defect is in a **2022 analysis program**, not Bitcoin’s original software.

## The same cases, measured two ways

The interval error can also be isolated on an **unchanged sample**.

Keep all **1,881 cases** selected by the published script and change only the measured interval from C−A to C−B. The below-300 count changes from **5 to 713 — 37.91%**. The 713 include **121 negative differences**.

![The same 1,881 original cases measured two ways: published C-minus-A gives 5 below 300 seconds; intended C-minus-B gives 713. Original selection and eligibility stay fixed.](docs/figures/same_sample_comparison.png)

This [fixed-sample diagnostic](results/reproduced/diagnostics.json) retains the original selection and eligibility. It isolates the measurement error; **276/754 remains the main result for the fully implemented stated test**.

## What this establishes

**The published near-absence of short following-block timestamp differences does not survive a correct implementation of the stated test.**

The broader Patoshi question remains separate. This correction does not identify Satoshi, independently validate the labels, or establish whether a miner paused or manipulated timestamps. Other miners can find a block during one miner’s pause. The [follow-up analysis](docs/context.md) preserves the timing, nonce and classification-sensitivity findings that remain observable.

## Reproduce it

Requires **Python 3.10+** and its standard library. From the project root:

```sh
python3 reproduce.py
```

The command validates the frozen inputs and header chain, regenerates every retained result row, and compares the complete evidence. No Bitcoin node, RPC credentials, live explorer or plotting packages are needed. Run without Python optimization flags.

## Inspect and review

- [Reviewer guide](docs/reviewer-guide.md): independent checks and fresh native-PHP reproduction.
- [Evidence index](docs/evidence-index.md): every case table, field, unit and sample definition.
- [Technical note](docs/technical-note.md) and [methodology](docs/methodology.md): the source error, selection effects and validation rules.
- [Provenance](docs/provenance.md) and [prior-art log](docs/prior-art.md): pinned inputs, attribution and bounded priority claims.
- [Verification and publication status](docs/verification.md): exact tested commits, CI, runtime records and remaining limits.
- [Contributing](CONTRIBUTING.md): reproduce a discrepancy or submit an outside review.

**Verified candidate:** [`v1.0.0-rc.1`](https://github.com/zakkeasterbrook/-patoshi-timing-audit/tree/v1.0.0-rc.1) · [Candidate CI passed](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756) · [Archive instructions](docs/release-artifacts.md). The recorded local suite passed 68 tests with PHP supplied; without it, eight native tests explicitly skip. Later README and figure updates on `main` do not move the candidate tag.

External human review remains pending. The separate frozen Bitquery dataset is unavailable, so that sensitivity is unverified. Header checks do not revalidate transactions or reconstruct historical receiving-node clocks.

Credit: Jameson Lopp for the article, source and classifications; Sergio Demian Lerner and earlier Patoshi researchers for the work this audit builds on. [MIT license](LICENSE) for newly authored material; [third-party scope](THIRD_PARTY.md) and [citation metadata](CITATION.cff).
