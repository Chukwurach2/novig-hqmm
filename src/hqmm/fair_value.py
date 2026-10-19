"""Proportional de-vig baseline. A hypothesis, not a calibrated predictive model."""
from decimal import Decimal as D
from hqmm.schemas import aware


def fresh(observed, now, max_age):
    aware(observed)
    aware(now)
    age = (now - observed).total_seconds()
    return 0 <= age <= max_age


def estimate(references, now, max_age=30):
    if max_age <= 0:
        raise ValueError("positive max_age required")
    rows = [r for r in references if fresh(r.observed_at, now, max_age)]
    if not rows:
        raise ValueError("no fresh reference prices")
    first = rows[0]
    names = set(first.outcomes)
    if any(r.event_id != first.event_id or r.market != first.market or set(r.outcomes) != names for r in rows):
        raise ValueError("incompatible reference contracts")
    if len({r.bookmaker for r in rows}) != len(rows):
        raise ValueError("duplicate bookmaker snapshot")
    values = {name: D(0) for name in first.outcomes}
    for row in rows:
        implied = [1 / odd for odd in row.decimal_odds]
        total = sum(implied)
        for name, p in zip(row.outcomes, implied):
            values[name] += p / total / len(rows)
    return values
