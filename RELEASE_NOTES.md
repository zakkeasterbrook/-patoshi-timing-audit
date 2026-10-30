# Patoshi Timing Audit v1.0.0 candidate

A reproducible correction to the three-block timing test linked from Jameson
Lopp's 2022 article, *Was Satoshi a Greedy Miner?*

The original PHP code assigns the first block's time to the second block's
variable. This defeats the time filter and measures C-minus-A instead of
C-minus-B. Separate run-tracking behavior omits eligible sequences.

For blocks 263–265, the preceding difference is 559 seconds and the intended
following difference is 71 seconds. The original implementation emits 630.

| Version | Cases | Negative | All differences <300 seconds |
|---|---:|---:|---:|
| Original | 1,881 | 1 | 5 (0.27%) |
| One assignment repaired | 400 | 10 | 144 (36.00%) |
| Direct stated rule | 754 | 30 | 276 (36.60%) |

The samples have different denominators. The below-300 counts include negative
values. These are block-header timestamp differences, not independently
measured elapsed mining times.

The candidate contains frozen inputs, complete per-case outputs, pinned
provenance, one-command offline Python reproduction, a separate direct
calculation, native PHP comparison, regression tests and generated figures.
The follow-up exports complete original-label comparison sequences, adjacent
pairs, era/gap adjustment cells and nonce-byte diagnostics.

Fresh PHP 8.4.27 execution with the offline RPC adapter matches every Python
CSV byte for the unchanged source, one-assignment repair and direct rule.
Archived PHP 8.3.6 records are retained separately. Neither run reconstructs
the author's complete 2022 environment.

From the repository root:

```sh
python3 reproduce.py
python3 scripts/check_direct.py
python3 -m unittest discover -s tests -v
```

See [verification status](docs/verification.md) for actual current command logs,
native-test setup, hosted-CI state and missing follow-up inputs. The Bitquery
classification-sensitivity input and the exact three-disputed-label experiment
remain unverified. A configured workflow is not a passing hosted run, and this
candidate file does not establish that a public release exists.

The correction concerns one published timing test. It does not disprove the
broader Patoshi pattern, identify Satoshi or determine whether a miner paused.
External human review remains pending.
