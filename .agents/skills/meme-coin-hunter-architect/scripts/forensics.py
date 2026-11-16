#!/usr/bin/env python3
"""Conservative offline Solana holder clustering and token-extension screening.

This module does not call RPC, establish wallet ownership, or place trades.
Inputs MUST be independently normalized on-chain records. A shared funder is
not proof of common beneficial ownership. Output names the heuristic evidence.
"""
import datetime as dt
import json
import math
from collections import defaultdict

HIGH_RISK_EXTENSIONS = {
    'permanent_delegate', 'non_transferable', 'pausable',
    'default_account_state_frozen', 'confidential_transfer', 'transfer_hook',
}
KNOWN_EXTENSIONS = HIGH_RISK_EXTENSIONS | {
    'transfer_fee_bps', 'metadata_pointer', 'token_metadata',
    'interest_bearing', 'memo_required', 'immutable_owner',
}


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        d = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return d.astimezone(dt.timezone.utc) if d.tzinfo else None
    except ValueError:
        return None


def token_extension_gate(program, extensions):
    """Conservative policy, not a complete on-chain mint decoder."""
    if program not in ('spl-token', 'token-2022'):
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['unverified token program']}
    if program == 'spl-token':
        return {'status': 'PASS', 'reasons': []}
    if not isinstance(extensions, dict):
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['missing full Token-2022 extension inventory']}
    unknown = set(extensions) - KNOWN_EXTENSIONS - {'inventory_complete'}
    if unknown:
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['unrecognized Token-2022 extensions: ' + ', '.join(sorted(unknown))]}
    if extensions.get('inventory_complete') is not True:
        # inventory_complete is a source-provenance flag, not a token extension.
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['Token-2022 extension inventory not independently complete']}
    unsafe = sorted(k for k in HIGH_RISK_EXTENSIONS if extensions.get(k) is True)
    fee = extensions.get('transfer_fee_bps', 0)
    if isinstance(fee, bool) or not isinstance(fee, (int, float)) or not math.isfinite(fee) or fee < 0:
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['unverified transfer fee']}
    if fee > 300:
        unsafe.append('excessive transfer fee')
    return {'status': 'REJECTED' if unsafe else 'PASS', 'reasons': unsafe}


def analyze_holders(holders, *, cluster_cap_pct=15.0, max_funding_gap_s=120,
                    max_buy_gap_s=90, require_provenance=True):
    """Find suspicious clusters using two independent timing/funding indicators.

    A link requires SAME private funding address + near-time funding +
    near-time first buys. Exchanges, pools, burns and known routers excluded.
    Missing wallet provenance is tracked rather than silently declared safe.
    """
    if not isinstance(holders, list) or not holders:
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['no verified holder snapshot'], 'clusters': []}
    by_wallet = {}
    missing = []
    for h in holders:
        if not isinstance(h, dict):
            return {'status': 'INSUFFICIENT_DATA', 'reasons': ['malformed holder entry'], 'clusters': []}
        wallet = h.get('wallet')
        pct = h.get('pct')
        if not isinstance(wallet, str) or not wallet or wallet in by_wallet:
            return {'status': 'INSUFFICIENT_DATA', 'reasons': ['empty or duplicate wallet'], 'clusters': []}
        if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not math.isfinite(pct) or pct < 0 or pct > 100:
            return {'status': 'INSUFFICIENT_DATA', 'reasons': ['invalid holding percentage'], 'clusters': []}
        by_wallet[wallet] = h
    if any(h.get('account_type') not in ('wallet', 'pool', 'burn', 'exchange', 'escrow') for h in holders):
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['unverified holder account classification'], 'clusters': []}
    if sum(h['pct'] for h in holders) > 100.001:
        return {'status': 'INSUFFICIENT_DATA', 'reasons': ['holder percentages exceed supply'], 'clusters': []}
    eligible = [h for h in holders if h.get('account_type') == 'wallet']
    for h in eligible:
        if not all((h.get('funder'), timestamp(h.get('funded_at')), timestamp(h.get('first_buy_at')),
                    h.get('funder_type') in ('private', 'exchange', 'bridge', 'unknown'))):
            missing.append(h['wallet'])
    parent = {h['wallet']: h['wallet'] for h in eligible}

    def root(w):
        while parent[w] != w:
            parent[w] = parent[parent[w]]
            w = parent[w]
        return w

    def link(a, b):
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[rb] = ra

    by_funder = defaultdict(list)
    for h in eligible:
        if h.get('funder_type') == 'private' and h.get('funder') and timestamp(h.get('funded_at')) and timestamp(h.get('first_buy_at')):
            by_funder[h['funder']].append(h)
    edges = []
    for funder, group in by_funder.items():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                fund_gap = abs((timestamp(a['funded_at']) - timestamp(b['funded_at'])).total_seconds())
                buy_gap = abs((timestamp(a['first_buy_at']) - timestamp(b['first_buy_at'])).total_seconds())
                if fund_gap <= max_funding_gap_s and buy_gap <= max_buy_gap_s:
                    link(a['wallet'], b['wallet'])
                    edges.append({'a': a['wallet'], 'b': b['wallet'], 'reason': 'same private funder and synchronized funding/buys',
                                  'funding_gap_s': fund_gap, 'buy_gap_s': buy_gap})
    groups = defaultdict(list)
    for h in eligible:
        groups[root(h['wallet'])].append(h)
    clusters = sorted(({'wallets': sorted(h['wallet'] for h in group),
                        'total_pct': round(sum(h['pct'] for h in group), 4),
                        'evidence': [e for e in edges if e['a'] in {h['wallet'] for h in group} and e['b'] in {h['wallet'] for h in group}]}
                       for group in groups.values() if len(group) > 1),
                      key=lambda g: (-g['total_pct'], g['wallets']))
    flags = [c for c in clusters if c['total_pct'] > cluster_cap_pct]
    reasons = []
    if flags:
        reasons.append('suspicious synchronized private-funded cluster exceeds configured share cap')
    if require_provenance and missing:
        reasons.append(f'{len(missing)} holder wallet(s) missing independent funding/buy provenance')
    status = 'REVIEW' if flags else ('INSUFFICIENT_DATA' if reasons else 'NO_CLUSTER_FLAG')
    return {'status': status, 'reasons': reasons, 'clusters': clusters,
            'missing_provenance_wallets': sorted(missing),
            'caveat': 'Heuristic association only; this does not prove common control or rule out concealed connections.'}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='OFFLINE wallet heuristics; no trading/network')
    p.add_argument('snapshot', help='JSON holder array or object with holders key')
    args = p.parse_args()
    with open(args.snapshot, encoding='utf-8') as f:
        data = json.load(f)
    print(json.dumps(analyze_holders(data.get('holders', []) if isinstance(data, dict) else data), indent=2))
