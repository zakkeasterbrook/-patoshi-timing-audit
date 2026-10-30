# Verification status

The three calculations are checked separately against fixed inputs. Local
execution, archived execution, hosted CI and a published release are distinct
claims. A release is not established by these files alone.

## Current implementation checks — 30 October 2026

The current work freshly reproduced all three Python calculations from the
bundled binary headers. Every saved CSV row, its order and its bytes matched:

| Calculation | Cases | Negative | All differences <300 s |
|---|---:|---:|---:|
| Published implementation | 1,881 | 1 | 5 |
| One assignment repaired | 400 | 10 | 144 |
| Direct stated rule | 754 | 30 | 276 |

The below-300 counts include negative values. The samples have different
denominators; the original output is C-minus-A and corrected outputs are
C-minus-B. Zero, positive-below-300 and at-least-300 counts are also exposed in
the machine-readable summary.

The freshly fetched original PHP source is 125,172 bytes with SHA-256
`104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119`.
The extracted 21,953 labels match the bundled list exactly.

**Native PHP was freshly executed using PHP 8.4.27**, obtained from signed
Debian package metadata and extracted locally. Configuration loading was
explicitly disabled with `-n`. The unchanged pinned source, the temporary
one-assignment repair and the direct PHP routine all matched fresh Python
output byte for byte. The interpreter is not bundled. Adapter tests check
lookup behavior, stable response objects and missing-data failures. This is
not a reconstruction of the author's complete 2022 Composer/node environment.

Current command records belong in [current verification](../results/current-verification/).
The [quality-expansion record](../results/current-verification/quality-pass/run.json)
records 68 passing local tests with zero skips, a fresh complete native-PHP run,
and unchanged original case CSVs. It identifies the checked source-file hashes;
hosted execution must still be inspected for the final published commit.
The [reproduced evidence](../results/reproduced/) contains deterministic
summaries, all event rows, mode differences, minimal-example evidence and the
original-label follow-up tables. The test log records the actual method count,
failures and skips; do not substitute an older package's test count.

## Checks performed by the offline command

- Exactly 50,000 serialized headers with the pinned 4,000,000-byte digest.
- Known mainnet genesis, displayed/internal hash byte order and every previous-hash link.
- Compact targets, proof of work, the mainnet limit and all difficulty rules,
  including the 24 retarget boundaries in scope.
- Median-time-past constraints using preceding available headers.
- Strict input-label type, uniqueness, range and digest checks.
- All three output CSVs against archived rows and exact bytes.
- Original-label follow-up comparisons, complete adjacent pairs, sensitivity
  exclusions, nonce-byte diagnostics and descriptive standardization.
- The separately cited three-label sensitivity, with every selected row and
  an unchanged main classification list.
- Complete frozen-reference inventories. Missing evidence cannot silently
  disable comparison. Outputs are staged and checked before publication;
  existing linked paths are rejected and unrelated build files are preserved.

The second direct calculation independently decodes raw timestamps and
compares every stated-rule row. Regression tests cover sequence selection,
strict thresholds, malformed inputs, altered headers and native adapter
semantics. Use the saved command logs for the final suite outcome.

## Archived records preserved from the supplied package

[`results/local-verification/`](../results/local-verification/) and
[`results/release-verification/`](../results/release-verification/) are preserved
records from before this implementation session. They describe their own tested
snapshots, including PHP 8.3.6, earlier fresh-source/header downloads, fixture
runs and same-host fresh-copy acceptance checks. Those observations have not
been relabeled as current executions. Their older critical-file hashes need
not match files subsequently changed here.

The ten saved observations in
[`provenance/independent_explorer_anchors.json`](../provenance/independent_explorer_anchors.json)
cover five heights against two explorers. The offline command matches their
headers and hashes, but performs no live explorer query.

## Network and publication state

The current Electrum prefix request was denied with HTTP 403 before downloading
the input. Its current network host, explorer hosts and publication API hosts
were requested in the environment configuration draft. A saved draft does not
activate that access. This does not affect calculation from the frozen local
headers, but the older live-prefix record is not a new online verification.

The GitHub repository is
[`zakkeasterbrook/-patoshi-timing-audit`](https://github.com/zakkeasterbrook/-patoshi-timing-audit).
The leading hyphen is part of its name. The
[workflow](../.github/workflows/verify.yml) configures offline Linux/Windows
reproduction and native PHP checks. **The hosted run passed for implementation
commit `dcd4a581041763daa970095a91fc3caa6fac5b6c`, published on `main`.**
[Actions run 41080882699](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41080882699)
reports success, including both offline matrix targets and native PHP. The
optional manual-trigger header-acquisition job was skipped. The result was
observed through GitHub's public Actions page; API access remains unavailable.
See the [publication record](../results/current-verification/publication.json).
Publication instructions are in [PUBLISHING.md](../PUBLISHING.md).

No tagged release or release asset upload has been observed. Hosted CI success
does not establish either a release or fresh execution of the optional online
provenance check.

## Outstanding evidence and limits

The Bitquery CSV and its follow-up scripts are not in the supplied package;
that classification-sensitivity calculation has not been reproduced. Its
reported numbers are not presented as fresh results. The separate three-label
experiment is now source-supported and reproduced: 753 cases, 30 negative and
276 below 300 seconds, with only child 24,505 removed. The original list remains
unchanged throughout the main audit.

The robustness expansion adds direct contextual MTP/difficulty rejection
tests, exact manifest/reference coverage, output failure/link regressions,
and deterministic archive identity tests. See
[`tests/test_header_rules.py`](../tests/test_header_rules.py) for the explicit
one-header hash stand-in used solely to isolate contextual unit-test branches;
the genuine 50,000-header validation always hashes the actual bytes.

Header validation and recorded chain anchoring do not revalidate transactions,
script execution or historical receiving-node clocks. Contemporaneous
future-time checks cannot be reconstructed from this input. Header timestamp
differences do not independently measure elapsed mining times or identify a
miner. External human review and worldwide priority remain unestablished.
