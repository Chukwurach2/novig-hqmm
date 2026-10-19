import unittest
from datetime import datetime, timezone
from hqmm.report import american_decimal,game_cards,markdown
from decimal import Decimal as D

NOW=datetime(2026,10,19,12,tzinfo=timezone.utc)
def row(**changes):
    item=dict(game_id='g',game='A @ B',starts_at='2026-10-19T20:00:00Z',
              observed_at='2026-10-19T11:59:00Z',quote_at='2026-10-19T11:58:00Z',
              participant='Player',market='completions',line='19.5',side='over',book='synthetic',
              american_odds='128',fair_probability='.46',fair_source='synthetic test',
              rationale='Test fixture only',identity_verified=True,cost_per_dollar='.01')
    item.update(changes);return item

class Reports(unittest.TestCase):
    def test_odds(self):
        self.assertEqual(american_decimal(200),D(3))
        self.assertEqual(american_decimal(-200),D('1.5'))
        for x in ('NaN',0,99):
            with self.assertRaises(ValueError):american_decimal(x)
    def test_cost_roi_and_duplicate_venues(self):
        card=game_cards([row(),row(book='other',american_odds='125')],NOW)['games'][0]
        self.assertEqual(len(card['picks']),1)
        self.assertEqual(card['shortfall'],3)
        self.assertEqual(D(card['picks'][0]['net_roi']),D('.0388'))
    def test_unverified_never_promoted(self):
        for changes in ({'quote_at':None},{'quote_at':'2026-10-19T11:00:00Z'},
                        {'identity_verified':False},{'starts_at':'2026-10-19T10:00:00Z'}):
            item=game_cards([row(**changes)],NOW)['games'][0]['picks'][0]
            self.assertEqual(item['classification'],'unverified lean')
    def test_four_distinct_and_negative_labeled(self):
        rows=[row(participant=str(i),fair_probability='.4') for i in range(5)]
        report=game_cards(rows,NOW)
        self.assertEqual(len(report['games'][0]['picks']),4)
        self.assertEqual(report['games'][0]['picks'][0]['classification'],'price watch / no positive edge')
        self.assertIn('not a parlay',markdown(report))
    def test_identity_conflict(self):
        with self.assertRaises(ValueError):game_cards([row(),row(game='C @ D')],NOW)
