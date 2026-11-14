import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

from hqmm.fair_value import estimate, leave_one_book_out
from hqmm.schemas import Reference


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def reference(book, odds, *, outcomes=('A', 'B'), observed_at=NOW, market='h2h'):
    return Reference('event', book, market, outcomes, tuple(map(D, odds)), observed_at)


class ReferenceSensitivityTests(unittest.TestCase):
    def test_offer_excluded_and_reversed_outcomes_aligned(self):
        first = reference('one', ('1.5', '3'))
        second = reference('two', ('2.5', '2.5'), outcomes=('B', 'A'))
        offered = reference('offer', ('1.2', '6'))
        report = leave_one_book_out([offered, first, second], NOW, offered_book='offer')
        self.assertEqual(report['fair'], estimate([first, second], NOW))
        self.assertEqual(report['leave_one_out']['one']['A'], D('.5'))
        self.assertEqual(report['leave_one_out']['two'], estimate([first], NOW))
        self.assertEqual(report['range']['A'], (D('.5'), estimate([first], NOW)['A']))

    def test_no_range_without_two_fresh_other_books(self):
        rows = [
            reference('one', ('2', '2')),
            reference('offer', ('2', '2')),
            reference('old', ('2', '2'), observed_at=NOW - timedelta(seconds=31)),
            reference('future', ('2', '2'), observed_at=NOW + timedelta(seconds=1)),
        ]
        with self.assertRaisesRegex(ValueError, 'two fresh'):
            leave_one_book_out(rows, NOW, offered_book='offer')

    def test_incompatible_or_duplicate_references_fail_closed(self):
        first = reference('one', ('2', '2'))
        for other, error in [
            (reference('two', ('2', '2'), market='spread'), 'incompatible'),
            (reference('one', ('2', '2')), 'duplicate'),
        ]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                leave_one_book_out([first, other], NOW, offered_book='offer')
