"""Long-only bids for mutually exclusive binary outcomes; no synthetic ask assumption."""
from decimal import Decimal as D
from datetime import timedelta
from hqmm.schemas import Quote, probability
from hqmm.edge import buy_edge

GRID = tuple([D(i)/1000 for i in range(1, 51)] +
             [D(i)/1000 for i in range(55, 946, 5)] +
             [D(i)/1000 for i in range(950, 1000)])


def quote_binary(market_id, fair, inventory, now, costs, size=100, max_contracts=1000,
                 half_spread=D("0.02"), inventory_skew=D("0.01"), ttl=10):
    if len(fair) != 2 or abs(sum(fair.values()) - 1) > D("0.00000001"):
        raise ValueError("exactly two exhaustive mapped outcomes required")
    if size <= 0 or max_contracts <= 0 or ttl <= 0 or half_spread < 0 or inventory_skew < 0:
        raise ValueError("invalid quote configuration")
    result = []
    for outcome, p in fair.items():
        probability(p)
        held = inventory.get(outcome, 0)
        if held < 0:
            raise ValueError("short inventory unsupported")
        quantity = min(size, max_contracts - held)
        target = p - half_spread - inventory_skew * D(held) / max_contracts
        prices = [x for x in GRID if x <= target]
        if quantity > 0 and prices and buy_edge(p, prices[-1], costs) > 0:
            result.append(Quote(market_id, outcome, prices[-1], quantity, now, now + timedelta(seconds=ttl)))
    return result
