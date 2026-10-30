# Third-party materials and license scope

The [MIT license](LICENSE) applies to the newly authored audit code and documentation. It does **not** relicense upstream source, third-party publications or historical data. The project makes no ownership claim over blockchain facts, historical classifications or factual provenance records.

## Original timing script

The audited source is Jameson Lopp's [`findNonPatoshiDeltasAfterFastPatoshiBlocks.php`](https://github.com/jlopp/bitcoin-utils/blob/66ee906b28ca13269d6f71d63f848973a1b747a2/findNonPatoshiDeltasAfterFastPatoshiBlocks.php), pinned to commit:

```text
66ee906b28ca13269d6f71d63f848973a1b747a2
```

The fresh licensing inspection found no repository-wide license file or target-script license grant. GitHub's repository metadata reported `license: null`, and the pinned license endpoint returned 404. Some unrelated subfiles carry MIT notices; those notices do not establish a license for the audited script. [The license scan](provenance/source-review/license_scan.json) records the inspected paths.

The complete original script is **not bundled**. The source-fetch command downloads its pinned bytes directly from the upstream repository and verifies the expected digest. The audit includes a minimal relevant [patch](provenance/timestamp_fix.patch), source references and integrity metadata. Any rights in the upstream source remain with its rights holders.

## Historical inputs

- **Bitcoin headers:** [data/headers_0_49999.bin](data/headers_0_49999.bin) contains public mainnet header bytes obtained from [Electrum's header archive](https://download.electrum.org/blockchain_headers). Additional factual header observations came from [Blockstream](https://blockstream.info/) and [mempool.space](https://mempool.space/). The audit's MIT grant does not claim ownership of or relicense these historical bytes.
- **Classification list:** [data/patoshi_heights.json](data/patoshi_heights.json) preserves the numerical array from the pinned Lopp script. It is credited to that source and the earlier Patoshi research by Sergio Demian Lerner. It is an attributed input, not a newly asserted classification or an independently licensed copy of the upstream program.
- **Provenance:** GitHub metadata, Internet Archive capture metadata, source URLs, hashes and retrieval observations are retained to make the audit checkable. Their inclusion does not imply endorsement by the source providers.

## Publications and runtime components

The audit links to [Lopp's original article](https://blog.lopp.net/was-satoshi-a-greedy-miner/) and the [earlier research](docs/prior-art.md). Full third-party articles, archived HTML, screenshots and downloaded method documents are not included.

PHP and Python runtimes are not distributed here. The native harness uses a newly written offline adapter for the small RPC/response interface called by the original script; it does not bundle the upstream Denpa library or claim to reproduce the author's complete dependency environment.

The optional plotting script requires an independently installed `matplotlib`. The numerical reproduction and regression tests use Python's standard library. The repository's PNG and SVG comparison figures are generated from the audit's reproduced results, rather than copied from the original article.

For exact source versions, hashes and verification records, see [provenance](docs/provenance.md).
