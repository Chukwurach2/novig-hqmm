# Reviewed sportsbook reference mapping

The paper fair-value baseline can now take a reviewed mapping from one provider
event and market to one Novig event and market. Each of the two provider outcome
labels is paired with its exact Novig outcome ID. The order of the provider's
quote outcomes can vary. The mapping preserves each price, bookmaker and source
timestamp and rejects a batch containing a mismatched event, market or outcome
set. The existing baseline applies freshness and duplicate-book checks.

Before creating a mapping, record a review of the participants, scheduled start,
market scope and settlement rules on both venues. Check overtime, tie or push,
and void treatment where applicable. Keep the evidence under the supplied
review ID. The function treats that ID as the caller's attestation. It does
not inspect evidence, confirm rule equivalence, check Novig market status or
establish independent fair value. Use the result only for the Novig event and
market in that review.

This is an opt-in offline helper for binary contracts. Existing adapters and
the default paper CLI retain their current behavior. The tests use synthetic
contracts and prices. Real-data mapping still requires a reviewed evidence
record for each contract.
