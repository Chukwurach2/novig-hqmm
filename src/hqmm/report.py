"""Per-game paper research cards from explicitly curated, authorized observations."""
import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal as D
from pathlib import Path


def american_decimal(odds):
    x = D(str(odds))
    if not x.is_finite() or abs(x) < 100:
        raise ValueError('American odds must be <= -100 or >= +100')
    return 1 + (x / 100 if x > 0 else 100 / -x)


def stamp(value):
    at = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if at.tzinfo is None:
        raise ValueError('timezone required')
    return at


def evaluate(row, now, max_age=600):
    start, observed = stamp(row['starts_at']), stamp(row['observed_at'])
    quote_time = stamp(row['quote_at']) if row.get('quote_at') else None
    p, fee = D(str(row['fair_probability'])), D(str(row.get('cost_per_dollar', '0')))
    odds = american_decimal(row['american_odds'])
    if not p.is_finite() or not 0 < p < 1 or not fee.is_finite() or fee < 0:
        raise ValueError('invalid fair probability or cost')
    if not row.get('fair_source') or not row.get('rationale'):
        raise ValueError('source and rationale required')
    if row['side'] not in ('over', 'under', 'yes', 'no', 'home', 'away'):
        raise ValueError('unknown side')
    if now.tzinfo is None:
        raise ValueError('timezone required')
    age = (now - observed).total_seconds()
    quote_age = (now - quote_time).total_seconds() if quote_time else None
    reasons = []
    if not 0 <= age <= max_age: reasons.append('observation stale or future')
    if quote_time is None: reasons.append('individual quote timestamp unverified')
    elif not 0 <= quote_age <= max_age: reasons.append('individual quote stale or future')
    if now >= start: reasons.append('game started')
    if row.get('identity_verified') is not True: reasons.append('contract identity unverified')
    net_roi = p * odds - 1 - fee
    return dict(row, decimal_odds=str(odds), net_roi=str(net_roi),
                break_even_decimal=str((1 + fee) / p),
                classification=('unverified lean' if reasons else
                                'estimated value' if net_roi > 0 else 'price watch / no positive edge'),
                warnings=reasons, observed_age_seconds=age)


def game_cards(rows, now, target=4, max_age=600):
    if not 3 <= target <= 4 or max_age <= 0:
        raise ValueError('target 3 or 4 and positive max_age required')
    grouped = {}
    for row in rows:
        evaluated = evaluate(row, now, max_age)
        game = grouped.setdefault(row['game_id'], {'game': row['game'], 'starts_at': row['starts_at'], 'candidates': []})
        if (game['game'],game['starts_at']) != (row['game'],row['starts_at']):
            raise ValueError('inconsistent game identity')
        game['candidates'].append(evaluated)
    cards = []
    for game_id, game in grouped.items():
        ranked = sorted(game.pop('candidates'), key=lambda r:(bool(r['warnings']),-D(r['net_roi'])))
        chosen, seen = [], set()
        for row in ranked:
            key = (row['participant'],row['market'],row.get('line'),row['side'])
            if key in seen: continue # Same selection at another book is an alternative, not another pick.
            chosen.append(row);seen.add(key)
            if len(chosen)==target: break
        cards.append(dict(game_id=game_id, **game, picks=chosen, coverage_target=target,
                          shortfall=max(0,target-len(chosen)),
                          note='Paper research leans, not a parlay. Shared game/player exposures may be correlated.'))
    return {'generated_at':now.isoformat(),'mode':'paper','games':cards}


def markdown(report):
    lines=['# Per-game paper leans', '', 'Generated: '+report['generated_at'],
           'Estimated values depend on the supplied fair probabilities; they are not proven returns.','']
    for game in report['games']:
        lines.extend(['## '+game['game'], '', 'Kickoff: '+game['starts_at'], '',
                      '| Rank | Selection | Book / odds | Fair probability | Estimated net ROI | Status |',
                      '|---|---|---|---|---|---|'])
        for i,p in enumerate(game['picks'],1):
            selection=f"{p['participant']} {p['side']} {p.get('line','')} {p['market']}"
            lines.append(f"| {i} | {selection} | {p['book']} / {p['american_odds']} | {D(p['fair_probability']):.2%} | {D(p['net_roi']):.2%} | {p['classification']} |")
        lines.extend(['',game['note'],''])
        for i,p in enumerate(game['picks'],1):
            lines.extend([f"{i}. {p['rationale']} Source: {p['fair_source']}. "
                          f"Break-even decimal odds: {D(p['break_even_decimal']):.4f}. "
                          f"Observed: {p['observed_at']}. Warnings: {', '.join(p['warnings']) or 'none'}. "
                          f"Capacity: {p.get('available_size','unknown')}."])
        if game['shortfall']:lines.append(f"Coverage shortfall: {game['shortfall']} candidates unavailable; none invented.")
        lines.append('')
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description='Curated per-game paper lean reports')
    parser.add_argument('input',help='Authorized local JSON observation list')
    parser.add_argument('--output',default='runs/game-cards')
    parser.add_argument('--now',help='Explicit ISO timestamp for deterministic replay')
    args=parser.parse_args()
    now=stamp(args.now) if args.now else datetime.now(timezone.utc)
    report=game_cards(json.loads(Path(args.input).read_text()),now)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    out.with_suffix('.md').write_text(markdown(report))
    print(out.with_suffix('.md'))


if __name__=='__main__':main()
