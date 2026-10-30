# Publish the verified audit

Use the existing repository:

**https://github.com/zakkeasterbrook/-patoshi-timing-audit**

The leading hyphen is part of its name. Do not create or rename a repository.
Use the existing checkout and authorized Git/GitHub authentication. Inspect the
remote and current branch, preserve existing work, and respect branch protection
and required reviews. Do not force-push or move an existing published tag.

## Validate the candidate

From the repository root:

```sh
python3 scripts/verify_manifest.py
python3 reproduce.py
python3 scripts/check_direct.py
python3 scripts/fetch_original_source.py build/original.php
python3 scripts/verify_source_labels.py --source build/original.php
python3 scripts/run_native.py --php php --source build/original.php
PATOSHI_TEST_PHP=php PATOSHI_TEST_SOURCE="$PWD/build/original.php" \
  python3 -m unittest discover -s tests -v
```

Use the actual PHP executable path when it is installed locally. Core tests can
run without PHP, but skipped native tests do not establish fresh native
verification. Keep current command logs separate from archived package records.
Optional live-source checks must report their own success or failure.

Rebuild the result tables and figures from verified inputs. Check relative
links, notices, the release contents and file checksums. Regenerate the file
manifest only after final edits; do not change expected data to hide a mismatch.
The [verification note](docs/verification.md) records current outcomes and
outstanding evidence.

## Commit through the existing repository workflow

Review the complete diff and verify that generated evidence belongs to the
current run. Commit with the repository's configured author identity. Push a
normal branch to the existing origin. If required reviews or protection rules
apply, open a pull request and wait for the actual merge requirements; do not
claim `main` changed while a gate remains unmet.

The intended destination is `main`. Record the full final commit SHA rather
than relying on a branch name that can move. Use the GitHub CLI with an explicit
repository selector, for example:

```sh
gh run list --repo zakkeasterbrook/-patoshi-timing-audit --commit "$verified_commit"
gh run view "$run_id" --repo zakkeasterbrook/-patoshi-timing-audit
```

All required offline Linux/Windows and native jobs must pass for the actual
release commit. Record the run URL and job outcomes. A workflow file, successful
local run or archived log is not hosted CI evidence. Diagnose network-provenance
failures separately from numerical mismatches.

## Tag and verify the release

Check whether `v1.0.0` already exists. Use it only if available and appropriate;
never retarget a published version. Once the exact commit and its required
checks are verified, create the release against that SHA:

```sh
gh release create v1.0.0 --repo zakkeasterbrook/-patoshi-timing-audit \
  --target "$verified_commit" --title "Patoshi Timing Audit v1.0.0" \
  --notes-file RELEASE_NOTES.md
```

Attach the actual versioned project/evidence archive and its checksum file.
Inspect the asset list, download the public assets again and verify their
checksums. Test an independent clean checkout at the release commit using the
frozen inputs. Record its command results and distinguish same-host checks
from another-machine replication.

Use the actual publication date in release metadata and `CITATION.cff`; internal
research dates are not earlier public release dates. Return the repository URL,
destination branch, full commit SHA, PR status if applicable, CI run URL and
outcome, release URL and exact asset names. If a permission, network operation
or required input is blocked, report the observed blocker and the prepared
local state instead of claiming publication succeeded.

## Communication scope

Prepared text in `docs/announcement-drafts.md` remains a draft. Publication of
this repository does not authorize sending outreach, contacting researchers,
or posting on social media. Keep private chat material out of the public tree.
