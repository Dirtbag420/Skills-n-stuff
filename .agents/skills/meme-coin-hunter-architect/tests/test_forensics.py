import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'scripts' / 'forensics.py'
s = importlib.util.spec_from_file_location('forensics', P)
f = importlib.util.module_from_spec(s)
s.loader.exec_module(f)


def wallet(name, pct, funder='private123', ftype='private', funded='2026-11-15T12:00:00Z', bought='2026-11-15T12:01:00Z'):
    return dict(wallet=name, pct=pct, account_type='wallet', funder=funder, funder_type=ftype, funded_at=funded, first_buy_at=bought)


class ForensicsTests(unittest.TestCase):
    def test_cluster_above_cap_is_flagged(self):
        r=f.analyze_holders([wallet('A', 12),wallet('B', 11),wallet('C', 2, funder='other')])
        self.assertEqual('REVIEW',r['status'])
        self.assertEqual(['A','B'],r['clusters'][0]['wallets'])
        self.assertEqual(23,r['clusters'][0]['total_pct'])

    def test_exchange_funder_is_not_evidence_of_common_owner(self):
        r=f.analyze_holders([wallet('A', 12, ftype='exchange'),wallet('B', 11, ftype='exchange')])
        self.assertEqual('NO_CLUSTER_FLAG',r['status'])
        self.assertEqual([],r['clusters'])

    def test_asynchronous_first_buys_not_clustered(self):
        r=f.analyze_holders([wallet('A', 12),wallet('B', 11, bought='2026-11-15T12:08:00Z')])
        self.assertEqual('NO_CLUSTER_FLAG',r['status'])

    def test_missing_evidence_does_not_pass(self):
        a=wallet('A', 15); a.pop('funded_at')
        r=f.analyze_holders([a])
        self.assertEqual('INSUFFICIENT_DATA',r['status'])

    def test_pool_address_not_clustered_with_wallet(self):
        p=wallet('pool', 40);p['account_type']='pool'
        r=f.analyze_holders([p, wallet('A', 10)])
        self.assertEqual('NO_CLUSTER_FLAG',r['status'])

    def test_duplicate_wallet_is_invalid(self):
        self.assertEqual('INSUFFICIENT_DATA', f.analyze_holders([wallet('A',1),wallet('A',1)])['status'])

    def test_cannot_exceed_supply(self):
        self.assertEqual('INSUFFICIENT_DATA', f.analyze_holders([wallet('A',70),wallet('B',70)])['status'])

    def test_unknown_account_type_quarantined(self):
        a=wallet('A', 8); a['account_type'] = 'unknown'
        self.assertEqual('INSUFFICIENT_DATA', f.analyze_holders([a])['status'])

    def test_token2022_unknown_extensions_quarantine(self):
        r=f.token_extension_gate('token-2022',{'inventory_complete':True,'unknown_new_extension':True})
        self.assertEqual('INSUFFICIENT_DATA',r['status'])

    def test_token2022_permanent_delegate_rejected(self):
        r=f.token_extension_gate('token-2022',{'inventory_complete':True,'permanent_delegate':True})
        self.assertEqual('REJECTED',r['status'])

    def test_token2022_transfer_hook_rejected(self):
        self.assertEqual('REJECTED', f.token_extension_gate('token-2022',{'inventory_complete':True,'transfer_hook':True})['status'])

    def test_token2022_missing_inventory_unknown(self):
        self.assertEqual('INSUFFICIENT_DATA', f.token_extension_gate('token-2022',{})['status'])

    def test_token2022_safe_known_inventory(self):
        self.assertEqual('PASS', f.token_extension_gate('token-2022',{'inventory_complete':True,'metadata_pointer':True,'transfer_fee_bps':100})['status'])

    def test_token2022_high_fee_rejected(self):
        self.assertEqual('REJECTED', f.token_extension_gate('token-2022',{'inventory_complete':True,'transfer_fee_bps':1000})['status'])


if __name__ == '__main__':unittest.main()
