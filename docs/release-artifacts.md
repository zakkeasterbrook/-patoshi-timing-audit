# Build and inspect a portable candidate

The source repository is the primary evidence. A portable archive makes the
same frozen inputs, code, documentation and complete result rows available
without a GitHub checkout. It is not a substitute for scientific review.

## Reproduce before packaging

Run the commands in the [reviewer guide](reviewer-guide.md), including fresh
native PHP where available. Record the actual tests, failures and skips. Then
review intentional changes and explicitly refresh the project-file checksums:

```sh
python3 scripts/update_manifest.py
python3 scripts/verify_manifest.py
git diff -- SHA256SUMS.txt
```

Do not regenerate a checksum to hide an unexplained mismatch, change the pinned
inputs, or force a reported numerical target. Commit only reviewed changes.
Packaging requires a **clean, committed Git checkout**:

```sh
python3 scripts/build_release.py --version 1.0.0-rc.1
```

The command verifies exact project-file coverage, compares worktree digests
with the committed blobs, and archives that exact commit. Uncommitted or
untracked content cannot be represented as verified committed content. Builds
write to `build/release/` by default and never modify source or frozen results.

## Artifacts and verification

The generated files are:

- `Patoshi_Timing_Audit_v1.0.0-rc.1.zip`: the complete manifested project in
  `patoshi-timing-audit/`, plus a top-level `RELEASE_MANIFEST.json`.
- `SHA256SUMS.txt`: the downloadable archive's SHA-256 and filename.
- `release.json`: the commit, version, byte count, digest and packaging scope.

The top-level release manifest records the exact commit and every source
file's size/digest. It lives outside the enclosed source directory so the
source-file manifest verifies unchanged after extraction. It does not hash
itself or claim an independent signature.

For the downloaded ZIP, first compare its SHA-256 with the published checksum.
After extraction, run from `patoshi-timing-audit/`:

```sh
python3 scripts/verify_manifest.py
python3 reproduce.py
python3 scripts/check_direct.py
```

ZIP entries use sorted paths, stored bytes without compression, fixed regular
file modes, and fixed 1980-01-01 container timestamps. These choices make the
archive byte-reproducible for the same committed input and version. Container
timestamps are format constants; they do not backdate publication. The source
commit time is retained separately in the release manifest. Tests compare
independent builds and verify an extracted archive's original source manifest.

## What CI establishes

The [workflow](../.github/workflows/verify.yml) configures offline Python
3.10/3.12/3.14 checks, Windows verification and native PHP. Its candidate job
depends on successful offline and native jobs, then uploads the complete
archive/checksum/report as `Patoshi-Timing-Audit-candidate`.

Inspect the actual run for the exact commit. Local archive construction alone
verifies artifact identity and completeness; it does not execute PHP or imply
that hosted tests passed. A CI artifact is also distinct from a tagged GitHub
Release. The [publication procedure](../PUBLISHING.md) records the remaining
release steps, and [verification status](verification.md) identifies unavailable
inputs and optional online checks. No archive independently establishes miner
identity or validates a historical classification.
