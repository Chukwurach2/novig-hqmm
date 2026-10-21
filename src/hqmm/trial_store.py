"""Local private paper decisions. No remote interface or execution."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
from .forward_trial import decide_capture, POLICY_HASH, stamp


def record_capture(path, capture, *, now=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError('Symlink ledger rejected')
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    os.close(fd)
    if path.stat().st_mode & 0o077:
        raise ValueError('Private ledger requires owner-only permissions')
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    try:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE TABLE IF NOT EXISTS decisions (policy TEXT NOT NULL, sport TEXT NOT NULL, game_id TEXT NOT NULL, decision TEXT NOT NULL, capture TEXT NOT NULL, PRIMARY KEY(policy,sport,game_id))')
        db.execute("CREATE TRIGGER IF NOT EXISTS no_decision_update BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT,'append only'); END")
        db.execute("CREATE TRIGGER IF NOT EXISTS no_decision_delete BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT,'append only'); END")
        key = (POLICY_HASH, capture['sport'], capture['game_id'])
        prior = db.execute('SELECT decision FROM decisions WHERE policy=? AND sport=? AND game_id=?', key).fetchone()
        if prior:
            result = decide_capture(capture, POLICY_HASH, json.loads(prior[0]))
        else:
            clock = now or datetime.now(timezone.utc)
            age = (clock-stamp(capture['captured_at'])).total_seconds()
            if not 0 <= age < 900:
                raise ValueError('New prospective capture must be current; no historical backfill')
            result = decide_capture(capture, POLICY_HASH)
            if result['locked']:
                db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (*key,json.dumps(result,sort_keys=True),json.dumps(capture,sort_keys=True)))
        db.execute('COMMIT')
        return result
    except Exception:
        if db.in_transaction:
            db.execute('ROLLBACK')
        raise
    finally:
        db.close()
