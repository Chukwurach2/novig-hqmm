from datetime import datetime, timedelta, timezone
import unittest

from hqmm.adapters.reference import parse_reference
from hqmm.fair_value import estimate


class ReferenceSourceTimeTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, 18, 0, tzinfo=timezone.utc)
        self.market = {
            "key": "h2h",
            "outcomes": [{"name": "Home", "price": 2}, {"name": "Away", "price": 2}],
        }
        self.book = {"key": "example", "markets": [self.market]}
        self.events = [{"id": "example-event", "bookmakers": [self.book]}]

    def test_market_time_is_sufficient_without_book_time(self):
        self.market["last_update"] = self.now.isoformat()
        self.assertEqual(parse_reference(self.events)[0].observed_at, self.now)

    def test_book_time_is_used_when_market_time_is_absent(self):
        self.book["last_update"] = self.now.isoformat()
        self.assertEqual(parse_reference(self.events)[0].observed_at, self.now)

    def test_invalid_timestamp_is_rejected(self):
        for value in (None, "", "invalid", "2026-11-12T18:00:00"):
            self.market["last_update"] = value
            self.book["last_update"] = self.now.isoformat()
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_reference(self.events)

    def test_missing_both_timestamps_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "source timestamp"):
            parse_reference(self.events)

    def test_book_time_cannot_hide_stale_or_future_market_time(self):
        self.book["last_update"] = self.now.isoformat()
        for offset in (-31, 1):
            self.market["last_update"] = (self.now + timedelta(seconds=offset)).isoformat()
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, "no fresh"):
                estimate(parse_reference(self.events), self.now)
