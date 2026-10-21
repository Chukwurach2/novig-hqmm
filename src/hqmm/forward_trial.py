"""Offline, one-event prospective paper decisions; no network or execution."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json

POLICY_HASH = 'a4949c871c7e3c2eae7b06108d7e2ec284a97d89944b7cbfa4e23273e20f776f'
EFFECTIVE = datetime.fromisoformat('2026-10-21T20:23:00+00:00')
BOOKS = {'fanduel','draftkings','betmgm','williamhill_us','fanatics','thescorebet','ballybet'}

def stamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed

def decimal(value):
    if isinstance(value, bool):
        raise ValueError('Boolean financial value')
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError('Nonfinite financial value')
    return result

def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def decide_capture(capture, policy_hash, previous=None):
    """Caller persists returned locked decisions append-only before later captures.

    Completeness and reviewed_* fields are explicit reviewer attestations, not
    verification of a provider license, rule webpage or executable book offer.
    """
    if policy_hash != POLICY_HASH:
        raise ValueError('Exact frozen policy SHA256 required')
    event = {k: capture[k] for k in ('sport','game_id','home_team','away_team','kickoff')}
    if event['sport'] not in ('nfl','nba') or not all(isinstance(v,str) and v for v in event.values()):
        raise ValueError('Explicit event identity required')
    event_hash = fingerprint(event)
    if previous is not None:
        if previous.get('event_hash') != event_hash or previous.get('policy_hash') != policy_hash or previous.get('locked') is not True:
            raise ValueError('Prior decision identity or policy mismatch')
        return previous.copy()
    at, kickoff = stamp(capture['captured_at']), stamp(event['kickoff'])
    base = dict(policy_id='forward-consensus-v1', policy_hash=policy_hash, event_hash=event_hash,
                event=event, capture_hash=fingerprint(capture), decision_at=capture['captured_at'], mode='paper')
    minutes = Decimal(str((kickoff-at).total_seconds())) / 60
    if at < EFFECTIVE or not Decimal(30) <= minutes <= Decimal(360):
        return dict(base, locked=False, status='pending', reason='outside_registered_window')
    if capture.get('authorized') is not True or capture.get('complete') is not True:
        return dict(base, locked=False, status='pending', reason='incomplete_or_unauthorized')
    candidates, rejected = [], []
    for item in capture['candidates']:
        try:
            if not isinstance(item.get('id'), str) or not item['id']:
                raise ValueError('observation_id')
            if any(item.get(k) != v for k,v in event.items()):
                raise ValueError('identity')
            if item.get('book_key') not in BOOKS or item.get('market') not in ('FULL_GAME_SPREAD','FULL_GAME_TOTAL'):
                raise ValueError('contract_or_venue')
            if not all(item.get(k) is True for k in ('reviewed_identity','reviewed_rules','reviewed_eligibility','availability_checked','offer_verified')):
                raise ValueError('review_incomplete')
            line, odds = decimal(item['line']), decimal(item['american_odds'])
            if abs(line % 1) != Decimal('.5') or odds != odds.to_integral_value() or abs(odds) < 100 or odds < -150:
                raise ValueError('line_or_odds')
            if item['selection'] not in (('Over','Under') if item['market']=='FULL_GAME_TOTAL' else (event['home_team'],event['away_team'])):
                raise ValueError('selection')
            def fresh(value):
                age = (at-stamp(value)).total_seconds()
                if not 0 <= age < 900:
                    raise ValueError('source_age')
            fresh(item['observed_at'])
            refs = item['reference_quotes']; operators=set(); probabilities=[]
            for ref in refs:
                operator = {'espnbet':'thescorebet'}.get(ref['book_key'],ref['book_key'])
                if operator == item['book_key'] or operator in operators or not operator:
                    raise ValueError('dependent_reference')
                if any(ref.get(k) != item.get(k) for k in (*event,'market','selection','line')):
                    raise ValueError('reference_identity')
                fresh(ref['observed_at']); p=decimal(ref['fair_probability'])
                if not 0 < p < 1:
                    raise ValueError('probability')
                probabilities.append(p); operators.add(operator)
            if len(operators)<2:
                raise ValueError('reference_count')
            p=decimal(item['fair_probability']); price=1+(odds/100 if odds>0 else 100/abs(odds))
            if not 0<p<1 or p-1/price < Decimal('.03') or p*price-1 < Decimal('.04') or min(probabilities)*price-1 <= 0:
                raise ValueError('threshold')
            key=json.dumps([item['market'],item['selection'],str(line),item['book_key']])
            candidates.append((min(probabilities)*price-1,p*price-1,key,item['id']))
        except (ValueError, KeyError, TypeError, InvalidOperation) as error:
            rejected.append({'id':item.get('id'), 'reason':str(error)})
    candidates.sort(key=lambda x:(-x[0],-x[1],x[2]))
    return dict(base, locked=True, status='selected' if candidates else 'abstain',
                selection_id=candidates[0][3] if candidates else None, rejection_reasons=rejected,
                candidate_count=len(capture['candidates']), accepted_price_verified=False, stake=None)
