"""Verified against the vendored Novig v3 specification; public GET only."""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from hqmm.schemas import Book, Level

BASE = "https://api.paper.novig.com"
MARKETS = "/v3/public/catalog/markets"
BOOK = "/v3/public/catalog/markets/{id}/book"


def parse_book(payload, received_at):
    return Book(payload["marketId"], payload["seq"], received_at, tuple(
        Level(outcome, row["orderId"], Decimal(row["price"]), row["qty"])
        for outcome, rows in payload["orders"].items() for row in rows
    ))


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
