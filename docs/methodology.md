# Methodology and reproducibility

## Inputs and provenance

The main universe is Bitcoin mainnet heights **0–49,999 inclusive**. The binary
input is exactly 50,000 consecutive 80-byte headers from genesis, SHA-256
`b9e200ba15c904e05283461469d5582a9580df15ff842436576a7490454b03ec`.
The canonical JSON serialization of the 21,953 original labels has SHA-256
`33c9927845ccd3016fb37bc2b860cfe7a3fea22522c67649d72c6dc50e9ae8e1`.
The source, acquisitions and saved explorer observations are described in
[provenance](provenance.md).

The exact original PHP commit is
`66ee906b28ca13269d6f71d63f848973a1b747a2`. Full upstream source is fetched
on demand and digest-checked rather than redistributed under the audit's
license. After fetching, verify the source list with:

```sh
python3 scripts/verify_source_labels.py --source build/original.php
```

## Header authentication

For height `h`, read bytes `[80*h, 80*(h+1))`. Hash the complete header twice
with SHA-256. Reverse the digest for the conventional displayed block hash;
the next serialized header's previous-hash field must equal the unreversed
digest. Header offsets 68, 72 and 76 hold the little-endian timestamp, compact
difficulty value and nonce, respectively.

Check mainnet genesis, positive permitted targets and proof of work. Between
retarget boundaries the difficulty value is unchanged. At multiples of 2,016,
use the previous header time minus the time 2,016 heights earlier, clamp the
span to one-quarter through four times two weeks, scale the previous target,
cap it at the mainnet limit and encode it compactly. There are 24 such
boundaries in this input. Each non-genesis timestamp must exceed the median
of the preceding up-to-11 timestamps.

These are header validation and chain-anchoring checks. They do not revalidate
transactions, scripts, historical node clocks or the contemporary future-time
acceptance rule.

## Three calculations

P means membership in the fixed published list; N means absence within this
universe. Never sort by timestamp. Consecutive heights A, B, C are eligible
under the stated rule when their labels are PPN and `tB - tA <600`. The
measurement is `tC - tB`. There is no nonnegative lower bound on the preceding
difference, and an outcome of exactly 300 is excluded from `<300`.

The published mode preserves the wrong-object assignment and the original
tracker, including its greater-than-two requirement, discarded reset height
and absent final flush. The assignment-only mode changes just the defective
assignment. The direct mode enumerates every three-height window. The final
legacy tracker is empty on these labels, so a missing final flush does not
change the historical totals.

Each CSV is compared with the archived expected rows in order and byte for
byte. The generated event records retain both intervals and all three heights;
mode membership and diagnostics make sample changes explicit. Below-300
counts include negative values, and all rates use their mode's own denominator.

## Follow-up definitions

[`followup.py`](../scripts/followup.py) exports complete rows for PPN and NPN
with preceding differences below 600, and with the common range 300–599.
All adjacent pairs are partitioned by their two labels. Medians are ordinary
sample medians of the integer timestamp differences.

For the exploratory common-range standardization, this repository assigns an
era using **parent height B divided by 10,000**, and a band using the preceding
difference divided by 100. The 15 common-range cells each contain PPN and NPN
observations. Compute each NPN cell's rate, weight it by that cell's fraction
of all PPN observations, and sum. The earlier follow-up script was not bundled;
this explicit reconstruction reproduces the recorded rounded targets. It is
not represented as execution of a recovered earlier script.

The later-period diagnostic requires every participating height to be at least
541 and excludes any pair or triple touching 1,400–1,916 inclusive. For nonce
comparisons, R denotes a raw byte at header offset 76 in 0–9 or 19–58 inclusive;
O denotes its complement. Check every serialized nonce byte separately to
make byte order explicit. These groups are descriptive, not independent miner
identification or validation of the attribution list.

## Execution and outputs

From the repository root, the standard-library offline command is:

```sh
python3 reproduce.py
python3 scripts/check_direct.py
python3 -m unittest discover -s tests -v
```

`reproduce.py --output-dir <directory>` supports generation away from saved
evidence. Compare the outputs before replacing frozen files. Follow-up outputs
can also be generated using
`python3 scripts/followup.py --output-dir <directory>`.

Fresh PHP execution requires a PHP 8 CLI and the verified source:

```sh
python3 scripts/fetch_original_source.py build/original.php
python3 scripts/run_native.py --php php --source build/original.php
PATOSHI_TEST_PHP=php PATOSHI_TEST_SOURCE="$PWD/build/original.php" \
  python3 -m unittest discover -s tests -v
```

The PHP harness uses `-n` and a documented offline RPC adapter. It executes the
unchanged source and a temporary one-assignment variant, then compares their
complete outputs with Python. This adapter does not recreate the author's
complete 2022 dependencies. Actual run versions and outcomes belong in
[current verification](verification.md), separate from preserved archive logs.

Optional figure dependencies are separate from the numerical calculation.
A live source check is an additional network operation, not a prerequisite
for the frozen-input offline calculation. A clean-checkout pass is not proof
that a hosted CI job or public release has completed.
