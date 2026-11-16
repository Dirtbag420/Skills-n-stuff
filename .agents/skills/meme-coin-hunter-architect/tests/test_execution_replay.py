import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'scripts' / 'execution_replay.py'
spec = importlib.util.spec_from_file_location('execution_replay', P)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def tick(i, price=1., liquidity=50000., signal=None, **changes):
    event = {'chain': 'solana', 'mint': 'FAKE', 'source_event_id': str(i),
             'observed_at': f'2026-11-15T12:00:{i:02d}Z',
             'market_observed_at': f'2026-11-15T12:00:{i:02d}Z',
             'price_usd': price, 'liquidity_usd': liquidity, 'risk_state': 'PASS',
             'tradable': True, 'pool_type': 'cpmm'}
    if signal: event['signal'] = signal
    event.update(changes)
    return event


class ExecutionTests(unittest.TestCase):
    def test_entry_uses_next_tick_not_signal_price(self):
        s = r.MarketReplay({'latency_seconds': 1})
        a=s.on_event(tick(0, price=1,signal='BUY'))
        self.assertEqual('QUEUED',a['actions'][0]['status'])
        self.assertEqual([],s.fills)
        s.on_event(tick(1, price=2))
        self.assertEqual(1,len(s.fills))
        self.assertGreater(s.fills[0]['fill_price'],2)

    def test_exit_uses_future_tick_not_sell_signal(self):
        s=r.MarketReplay({'latency_seconds': 1})
        s.on_event(tick(0, signal='BUY'))
        s.on_event(tick(1))
        self.assertEqual(1,len(s.fills))
        s.on_event(tick(2, price=5,signal='SELL'))
        self.assertEqual(1,len(s.fills))
        s.on_event(tick(3, price=.5))
        self.assertEqual('SELL',s.fills[-1]['side'])
        self.assertLess(s.fills[-1]['fill_price'], .5)

    def test_missing_liquidity_cannot_make_successful_exit(self):
        s=r.MarketReplay({'latency_seconds':1})
        s.on_event(tick(0,signal='BUY'));s.on_event(tick(1))
        s.on_event(tick(2,signal='SELL'))
        res=s.on_event(tick(3,price=2,liquidity=0))
        self.assertEqual('UNFILLED',res['actions'][0]['status'])
        self.assertEqual(1,len(s.positions))
        self.assertEqual(s.cash,s.equity())

    def test_unsupported_bonding_curve_fails_closed(self):
        s=r.MarketReplay()
        a=s.on_event(tick(0,signal='BUY',pool_type='bonding-curve'))
        self.assertEqual('BLOCKED_SIGNAL',a['actions'][0]['status'])

    def test_stale_quote_cannot_fill(self):
        s=r.MarketReplay({'latency_seconds':1,'max_quote_age_seconds':3})
        s.on_event(tick(0,signal='BUY'))
        a=s.on_event(tick(10,market_observed_at='2026-11-15T12:00:00Z'))
        self.assertEqual('UNFILLED',a['actions'][0]['status'])
        self.assertEqual([],s.fills)

    def test_risk_gate_blocks_entry(self):
        s=r.MarketReplay()
        self.assertEqual('BLOCKED_SIGNAL',s.on_event(tick(0,signal='BUY',risk_state='UNKNOWN'))['actions'][0]['status'])

    def test_duplicate_does_not_fill(self):
        s=r.MarketReplay({'latency_seconds':0})
        a=tick(0,signal='BUY');s.on_event(a)
        self.assertEqual('DUPLICATE',s.on_event(a)['status'])
        self.assertEqual([],s.fills)

    def test_order_expiration(self):
        s=r.MarketReplay({'buy_order_ttl_seconds':3})
        s.on_event(tick(0,signal='BUY'))
        result=s.on_event(tick(10))
        self.assertEqual('EXPIRED',result['actions'][0]['status'])
        self.assertEqual([],s.orders)

    def test_fee_impact_and_cash_budget(self):
        s=r.MarketReplay({'latency_seconds':1})
        s.on_event(tick(0,signal='BUY'))
        s.on_event(tick(1))
        self.assertGreater(s.fills[0]['impact_bps'],0)
        self.assertGreater(s.fills[0]['fee_usd'],0)
        self.assertGreater(s.cash,0)
        self.assertLess(s.cash,1000)

    def test_mark_to_market_uses_quote_freshness_across_other_tokens(self):
        s=r.MarketReplay({'latency_seconds':1,'max_quote_age_seconds':3})
        s.on_event(tick(0,signal='BUY'))
        s.on_event(tick(1))
        self.assertGreater(s.equity(),s.cash)
        s.on_event(tick(12,mint='DIFFERENT',source_event_id='different'))
        self.assertEqual(s.cash,s.equity())

    def test_pool_liquidity_cap(self):
        s=r.MarketReplay({'latency_seconds':1,'max_trade_liquidity_fraction':.001})
        s.on_event(tick(0,signal='BUY'))
        s.on_event(tick(1))
        self.assertLessEqual(s.fills[0]['gross_usd'],50)

    def test_time_order_required(self):
        s=r.MarketReplay()
        s.on_event(tick(3))
        with self.assertRaises(ValueError): s.on_event(tick(2))


if __name__=='__main__':unittest.main()
