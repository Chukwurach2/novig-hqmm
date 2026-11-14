from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
import unittest

from hqmm.paper import PaperBroker
from hqmm.schemas import Quote


class PaperQueueInputTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, tzinfo=timezone.utc)
        self.quote = Quote("market", "A", D(".5"), 3, self.now, self.now + timedelta(seconds=10))
        self.broker = PaperBroker(D(1))

    def test_replacement_accepts_one_pass_quotes_and_fills_whole_contracts(self):
        self.broker.replace(iter([self.quote]), queue_ahead=1, latency_seconds=.5)
        fills = self.broker.sell_flow("market", "A", D(".5"), 3, self.now + timedelta(seconds=.5))
        self.assertEqual(fills[0]["contracts"], 2)
        self.assertEqual(self.broker.inventory[("market", "A")], 2)

    def test_invalid_configuration_leaves_resting_order_intact(self):
        self.broker.replace([self.quote])
        original = self.broker.orders
        for queue, latency in ((.5, 0), (True, 0), (-1, 0), (0, float("nan")),
                               (0, float("inf")), (0, -1)):
            with self.subTest(queue=queue, latency=latency), self.assertRaises(ValueError):
                self.broker.replace([self.quote], queue_ahead=queue, latency_seconds=latency)
            self.assertIs(self.broker.orders, original)

    def test_inventory_cap_is_a_whole_contract_count(self):
        for cap in (1.5, D("1.5"), True, -1):
            with self.subTest(cap=cap), self.assertRaisesRegex(ValueError, "inventory cap"):
                PaperBroker(D(1), max_contracts=cap)

        broker = PaperBroker(D(1), max_contracts=2)
        broker.replace([self.quote], queue_ahead=0, latency_seconds=0)
        fills = broker.sell_flow("market", "A", D(".5"), 3, self.now)
        self.assertEqual(fills[0]["contracts"], 2)
        self.assertIs(type(fills[0]["contracts"]), int)
        self.assertEqual(broker.sell_flow("market", "A", D(".5"), 1, self.now), [])

    def test_zero_inventory_cap_disables_fills(self):
        broker = PaperBroker(D(1), max_contracts=0)
        broker.replace([self.quote], queue_ahead=0, latency_seconds=0)
        self.assertEqual(broker.sell_flow("market", "A", D(".5"), 3, self.now), [])
        self.assertEqual(broker.cash, D(1))
