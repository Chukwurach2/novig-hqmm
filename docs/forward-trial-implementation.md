# Offline prospective decision helper

`hqmm.forward_trial.decide_capture(capture, POLICY_HASH, previous=None)` implements
the registered v1 eligibility/ranking thresholds with Decimal financial arithmetic.
Its frozen policy hash binds to the exact registered JSON bytes. No network, bets,
account data, scheduler or phone model is used. This helper is not an activated trial.

A capture supplies exact sport/event/teams/start, capture time, complete/authorized
review attestations and candidates. Each candidate supplies those same identity
fields, exact supported market/selection/half-point line, book, odds, fair probability,
source time and exact-contract reference quotes. Require explicit reviewed_identity,
reviewed_rules, reviewed_eligibility, availability_checked and offer_verified flags.
These attestations must be backed by privately reviewed evidence; a flag is not an
independent verification. Reference aliases collapse and cannot include the offer.

The helper rejects pre-registration/out-of-window captures as pending. The first
complete authorized capture locks either one selection or an abstention, with
policy/event/capture hashes, decision time and rejection reasons. Passing the same
locked prior decision returns it unchanged; another identity/policy is an error.
No later price replaces an abstention. Missing review evidence cannot manufacture
a qualifying entry; the helper does not fetch or infer it.

Caller responsibility before any real prospective count: persist each locked
return privately and append-only, load it before processing later captures, reject
concurrent writes, and verify capture chronology/completeness. There is no durable
recorder or automatic capture adapter in this increment. Consequently no existing
or current phone observation is claimed as a registered trial selection. Preserve
original exploratory leans and the user's requested broader game-card coverage.

Validation: eight synthetic regressions plus 19 existing tests pass. They cover
selection, locked abstention, pending captures, source/review thresholds, exact
reference identity/operator aliases, ranking, prior identity and frozen policy hash.
Synthetic successful selection is not an observed market edge or evidence of profit.
Next: an exclusive append-only private decision recorder and reviewed capture adapter
before running the pilot prospectively. No new polling or spending is authorized.
