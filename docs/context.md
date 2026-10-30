# What survives the correction

The defect belongs to a 2022 analysis program. It does not identify a defect in
Bitcoin's 2009 software or consensus rules. The following descriptive comparisons
use the same frozen mainnet headers, heights 0–49,999, and the original labels.

`python3 reproduce.py` produces the core audit and the follow-up rows and
summaries. The follow-up calculation can also run separately with
`python3 scripts/followup.py`. The second
implementation, [`scripts/check_direct.py`](../scripts/check_direct.py),
cross-checks the principal PPN rows and basic context from raw bytes without
importing the audit calculations. See [methodology](methodology.md) and
[verification status](verification.md).

## Comparison sequences

P means membership in the original list and N means absence from that list.
For consecutive heights A, B, C, the following difference is `tC - tB` and
the preceding difference is `AB = tB - tA`.

| Selection | Cases | Negative following differences | All following differences <300 s | Rate | Median following difference |
|---|---:|---:|---:|---:|---:|
| PPN, AB <600 s | 754 | 30 | 276 | 36.60% | 429.5 s |
| NPN, AB <600 s | 2,780 | 55 | 1,042 | 37.48% | 421.5 s |
| PPN, 300 ≤AB <600 s | 727 | 30 | 263 | 36.18% | 431 s |
| NPN, 300 ≤AB <600 s | 1,192 | 35 | 445 | 37.33% | 436 s |
| Every adjacent P→N pair | 8,900 | 398 | 3,215 | 36.12% | 455.5 s |

The below-300 counts **include negative values**. Each row has its own
denominator. The unrestricted NPN sample contains 36 negative preceding
differences; the common 300–599-second range excludes them. A negative
preceding difference is permitted by the literal `AB <600` rule.

The follow-up also standardizes the common-range NPN comparison to the PPN
sample's composition in 10,000-height eras of B and 100-second preceding-gap
bands. All 15 cells have observations in both groups. Each cell's NPN rate
is weighted by its fraction of PPN observations. The adjusted NPN below-300
rate is **37.88%**, compared with **36.18%** for PPN. For negative differences,
the pooled NPN rate is **2.94%**, the standardized NPN rate **5.56%**, and the
PPN rate **4.13%**. The exported cells make this reversal inspectable.

The earlier follow-up script was not included in the archive. This repository's
explicit parent-B era definition reproduces the recorded rounded targets;
it is a reconstruction, not execution of an inspected earlier script.

This is exploratory descriptive adjustment, not a causal estimate. These
samples are not randomized. Mining conditions vary by era, labels are
uncertain, and PPN is contained in the all-PN baseline. Similar percentages do
not establish equivalent mechanisms. No independent-observation p-value is
claimed.

## The timing structure remains

| Adjacent labels | Pairs | Negative differences | All differences <300 s |
|---|---:|---:|---:|
| P/P | 13,053 | 0 | 139 |
| P/N | 8,900 | 398 | 3,215 |
| N/P | 8,900 | 72 | 2,497 |
| N/N | 19,146 | 224 | 8,238 |

These groups partition all 49,999 adjacent pairs. For a later-period diagnostic,
require both heights to be at least 541 and exclude pairs touching heights
1,400–1,916, inclusive. Then **12,239 of 12,240 P/P differences are at least
312 seconds**. The exception is 24,503→24,504, with a 65-second difference.

These early-period exclusions come from earlier research rather than newly
established change points. Height 24,504 was also questioned before this audit;
the objection is not a new discovery here. The main calculation retains the
original list. Historical context is provided by
[Lerner's timestamp analysis](https://bitslog.com/2020/06/22/a-new-mystery-in-patoshi-timestamps/)
and the [public label discussion](https://github.com/janoside/btc-rpc-explorer/discussions/465).

Applying the related exclusion to whole PPN triples—A at least 541 and none of
A, B, C in 1,400–1,916—leaves **695 cases, 30 negative differences, and 248
below 300 seconds (35.68%)**. This is a sensitivity choice informed by prior
work, not the main analysis.

## The nonce structure remains

The first serialized nonce byte is at offset 76 in each 80-byte header. It is
the low byte of the little-endian numeric nonce. The coarse band discussed in
[Lerner's nonce research](https://bitslog.com/2020/08/22/the-patoshi-mining-machine/)
is **0–9 or 19–58 inclusive**.

| Membership | Inside the band | Outside the band |
|---|---:|---:|
| Original P labels | 21,953 | 0 |
| Unlisted blocks | 5,655 | 22,392 |
| All headers | 27,608 | 22,392 |

Overall, 55.216% of headers fall inside. Applying the same band separately to
serialized nonce bytes 0, 1, 2, 3 yields **21,953 / 4,309 / 4,280 / 4,328**
matches among P labels. This guards against confusing a raw byte with a
displayed nonce byte.

For the same later-period pair exclusions, R denotes raw-byte band membership
and O denotes absence from the band, without using the P list for grouping:

| Adjacent raw-byte groups | Pairs | Negative differences | All differences <300 s | Median |
|---|---:|---:|---:|---:|
| R/R | 16,477 | 93 | 1,424 (8.64%) | 887 s |
| O/O | 12,124 | 141 | 5,204 (42.92%) | 367 s |

This is evidence of structure in the headers. Band membership alone does not
identify a miner, and it does not independently validate labels potentially
constructed using related features. This analysis does not reconstruct
ExtraNonce slopes.

## A pause is still an open explanation

If one miner pauses after finding a block, other miners can continue and find
the next block within seconds. Short P→N differences can therefore coexist
with a pause by P.

An **idealized, unfitted analytical example** makes this distinction explicit.
Let P resume after a pause `d`, with exponential active waiting time
`X ~ Exp(lambda)`, while other miners have `Y ~ Exp(mu)`. The next-block time
is `min(d + X, Y)`. The probability that the next block is from the others is

```text
q = 1 - exp(-mu*d) + exp(-mu*d) * mu/(lambda + mu).
```

Conditioned on that next block coming from the others, the probability that
it arrives before the pause ends is `(1 - exp(-mu*d))/q`. This is an illustration,
not a fit to the historical observations or evidence that a particular pause
occurred.

Recorded header times do not independently measure discovery or broadcast times.
A fixed clock offset, an offset applied conditionally after a P parent, and a
recursive minimum timestamp-spacing rule have different consequences. The audit
does not select among these mechanisms. A stronger causal project would need
specified competing models and held-out validation.

## Follow-up inputs still required

The separately published
[Bitquery investigation](https://www.bitquery.io/investigations/satoshi-nakamoto-net-worth)
is a proposed classification-sensitivity check. Its CSV is absent from the
supplied release package. Its numerical targets have **not** been freshly
verified here and are not presented as reproduced results. The full-source
population must be distinguished from heights below 50,000. In a high-grade
analysis, medium/low positives must remain unknown, not be recoded as negative;
genesis is unclassified. Using its published labels would not independently
validate or rerun its classifier.

The separate experiment removing three disputed labels also requires their
exact identities and historical citation before inclusion. No labels have
been removed from the main calculation. See [verification status](verification.md)
for the current completion limits.
