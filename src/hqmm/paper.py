"""Conservative user-supplied sell-flow replay, with queue and latency assumptions."""
from dataclasses import dataclass, field
from decimal import Decimal as D
from hqmm.schemas import PAYOUT_USD, probability, aware


@dataclass
class PaperBroker:
    cash: D
    max_contracts: int = 1000
    inventory: dict = field(default_factory=dict)
    orders: list = field(default_factory=list)
    fees_usd: D = D(0)
    settled: set = field(default_factory=set)
    _fill_basis: dict = field(default_factory=dict, init=False, repr=False)

    def replace(self, quotes, queue_ahead=100, latency_seconds=1):
        if queue_ahead < 0 or latency_seconds < 0:
            raise ValueError("invalid queue/latency")
        if len({(q.market_id, q.outcome_id) for q in quotes}) != len(quotes):
            raise ValueError("duplicate quote")
        if any(q.market_id in self.settled for q in quotes):
            raise ValueError("market settled")
        self.orders = [[q, q.contracts, queue_ahead, latency_seconds] for q in quotes]

    def sell_flow(self, market_id, outcome_id, limit_price, contracts, at, fee=D("0.001")):
        """Exogenous aggressive sell volume. Snapshots alone never imply fills.

        Fee is a configurable probability-unit stress cost charged on every paper fill.
        """
        probability(limit_price)
        aware(at)
        if type(contracts) is not int or contracts < 0 or not fee.is_finite() or fee < 0:
            raise ValueError("invalid flow/fee")
        fills = []
        for order in self.orders:
            q, remaining, ahead, latency = order
            if (q.market_id, q.outcome_id) != (market_id, outcome_id):
                continue
            if not q.created_at.timestamp() + latency <= at.timestamp() < q.expires_at.timestamp():
                continue
            if q.price < limit_price:
                continue
            consumed = min(ahead, contracts)
            order[2] -= consumed
            contracts -= consumed
            key = (market_id, outcome_id)
            unit_cost = (q.price + fee) * PAYOUT_USD
            filled = min(remaining, contracts, int(self.cash / unit_cost),
                         max(0, self.max_contracts - self.inventory.get(key, 0)))
            if filled <= 0:
                continue
            self.cash -= unit_cost * filled
            self.fees_usd += fee * PAYOUT_USD * filled
            self.inventory[key] = self.inventory.get(key, 0) + filled
            basis_count, basis_usd = self._fill_basis.get(key, (0, D(0)))
            self._fill_basis[key] = (basis_count + filled, basis_usd + q.price * PAYOUT_USD * filled)
            order[1] -= filled
            contracts -= filled
            fills.append({"market": market_id, "outcome": outcome_id, "contracts": filled, "price": str(q.price)})
        return fills

    def settle(self, market_id, payouts):
        """Settle an explicit winner or FMV payout vector."""
        if market_id in self.settled:
            raise ValueError("duplicate settlement")
        held = {o for m, o in self.inventory if m == market_id}
        if not held <= payouts.keys() or any(not p.is_finite() or not 0 <= p <= 1 for p in payouts.values()):
            raise ValueError("complete valid payout vector required")
        credits = {
            key: quantity * PAYOUT_USD * payouts[key[1]]
            for key, quantity in self.inventory.items() if key[0] == market_id
        }
        self._close_market(market_id, credits)

    def settle_push(self, market_id):
        """Refund verified PUSH fill principal and retain simulated stress fees."""
        if market_id in self.settled:
            raise ValueError("duplicate settlement")
        credits = {}
        for key, quantity in self.inventory.items():
            if key[0] != market_id:
                continue
            basis_count, basis_usd = self._fill_basis.get(key, (0, D(0)))
            if basis_count != quantity:
                raise ValueError("complete fill cost basis required")
            credits[key] = basis_usd
        self._close_market(market_id, credits)

    def _close_market(self, market_id, credits):
        self.cash += sum(credits.values(), D(0))
        for key in credits:
            del self.inventory[key]
            self._fill_basis.pop(key, None)
        self.orders = [o for o in self.orders if o[0].market_id != market_id]
        self.settled.add(market_id)

    def equity(self, marks):
        return self.cash + sum(n * PAYOUT_USD * marks[key] for key, n in self.inventory.items())
