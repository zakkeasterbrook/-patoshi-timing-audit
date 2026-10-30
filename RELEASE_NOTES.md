# Patoshi Timing Audit v1.0.0

A reproducible correction to the timing script linked from Jameson Lopp's 2022 article [“Was Satoshi a Greedy Miner?”](https://blog.lopp.net/was-satoshi-a-greedy-miner/).

For consecutive blocks 263, 264 and 265, the intended following timestamp difference is **71 seconds**. The published program reports **630 seconds** because it reads the first block's timestamp into the variable meant for the second. The same assignment also defeats the intended eligibility filter.

Using 50,000 frozen mainnet headers and the same 21,953 published labels:

| Calculation | Cases | Negative | All differences <300 seconds |
|---|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 — 0.27% |
| One assignment repaired | 400 | 10 | 144 — 36.00% |
| Direct stated rule | 754 | 30 | 276 — 36.60% |

**The below-300 totals include negative values. Each row has its own denominator.**

Holding all 1,881 original cases fixed and changing only the interval gives **713 below 300 seconds, including 121 negatives**. This diagnostic isolates the interval error; it is separate from the main 276/754 result.

## Included evidence

The release contains the frozen inputs, complete selected rows and comparisons, pinned-source metadata, technical documentation, reader-facing figures, original-label follow-ups and the separately cited three-label sensitivity. The main classifications remain unchanged.

Native PHP and Python are compared byte for byte. Automated checks cover Linux, Windows, Python 3.10/3.12/3.14, header validation, strict numerical boundaries and artifact integrity. Tagged publication verifies the uploaded assets by downloading and comparing them again.

## Download and reproduce

Assets:

- `Patoshi_Timing_Audit_v1.0.0.zip`
- `SHA256SUMS.txt`
- `release.json`

After checking the archive digest, extract it and run from `patoshi-timing-audit/`:

```sh
python3 scripts/verify_manifest.py
python3 reproduce.py
```

The top-level `RELEASE_MANIFEST.json` records the exact source commit and source-file digests.

The finding concerns one published calculation. It does not identify Satoshi, independently validate the supplied classifications, establish a mining pause or timestamp mechanism, or reconstruct full transaction validation. Computational agreement is not an external peer-review endorsement.
