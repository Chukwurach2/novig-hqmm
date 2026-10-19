# Per-game paper cards

Delivery target: four distinct ranked NFL leans for each upcoming game once prices
are available, starting with the next game. A lean may be exploratory and need not
come from a fully proven strategy. It must still have an observed price and an
explicitly sourced rationale. Never fabricate picks or label negative EV positive.
If coverage is short, report the shortfall and price-watch conditions.

The initial report layer consumes manually curated, authorized observations:

```sh
PYTHONPATH=src python -m hqmm.report runs/observations.json --output runs/game-cards
```

Input is a JSON list. Each row requires game_id, game, starts_at, observed_at,
participant, market, line, side, book, american_odds, fair_probability, fair_source,
and rationale. Timestamps use ISO 8601 with timezone. Optional quote_at is the
individual quote timestamp; it is not the report publication time. Set
identity_verified only after verifying exact event/participant/period/line/side and
settlement rules. Set available_size with units and provenance where known.
cost_per_dollar is a nonnegative cost in dollars per dollar staked (default zero,
which excludes fees rather than certifying a zero-fee venue).

Example synthetic observation (not a real pick):

```json
[{"game_id":"synthetic","game":"A @ B","starts_at":"2026-10-20T00:15:00Z",
"observed_at":"2026-10-19T22:00:00Z","quote_at":"2026-10-19T22:00:00Z",
"participant":"Player A","market":"receptions","line":"4.5","side":"over",
"book":"synthetic","american_odds":"110","fair_probability":"0.50",
"fair_source":"synthetic fixture","rationale":"Demonstration only",
"identity_verified":true,"cost_per_dollar":"0.01"}]
```

JSON and Markdown outputs contain estimate attribution, net ROI, break-even decimal
odds, stale/future/missing-quote warnings and coverage shortfall. Alternative venues
for the same exact selection count once. ROI is p × decimal_odds - 1 - cost per
stake dollar, not the probability-price difference used by the Novig contract quoter.
No confidence interval or calibrated model is implied by a supplied fair value.

Current limitations: this is a curated-input reporting component, not autonomous
feed ingestion, a complete historical ledger or an injury-verification service.
No game without an observation row can be inferred; the caller must reconcile
coverage against an official schedule. Missing quote timestamps or identity checks
produce unverified leans. The default ranking uses freshness/verification then
estimated ROI; the analyst must review reference quality, injury conditions,
correlation and available venues before presenting a final ordered shortlist.

Record official injury reports, active-status conditions, market uncertainty and
exposure in rationale. An unavailable player is not an executable pick. Four
entries are a research coverage goal, not instructions to place four bets or a
parlay. Keep detailed subscriber-derived observations and reports in ignored runs/
or the private chat; publish original code, methodology and progress to GitHub.
