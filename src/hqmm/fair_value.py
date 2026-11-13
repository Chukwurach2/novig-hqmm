"""Proportional de-vig baseline and reference-book sensitivity."""
from datetime import timezone
from decimal import Decimal as D
from hqmm.schemas import aware


def fresh(observed, now, max_age):
    observed = aware(observed).astimezone(timezone.utc)
    now = aware(now).astimezone(timezone.utc)
    age = (now - observed).total_seconds()
    return 0 <= age <= max_age


def _reference_probabilities(references, now, max_age):
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
    probabilities = {}
    for row in rows:
        implied = [1 / odd for odd in row.decimal_odds]
        total = sum(implied)
        probabilities[row.bookmaker] = {
            name: p / total for name, p in zip(row.outcomes, implied)
        }
    return first.outcomes, probabilities


def _average(outcomes, probabilities):
    count = len(probabilities)
    return {
        outcome: sum((row[outcome] / count for row in probabilities), D(0))
        for outcome in outcomes
    }


def estimate(references, now, max_age=30):
    outcomes, books = _reference_probabilities(references, now, max_age)
    return _average(outcomes, list(books.values()))


def leave_one_book_out(references, now, max_age=30, *, offered_book):
    """Return fair probabilities and how they change when each reference is omitted.

    Inputs must use canonical operator IDs. Two fresh other operators are the
    minimum needed to compute a sensitivity range.
    """
    if not offered_book:
        raise ValueError("offered bookmaker identity required")
    outcomes, books = _reference_probabilities(
        (row for row in references if row.bookmaker != offered_book), now, max_age
    )
    if len(books) < 2:
        raise ValueError("at least two fresh reference bookmakers required")
    omitted = {
        excluded: _average(outcomes, [row for book, row in books.items() if book != excluded])
        for excluded in books
    }
    ranges = {
        outcome: (min(row[outcome] for row in omitted.values()),
                  max(row[outcome] for row in omitted.values()))
        for outcome in outcomes
    }
    return {"fair": _average(outcomes, list(books.values())),
            "leave_one_out": omitted, "range": ranges}
