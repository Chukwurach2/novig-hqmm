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
FMV voids are not guaranteed cost refunds. PUSH needs per-fill cost accounting.

`GET /v3/ws` exists but is not implemented. Future streaming must authenticate
where required, reconstruct order-level deltas, detect gaps, and resnapshot.
The current adapter polls complete snapshots; errors/regressions stop it.
Public read paths do not declare signed security. Signed routes are unused.

Reference adapter verified against [The Odds API v4 official guide](https://the-odds-api.com/liveapi/guides/v4/):
`GET /v4/sports/{sport}/odds/`, `apiKey`, `regions`, `markets=h2h`,
`oddsFormat=decimal`; event → bookmakers → markets → outcomes. Preserve provider
IDs and source timestamps. This is a multi-sportsbook feed, not direct sportsbook APIs.
