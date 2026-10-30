# Verification and scope

The audit is reproducible from the frozen inputs. Its principal claim is an
implementation mismatch: the published timing program measures a different
interval and selects a different set of sequences from the rule described
in its source and accompanying article.

## Release identity

[Version 1.0.0](https://github.com/zakkeasterbrook/-patoshi-timing-audit/releases/tag/v1.0.0)
is identified by the immutable
[`v1.0.0` source tag](https://github.com/zakkeasterbrook/-patoshi-timing-audit/tree/v1.0.0).
The downloadable archive's top-level `RELEASE_MANIFEST.json` records the full
Git commit and every source-file digest. `release.json` records the archive
digest, byte count and version.

The [release workflow](../.github/workflows/verify.yml) validates the tagged
source before publishing its assets. It covers Linux on Python 3.10, 3.12 and
3.14, Windows on Python 3.12, fresh native PHP, and deterministic archive
construction. The [workflow runs](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml)
provide job outcomes and execution logs for each commit. The machine-readable
[evidence index](../results/status.json) links the release to its inputs,
results and recorded checks.

## Numerical reproduction

Every ordered core CSV row and byte is compared with the frozen evidence:

| Calculation | Cases | Negative | All differences <300 s |
|---|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 |
| One assignment repaired | 400 | 10 | 144 |
| Direct stated rule | 754 | 30 | 276 |

Below-300 totals include negative values. The samples have different
denominators. The published implementation emits C-minus-A; corrected modes
emit C-minus-B.

The [fixed-sample diagnostic](../results/reproduced/diagnostics.json) retains
all 1,881 original cases and changes only the measured interval. It gives
**713 differences below 300 seconds (37.91%), including 121 negatives**.
This isolates the interval error while retaining legacy selection and
eligibility; it is not the fully corrected sample.

The separately cited [three-label sensitivity](../results/reproduced/disputed_labels/)
removes 24,504; 35,573; and 35,599 from a copy of the classification list.
It gives **753 cases, 30 negatives and 276 below 300 seconds**. Only child
height 24,505 leaves the sample; no cases enter. The main list is unchanged.
Historical criticisms of those labels remain source assertions.

## Input and header checks

The original source is pinned to commit
`66ee906b28ca13269d6f71d63f848973a1b747a2`: 125,172 bytes, SHA-256
`104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119`.
Its 21,953 extracted labels match the bundled list in order.

The offline calculation validates:

- The 4,000,000-byte input and its digest: 50,000 serialized mainnet headers.
- Known genesis, header hashes, byte order and every previous-hash link.
- Compact targets, proof of work, the mainnet target limit and difficulty rules
  at all 24 retarget boundaries in scope.
- Median time past, using the preceding available headers.
- Label types, ordering, uniqueness, range and canonical-content digest.
- Complete reference-file inventories and exact regenerated output bytes.

The ten [recorded explorer observations](../provenance/independent_explorer_anchors.json)
cover five heights against two explorers. Their hashes and headers match the
frozen input. These are preserved observations, not fresh explorer queries
performed by the offline command.

See [methodology](methodology.md) for the rules and [input provenance](provenance.md)
for the acquisition evidence.

## Computational cross-checks

The original source, a temporary one-assignment repair, and a separate direct
PHP routine are executed against a deterministic offline RPC adapter. Every
emitted core CSV byte and row order must agree with fresh Python output.
Configuration loading is disabled with PHP's `-n` option.

The retained [local acceptance record](../results/current-verification/quality-pass/run.json)
reports **68 passed tests with zero failures or skips**, using PHP 8.4.27.
It identifies the checked source-file hashes. The
[pre-release hosted run](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756)
also covers the subsequent Windows archive-fixture correction. Release
verification applies the same checks to the final tagged tree.

Without the explicit PHP environment, eight native-dependent tests skip.
That mode validates the Python workflow but does not establish fresh PHP
execution. The [reviewer guide](reviewer-guide.md) provides the complete
native commands.

The independent raw-byte implementation compares every direct-rule row.
Regression cases cover sequence boundaries, strict timing thresholds,
malformed inputs, altered headers, native response independence, missing
evidence and output-file protection. The contextual header-rule unit tests
document their one-header hash stand-in; genuine full-chain validation always
hashes the actual input bytes.

## Scope of the evidence

This is header validation and recorded chain anchoring, not transaction or
script revalidation. Historical receiving-node clocks are not reconstructed.
Header timestamps do not independently measure discovery or broadcast times.

The supplied classifications are fixed inputs, not identities established by
this audit. Timing and nonce comparisons are descriptive; they do not
independently validate a classifier, select a causal clock/mining model, or
identify Satoshi. Alternative Bitquery classifications are outside this
release's numerical analysis. The [analysis-scope record](../provenance/analysis_scope.json)
states the boundaries explicitly.

Separately written implementations and passing tests are computational
cross-checks. They are not an external human peer-review endorsement or a
reconstruction of the original author's complete 2022 dependency environment.
The [prior-art search](prior-art.md) is bounded and does not establish
worldwide priority.

## Archived evidence

Earlier execution records retain their original dates and scope:

| Record | Scope |
|---|---|
| [Quality acceptance](../results/current-verification/quality-pass/) | Commands, source hashes and the 68-test local run |
| [Earlier local run](../results/current-verification/run.json) | A preceding 36-test snapshot |
| [Earlier publication observation](../results/current-verification/publication.json) | Initial source publication and CI for `dcd4a58` |
| [Supplied-package records](../results/local-verification/) and [release-verification records](../results/release-verification/) | Earlier package snapshots, including PHP 8.3.6 execution and source/header downloads |

The historical directory names are retained for stable references. Their
[index](../results/current-verification/README.md) distinguishes the snapshots;
a folder name is not a claim about which commit was executed.
