from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from hqmm.reference_mapping import ReviewedReferenceMapping, estimate_mapped
from hqmm.schemas import Reference


class ReviewedReferenceMappingTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, tzinfo=timezone.utc)
        self.mapping = ReviewedReferenceMapping(
            "provider-event", "h2h", "novig-event", "novig-market",
            (("Home", "outcome-1"), ("Away", "outcome-2")), "review-1",
        )
        self.row = Reference(
            "provider-event", "book-1", "h2h", ("Away", "Home"),
            (Decimal("4"), Decimal("2")), self.now,
        )

    def test_maps_odds_by_label_even_when_order_is_reversed(self):
        probabilities = estimate_mapped([self.row], self.mapping, self.now)
        self.assertEqual(probabilities["outcome-1"], Decimal(2) / 3)
        self.assertEqual(probabilities["outcome-2"], Decimal(1) / 3)
        self.assertEqual(self.row.outcomes, ("Away", "Home"))

    def test_rejects_wrong_event_market_or_labels(self):
        for row in (
            replace(self.row, event_id="same-teams-different-event"),
            replace(self.row, market="different-rules"),
            replace(self.row, outcomes=("away", "Home")),
        ):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, "reviewed"):
                estimate_mapped([self.row, row], self.mapping, self.now)

    def test_rejects_ambiguous_or_undocumented_mapping(self):
        for changes in (
            {"outcomes": (("Home", "outcome-1"), ("Away", "outcome-1"))},
            {"outcomes": (("Home", "outcome-1"), ("Home", "outcome-2"))},
            {"evidence_id": " "},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(self.mapping, **changes)

    def test_preserves_source_clock_and_bookmaker_checks(self):
        for offset in (-31, 1):
            row = replace(self.row, observed_at=self.now + timedelta(seconds=offset))
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, "no fresh"):
                estimate_mapped([row], self.mapping, self.now)
        with self.assertRaisesRegex(ValueError, "duplicate bookmaker"):
            estimate_mapped([self.row, self.row], self.mapping, self.now)
