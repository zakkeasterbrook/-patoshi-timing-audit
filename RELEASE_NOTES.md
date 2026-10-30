# Patoshi Timing Audit v1.0.0-rc.1

Candidate for technical review, pinned to
[`59d150f9d95c572f539705561f71f1e248ef2a36`](https://github.com/zakkeasterbrook/-patoshi-timing-audit/commit/59d150f9d95c572f539705561f71f1e248ef2a36)
and the existing `v1.0.0-rc.1` tag. Later documentation updates on `main` do not
change this frozen snapshot.

The script linked from Jameson Lopp's 2022 article
[“Was Satoshi a Greedy Miner?”](https://blog.lopp.net/was-satoshi-a-greedy-miner/)
reads the first block's timestamp into the second block's variable. This
defeats the intended time filter and measures C−A instead of C−B. Separate
run-tracking behavior omits eligible sequences.

At heights **263–265**, the preceding gap is **559 seconds**, the intended
following gap **71 seconds**, and the original output **630 seconds**.

Using the same 50,000 frozen mainnet headers and 21,953 original labels:

| Calculation | Cases | Negative | All differences <300 s |
|---|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 — 0.27% |
| One assignment repaired | 400 | 10 | 144 — 36.00% |
| Direct stated rule | 754 | 30 | 276 — 36.60% |

**Below-300 counts include negatives; each sample has its own denominator.**

**Fixed-sample diagnostic:** retaining the original 1,881 cases and changing
only the measured interval raises the below-300 count from **5 to 713
(37.91%)**, including 121 negatives rather than one. This isolates the interval
error. It retains legacy selection and eligibility; **276/754 remains the main
result for the fully implemented stated test**.

## Verification and reproduction

[CI passed for this exact commit](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756),
including Linux on Python 3.10/3.12/3.14, Windows, native PHP and portable
archive construction. Fresh local PHP 8.4.27 execution matches every core
Python CSV byte and row order. The local suite passes all **68 tests** with
PHP; without it, **60 pass and eight native tests skip**.

From the extracted `patoshi-timing-audit/` directory:

```sh
python3 scripts/verify_manifest.py
python3 reproduce.py
```

Assets: `Patoshi_Timing_Audit_v1.0.0-rc.1.zip`, `SHA256SUMS.txt` and
`release.json`. The archive includes frozen inputs, complete rows, code,
documentation and a top-level `RELEASE_MANIFEST.json` recording file digests
and the exact commit.

## Scope

These are miner-supplied header timestamp differences, not observed mining
durations. The error belongs to a 2022 analysis script, not Bitcoin's original
software. The correction does not identify Satoshi or determine whether a
miner paused. Bitquery sensitivity and external human review remain pending.
