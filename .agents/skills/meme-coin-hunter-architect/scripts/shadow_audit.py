#!/usr/bin/env python3
"""Offline counterfactual monitor for rejected or accepted memecoin candidates.

Prices in this report are *observed*, not executable. It intentionally avoids
calling a rejected token a mistake just because its chart later went up.
No wallet, no network, no live trading.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

DECISIONS = {'REJECTED', 'INSUFFICIENT_DATA', 'WATCH', 'PAPER_CANDIDATE'}


def utc(value):
    if not isinstance(value, str):
        raise ValueError('UTC timestamp required')
    d = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('timestamp must have timezone')
    return d.astimezone(dt.timezone.utc)


def valid_price(p):
    return isinstance(p, (float, int)) and not isinstance(p, bool) and math.isfinite(p) and p > 0


def analyze(stream, horizon_seconds=1800, max_terminal_gap_seconds=120, runner_return=1.0):
    """Evaluate future chart movements without hindsight in decision production.

    Required input: monotonically time-ordered JSON events. Decisions include
    kind, mint, observed_at, decision, price_usd, and reason. Market snapshots
    include kind, mint, observed_at, price_usd, liquidity_usd, tradable.
    For terminal evaluation, a final event at/after horizon is required.
    """
    if horizon_seconds <= 0 or max_terminal_gap_seconds <= 0:
        raise ValueError('positive horizon and max gap required')
    decisions = []
    by_mint = {}
    last = None
    for row in stream:
        t = utc(row.get('observed_at'))
        if last is not None and t < last:
            raise ValueError('events must be ordered by observed_at')
        last = t
        mint = row.get('mint')
        if not isinstance(mint, str) or not mint:
            raise ValueError('mint is required')
        if row.get('kind') == 'decision':
            if row.get('decision') not in DECISIONS or not valid_price(row.get('price_usd')):
                raise ValueError('valid decision and reference price required')
            case = {'mint': mint, 'decision': row['decision'], 'decision_at': t,
                    'reference_price': row['price_usd'], 'reason': row.get('reason', 'unspecified'),
                    'quotes': [], 'horizon_reached': False}
            decisions.append(case)
            by_mint.setdefault(mint, []).append(case)
        elif row.get('kind') == 'market':
            for case in by_mint.get(mint, []):
                delta = (t - case['decision_at']).total_seconds()
                if delta >= horizon_seconds:
                    case['horizon_reached'] = True
                if delta <= 0 or delta > horizon_seconds:
                    continue
                if not valid_price(row.get('price_usd')) or not valid_price(row.get('liquidity_usd')) or row.get('tradable') is not True:
                    continue
                case['quotes'].append((t, row['price_usd']))
        else:
            raise ValueError('unknown event kind')
    results = []
    for case in decisions:
        quotes = case['quotes']
        deadline = case['decision_at'] + dt.timedelta(seconds=horizon_seconds)
        recent = bool(quotes) and (deadline - quotes[-1][0]).total_seconds() <= max_terminal_gap_seconds
        complete = case['horizon_reached'] and recent
        d = {'mint': case['mint'], 'decision': case['decision'],
             'decision_at': case['decision_at'].isoformat(), 'reason': case['reason'],
             'status': 'OBSERVED' if complete else 'CENSORED', 'quote_count': len(quotes),
             'note': 'Returns are chart observations, not proof of executable trades.'}
        if complete:
            prices = [p for _, p in quotes]
            reference = case['reference_price']
            d.update(max_observed_return_pct=round(100 * (max(prices) / reference - 1), 2),
                     min_observed_return_pct=round(100 * (min(prices) / reference - 1), 2),
                     terminal_return_pct=round(100 * (prices[-1] / reference - 1), 2),
                     observed_runner=max(prices) / reference - 1 >= runner_return)
        results.append(d)
    summary = {}
    for status in sorted(DECISIONS):
        subset = [r for r in results if r['decision'] == status]
        observed = [r for r in subset if r['status'] == 'OBSERVED']
        summary[status] = {'total': len(subset), 'observed': len(observed),
                           'censored': len(subset) - len(observed),
                           'observed_runners': sum(bool(r['observed_runner']) for r in observed),
                           'runner_rate_on_observed_only': (round(sum(bool(r['observed_runner']) for r in observed) / len(observed), 4)
                                                            if observed else None)}
    return {'horizon_seconds': horizon_seconds, 'cases': results, 'summary': summary,
            'limitations': ['No inference about fills, wallet profitability or causal advantage',
                            'Missing future data is censored rather than counted as a loss',
                            'Unsafe rejected tokens remain unsafe even if later chart price rose']}


def main():
    p=argparse.ArgumentParser(description='OFFLINE rejection counterfactuals')
    p.add_argument('events', type=Path)
    p.add_argument('--horizon-seconds', type=int, default=1800)
    p.add_argument('--max-terminal-gap-seconds', type=int, default=120)
    args=p.parse_args()
    with args.events.open(encoding='utf-8') as f:
        data=[json.loads(line) for line in f if line.strip()]
    print(json.dumps(analyze(data,args.horizon_seconds,args.max_terminal_gap_seconds),indent=2))


if __name__=='__main__':main()
