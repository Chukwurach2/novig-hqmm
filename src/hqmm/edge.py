from dataclasses import dataclass
from decimal import Decimal as D
from hqmm.schemas import PAYOUT_USD, probability


@dataclass(frozen=True)
class Costs:
    # Probability-equivalent cost per 1-cent contract, NOT a verified Novig fee formula.
    fee_per_contract: D = D("0.001")
    adverse_selection_buffer: D = D("0.005")

    def __post_init__(self):
        if any(not x.is_finite() or x < 0 for x in (self.fee_per_contract, self.adverse_selection_buffer)):
            raise ValueError("finite nonnegative costs required")


def buy_edge(fair, price, costs):
    probability(fair)
    probability(price)
    return fair - price - costs.fee_per_contract - costs.adverse_selection_buffer


def buy_edge_range(fair_bounds, price, contracts, costs):
    """Stress a paper buy at both endpoints of an assumed fair-value range."""
    low, high = map(probability, fair_bounds)
    if low > high:
        raise ValueError("fair probability bounds must be ordered")
    if type(contracts) is not int or contracts <= 0:
        raise ValueError("positive integer contracts required")
    price = probability(price)
    payout = PAYOUT_USD * contracts
    return (
        buy_edge(low, price, costs) * payout,
        buy_edge(high, price, costs) * payout,
    )
