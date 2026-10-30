# Regression tests

The historical replication establishes what the scripts produce on the
published 50,000-header input. These additional tests check specific boundary
and sequence cases that the historical input alone might not exercise.
They do not repeat the historical computation or test a miner's identity.

## Run the Python checks

From the repository root:

```sh
python3 -m unittest discover -s tests -v
```

Only Python's standard library is required. The native PHP tests are explicitly
reported as skipped unless both environment variables below are provided.
Skipping them is not reported as a successful native execution.

## Run the native PHP checks too

First retrieve the pinned external source with the repository's source-fetch
instructions. Set these two variables, then run the same command. The PHP
variable accepts an absolute executable path or a command available on `PATH`;
the source variable identifies the local file:

```sh
PATOSHI_TEST_PHP=/absolute/path/to/php \
PATOSHI_TEST_SOURCE=/absolute/path/to/patoshi-original.php \
python3 -m unittest discover -s tests -v
```

The source must have SHA-256
`104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119`.
The tests reject a different source. The recorded execution used PHP 8.3.6.
They use `-n` to avoid loading a user PHP configuration.

## What is covered

Fifteen manually specified fixtures in `tests/timing_fixtures.json` cover:

| Case | Required behavior |
|---|---|
| Exactly two consecutive P heights | Select the following N child when AB is below 600 seconds. |
| A later qualifying run | Retain the current P height when it begins the next run. |
| AB = 559, BC = 71 | Measure 71 seconds; AC = 630 is the wrong interval. |
| AB = 599 versus 600 | Include 599; exclude exactly 600. |
| Negative or zero AB | Apply the stated AB <600 rule without silently adding a lower bound. |
| BC negative, zero, 299, or 300 | Retain every selected row; count strict threshold categories correctly. |
| P/P/P or nonconsecutive P heights | Exclude them from the consecutive P/P/N test. |
| Terminal P run with an available N child | The direct rule includes that child even without a later P to break the run tracker. |
| Child beyond the available prefix | Produce no measurement; the original native loop explicitly reports missing data. |

Each expected selected height and timestamp difference is written in the
fixture data. The Python tests call `scripts/timing.py`; they do not use a
second selection algorithm to manufacture expected outputs.

The optional native checks perform 75 PHP invocations: five variants for
each fixture. They compare the original and one-assignment-repaired logic to
the Python emulation, and compare the direct PHP rule to the handwritten
expected outcomes. Two further diagnostic variants isolate the run-length
condition and discarded run head. Those variants are explanatory and are
not promoted as additional historical estimates.

## Synthetic inputs and source changes

The fixtures contain integer timestamps, classification sets, and synthetic
lookup identifiers. They contain no serialized Bitcoin headers and are not
presented as consensus-valid blocks or observations of actual miners.

For native fixture execution, the test replaces the fetched source's numeric
classification array with a small synthetic array in a temporary file. The
named diagnostic variants also change the relevant assignment or run-control
lines. The supplied original source is never overwritten; all modified copies
are deleted afterward. These are modified semantic test inputs, distinct from
the unchanged-source execution used for the historical replication.

The missing-final-flush example is an artificial edge case. The real published
classification input ends with an empty tracker, so that omission makes no
change to the reported historical totals. Similarly, the negative-AB example
shows why output inflation cannot be assumed for every possible input. The
positive AB gaps in all 1,881 original historical cases were checked separately.

## Scope of the checks

Passing these fixtures verifies the specified sequence and threshold behavior
and checks the emulation against actual PHP on those cases. It does not validate
the supplied miner classifications, prove a clock or mining-pause mechanism,
establish publication priority, or constitute external human peer review.
