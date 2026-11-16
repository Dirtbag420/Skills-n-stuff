import importlib.util
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/'scripts'/'shadow_audit.py'
s=importlib.util.spec_from_file_location('shadow',P)
a=importlib.util.module_from_spec(s);s.loader.exec_module(a)


def e(i,kind='market',decision='REJECTED',price=1,tradable=True):
    d=dict(kind=kind,mint='FAKE',observed_at=f'2026-11-15T12:{i:02d}:00Z',price_usd=price)
    if kind=='decision':d['decision']=decision
    else:d.update(liquidity_usd=100000,tradable=tradable)
    return d


class ShadowTests(unittest.TestCase):
    def test_rejected_runner_visible_but_not_executable(self):
        r=a.analyze([e(0,'decision'),e(1,price=3),e(5,price=2),e(10,price=1.8)],horizon_seconds=600,max_terminal_gap_seconds=60)
        c=r['cases'][0]
        self.assertEqual('OBSERVED',c['status'])
        self.assertEqual(200,c['max_observed_return_pct'])
        self.assertTrue(c['observed_runner'])
        self.assertEqual(1,r['summary']['REJECTED']['observed_runners'])

    def test_missing_horizon_is_censored(self):
        r=a.analyze([e(0,'decision'),e(1,price=100)],horizon_seconds=600)
        self.assertEqual('CENSORED',r['cases'][0]['status'])
        self.assertIsNone(r['summary']['REJECTED']['runner_rate_on_observed_only'])

    def test_gap_near_horizon_censored(self):
        r=a.analyze([e(0,'decision'),e(1,price=100),e(10,price=1,tradable=False)],horizon_seconds=600,max_terminal_gap_seconds=60)
        self.assertEqual('CENSORED',r['cases'][0]['status'])

    def test_bad_liquidity_excludes_quote(self):
        d=e(5,price=9);d['liquidity_usd']=0
        r=a.analyze([e(0,'decision'),d,e(10,price=1)],horizon_seconds=600,max_terminal_gap_seconds=60)
        self.assertEqual(0,r['cases'][0]['max_observed_return_pct'])

    def test_reference_cannot_be_null(self):
        with self.assertRaises(ValueError): a.analyze([e(0,'decision',price=None)])

    def test_unsorted_input_rejected(self):
        with self.assertRaises(ValueError):a.analyze([e(5),e(0,'decision')])


if __name__=='__main__':unittest.main()
