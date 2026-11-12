"""Offline fair value for a reviewed cross-venue binary contract."""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable

from hqmm.fair_value import estimate
from hqmm.schemas import Reference, aware


@dataclass(frozen=True)
class ReviewedReferenceMapping:
    provider_event_id: str
    provider_market: str
    novig_event_id: str
    novig_market_id: str
    outcomes: tuple[tuple[str, str], tuple[str, str]]
    evidence_id: str
    reviewed_at: datetime

    def __post_init__(self):
        aware(self.reviewed_at)
        identifiers = (
            self.provider_event_id, self.provider_market, self.novig_event_id,
            self.novig_market_id, self.evidence_id,
        )
        if any(not isinstance(value, str) or not value.strip() for value in identifiers):
            raise ValueError("event, market and review evidence identifiers required")
        if (
            not isinstance(self.outcomes, tuple)
            or len(self.outcomes) != 2
            or any(
                not isinstance(pair, tuple)
                or len(pair) != 2
                or any(not isinstance(value, str) or not value.strip() for value in pair)
                for pair in self.outcomes
            )
        ):
            raise ValueError("two explicit outcome pairs required")
        source, target = zip(*self.outcomes)
        if len(set(source)) != 2 or len(set(target)) != 2:
            raise ValueError("outcome mapping must be one-to-one")


def estimate_mapped(
    references: Iterable[Reference],
    mapping: ReviewedReferenceMapping,
    now: datetime,
    max_age: float = 30,
) -> dict[str, Decimal]:
    """Estimate probabilities keyed by Novig outcome ID for this mapping."""
    if aware(now).astimezone(timezone.utc) < mapping.reviewed_at.astimezone(timezone.utc):
        raise ValueError("mapping review occurred after evaluation time")
    by_label = dict(mapping.outcomes)
    mapped = []
    for row in references:
        if (
            row.event_id != mapping.provider_event_id
            or row.market != mapping.provider_market
            or set(row.outcomes) != by_label.keys()
        ):
            raise ValueError("reference does not match reviewed event, market and outcomes")
        mapped.append(Reference(
            event_id=mapping.novig_event_id,
            bookmaker=row.bookmaker,
            market=mapping.novig_market_id,
            outcomes=tuple(by_label[label] for label in row.outcomes),
            decimal_odds=row.decimal_odds,
            observed_at=row.observed_at,
        ))
    return estimate(mapped, now, max_age)
