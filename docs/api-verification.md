# API verification

Inspected 2026-10-19: [user-provided Novig OpenAPI v3 JSON](https://docs.novig.com/api-reference/spec-files/openapi-v3.json).
The exact snapshot and SHA-256 provenance are in `spec/`. Contract tests verify
paths, fields, response references, server, contract unit and valid price grid.
This is specification verification, not an authenticated integration certification.

Implemented public GET routes:
- `/v3/public/catalog/markets`: `league`, `limit`, opaque `after`; `items`, optional `next`.
- `/v3/public/catalog/markets/{id}/book`: depth 1–20; `marketId`, `seq`, `orders` by outcome ID.
- Each resting order contains `orderId`, decimal-string `price`, integer `qty`.

The spec advertises `https://api.paper.novig.com`. No production hostname is guessed.
`RestingOrder.qty` counts contracts; one winning contract pays 1 cent. The three-band
price grid is 0.001–0.050 step .001, .055–.945 step .005, .950–.999 step .001.
Do not synthesize asks from opposing bids without exhaustive outcomes and settlement analysis.

Catalog responses include market `status`, `startsTs`, `voids`, `fee`, and outcomes.
`MarketFee` includes `coefficient`, `makerCredit`, and `charged` (`ALWAYS` or
`WHEN_LIVE`). The schema names a coefficient but does not specify the full fee
calculation and rounding here. The starter therefore uses an explicitly labeled
configurable flat paper cost rather than inventing an exchange formula or rebate.
FMV voids use explicit payout vectors. For an independently verified PUSH,
`PaperBroker.settle_push` refunds the actual principal of the simulated fills
in that market, including fills at different prices. It rejects positions with
incomplete cost basis before changing cash or inventory. The simulated stress
fee remains a cost because the specification does not establish fee refund
treatment. The broker does not infer the void type or assume a 50/50 payout.

`GET /v3/ws` exists but is not implemented. Future streaming must authenticate
where required, reconstruct order-level deltas, detect gaps, and resnapshot.
The current adapter polls complete snapshots; errors/regressions stop it.
Public read paths do not declare signed security. Signed routes are unused.

Paper sell flow must arrive in chronological order across the broker. A late
older record is rejected before it can consume queue or fill after future
volume has already changed replay state. Equal timestamps retain the caller's
ordering, which must come from the capture when sequence is material. This
guard does not deduplicate trade IDs or reconstruct order-book sequence.

Reference adapter verified against [The Odds API v4 official guide](https://the-odds-api.com/liveapi/guides/v4/):
`GET /v4/sports/{sport}/odds/`, `apiKey`, `regions`, `markets=h2h`,
`oddsFormat=decimal`; event → bookmakers → markets → outcomes. Preserve provider
IDs and source timestamps. This is a multi-sportsbook feed, not direct sportsbook APIs.
