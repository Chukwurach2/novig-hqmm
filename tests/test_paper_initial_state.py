import unittest
from decimal import Decimal as D

from hqmm.paper import PaperBroker


class InitialPaperState(unittest.TestCase):
    def test_invalid_funds_fail_before_replay(self):
        for value in (D('-1'), D('NaN'), D('sNaN'), D('Infinity'),
                      D('-Infinity'), 1, 1.0, True, '1', None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'cash'):
                    PaperBroker(value)

    def test_invalid_starting_fees_fail_before_accounting(self):
        for value in (D('-0.01'), D('NaN'), D('Infinity'), 0, False, '0'):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'fees'):
                    PaperBroker(D(1), fees_usd=value)

    def test_fractional_and_short_initial_positions_are_rejected(self):
        for quantity in (-1, .5, D('0.5'), D(1), True, '1', None):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, 'initial inventory'):
                    PaperBroker(D(0), inventory={('m', 'yes'): quantity})

    def test_valid_seeded_position_settles_in_payout_units(self):
        broker = PaperBroker(D(0), inventory={('m', 'yes'): 2, ('m', 'no'): 0})
        broker.settle('m', {'yes': D(1), 'no': D(0)})
        self.assertEqual(broker.cash, D('0.02'))
        self.assertEqual(broker.inventory, {})
        self.assertEqual(broker.fees_usd, D(0))

    def test_reservation_fee_requires_decimal_units(self):
        for value in (1, .001, '0.001', True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'reservation fee'):
                    PaperBroker(D(1), reserve_fee=value)
        PaperBroker(D(0), reserve_fee=D(0))


if __name__ == '__main__':
    unittest.main()
