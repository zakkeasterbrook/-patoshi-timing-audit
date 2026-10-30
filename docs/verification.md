# Verification status

## Latest inspected candidate — 30 October 2026

| Item | Verified state |
|---|---|
| Reviewed source commit | [`59d150f9d95c572f539705561f71f1e248ef2a36`](https://github.com/zakkeasterbrook/-patoshi-timing-audit/commit/59d150f9d95c572f539705561f71f1e248ef2a36) |
| Existing source tag | [`v1.0.0-rc.1`](https://github.com/zakkeasterbrook/-patoshi-timing-audit/tree/v1.0.0-rc.1), pointing to that commit |
| Hosted verification | **[Passed — Actions run 41086244756](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756)** for that exact commit |
| Hosted coverage | Linux on Python 3.10, 3.12 and 3.14; Windows on Python 3.12; fresh native PHP; portable candidate archive |
| Recorded local acceptance | [68 passed, zero failures or skips](../results/current-verification/quality-pass/run.json), with PHP supplied explicitly |
| Formal GitHub prerelease | Not published: the verified assets and notes are prepared, but the publication API request was denied; the public Releases page lists no releases |
| Remaining review/data limits | External human review is pending; the frozen Bitquery CSV is unavailable |

The reviewed candidate is an immutable source snapshot. Later documentation
commits on `main` do not move the tag or change which commit that CI run tested.
For another commit, inspect its own workflow result. The optional manual-trigger
online header-acquisition job was skipped in this push-triggered run.

[Machine-readable status](../results/status.json) identifies this candidate and
its evidence. The local record identifies source-file hashes; its 68-test run
preceded the final Windows archive-fixture correction, which the exact-commit
hosted run covers. Without the PHP environment, eight native-dependent tests
are skipped; that mode does not establish fresh PHP execution.

The latest publication attempt also could not update the repository's About
description or topics. These API-only finishing steps remain pending. Git
pushes work; this access failure does not invalidate the passed calculations
or CI. The pinned archive and exact publication command are documented in
[PUBLISHING.md](../PUBLISHING.md).

## Reproduced findings

Every ordered core CSV row and byte agrees with the frozen evidence:

| Calculation | Cases | Negative | All differences <300 s |
|---|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 |
| One assignment repaired | 400 | 10 | 144 |
| Direct stated rule | 754 | 30 | 276 |

Below-300 totals include negative values, and the samples have different
denominators. The original emits C-minus-A; corrected modes emit C-minus-B.

The [fixed-sample diagnostic](../results/reproduced/diagnostics.json) retains
all 1,881 original cases and changes only the measured interval: **713 are
below 300 seconds (37.91%), including 121 negatives**. It isolates the interval
error and is not the fully corrected selection.

The separately cited [three-label sensitivity](../results/reproduced/disputed_labels/)
reproduces **753 cases, 30 negative and 276 below 300 seconds** after removing
24,504; 35,573; and 35,599. Only child 24,505 leaves the sample. The main list
remains unchanged; historical attribution criticisms remain source assertions.

## What was executed and checked

The [local acceptance logs](../results/current-verification/quality-pass/)
record fresh Python calculations, a separately written raw-byte check and
actual PHP 8.4.27 execution with configuration disabled by `-n`. The pinned
original source, temporary one-assignment repair and direct PHP routine match
Python byte for byte. This does not reconstruct the author's complete 2022
Composer/Bitcoin Core environment.

The original source is pinned to commit
`66ee906b28ca13269d6f71d63f848973a1b747a2`: 125,172 bytes, SHA-256
`104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119`.
Its 21,953 extracted labels match the bundled list exactly.

The offline reproduction validates the 4,000,000-byte input, all 50,000
headers, genesis, hash linkage, compact targets, proof of work, mainnet
difficulty rules at all 24 retarget boundaries, and median time past. It
regenerates complete core, original-label follow-up and cited sensitivity
rows, requiring the exact frozen reference inventory before publishing outputs.

See the [reviewer guide](reviewer-guide.md) for commands and independent
questions, the [evidence index](evidence-index.md) for field definitions, and
[artifact contracts](release-artifacts.md) for the portable archive.
The contextual header-rule unit tests document their one-header hash stand-in;
genuine full-chain validation always hashes the actual input bytes.

## Historical execution and publication records

All earlier records retain their original dates and scope:

| Record | What it establishes |
|---|---|
| [`current-verification/quality-pass/`](../results/current-verification/quality-pass/) | Local quality-expansion acceptance, with commands and checked source hashes |
| [Earlier `current-verification/run.json`](../results/current-verification/run.json) | An earlier 36-test acceptance snapshot, not the candidate's complete test count |
| [Earlier `publication.json`](../results/current-verification/publication.json) | Initial publication and CI for `dcd4a58`; its then-missing three-label evidence and access failures are historical observations |
| [`local-verification/`](../results/local-verification/) and [`release-verification/`](../results/release-verification/) | Preserved supplied-package records, including PHP 8.3.6 and earlier source/header downloads |

The directory name `current-verification` is retained for link stability. Its
[index](../results/current-verification/README.md) separates the snapshots;
folder names alone do not establish freshness, hosted CI or a public release.

## Remaining limits

The frozen Bitquery CSV is unavailable, so its classification sensitivity is
not presented as reproduced. The [pending-input record](../provenance/pending_inputs.json)
preserves the source and unverified acquisition target. No external human
peer review or original-author confirmation is asserted.

Ten [recorded explorer observations](../provenance/independent_explorer_anchors.json)
match the frozen headers and hashes offline. They are historical observations,
not new explorer queries. The later local Electrum request received HTTP 403;
the old successful download record has not been relabeled as a fresh check.

Header validation and recorded chain anchoring do not revalidate transactions,
scripts or historical receiving-node clocks. Header timestamp differences do
not independently measure elapsed mining time, establish miner identity or
settle whether a miner paused. Worldwide priority remains unestablished.
