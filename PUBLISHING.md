# Release policy

Stable releases are immutable source snapshots identified by a `vMAJOR.MINOR.PATCH` Git tag. The release archive records the full commit and the size and SHA-256 of every source file. Previously published tags and assets are not moved or silently replaced.

## Verification gates

The [verification workflow](.github/workflows/verify.yml) checks:

- Offline reproduction and regression tests on Linux with Python 3.10, 3.12 and 3.14, and Windows with Python 3.12.
- Fresh execution of the pinned PHP source and assignment repair against verified offline headers, including complete byte-for-byte output comparison.
- Exact file-manifest coverage and deterministic source-archive construction.

Branch builds produce development archives labelled with their commit. Stable-tag builds use the tag's version. The archive filename is not a substitute for checking its recorded commit.

## Publication and asset checks

On a stable version tag, the release job runs only after the required verification and packaging jobs succeed. It builds the archive from that tagged tree, stages the release notes and three assets as a draft, then downloads them again and requires byte-for-byte equality before publication:

- `Patoshi_Timing_Audit_v<version>.zip`
- `SHA256SUMS.txt`
- `release.json`

The publication token is limited to repository-content writes in the release job. Checkout does not persist credentials. Existing releases are verified rather than overwritten.

For local archive construction, use a clean checkout of the release tag:

```sh
python3 scripts/build_release.py --version 1.0.0
```

See [artifact contracts](docs/release-artifacts.md) for extraction, checksums and reproduction. Scientific validation, source-file integrity, archive identity and publication are distinct checks; release metadata records their scopes.
