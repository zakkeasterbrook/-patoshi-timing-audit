# Inputs

| File | Contents | Size or count |
|---|---|---:|
| `headers_0_49999.bin` | Consecutive 80-byte mainnet headers, starting at genesis | 4,000,000 bytes |
| `patoshi_heights.json` | The P-labelled heights in the pinned 2022 PHP source | 21,953 integers |

The raw-header SHA-256 is
`b9e200ba15c904e05283461469d5582a9580df15ff842436576a7490454b03ec`.

The label-list SHA-256, after compact JSON encoding with no spaces or trailing
newline, is
`33c9927845ccd3016fb37bc2b860cfe7a3fea22522c67649d72c6dc50e9ae8e1`.
This canonical-content hash is intentionally different from a pretty-printed
file's byte hash.

Each header occupies bytes `80*h` through `80*h+79` for height `h`.
The timestamp is a four-byte little-endian integer at offset 68 within the
header. `python reproduce.py` verifies the binary chain and writes all decoded
fields to `build/headers_0_49999.json`.

N means a height absent from this particular classification list. The labels
are retained as supplied; this audit does not independently identify miners.

See [provenance](../docs/provenance.md) for source URLs and acquisition records,
and [third-party materials](../THIRD_PARTY.md) for attribution and license scope.
