# Prior work and search scope

This project credits the original pattern research and the published test it audits. Its contribution is the reproducible correction of a specific implementation, with the original classifications held fixed.

## Relevant earlier work

| Source | Relevance to this audit |
|---|---|
| Sergio Demian Lerner, [*The Well Deserved Fortune of Satoshi Nakamoto*](https://bitslog.com/2013/04/17/the-well-deserved-fortune-of-satoshi-nakamoto/) (2013) | Early extranonce-based mining-pattern analysis. |
| Lerner, [*The Return of the Deniers and the Revenge of Patoshi*](https://bitslog.com/2019/04/16/the-return-of-the-deniers-and-the-revenge-of-patoshi/) (2019) | Nonce-range evidence and separate timestamp-inversion counts for P/P, N/N, P/N and N/P pairs. |
| Lerner, [*A New Mystery in Patoshi Timestamps*](https://bitslog.com/2020/06/22/a-new-mystery-in-patoshi-timestamps/) (2020) | The roughly five-minute P/P timing feature, known phase differences, and competing pause/timestamp explanations. |
| Lerner, [*The Patoshi Mining Machine*](https://bitslog.com/2020/08/22/the-patoshi-mining-machine/) (2020) | Additional mining-process evidence from nonce distributions and re-mining experiments. |
| Jameson Lopp, [*Was Satoshi a Greedy Miner?*](https://blog.lopp.net/was-satoshi-a-greedy-miner/) (2022) | The stated P/P/N test, linked PHP implementation and reported 1,881 / 1 / 5 result audited here. |
| [btc-rpc-explorer discussion #465](https://github.com/janoside/btc-rpc-explorer/discussions/465) (2022–2023) | Public discussion of uncertain classification labels, including heights 24,504, 35,573 and 35,599. |

The existence of unusual timestamp distributions and the ambiguity between mining pauses and timestamp behavior were already public. Neither is presented here as a new discovery. Discussion of label uncertainty is also prior work; the core reproduction keeps the original list intact so a classification change cannot be confused with an implementation correction.

## What the search examined

The search was conducted on **30 October 2026 UTC** and focused on the exact script, its wrong-block timestamp assignment and possible earlier corrections. The repository contains the [exact web queries and outcomes](../provenance/prior-art/web_search_log.json), [GitHub search summary](../provenance/prior-art/github_search_results_summary.json) and [retrieval metadata](../provenance/prior-art/metadata_provenance.json).

| Search surface | Recorded coverage and result |
|---|---|
| Indexed web | 23 focused queries across two search systems. No earlier report of the specific assignment error was located. |
| GitHub search | 10 code, commit, issue and pull-request queries. Related references were inspected for relevance. |
| Upstream repository | One returned branch; no returned issues or pull requests in the inspected all-state collections; discussions disabled. |
| Target-file history | The retrieved upstream history contains its initial addition on 15 September 2022. The initial and inspected current file bytes match. |
| Listed forks | 17 returned fork records, of which 15 were accessible. Seven accessible forks contained the target file, unchanged. |
| Additional public copies | Two further accessible copies contained the same file bytes. |
| Copy histories | All nine accessible copies containing the file returned an initial addition without a later correction in the inspected file history. |
| Article archives | 26 distinct-digest HTML captures, from 16 September 2022 through 31 August 2026, plus the inspected live page. The normalized timing-test passage matched throughout. |

The fork endpoint's returned list and the repository's aggregate fork counter differed; the report uses the actual returned records. Two listed repositories were inaccessible and are not counted as inspected copies. See [fork checks](../provenance/prior-art/fork_file_checks.json), [branch checks](../provenance/prior-art/all_fork_branch_checks.json) and [copy histories](../provenance/prior-art/copy_file_histories.json).

The archived figures matter because they establish that the affected **1,881 / 1 / 5** result was present in the original-day article, rather than introduced by a later edit. [Archive checks](../provenance/prior-art/archive_passage_checks.json) identify the capture times and passage hashes. They do not claim that every part of the article remained unchanged.

## Conclusion the search supports

**No earlier public report of this specific wrong-block assignment was located in the documented search.** That is a bounded search result. Unindexed pages, deleted material, inaccessible repositories, differently worded reports and private work are outside what it establishes.

Accordingly, the project makes no claim of worldwide publication priority. The finding can be assessed on its source correction and reproducible outputs regardless of who may have noticed the error previously. A dated earlier report would update the attribution record without changing the arithmetic.

This search is also separate from external human review of the correction. Current review status is stated in [verification status](verification.md); earlier researchers' publications and the existence of automated checks do not imply their endorsement of this audit.
