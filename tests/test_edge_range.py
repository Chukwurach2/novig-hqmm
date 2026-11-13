from decimal import Decimal as D
import unittest

from hqmm.edge import Costs, buy_edge_range


class PaperBuyEdgeRangeTests(unittest.TestCase):
    def test_stress_range_spans_break_even_in_dollars(self):
        self.assertEqual(
            buy_edge_range((".49", ".53"), D(".50"), 100, Costs()),
            (D("-.016"), D(".024")),
        )

    def test_equal_bounds_and_costs_can_erase_positive_gross_edge(self):
        self.assertEqual(
            buy_edge_range((D(".505"), D(".505")), D(".50"), 200, Costs()),
            (D("-.002"), D("-.002")),
        )

    def test_invalid_bounds_or_size_are_rejected(self):
        for bounds, size in (((".6", ".5"), 100), ((".4", "1"), 100),
                             ((".4", ".5"), 0), ((".4", ".5"), True)):
            with self.subTest(bounds=bounds, size=size), self.assertRaises(ValueError):
                buy_edge_range(bounds, D(".5"), size, Costs())
