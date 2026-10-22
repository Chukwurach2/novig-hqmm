from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from hqmm.trial_store import record_capture

class TrialStoreTests(unittest.TestCase):
    def fixture(self):
        return dict(sport='nba',game_id='synthetic',home_team='Home',away_team='Away',kickoff='2026-10-22T00:00:00Z',captured_at='2026-10-21T21:30:00Z',authorized=True,complete=True,candidates=[])
    def test_reopen_keeps_abstention_and_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private.sqlite';c=self.fixture();now=datetime.fromisoformat('2026-10-21T21:30:01+00:00')
            r=record_capture(p,c,now=now);self.assertEqual(r['status'],'abstain')
            self.assertEqual(record_capture(p,c),r)
            with sqlite3.connect(p) as db:
                self.assertEqual(json.loads(db.execute('SELECT capture FROM decisions').fetchone()[0]),c)
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM decisions')
            self.assertEqual(p.stat().st_mode & 0o777,0o600)
    def test_concurrent_writers_create_one_decision(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private.sqlite';now=datetime.fromisoformat('2026-10-21T21:30:01+00:00')
            with ThreadPoolExecutor(max_workers=2) as pool:rs=list(pool.map(lambda _:record_capture(p,self.fixture(),now=now),range(2)))
            self.assertEqual(rs[0],rs[1])
            with sqlite3.connect(p) as db:self.assertEqual(db.execute('SELECT count(*) FROM decisions').fetchone()[0],1)
    def test_identity_change_does_not_create_second_event(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.sqlite';now=datetime.fromisoformat('2026-10-21T21:30:01+00:00');record_capture(p,self.fixture(),now=now)
            with self.assertRaises(ValueError):record_capture(p,dict(self.fixture(),kickoff='2026-10-22T00:10:00Z'),now=now)
    def test_old_and_future_new_captures_are_not_backfilled(self):
        for clock in ['2026-10-21T21:29:00+00:00','2026-10-21T21:45:00+00:00']:
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaises(ValueError):record_capture(Path(d)/'p.sqlite',self.fixture(),now=datetime.fromisoformat(clock))
    def test_pending_capture_does_not_lock_event(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.sqlite';now=datetime.fromisoformat('2026-10-21T21:30:01+00:00');self.assertFalse(record_capture(p,dict(self.fixture(),complete=False),now=now)['locked']);self.assertTrue(record_capture(p,self.fixture(),now=now)['locked'])
