# Novig Hybrid Quantitative Market Maker

A paper-only research platform investigating whether fresh sportsbook consensus,
selective liquidity provision, and inventory controls can produce positive expected
returns **after fees, adverse selection, and realistic execution assumptions**.
No profitability claim. No live execution code, signing keys, deposits, or orders.

## Research hypotheses

1. Fresh, de-vigged multi-book probabilities improve fair-value estimates over the Novig midpoint.
2. Quoting only when conservative net edge is positive reduces adverse-selection losses.
3. Inventory skew and hard cash/position limits improve drawdowns versus static quotes.

Reject hypotheses using chronological held-out data, fee/latency stress tests,
calibration, markouts, fill rates, net P&L and maximum drawdown. Compare with
midpoint, single-book and static-spread baselines. Synthetic demo P&L is not evidence.

## Quick start (Python 3.10+)

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
novig-hqmm
```

The deterministic offline demo writes `runs/demo.json`, including assumptions,
fills, fees, marked equity and settlement P&L. No API key or network needed.
Without installation: `PYTHONPATH=src python3 -m hqmm.cli`.
Open this folder in VS Code; select `.venv`, use the Paper demo launch target,
or choose **Dev Containers: Reopen in Container**. Codex guidance is in `AGENTS.md`.

```sh
docker build -t novig-hqmm .
docker run --rm novig-hqmm
```

## Architecture and layout

```text
Novig public snapshots ──> canonical Book ───────────────┐
Sportsbook feed ──> Reference ──> de-vig fair values     │
                  explicit verified contract mapping  │
                             ↓                         ↓
                        net edge → bid quotes → paper broker → JSON results
```

| Path | Responsibility |
|---|---|
| `src/hqmm/adapters/` | Async Novig public GET polling and The Odds API multi-book h2h feed |
| `schemas.py` | Immutable canonical books, reference odds and quote records |
| `fair_value.py`, `edge.py` | Freshness checks, proportional de-vig consensus, conservative cost-adjusted edge |
| `quoting.py` | Binary-outcome bid grid, inventory skew, per-outcome quantity limits |
| `paper.py` | Queue/latency sell-flow fills, cash limits, inventory, explicit settlement |
| `cli.py`, `config/` | Offline reproducible experiment and cost/risk assumptions |
| `docs/` | Spec snapshot, API verification, research protocol and roadmap |
| `tests/` | Financial invariants, adapter contracts and safety defaults |
| `data/raw/`, `runs/` | Ignored licensed inputs and local experiment outputs |

Prices are probabilities; cash/P&L are USD Decimals. **A Novig contract pays
$0.01**, so expected USD edge is `(fair - price - costs) × contracts × 0.01`.
Quotes are bids on each of two exhaustive outcomes; they are not uncovered asks.
The paper broker charges a configurable flat stress fee on every fill. This is
**not the exchange fee formula**; `MarketFee` metadata remains available in catalog
responses. See [API verification](docs/api-verification.md).

## Remote data, intentionally opt-in

The default entry point is offline. Library adapters require `JsonHTTP(allowed=True)`;
this is an explicit operator attestation that remote data access and automation are
permitted for the account and physical location. The environment example documents
intent but never silently enables network access. Do not bypass geolocation, age,
account, subscription, licensing or automation restrictions. Do not use proxies to
circumvent them. No jurisdiction eligibility is inferred by this project.

```python
from hqmm.adapters.http import JsonHTTP
from hqmm.adapters.novig import NovigData
# In an async function, only after verifying access authorization:
feed = NovigData(JsonHTTP(allowed=True))
async for market in feed.markets("NFL"):
    print(market["marketId"], market["fee"])
```

Use `SportsbookData(http, api_key).snapshot()` for paid/licensed reference data.
Errors stop collection; retry/backoff and quota budgeting must be designed before
continuous ingestion. Do not log API keys, exception URLs, or licensed responses.

## Current boundaries

Adapters and strategy modules are composable library components. The demo uses
synthetic references and sell flow; an automatic Novig/reference join is deliberately
absent. Map event, start time, period, market type, line, outcome and settlement rules
explicitly before estimating cross-venue edge. Three-way reference markets cannot
feed the binary quoter. Snapshot receipt time is not exchange creation time.

No websocket reconstruction, production fee engine, calibrated fill model,
automated live-feed strategy loop, shorting, portfolio correlation limits, PUSH
cost refunds, or production execution is claimed. Paper fills require explicit
exogenous sell flow; a displayed touch alone never creates a fill. Cash is checked
at fill time; orders do not reserve cash, so some displayed paper size may not fill.
See the [roadmap](docs/roadmap.md) and [research protocol](docs/research.md).
