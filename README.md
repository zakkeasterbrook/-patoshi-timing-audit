# Patoshi Timing Audit

**A 71-second timestamp gap was reported as 630 seconds. That changes a published test of early Bitcoin mining.**

Zakk Easterbrook · [v1.0.0](https://github.com/zakkeasterbrook/-patoshi-timing-audit/releases/tag/v1.0.0)

[![Verify audit](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml)

On 13 January 2009, Bitcoin block 264 recorded the time **00:19:40 UTC**. The next block, 265, recorded **00:20:51**: a difference of **71 seconds**. A timing script published in 2022 reports **630 seconds** for that same following block observation. It subtracts the timestamp of block 263 instead of block 264.

The error matters because the script was counting differences below five minutes. This example crosses that threshold entirely because the program starts one block too early.

Across the audited data, the published implementation produces **5 differences below five minutes among 1,881 selected cases**. Implementing its stated test gives **276 among 754**. The same historical headers and classifications underlie both results. The calculation and which cases qualify changes.

**These counts include negative timestamp differences, and the samples have different denominators.** A block timestamp is supplied by its miner; it is not an independently observed discovery time.

![Three reproduced calculations: the published implementation reports 5 of 1,881 differences below five minutes; repairing one timestamp assignment gives 144 of 400; implementing the stated sequence rule gives 276 of 754. Negative values are shown separately within those totals.](docs/figures/timing_test_comparison.png)

This repository documents the source error, reproduces the original output, and separates the effects of correcting its measurement and selection rules. The inputs, every selected case, independent calculations and figure-generation code are included so the finding can be checked from the bytes upward.

## Why this test matters

The calculation comes from the script linked in Jameson Lopp’s September 2022 article [*Was Satoshi a Greedy Miner?*](https://blog.lopp.net/was-satoshi-a-greedy-miner/). It formed part of a discussion about unusual early-block timing: did a mining operation pause between blocks, or did the recorded timestamps reflect some other behaviour?

That discussion belongs to the wider **Patoshi hypothesis**—the proposal that many early Bitcoin blocks can be associated with a common mining operation, often discussed in connection with Bitcoin’s pseudonymous creator, Satoshi Nakamoto.

The hypothesis predates Lopp’s test. Sergio Demian Lerner published [early mining-pattern analysis in 2013](https://bitslog.com/2013/04/17/the-well-deserved-fortune-of-satoshi-nakamoto/), followed by [Patoshi and nonce-range research in 2019](https://bitslog.com/2019/04/16/the-return-of-the-deniers-and-the-revenge-of-patoshi/). His [2020 timestamp investigation](https://bitslog.com/2020/06/22/a-new-mystery-in-patoshi-timestamps/) described unusual spacing and discussed possible explanations. Earlier work also examined mining-related counters and search values rather than relying on this one timing statistic.

An error in the 2022 script therefore changes one argument within that history. It does not establish that the broader pattern is fictitious, that every classification is sound, or that an attributed miner was Satoshi. Those claims require evidence beyond this calculation.

The purpose of this audit is narrower and directly testable: determine whether the published program measured the test it described, and show what happens when that test is implemented correctly.

## What was supposed to be measured

Bitcoin’s ledger is an ordered sequence of **blocks**, each containing transactions. **Miners** compete to add the next block. A block’s **height** is its position in that sequence. Its **header** is a small identifying record containing, among other fields, a timestamp selected by the miner.

For this audit, **P** means membership in the exact published Patoshi list; **N** means absence from it. These are classifications, not established identities. An N block is not proof that a different real world miner produced it.

The stated test examines three consecutive heights:

1. **A:** a block labelled P.
2. **B:** another P block, with `timestamp(B) − timestamp(A) < 600 seconds`.
3. **C:** the next block, labelled N.

The intended observation is **`timestamp(C) − timestamp(B)`**. The reported short-gap statistic counts values **strictly below 300 seconds**—five minutes. No nonnegative lower bound is added to either the stated preceding-gap condition or the short-gap count.

Those details matter. A miner supplied clock can go backward relative to the previous header while the blocks remain in their fixed chain order. A negative timestamp difference is not negative elapsed time, and it must not silently disappear from a reproduction of the published rule.

## The error in three real blocks

The first 500 blocks already contain an example that can be checked without interpreting an aggregate statistic:

| Height | Supplied label | Header timestamp, UTC |
|---|---|---|
| 263 — A | P | 2009-01-13 00:10:21 |
| 264 — B | P | 2009-01-13 00:19:40 |
| 265 — C | N | 2009-01-13 00:20:51 |

A→B is **559 seconds**, or 9 minutes 19 seconds, so the preceding-gap condition passes. B→C is **71 seconds**, or 1 minute 11 seconds. The published output is A→C: **630 seconds**, or 10 minutes 30 seconds.

![The verified 263–265 example: 559 seconds between the two P blocks, then 71 seconds to the N block. Measuring from the first P block instead produces 630 seconds. Block positions are schematic.](docs/figures/interval_example.png)

The [pinned PHP source](https://github.com/jlopp/bitcoin-utils/blob/66ee906b28ca13269d6f71d63f848973a1b747a2/findNonPatoshiDeltasAfterFastPatoshiBlocks.php) fetches B but reads A’s response when assigning B’s time:

```diff
-$patoshiBlock2Time = $patoshiBlock1->get('time');
+$patoshiBlock2Time = $patoshiBlock2->get('time');
```

This affects two operations. The intended filter, `tB < tA + 600`, becomes `tA < tA + 600`, which always passes for these integer timestamps. The intended difference, `tC − tB`, becomes `tC − tA` and includes the preceding interval as well.

The [example evidence](results/reproduced/example_263_265.json) includes the integer timestamps, calculated block hashes and actual serialized headers. Run `python3 scripts/demo.py` to reproduce the arithmetic. This demonstrates a defect in a **2022 analysis program**, not a defect in Bitcoin’s 2009 software.

## Reproduce first, then correct

The dataset contains **50,000 consecutive mainnet headers**, heights 0–49,999, with recorded timestamps spanning January 2009 to April 2010. The **21,953 published labels remain unchanged** in all three main calculations. Reclassifying the blocks would answer a different question and make it harder to isolate the implementation error.

The published algorithm is reproduced first, including its timestamp assignment and sequence tracker. It returns the article’s original counts: 1,881 cases, one negative difference and five below five minutes. The table expresses 5/1,881 as 0.27%, to two decimal places.

The one-line repair changes only the assignment shown above. A separate direct implementation scans every consecutive P→P→N triple and applies the stated condition and interval without using the original tracker.

| Calculation | Selected cases | Negative | Nonnegative under 5 minutes | At least 5 minutes | All under 5 minutes |
|---|---:|---:|---:|---:|---:|
| Published implementation | 1,881 | 1 | 4 | 1,876 | **5 — 0.27%** |
| One timestamp assignment repaired | 400 | 10 | 134 | 256 | **144 — 36.00%** |
| Direct stated rule | 754 | 30 | 246 | 478 | **276 — 36.60%** |

**All-under-five-minute totals include negatives. Each row uses its own denominator.** The original measures A→C; corrected versions measure B→C. None of these samples contains a zero-valued output.

Fixing the assignment restores the timing filter and removes 1,481 originally selected cases, leaving 400. The tracker has separate selection omissions: it requires more than two stored P heights and discards a potential new run’s first height when resetting. The direct rule includes 354 additional qualifying cases, giving **400 + 354 = 754**. The [technical note](docs/technical-note.md) traces these behaviours and the complete inclusion differences.

## Reading the line graphs

A single threshold can hide the shape of the data. These lines show the distribution of every selected timestamp difference.

Choose a gap along the bottom axis, move up to a line, then read the percentage on the left. That is the share of the selected cases with a recorded difference **at or below** that value. A line rising earlier contains more short gaps. The horizontal axis is a gap in minutes, not a timeline through Bitcoin’s history.

![Cumulative distributions of all three calculations, shown in minutes and percentages. Near five minutes, the corrected curves have accumulated about a third of their cases while the original curve remains near zero.](docs/figures/reader_timing_lines.png)

At the five-minute reference, the corrected curves contain about a third of their selected cases. The original curve remains near zero. The historical headers have not changed; the program selects and measures them differently.

The displayed range is a zoom. Negative differences and gaps beyond the right edge still contribute to the denominators. The curves use **at or below**; the exact short-gap counts use **strictly below** five minutes. Each corrected sample has one observation exactly at 300 seconds, included in its curve at that point but excluded from its short-gap total.

<details>
<summary>Full-range distributions and the long tail</summary>

![Complete observed distributions and a disclosed zoom, generated from every selected row. The horizontal units here are seconds; all negative and long differences remain included.](docs/figures/timing_gap_distributions.png)

The full observed range is −1,407 to 31,007 seconds. Both panels use each version’s entire selected sample; the right panel changes only the displayed horizontal range.

</details>

## Hold the sample fixed

Changing the selected cases is not the only source of the difference. The measurement error can be isolated while retaining **all 1,881 original cases**, with their original selection and eligibility.

Change only the reported interval from A→C to B→C. The count below five minutes rises from **5 to 713: 37.91%**, including **121 negatives**.

![The same 1,881 cases measured two ways: 5 below five minutes using the published A-to-C interval, and 713 using B-to-C. The legacy selection and eligibility remain unchanged.](docs/figures/same_sample_comparison.png)

This diagnostic keeps the sample constant; it does not restore the intended timing filter or sequence selection. **276/754 remains the main result for the fully implemented stated test.** The [diagnostic record](results/reproduced/diagnostics.json) and [mode-membership table](results/reproduced/mode_membership.csv) expose the per-case effects.

## The structure that remains

The corrected following-block test and the earlier observations about spacing between attributed blocks ask different questions. One measures the gap from an in-list block to the next outside-list block after a qualifying P→P pair. The other can examine the spacing between two in-list blocks themselves.

Across the frozen dataset’s **49,999 adjacent pairs**, the supplied groups retain markedly different recorded timing distributions:

![Cumulative timing distributions for adjacent P-to-P and N-to-N pairs. The supplied groups have different recorded spacing; the plot is not independent validation of their attribution or miner identity.](docs/figures/remaining_timing_structure.png)

For pairs whose two blocks are in the supplied group, **139 of 13,053** differences are below five minutes. For pairs whose two blocks are outside it, **8,238 of 19,146** are below five minutes. Negatives are included, each group has its own denominator, and this comparison applies no preceding-gap filter.

These are observations under the published classification. The labels may themselves have used related timing or nonce features, so the separation is **not independent proof that the labels identify one miner**.

Nonce structure also remains. A nonce is a number varied during mining’s search for a valid block. A previously discussed band of values in one part of that number contains all 21,953 P-labelled blocks, but **5,655 unlisted blocks fall inside it too**. That feature alone does not establish attribution. Earlier ExtraNonce analysis concerns a different value in the mining-reward transaction; this header audit does not reconstruct that classifier. The [follow-up analysis](docs/context.md) provides the exact byte-order checks, comparison groups and classification sensitivities.

Nor does a short following gap rule out a pause: other miners can find a block while one miner is inactive. Timestamp differences alone cannot distinguish every mining or clock mechanism. A visible pattern, a reliable attribution to one operation and identification as Satoshi are separate evidential steps.

## What this audit establishes

The source and reproduced outputs support a specific conclusion: **the published near-absence of short following-block timestamp differences does not survive a correct implementation of the stated test**.

The error is directly visible in the code, demonstrable on real headers and substantial both on the original fixed sample and under the corrected selection. It changes that statistic’s contribution to the pause-versus-timestamp discussion. It does not identify Satoshi, independently validate the supplied labels, or settle how the recorded timing pattern arose.

Verification here is computational. For each version, native PHP and Python agree on every ordered output row. That agreement is not an external peer-review endorsement. The [methodology](docs/methodology.md) defines the validation scope; the [prior-art record](docs/prior-art.md) documents a bounded search rather than a claim of worldwide priority.

## Reproduce the release

The numerical audit uses **Python 3.10+ and its standard library**. From the project root:

```sh
python3 reproduce.py
```

It checks the frozen input digests, known mainnet genesis, header links, proof of work, difficulty rules at all 24 retarget boundaries and median time past. It regenerates every retained row and compares the complete evidence. Header validation does not revalidate transactions or reconstruct historical receiving-node clocks.

The core calculation runs offline without a Bitcoin node, RPC credentials or plotting dependencies. Use Python without optimization flags. Fresh native-PHP verification and independent checks are described in the [reviewer guide](docs/reviewer-guide.md).

**[Download v1.0.0](https://github.com/zakkeasterbrook/-patoshi-timing-audit/releases/tag/v1.0.0)** · [Verification](docs/verification.md) · [Input provenance](docs/provenance.md) · [Complete results](results/reproduced/) · [Evidence schemas](docs/evidence-index.md)

<details>
<summary>Regenerate the figures</summary>

The optional plotting dependencies and commands are separate from numerical reproduction:

```sh
python3 -m pip install -r requirements-figures.txt
python3 scripts/plot_results.py
python3 scripts/story_figures.py
```

Each scientific figure is generated from reproduced data. Zooming a graph does not remove observations from its sample.

</details>

Credit to Jameson Lopp for the published article, source and classifications, and to Sergio Demian Lerner and earlier researchers for the Patoshi work this audit builds on. Newly authored code and documentation use the [MIT license](LICENSE); [third-party scope](THIRD_PARTY.md) and [citation metadata](CITATION.cff) apply. Reproducible corrections and outside assessments are welcome through [CONTRIBUTING.md](CONTRIBUTING.md).
