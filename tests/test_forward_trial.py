import copy
import unittest
from hqmm.forward_trial import decide_capture, POLICY_HASH

class ForwardTrialTests(unittest.TestCase):
    def fixture(self):
        event=dict(sport='nba',game_id='synthetic',home_team='Home',away_team='Away',kickoff='2026-10-22T00:00:00Z')
        item=dict(event,id='a',market_status='open',market='FULL_GAME_TOTAL',selection='Over',line='210.5',book_key='draftkings',american_odds='100',fair_probability='.56',observed_at='2026-10-21T21:29:00Z',reviewed_identity=True,reviewed_rules=True,reviewed_eligibility=True,availability_checked=True,offer_verified=True)
        item['reference_quotes']=[dict(event,book_key=b,market_status='open',market=item['market'],selection=item['selection'],line=item['line'],fair_probability='.55',observed_at=item['observed_at']) for b in ('fanduel','betmgm')]
        return dict(event,captured_at='2026-10-21T21:30:00Z',authorized=True,complete=True,candidates=[item])
    def decide(self,c,previous=None):return decide_capture(c,POLICY_HASH,previous)
    def test_selects_with_hashes_and_no_wager(self):
        r=self.decide(self.fixture());self.assertEqual(r['selection_id'],'a');self.assertTrue(r['locked']);self.assertIsNone(r['stake']);self.assertEqual(len(r['capture_hash']),64)
    def test_abstention_locks_first_complete_capture(self):
        c=self.fixture();c['candidates'][0]['fair_probability']='.50';r=self.decide(c);self.assertEqual(r['status'],'abstain');self.assertEqual(self.decide(self.fixture(),r),r)
    def test_pending_does_not_lock(self):
        for patch in ({'complete':False},{'authorized':False},{'captured_at':'2026-10-21T20:00:00Z'}):
            self.assertFalse(self.decide(dict(self.fixture(),**patch))['locked'])
    def test_source_and_reference_gates(self):
        for patch in ({'observed_at':'2026-10-21T21:31:00Z'},{'observed_at':'2026-10-21T21:15:00Z'},{'offer_verified':False},{'line':'210'},{'american_odds':'-151'},{'fair_probability':'NaN'}):
            c=self.fixture();c['candidates'][0].update(patch);self.assertEqual(self.decide(c)['status'],'abstain')
    def test_alias_and_exact_reference_identity(self):
        for patch in ({'book_key':'fanduel'},{'kickoff':'2026-10-22T00:01:00Z'},{'line':'211.5'}):
            c=self.fixture();c['candidates'][0]['reference_quotes'][1].update(patch);self.assertEqual(self.decide(c)['status'],'abstain')
    def test_deterministic_ranking_and_one_per_event(self):
        c=self.fixture();b=copy.deepcopy(c['candidates'][0]);b['id']='b';b['fair_probability']='.57';c['candidates'].append(b);self.assertEqual(self.decide(c)['selection_id'],'b')
    def test_mismatched_previous_rejected(self):
        r=self.decide(self.fixture());c=self.fixture();c['game_id']='other'
        with self.assertRaises(ValueError):self.decide(c,r)

    def test_frozen_policy_hash_required(self):
        with self.assertRaises(ValueError):decide_capture(self.fixture(),"b"*64)

    def test_suspended_closed_and_unknown_offers_rejected(self):
        for status in ('suspended','closed','settled',None):
            c=self.fixture();c['candidates'][0]['market_status']=status
            r=self.decide(c);self.assertEqual(r['status'],'abstain');self.assertEqual(r['rejection_reasons'][0]['reason'],'offer_market_not_open')
    def test_suspended_or_missing_reference_state_rejected(self):
        for status in ('suspended','closed',None):
            c=self.fixture();c['candidates'][0]['reference_quotes'][0]['market_status']=status
            r=self.decide(c);self.assertEqual(r['status'],'abstain');self.assertEqual(r['rejection_reasons'][0]['reason'],'reference_market_not_open')
    def test_boolean_review_does_not_override_market_state(self):
        c=self.fixture();c['candidates'][0].pop('market_status');self.assertEqual(self.decide(c)['status'],'abstain')
