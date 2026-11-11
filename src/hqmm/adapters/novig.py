"""Verified against the vendored Novig v3 specification; public GET only."""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from hqmm.schemas import Book, Level, aware

BASE = "https://api.paper.novig.com"
MARKETS = "/v3/public/catalog/markets"
BOOK = "/v3/public/catalog/markets/{id}/book"


def parse_book(payload, received_at):
    return Book(payload["marketId"], payload["seq"], received_at, tuple(
        Level(outcome, row["orderId"], Decimal(row["price"]), row["qty"])
        for outcome, rows in payload["orders"].items() for row in rows
    ))


def review_pregame_book(market, book, *, catalog_received_at, now,
                        event_id, market_id, outcome_ids, max_age_seconds=30):
    """Gate a captured book against an explicit mapping and recent catalog receipt."""
    now = aware(now).astimezone(timezone.utc)
    catalog_time = aware(catalog_received_at).astimezone(timezone.utc)
    book_time = book.received_at.astimezone(timezone.utc)
    if type(max_age_seconds) is not int or max_age_seconds <= 0:
        raise ValueError("positive integer capture age required")
    if not now - timedelta(seconds=max_age_seconds) <= catalog_time <= book_time <= now:
        raise ValueError("stale, future or misordered capture receipt")
    if not event_id or not market_id or (market.get("eventId"), market.get("marketId"), book.market_id) != (
        event_id, market_id, market_id
    ):
        raise ValueError("reviewed event and market IDs must match")
    starts_ms = market.get("startsTs")
    now_ms = (now - datetime(1970, 1, 1, tzinfo=timezone.utc)) // timedelta(milliseconds=1)
    if market.get("status") != "OPEN" or type(starts_ms) is not int or starts_ms <= now_ms:
        raise ValueError("market must be OPEN before its scheduled start")
    outcomes = market.get("outcomes", [])
    captured_ids = [outcome.get("outcomeId") for outcome in outcomes]
    reviewed_ids = set(outcome_ids)
    if (len(reviewed_ids) < 2 or len(captured_ids) != len(reviewed_ids)
            or set(captured_ids) != reviewed_ids
            or not all(isinstance(key, str) and key for key in reviewed_ids)
            or any(outcome.get("status") != "TBD" for outcome in outcomes)
            or any(level.outcome_id not in reviewed_ids for level in book.bids)):
        raise ValueError("reviewed unresolved outcome IDs must match")
    return book


class NovigData:
    def __init__(self, http):
        self.http = http

    async def markets(self, league="NFL"):
        params = {"league": league, "limit": 500}
        seen = set()
        while True:
            page = await self.http.get(BASE, MARKETS, params)
            for market in page["items"]:
                yield market  # Includes per-market fee, status and void policy.
            cursor = page.get("next")
            if not cursor:
                break
            if cursor in seen:
                raise ValueError("repeated pagination cursor")
            seen.add(cursor)
            params["after"] = cursor

    async def book(self, market_id, depth=20):
        UUID(market_id)
        if not 1 <= depth <= 20:
            raise ValueError("depth must be 1..20")
        payload = await self.http.get(BASE, BOOK.format(id=market_id), {"depth": depth})
        if payload["marketId"] != market_id:
            raise ValueError("market ID mismatch")
        return parse_book(payload, datetime.now(timezone.utc))

    async def stream(self, market_id, interval=5):
        """Snapshot polling, NOT a websocket delta implementation. Errors stop the stream."""
        if interval < 1:
            raise ValueError("minimum polling interval is one second")
        last = -1
        while True:
            book = await self.book(market_id)
            if book.sequence < last:
                raise ValueError("sequence regression; discard state and investigate")
            last = book.sequence
            yield book
            await asyncio.sleep(interval)
