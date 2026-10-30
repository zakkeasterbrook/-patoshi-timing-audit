# Announcement drafts

Prepared text only. Publish after the repository is public and its release-commit checks have been inspected. Replace `[repository link]` with the actual live repository URL.

## X: opening post

A published Patoshi timing test counted 5 short timestamp gaps out of 1,881 cases.

Implementing its stated rule gives 276 out of 754: 36.60%.

I’m releasing the audit, data and reproduction code. The samples differ; details and limits are documented.

[repository link]

## X: thread replies

1. The script fetches the second block, then reads the first block’s timestamp into its variable. This both defeats the time filter and measures A→C instead of B→C. Separate sequence-tracking errors also omit eligible cases.

2. A concrete example: blocks 263→264→265. The first gap is 559 seconds; the following gap is 71 seconds. The original script reports 630 seconds. The repository includes a tiny command that reproduces this example.

3. I kept the published classifications fixed and used the first 50,000 headers. The release includes every result row, input hashes, offline reproduction, regression tests and a native PHP comparison. Please check it and report discrepancies.

4. The wider timing and nonce fingerprints remain. This correction changes one test’s numerical evidence; it does not identify Satoshi or determine whether a miner paused. External human review is pending, and reproducible criticism is welcome.

## Longer announcement

I’m releasing **Patoshi Timing Audit**, a reproducible correction to the three-block timing test linked from Jameson Lopp’s 2022 article, *Was Satoshi a Greedy Miner?*

The original script reads the wrong block’s timestamp. That defeats its time filter and measures the first-to-third interval rather than the second-to-third interval. Separate sequence-tracking behavior also omits eligible examples.

Using the same fixed classifications and 50,000 Bitcoin block headers, the original implementation reproduces its published count: five gaps below 300 seconds among 1,881 cases. Repairing the timestamp assignment gives 144 among 400. Implementing the stated sequence rule gives 276 among 754, or 36.60%.

The samples differ because the corrections change eligibility. These are miner-supplied header timestamps, not independently observed mining durations.

The repository includes the data, complete output tables, provenance, Python reproduction, a second direct calculation, a PHP harness, tests and explanations. The separate Patoshi timing and nonce fingerprints remain observable. This finding does not settle the miner’s identity or behavior.

External human review is pending. I welcome anyone checking the code, reproducing the results or identifying a mistake.

[repository link]

## Short description for GitHub’s About field

Reproducible audit of the 2022 Patoshi timing test: pinned headers, corrected statistics, Python/PHP checks, and explicit limits.

## Suggested topics

bitcoin, patoshi, reproducible-research, blockchain-analysis, timestamp-analysis, research-audit, python, php
