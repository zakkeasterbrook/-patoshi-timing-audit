# Release artifacts

The [v1.0.0 release](https://github.com/zakkeasterbrook/-patoshi-timing-audit/releases/tag/v1.0.0)
contains the code, frozen inputs, complete numerical evidence and documentation.
Its archive is a portable copy of the tagged source tree, not an additional
source of scientific observations.

## Download and verify

| Asset | Contents |
|---|---|
| `Patoshi_Timing_Audit_v1.0.0.zip` | Complete project under `patoshi-timing-audit/`, plus a top-level `RELEASE_MANIFEST.json` |
| `SHA256SUMS.txt` | The archive's SHA-256 digest and filename |
| `release.json` | Artifact type, exact source commit, version, byte count and digest |

First compare the downloaded archive's SHA-256 with the published checksum.
On a system with `sha256sum`, run beside the downloaded assets:

```sh
sha256sum --check SHA256SUMS.txt
```

After extraction, run from `patoshi-timing-audit/`:

```sh
python3 scripts/verify_manifest.py
python3 reproduce.py
python3 scripts/check_direct.py
```

The first command verifies exact source-file coverage and every recorded
digest. The next two regenerate the numerical evidence and independently
cross-check the stated rule. Core reproduction uses Python's standard library
and frozen local data. Fresh native-PHP instructions are in the
[reviewer guide](reviewer-guide.md).

A matching checksum detects a mismatch against the published artifact. It is
not an independent signature, scientific endorsement or proof of authorship.

## The two manifests

The archive's top-level `RELEASE_MANIFEST.json` records the exact Git commit
and each source file's size and digest. It lives outside the enclosed source
directory so the original project-file manifest can verify unchanged.

Inside `patoshi-timing-audit/`, the repository's `SHA256SUMS.txt` covers the
complete published project-file inventory. It is distinct from the release
asset of the same name, which hashes the downloadable ZIP. The generated
release manifest does not hash itself.

## Rebuilding the same archive

From a clean checkout of `v1.0.0`:

```sh
python3 scripts/build_release.py --version 1.0.0
```

The builder verifies the complete source inventory, compares worktree digests
with committed blobs, and writes the archive, checksum and packaging report
to `build/release/`. Uncommitted and untracked changes cannot be represented
as the verified Git tree.

Archive members have sorted paths, stored bytes without compression, fixed
regular-file modes and fixed 1980-01-01 container timestamps. Those timestamps
are format constants, not publication dates. The source commit time is
recorded separately. The same source commit and version produce identical
archive bytes; tests compare independent builds and verify the extracted
project's original source manifest.

Changing the version or source commit changes the artifact identity. An
archive built from another `main` commit is not interchangeable with the
tagged v1.0.0 asset.

## Release validation

The [workflow](../.github/workflows/verify.yml) checks Linux on Python
3.10/3.12/3.14, Windows on Python 3.12 and actual native PHP execution. The
portable-archive job depends on successful offline and native verification.
Its build artifacts use the name `Patoshi-Timing-Audit-package`.

For a version tag, the release-publishing job runs only after those checks.
The [workflow results](https://github.com/zakkeasterbrook/-patoshi-timing-audit/actions/workflows/verify.yml)
identify the executed commit and job outcomes. The downloadable metadata
records the exact commit contained in the release.

Archive construction verifies artifact identity and completeness. Scientific
claims depend on the reproduced calculations and their stated
[scope](verification.md), not on the existence of a ZIP file.
