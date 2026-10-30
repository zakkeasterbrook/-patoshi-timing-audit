# Reviewing this audit

Useful review begins with a reproducible discrepancy. Include the repository commit,
command, runtime version, expected result, and actual result. For a disputed row,
include its three block heights and header timestamps. The bundled CSV files make
it possible to compare individual observations instead of relying on totals.

Please distinguish these questions:

1. Does the original program execute as reproduced?
2. Does the corrected predicate implement the article's stated rule?
3. Are the supplied miner labels independently valid?
4. What, if anything, can the resulting timestamps establish about mining behavior?

This repository directly tests the first two. A change to the label list or a new
causal interpretation should be presented as a separate analysis with its own inputs.

External human review is welcome. Reports should identify the reviewer and the
work actually performed; a passing automated check is not a peer-review endorsement.
