"""The Odds API v4, decimal h2h only; no bookmaker execution or scraping."""
from datetime import datetime
from decimal import Decimal
from urllib.parse import quote
from hqmm.schemas import Reference

BASE = "https://api.the-odds-api.com"


def parse_reference(events):
    rows = []
    for event in events:
        for book in event["bookmakers"]:
            for market in book["markets"]:
                if market["key"] != "h2h":
                    continue
                rows.append(Reference(
                    event["id"], book["key"], "h2h",
                    tuple(x["name"] for x in market["outcomes"]),
                    tuple(Decimal(str(x["price"])) for x in market["outcomes"]),
                    datetime.fromisoformat(market.get("last_update", book["last_update"]).replace("Z", "+00:00")),
                ))
    return rows


class SportsbookData:
    def __init__(self, http, api_key):
        if not api_key:
            raise ValueError("reference data API key required")
        self.http, self.api_key = http, api_key

    async def snapshot(self, sport="americanfootball_nfl", regions="us"):
        events = await self.http.get(BASE, f"/v4/sports/{quote(sport, safe='')}/odds/", {
            "apiKey": self.api_key, "regions": regions, "markets": "h2h", "oddsFormat": "decimal"
        })
        return parse_reference(events)
