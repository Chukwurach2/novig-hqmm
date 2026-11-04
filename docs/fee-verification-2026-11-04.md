# Fee verification: unresolved documentation scope — 2026-11-04

Status: blocked for an exchange-faithful fee adapter. The configurable paper cost remains an explicit assumption. No payout constant, fee implementation, endpoint or venue-eligibility gate changes in this audit.

## Primary-source observations

Reviewed the [current OpenAPI](https://docs.novig.com/api-reference/spec-files/openapi-v3.json) and the retained October19 snapshot. Both describe RestingOrder.qty as contracts with a winning payout of one cent. The advertised server is the paper environment. MarketFee requires per-market coefficient, makerCredit and charged; league-based fee inference is expressly discouraged.

The [help-center fee article](https://support.novig.com/en/articles/16195057-fees-on-novig), retrieved November4, describes dollar-payout contracts, a price/uncertainty-based charge, five-decimal half-up rounding and a VWAP calculation across matched levels. Its table and live example use coefficient0.06; its final VWAP paragraph instead names0.03 for live. The cent-rounded display examples do not replace the stated assessment precision. The article supplies no explicit conversion to the paper API quantity unit.

The [official comparison article](https://landing.novig.com/blog/prediction-market-fees-compared), last updated October12, distinguishes0.03 on most app/web live markets from0.06 on live NCAAF/NHL/MLB. Its scope does not reconcile the help article's API table or supply an API-specific rounding receipt. It describes contingent maker credits; none is booked by this project.

## Dimensional diagnostic, not a fee certification

For100 dollar-payout contracts at probability0.5, c×p×(1−p)×quantity gives0.75 dollars with c=0.03 or1.50 dollars with c=0.06. If quantity instead denotes100 cent-payout units, multiplying by0.01 gives0.00750 or0.01500 dollars. Thus an unreviewed unit substitution can create a100-fold cost difference, independently of the twofold coefficient ambiguity. This is a scope mismatch needing reconciliation, not proof either product's documentation is wrong.

Do not change the repository's specified0.01 payout to1, assume app/web contracts and paper API contracts are interchangeable, choose a preferred coefficient from conflicting prose, or claim real fee-adjusted EV. Formula shape and a rounding sentence are insufficient to establish the complete executable accounting contract.

## Evidence needed to unblock

1. A versioned API-specific statement binding quantity/payout units, price interpretation and market-level fee fields to a worked dollar example.
2. Reconciled live coefficients and chargeability for the exact channel/market; maker-credit eligibility, timing and collection conditions.
3. Authoritative examples for VWAP aggregation, separately arriving partial executions, half-up midpoint assessment, refunds/voids and rebate timing. No assumption that several independent fills form one rounding group.

Then implement Decimal arithmetic and replay those examples before changing the paper model. Scope uncertainty remains fail-closed; no authenticated trade, support message, account action or live-mode request was made.

Validation: source passages checked against the public pages and vendored schema; Decimal recomputation of the dimensional examples and midpoint arithmetic passed. Local workspace35tests and offline synthetic CLI passed; that workspace contains other unmerged research changes, so those35tests are not attributed to this documentation-only branch. Hosted exact-branch checks remain separate. No new statistical experiment or historical row download.
