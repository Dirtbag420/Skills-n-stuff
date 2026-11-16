#!/usr/bin/env python3
"""Offline, next-observation, CPMM-only Solana paper execution simulator.

No wallet, network, signing, trade submission or exchange APIs.
Not a live execution forecast: price impact is only an approximation for a
constant-product pool with roughly balanced reserves. Unrecognized pool curves
must NOT be filled with this estimator.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

DEFAULTS = {
    'starting_cash_usd': 1000., 'latency_seconds': 2.,
    'max_quote_age_seconds': 15., 'min_liquidity_usd': 30000.,
    'max_position_fraction': .05, 'max_total_exposure_fraction': .10,
    'max_trade_liquidity_fraction': .01, 'max_impact_bps': 200.,
    'fee_bps': 30., 'adverse_spread_bps': 25., 'fixed_fee_usd': .05,
    'buy_order_ttl_seconds': 45.,
}


def utc(s):
    if not isinstance(s, str):
        raise ValueError('timestamp required')
    d = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('timestamps require timezone')
    return d.astimezone(dt.timezone.utc)


def finite_positive(x):
    return isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x) and x > 0


class MarketReplay:
    def __init__(self, cfg=None):
        self.cfg = {**DEFAULTS, **(cfg or {})}
        if not finite_positive(self.cfg['starting_cash_usd']):
            raise ValueError('starting cash must be positive')
        self.cash = float(self.cfg['starting_cash_usd'])
        self.positions = {}  # mint => {qty, cost, last_price, last_time}
        self.orders = []
        self.fills = []
        self.events = []
        self.seen = set()
        self.last_time = None
        self.next_order_id = 1
        self.realized_pnl = 0.

    def liquidity_exposure(self):
        return sum(p['qty'] * p['last_price'] for p in self.positions.values())

    def equity(self):
        # Missing/non-tradable/stale positions are marked at zero conservatively.
        return self.cash + sum(
            p['qty'] * p['last_price']
            if p['mark_valid'] and self.last_time is not None
            and 0 <= (self.last_time - utc(p['last_time'])).total_seconds() <= self.cfg['max_quote_age_seconds']
            else 0. for p in self.positions.values())

    def _quote(self, row, event_time):
        if row.get('risk_state') != 'PASS' or row.get('tradable') is not True:
            return None, 'not independently verified tradable'
        if row.get('pool_type') != 'cpmm':
            return None, 'unsupported pool curve'
        p, l = row.get('price_usd'), row.get('liquidity_usd')
        if not finite_positive(p) or not finite_positive(l) or l < self.cfg['min_liquidity_usd']:
            return None, 'missing/insufficient price or liquidity'
        try:
            age = (event_time - utc(row['market_observed_at'])).total_seconds()
        except (KeyError, ValueError, TypeError):
            return None, 'missing quote timestamp'
        if age < 0 or age > self.cfg['max_quote_age_seconds']:
            return None, 'stale or future quote'
        return (float(p), float(l)), None

    def _buy(self, order, price, liquidity, time):
        c = self.cfg
        existing_exposure = self.liquidity_exposure()
        allowed = min(order['requested_usd'], self.equity() * c['max_position_fraction'],
                      max(0., self.equity() * c['max_total_exposure_fraction'] - existing_exposure),
                      liquidity * c['max_trade_liquidity_fraction'],
                      max(0., (self.cash - c['fixed_fee_usd']) / (1 + c['fee_bps'] / 10000)))
        if allowed <= 0:
            return None, 'position/cash/liquidity cap'
        # CPMM approximation: effective buy average price rises with quote amount / quote reserve.
        impact_bps = 10000 * allowed / (liquidity / 2)
        if impact_bps > c['max_impact_bps']:
            return None, 'projected price impact exceeds cap'
        price_fill = price * (1 + impact_bps / 10000) * (1 + c['adverse_spread_bps'] / 10000)
        fee = allowed * c['fee_bps'] / 10000 + c['fixed_fee_usd']
        qty = allowed / price_fill
        self.cash -= allowed + fee
        self.positions[order['mint']] = {'qty': qty, 'cost': allowed + fee, 'last_price': price,
                                         'last_time': time.isoformat(), 'mark_valid': True}
        return {'side': 'BUY', 'qty': qty, 'gross_usd': allowed, 'fee_usd': fee,
                'fill_price': price_fill, 'impact_bps': impact_bps}, None

    def _sell(self, order, price, liquidity, time):
        c = self.cfg
        pos = self.positions.get(order['mint'])
        if pos is None:
            return None, 'no open position'
        raw_value = pos['qty'] * price
        impact_bps = 10000 * raw_value / (liquidity / 2)
        if raw_value > liquidity * c['max_trade_liquidity_fraction'] or impact_bps > c['max_impact_bps']:
            return None, 'exit cannot be sized safely at observed liquidity'
        gross = raw_value / (1 + impact_bps / 10000) * (1 - c['adverse_spread_bps'] / 10000)
        fee = gross * c['fee_bps'] / 10000 + c['fixed_fee_usd']
        net = max(0., gross - fee)
        self.cash += net
        pnl = net - pos['cost']
        self.realized_pnl += pnl
        del self.positions[order['mint']]
        return {'side': 'SELL', 'qty': pos['qty'], 'gross_usd': gross, 'fee_usd': fee,
                'fill_price': gross / pos['qty'], 'impact_bps': impact_bps, 'realized_pnl_usd': pnl}, None

    def on_event(self, row):
        when = utc(row.get('observed_at'))
        if self.last_time is not None and when < self.last_time:
            raise ValueError('events must be ordered by UTC event time')
        mint, source = row.get('mint'), row.get('source_event_id')
        if row.get('chain') != 'solana' or not isinstance(mint, str) or not mint or not source:
            raise ValueError('Solana mint and source_event_id required')
        key = (mint, str(source))
        if key in self.seen:
            return {'status': 'DUPLICATE', 'mint': mint, 'source_event_id': source}
        self.seen.add(key)
        self.last_time = when
        quote, reason = self._quote(row, when)
        pos = self.positions.get(mint)
        if pos:
            pos['mark_valid'] = quote is not None
            if quote:
                pos['last_price'], pos['last_time'] = quote[0], utc(row['market_observed_at']).isoformat()
        processed = []
        for order in list(self.orders):
            if order['mint'] != mint or when <= order['created']:
                continue
            elapsed = (when - order['created']).total_seconds()
            if order['side'] == 'BUY' and elapsed > self.cfg['buy_order_ttl_seconds']:
                self.orders.remove(order)
                processed.append({'order_id': order['id'], 'status': 'EXPIRED'})
                continue
            if elapsed < self.cfg['latency_seconds']:
                continue
            if quote is None:
                processed.append({'order_id': order['id'], 'status': 'UNFILLED', 'reason': reason})
                continue
            if order['side'] == 'BUY':
                if mint in self.positions:
                    self.orders.remove(order)
                    processed.append({'order_id': order['id'], 'status': 'CANCELLED', 'reason': 'already invested'})
                    continue
                fill, fail = self._buy(order, *quote, when)
            else:
                fill, fail = self._sell(order, *quote, when)
            if fill:
                event = {**fill, 'mint': mint, 'order_id': order['id'], 'filled_at': when.isoformat(),
                         'from_observation_id': source}
                self.fills.append(event)
                if fill['side'] == 'BUY':
                    self.positions[mint]['last_time'] = utc(row['market_observed_at']).isoformat()
                self.orders.remove(order)
                processed.append({'order_id': order['id'], 'status': 'PAPER_FILLED', 'detail': event})
            else:
                processed.append({'order_id': order['id'], 'status': 'UNFILLED', 'reason': fail})
        signal = row.get('signal')
        if signal in ('BUY', 'SELL'):
            has_pending = any(o['mint'] == mint for o in self.orders)
            permitted = signal == 'SELL' or quote is not None
            if not has_pending and permitted and ((signal == 'BUY' and mint not in self.positions) or
                                                  (signal == 'SELL' and mint in self.positions)):
                req = row.get('requested_usd', self.equity() * self.cfg['max_position_fraction'])
                if signal == 'SELL' or finite_positive(req):
                    self.orders.append({'id': self.next_order_id, 'mint': mint, 'side': signal,
                                        'requested_usd': float(req) if signal == 'BUY' else 0., 'created': when})
                    processed.append({'order_id': self.next_order_id, 'status': 'QUEUED', 'side': signal})
                    self.next_order_id += 1
            elif signal == 'BUY' and not permitted:
                processed.append({'status': 'BLOCKED_SIGNAL', 'reason': reason})
        evt = {'mint': mint, 'source_event_id': source, 'time': when.isoformat(), 'actions': processed,
               'cash_usd': round(self.cash, 5), 'conservative_equity_usd': round(self.equity(), 5)}
        self.events.append(evt)
        return evt

    def summary(self):
        return {'cash_usd': round(self.cash, 4), 'conservative_equity_usd': round(self.equity(), 4),
                'realized_pnl_usd': round(self.realized_pnl, 4), 'fills': len(self.fills),
                'pending_orders': len(self.orders), 'open_positions': len(self.positions),
                'notes': ['Only CPMM approximation; other pool curves require a validated quote model',
                          'Unknown liquidity or token safety blocks paper fills; stranded exits remain open']}


def main():
    p = argparse.ArgumentParser(description='OFFLINE next-observation paper replay only')
    p.add_argument('events', type=Path, help='ordered JSONL events with timestamps and optional BUY/SELL signals')
    p.add_argument('--config', type=Path)
    args = p.parse_args()
    cfg = json.loads(args.config.read_text()) if args.config else None
    replay = MarketReplay(cfg)
    with args.events.open(encoding='utf-8') as f:
        for line in f:
            if line.strip():
                print(json.dumps(replay.on_event(json.loads(line)), sort_keys=True))
    print(json.dumps({'summary': replay.summary(), 'fills': replay.fills}, sort_keys=True))


if __name__ == '__main__':
    main()
