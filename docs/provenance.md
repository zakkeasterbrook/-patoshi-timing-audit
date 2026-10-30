# Source and data provenance

The timing calculation uses two fixed inputs: the raw Bitcoin header prefix and the numerical classification list extracted from a pinned source file. Verification records are kept under [provenance/](../provenance/). Acquisition timestamps are in UTC on **30 October 2026**.

## Inputs

| Input | Coverage | Origin |
|---|---|---|
| [Raw headers](../data/headers_0_49999.bin) | 50,000 consecutive 80-byte headers; heights 0–49,999 | [Electrum header archive](https://download.electrum.org/blockchain_headers) |
| [Classification list](../data/patoshi_heights.json) | 21,953 unique ascending heights; minimum 3, maximum 49,973 | Numerical array in the pinned Lopp script |
| Original PHP source, fetched separately | 125,172 bytes | [`jlopp/bitcoin-utils`, pinned commit](https://github.com/jlopp/bitcoin-utils/commit/66ee906b28ca13269d6f71d63f848973a1b747a2) |

The complete original PHP source is not bundled. [The fetch script](../scripts/fetch_original_source.py) accepts only its expected size and SHA-256. The classification list is a fixed historical input; reproducing its output does not independently validate its attribution decisions.

### SHA-256 values

Raw header bytes:

```text
b9e200ba15c904e05283461469d5582a9580df15ff842436576a7490454b03ec
```

Classification array, serialized as compact JSON without a trailing newline:

```text
33c9927845ccd3016fb37bc2b860cfe7a3fea22522c67649d72c6dc50e9ae8e1
```

Pinned upstream PHP bytes:

```text
104d0df1854802a2e0a5333fda51ee657bb2b17006a48f820bc446c21993e119
```

The classification digest is a canonical-content hash, rather than necessarily the byte hash of an indented JSON file. The loader checks the canonical representation explicitly. See [header acquisition](../provenance/header_download.json), [label extraction](../provenance/label_provenance.json) and [input checks](../scripts/inputs.py).

## Original source verification

The original source is pinned to:

```text
66ee906b28ca13269d6f71d63f848973a1b747a2
```

That commit records the script's addition on **15 September 2022 at 20:49:17 UTC**. A fresh raw HTTPS retrieval and a separate shallow Git-protocol fetch returned identical PHP bytes. Recomputing the Git commit-object hash reproduced the pinned commit, and the file's recomputed blob hash matched its entry in the commit tree:

| Git object | Hash |
|---|---|
| Root tree | `56f3b83fa8b748a4e9e7c37752b8a5305db731e5` |
| Target PHP blob | `905ab04b5fece476eda19b4b32a0bd749a0e9327` |

GitHub reports the commit's PGP signature as valid. That service report is recorded separately from the local object-hash checks; the signer's key identity was not independently verified locally. The timestamp assignment under review is present at line 30 of the pinned file.

Records: [source verification](../provenance/source-review/source_verification.json), [Git-protocol verification](../provenance/source-review/git_protocol_verification.json) and [upstream file history](../provenance/prior-art/file_history.json).

## Article and archive

The source article is [Jameson Lopp, *Was Satoshi a Greedy Miner?*](https://blog.lopp.net/was-satoshi-a-greedy-miner/). Its metadata gives a publication time of **16 September 2022 at 13:25:07 UTC**. The live page links the affected script and reports **1,881 selected cases, 1 negative difference and 5 differences below five minutes**, with the printed percentage 0.3%.

The [earliest inspected archive capture](https://web.archive.org/web/20220916132943/https://blog.lopp.net/was-satoshi-a-greedy-miner/) is from **13:29:43 UTC on the same day**. A fresh retrieval of that capture reproduces the same figures. The affected timing passage is identical after removing HTML and collapsing whitespace:

```text
9b40e4309bf6ab1436329c93041505040e0471ce6aa7604e2e4f8c94b6f32f88
```

That hash covers a **1,422-character passage**, not the complete article. The documented broader archive search inspected 26 distinct-digest HTML captures through 31 August 2026; all contained the same normalized passage. This establishes agreement among the inspected snapshots. It does not establish that the entire article remained unchanged or exclude edits between captures.

Records: [live passage metadata](../provenance/source-review/lopp_article_verification.json), [fresh original-day retrieval](../provenance/source-review/fresh_lopp_archive_verification.json), [archive index response](../provenance/prior-art/archive_cdx.json) and [capture checks](../provenance/prior-art/archive_passage_checks.json).

## Header validation and external anchors

The initial acquisition requested bytes `0–3999999` from the Electrum archive and received a 4,000,000-byte HTTP 206 response. The reproduction checks:

- The known Bitcoin mainnet genesis hash and every previous-hash link.
- Each header's proof of work and permitted target.
- Every difficulty value, including all **24 retarget boundaries** in this prefix.
- Median-time-past conditions for every non-genesis header.
- The exact input SHA-256 and canonical classification-list hash.

Recorded comparisons cover heights **265, 8,827, 22,565, 24,143 and 49,999** at both Blockstream and mempool.space. All ten recorded header/hash observations match the bundled bytes. The final matched header hash also commits to the preceding linked sequence under the hash function. [The anchor records](../provenance/independent_explorer_anchors.json) include the provider URLs and returned values.

The offline command checks those saved observations; it does not make live explorer requests. A separate [fresh archive check](../scripts/verify_live_headers.py) verifies the downloaded prefix against the bundled bytes. Its latest local result is recorded in [live_header_verification.json](../results/local-verification/live_header_verification.json).

These checks authenticate and validate the header input used by this calculation. They are not a new full-block synchronization or a revalidation of transaction scripts. Historical node clocks are unavailable for reconstructing the contemporaneous two-hour future-time check.

## Outputs and runtime evidence

The three [expected CSV files](../results/expected/) record native-PHP results with a descriptive CSV header. The Python reproduction requires every row, its order and the complete generated CSV bytes to match. The native runner executes PHP again and compares its outputs with fresh Python results.

Small records from the current local run are available as [summary.json](../results/local-verification/summary.json) and [native_verification.json](../results/local-verification/native_verification.json). They identify the inputs and actual runtime used. Current runnable commands are documented in the [README](../README.md).

The [fresh-copy acceptance record](../results/local-verification/fresh_copy_acceptance.json) documents execution from a separate local copy, including runtime details, commands and hashes of the tested files. Its claims apply to the recorded snapshot and matching files. Consult [verification status](verification.md) for the distinction between local execution, configured CI and external human review.

## Reuse of third-party material

The repository includes numerical historical inputs, factual metadata, a minimal source patch and the newly written audit materials. Full third-party articles and the original upstream PHP file are not bundled. [THIRD_PARTY.md](../THIRD_PARTY.md) records attribution and the limits of this project's license.
