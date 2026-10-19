import argparse
import json
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D
from pathlib import Path
from hqmm.schemas import Reference
from hqmm.fair_value import estimate
from hqmm.edge import Costs
from hqmm.quoting import quote_binary
from hqmm.paper import PaperBroker


def main():
    parser = argparse.ArgumentParser(description="Offline paper-only synthetic experiment")
    parser.add_argument("--config", default="config/paper.json")
    parser.add_argument("--output", default="runs/demo.json")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    if cfg["mode"] != "paper" or os.getenv("HQMM_MODE", "paper") != "paper":
        raise SystemExit("Only paper mode is implemented")
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    refs = [Reference("synthetic-event", "synthetic-book", "h2h", ("A", "B"), (D("1.8"), D("2.2")), now)]
    fair = estimate(refs, now, cfg["max_age_seconds"])
    costs = Costs(D(cfg["fee_per_contract"]), D(cfg["adverse_selection_buffer"]))
    broker = PaperBroker(D(cfg["cash_usd"]), cfg["max_contracts"])
    quotes = quote_binary("demo", fair, {}, now, costs, size=cfg["quote_size"],
                          max_contracts=cfg["max_contracts"], half_spread=D(cfg["half_spread"]),
                          inventory_skew=D(cfg["inventory_skew"]))
    broker.replace(quotes)
    fills = broker.sell_flow("demo", "A", D("0.50"), 150, now + timedelta(seconds=2), costs.fee_per_contract)
    equity = broker.equity({("demo", key): value for key, value in fair.items()})
    broker.settle("demo", {"A": D(1), "B": D(0)})
    result = {"mode": "paper", "synthetic": True, "fair": {k: str(v) for k, v in fair.items()},
              "fills": fills, "marked_equity_usd": str(equity), "final_cash_usd": str(broker.cash),
              "pnl_usd": str(broker.cash - D(cfg["cash_usd"])), "fees_usd": str(broker.fees_usd),
              "warning": "Synthetic mechanics demonstration; no evidence of profitability", "config": cfg}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
