import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from hqmm.adapters.novig import review_pregame_book
from hqmm.schemas import Book, Level


class PregameBookTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.market = {
            'eventId': 'event',
            'marketId': 'market',
            'status': 'OPEN',
            'startsTs': int(self.now.timestamp()) * 1000 + 1,
            'outcomes': [
                {'outcomeId': 'A', 'status': 'TBD'},
                {'outcomeId': 'B', 'status': 'TBD'},
            ],
        }
        self.book = Book('market', 1, self.now, (Level('A', 'order', Decimal('.5'), 10),))

    def review(self, **changes):
        kwargs = dict(
            market=self.market, book=self.book, now=self.now,
            catalog_received_at=self.now - timedelta(seconds=30),
            event_id='event', market_id='market', outcome_ids=('B', 'A'),
        )
        return review_pregame_book(**(kwargs | changes))

    def test_matching_open_pregame_book(self):
        self.assertIs(self.review(), self.book)

    def test_rejects_nonopen_unknown_and_started_markets(self):
        for status in ('CLOSED', 'SETTLED', 'SUSPENDED', None):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, 'OPEN'):
                self.review(market=self.market | {'status': status})
        with self.assertRaisesRegex(ValueError, 'OPEN'):
            self.review(now=self.now + timedelta(milliseconds=1),
                        catalog_received_at=self.now)

    def test_rejects_bad_receipt_order_or_age(self):
        for catalog_time, book_time in [
            (self.now - timedelta(seconds=31), self.now),
            (self.now, self.now + timedelta(seconds=1)),
            (self.now, self.now - timedelta(seconds=1)),
        ]:
            with self.subTest(catalog_time=catalog_time, book_time=book_time):
                with self.assertRaisesRegex(ValueError, 'capture receipt'):
                    self.review(catalog_received_at=catalog_time,
                                book=Book('market', 1, book_time, ()))

    def test_rejects_mismatched_identity_and_unresolved_outcomes(self):
        with self.assertRaisesRegex(ValueError, 'event and market IDs'):
            self.review(event_id='different')
        with self.assertRaisesRegex(ValueError, 'event and market IDs'):
            self.review(book=Book('another-market', 1, self.now, ()))
        with self.assertRaisesRegex(ValueError, 'outcome IDs'):
            self.review(outcome_ids=('A', 'C'))
        with self.assertRaisesRegex(ValueError, 'outcome IDs'):
            self.review(book=Book('market', 1, self.now, (
                Level('C', 'order', Decimal('.5'), 10),
            )))
        settled = [self.market['outcomes'][0], {'outcomeId': 'B', 'status': 'PUSH'}]
        with self.assertRaisesRegex(ValueError, 'outcome IDs'):
            self.review(market=self.market | {'outcomes': settled})
