from datetime import datetime, timezone
import unittest
from zoneinfo import ZoneInfo

from hqmm.fair_value import fresh


class ReferenceClockTests(unittest.TestCase):
    def test_repeated_wall_time_can_be_stale_or_future(self):
        zone = ZoneInfo("America/New_York")
        first = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
        second = first.replace(fold=1)
        self.assertFalse(fresh(first, second, 30))
        self.assertFalse(fresh(second, first, 30))

    def test_spring_clock_jump_does_not_age_a_fresh_quote(self):
        zone = ZoneInfo("America/New_York")
        observed = datetime(2026, 3, 8, 1, 59, 55, tzinfo=zone)
        now = datetime(2026, 3, 8, 3, 0, 5, tzinfo=zone)
        self.assertTrue(fresh(observed, now, 10))
        self.assertTrue(fresh(observed.astimezone(timezone.utc), now, 10))
        self.assertFalse(fresh(observed, now, 9))
