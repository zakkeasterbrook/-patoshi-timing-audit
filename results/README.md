# Result provenance

- `expected/`: unchanged core CSV evidence from the supplied release package.
- `local-verification/` and `release-verification/`: unchanged archived execution
  records. They describe earlier package snapshots, not the current session.
- `reproduced/`: complete deterministic rows and summaries freshly regenerated
  from the verified frozen inputs. `python3 reproduce.py` compares all these
  bytes before reporting success. Regeneration writes to `build/` or outside
  the checkout and never overwrites these reference files.
- `current-verification/`: actual commands, logs and native-PHP evidence from
  this implementation session, including explicit unavailable checks. A local
  pass does not imply a passing hosted CI run or a published GitHub release.

Every original-label adjacent pair is in
`reproduced/followup/all_adjacent_pairs.csv`. Its label, nonce-band and
`later_eligible` columns allow the pair comparisons to be reconstructed without
guessing excluded cases. Comparison triples and all fifteen adjustment cells
are exported separately. Negative values remain in strict below-300 counts.

The separate Bitquery CSV and exact three disputed-label identities/citation
were not supplied. Their sensitivities are not represented as reproduced data.
