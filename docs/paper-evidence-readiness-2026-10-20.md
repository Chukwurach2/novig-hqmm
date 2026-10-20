# Forward-paper evidence readiness — 2026-10-20

This audit measures evidence completeness, not strategy profitability. The private phone-research ledger is a collection of quote observations and alternative contracts; it is not a record of executed wagers. No raw feed, subscriber table, owner identity or private selection is published here.

## Aggregate audit

| Measure | Count |
|---|---:|
| Quote observations | 208 |
| Distinct sport/event identifiers | 16 |
| Distinct sport/event/market/selection/line contracts | 72 |
| Legacy v1 observations | 54 |
| v2 observations retaining supporting source sets | 154 |
| Positive point estimates | 1 |
| Nonpositive point estimates | 207 |
| Verified accepted prices | 0 |
| Settled observations | 0 |
| Observations without a stake | 208 |

The single positive point estimate was small and reference-sensitive. It does not establish an edge. Nonpositive entries are price watches; observing them does not define a bet-all strategy.

## Interpretation and evidence gates

- Repeated captures of a contract are dependent observations. Opposing selections and contracts in the same game are also correlated. Neither 208 observations nor 72 contracts can be reported as independent trials. Sixteen event identifiers is a grouping count, not proof of independence.
- Separate the 54 legacy rows from freshness-sensitive and closing-price analysis: their complete supporting quote sets were not retained. Keep the original records immutable; do not reconstruct historical source times from later observations.
- Preserved reference sets in 154 rows improve auditability but do not prove executable liquidity, independent benchmarks, valid settlement rules or accurate fair probability.
- Zero accepted prices, zero settlements and absent stakes mean realized ROI is unavailable. Do not substitute expected value for realized returns or infer profit from displayed odds.
- Before outcome review, require a final score from an identified source, exact event/team/start mapping, and matching full-game contract and overtime/void rules. Unsupported or nonfinal cases remain unresolved. The proposed offline review helper is tracked in [ev-betting PR36](https://github.com/Chukwurach2/ev-betting/pull/36).
- Keep outcome labels separate from the frozen pregame evidence. Append corrections with provenance. Report unresolved coverage alongside results, including all predeclared candidates rather than only winners.
- Predeclare a prospective selection rule and price threshold before the next sample. Evaluate by chronological holdout and event clusters, with fee, price movement and benchmark sensitivity. Paper observations remain distinct from accepted fills.

## Reproduction

Snapshot: private ignored `runs/phone-paper.jsonl`; SHA-256
`5e0f6db2b2cf1efe67ab06113341b2ff0da1ecc898d6fcb38d8596b864624eb1`.

Count only observation records. Deduplicate events by (sport, game_id), and contracts by (sport, game_id, market, selection, line), excluding book and capture time. Count schema versions and retained supporting source sets separately. Partition point estimates into positive and nonpositive. Independently count accepted-price verification, settlements and missing stakes.

Arithmetic checks: 54 + 154 = 208; 1 + 207 = 208. The ignored local audit JSON retains these aggregate results. Do not upload the underlying private ledger to reproduce this report.

## Next research increment

Resolve eligible completed games using verified finals and exact rules, retaining unresolved cases explicitly. Then evaluate prospective, source-complete observations under a fixed selection policy. This audit consumed no provider credits, changed no freshness limits, and enabled no execution.
