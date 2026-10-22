# Durable local paper decisions

This extends the offline helper in forward-trial-implementation.md: a local recorder
now exists, superseding that document's earlier statement that persistence is pending.
`hqmm.trial_store.record_capture(path, capture)` uses SQLite BEGIN IMMEDIATE and a
unique frozen-policy/sport/provider-event key. Concurrent runs serialize; a later
capture returns the existing decision instead of replacing it. Changed teams/start
under that event key fail identity verification rather than becoming another entry.

Use an ignored private runs/ path. New files have owner-only permissions; permissive
existing files and symlink ledgers are rejected. Full synchronous commits preserve
the decision and original capture together. UPDATE/DELETE triggers protect the normal
API's append-only contract; this is not protection against a user editing the file.
Never upload the database, its journal files, original licensed source rows or owner
identity to GitHub. The recorder performs no external requests and collects no keys.

New decisions require capture time no more than 15 minutes old and not in the future
at recording. Historical snapshots cannot be relabeled as prospective selections.
Pending incomplete/out-of-window captures do not lock an event; the first complete
in-window capture locks selection or abstention. Load-existing and insert happen in
the same transaction. Preserve rejected/pending capture coverage in the separate
observation ledger. The frozen rule and review attestations are unchanged.

Validation: five new tests cover reopen/evidence preservation/private permissions,
concurrent writers, changed event identity, historical/future backfill rejection,
and incomplete-capture behavior. All 32 project tests and offline demo pass.
No current observation has been registered as a live prospective selection.

Next: reviewed capture adapter and operational chronology checks before trial use.
This recorder alone cannot prove that a supplied capture is the first complete
capture or that its source/rules/eligibility attestations are correct. It changes
no phone data, freshness window, collector schedule, model or betting journal.
