from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

D = Decimal
PAYOUT_USD = D("0.01")  # One Novig contract pays one cent.


def probability(value):
    p = D(str(value))
    if not p.is_finite() or not 0 < p < 1:
        raise ValueError("probability must be finite and strictly between 0 and 1")
    return p


def aware(value):
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone-aware timestamps required")
    return value


@dataclass(frozen=True)
class Level:
    outcome_id: str
    order_id: str
    price: Decimal
    contracts: int

    def __post_init__(self):
        probability(self.price)
        if type(self.contracts) is not int or self.contracts < 0:
            raise ValueError("nonnegative integer contracts required")


@dataclass(frozen=True)
class Book:
    market_id: str
    sequence: int
    received_at: datetime
    bids: tuple[Level, ...]

    def __post_init__(self):
        aware(self.received_at)
        if self.sequence < 0:
            raise ValueError("negative sequence")


@dataclass(frozen=True)
class Reference:
    # Provider-native IDs remain distinct until an explicit mapping is approved.
    event_id: str
    bookmaker: str
    market: str
    outcomes: tuple[str, ...]
    decimal_odds: tuple[Decimal, ...]
    observed_at: datetime

    def __post_init__(self):
        aware(self.observed_at)
        if len(self.outcomes) < 2 or len(set(self.outcomes)) != len(self.outcomes):
            raise ValueError("complete, unique outcomes required")
        if len(self.outcomes) != len(self.decimal_odds):
            raise ValueError("outcome/odds mismatch")
        if any(not x.is_finite() or x <= 1 for x in self.decimal_odds):
            raise ValueError("decimal odds must exceed 1")


@dataclass(frozen=True)
class Quote:
    market_id: str
    outcome_id: str
    price: Decimal
    contracts: int
    created_at: datetime
    expires_at: datetime

    def __post_init__(self):
        probability(self.price)
        aware(self.created_at)
        aware(self.expires_at)
        if type(self.contracts) is not int or self.contracts <= 0:
            raise ValueError("positive integer contracts required")
        if self.expires_at <= self.created_at:
            raise ValueError("expiry must follow creation")
