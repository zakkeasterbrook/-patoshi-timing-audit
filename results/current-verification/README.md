# Execution-record index

For the latest inspected candidate, start with [results/status.json](../status.json)
and the [verification page](../../docs/verification.md). They identify source
tag `v1.0.0-rc.1`, commit `59d150f9d95c572f539705561f71f1e248ef2a36`, and
[successful hosted run 41086244756](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/runs/41086244756).

This directory retains successive records, not a live aggregate dashboard.
The name is preserved so existing evidence links remain valid. Each JSON/log
belongs to its own recorded date, source hashes and execution mode.

| Snapshot | Date | Scope |
|---|---|---|
| [`quality-pass/run.json`](quality-pass/run.json) and adjacent logs | 30 October 2026, 15:55 UTC | Local quality-expansion acceptance: 68 tests passed with PHP enabled, zero skips; full Python/native agreement; unchanged original case CSVs. Source-file hashes identify the inspected code. |
| [`run.json`](run.json) and adjacent logs | 30 October 2026, 15:17 UTC | Earlier acceptance: 36 tests passed with PHP enabled. These files are not the later candidate's full test report. |
| [`publication.json`](publication.json) | 30 October 2026, 15:31 UTC | Initial publication and hosted CI for `dcd4a58`. Statements about then-missing disputed labels and access failures describe that observation, not current evidence requirements. |
| [`source_verification.json`](source_verification.json) | 30 October 2026, 15:05 UTC | Fresh pinned PHP bytes and label-only tracker checks; explicitly not timestamp-dependent totals. |

The 68-test local acceptance preceded the final Windows archive-fixture
correction. The exact candidate-commit hosted run includes that correction
and covers the expanded Linux/Windows, PHP and archive jobs. Eight native
tests skip when the required PHP/source environment is absent; such a run
must not be described as fresh native verification.

The separate [`local-verification/`](../local-verification/) and
[`release-verification/`](../release-verification/) directories preserve earlier
supplied-package evidence. None of these directory names alone establishes a
formal GitHub Release. Historical records have not been overwritten to make
their timestamps, counts or publication state look current.
