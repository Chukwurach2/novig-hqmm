from datetime import datetime, timezone
from decimal import Decimal
import unittest

from hqmm.adapters.novig import parse_book


class BookIdentityTests(unittest.TestCase):
    def setUp(self):
        self.received = datetime(2026, 11, 12, tzinfo=timezone.utc)
        self.bid = {"orderId": "order-a", "price": "0.500", "qty": 25}
        self.payload = {"marketId": "market", "seq": 0, "orders": {"A": [self.bid]}}

    def test_accepts_distinct_orders_at_the_same_price(self):
        self.payload["orders"]["A"].append(dict(self.bid, orderId="order-b"))
        book = parse_book(self.payload, self.received)
        self.assertEqual([bid.order_id for bid in book.bids], ["order-a", "order-b"])
        self.assertEqual(sum(bid.contracts for bid in book.bids), 50)
        self.assertEqual(book.bids[0].price, Decimal("0.500"))

    def test_rejects_duplicate_orders_within_and_across_outcomes(self):
        for orders in ({"A": [self.bid, self.bid]}, {"A": [self.bid], "B": [self.bid]}):
            with self.subTest(orders=orders), self.assertRaisesRegex(ValueError, "duplicate"):
                parse_book(dict(self.payload, orders=orders), self.received)

    def test_rejects_non_integer_or_negative_sequences(self):
        for sequence in (True, 1.5, "1", -1):
            with self.subTest(sequence=sequence), self.assertRaisesRegex(ValueError, "sequence"):
                parse_book(dict(self.payload, seq=sequence), self.received)
