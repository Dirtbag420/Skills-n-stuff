# Meme Coin Hunter 2.0: Evidence-first design and build gates

Updated: 2026-11-16 UTC. Scope: **Solana discovery and offline paper-trading research only**. This plan does not authorize live execution or wallet access.

## Objective

Find genuinely liquid, organic early-momentum opportunities and measure a **net-of-realistic-costs** edge against simple baselines. Optimize drawdown, data integrity and robustness before hypothetical returns. No claimed win rate, stop-loss guarantee or deterministic prediction of future pumps.

## Research findings that change the design

- Solana Token-2022 may contain **permanent delegate**, **transfer hook**, **transfer fee**, **pausable**, **default-frozen** and **non-transferable** extensions. Checking only mint/freeze authority is insufficient. See [permanent delegate](https://solana.com/docs/tokens/extensions/permanent-delegate), [transfer hook](https://solana.com/docs/tokens/extensions/transfer-hook), and [Solana exchange integration safety](https://solana.com/docs/defi/exchange).
- Solana RPC `getTokenLargestAccounts` returns token *accounts*, not necessarily unique beneficial wallet owners. Resolve owners and identify known pool/burn/custodial addresses before concentration analysis: [Solana RPC](https://solana.com/docs/rpc/http/gettokenlargestaccounts).
- DEX Screener token-pair endpoints expose price, pool, volume and recent buys/sells, but do **not** supply authoritative linked-wallet identity, verified token safety or unique economic buyers. Rate-limit the documented endpoints and treat marketing boosts as non-organic: [official API reference](https://docs.dexscreener.com/api/reference).
- Geyser/Yellowstone can stream transactions and account events, but provider ingestion still requires slot status, replay, deduplication and provider-failure handling: [Solana indexing documentation](https://solana.com/docs/payments/accept-payments/indexing).
- Protocol listings change. Launchpad program registries can help discover candidates but require validating every on-chain program ID and keeping a versioned schema. [Community registry](https://github.com/dynamolabs/launchpad-registry).
- A 2026 paper-trading study emphasizes counterfactual rejected-token tracking, sample fragility and fees. Treat its results as a research example, not a transferable trading edge: [research abstract](https://zenodo.org/records/20481389).

## Architecture

```text
PROGRAM REGISTRY / Geyser+RPC / DEX Screener / independent token checks
        |
        v
ingest -> identity and lifecycle -> event-store -> freshness/slot validation
        |
        v
mint / token extensions / creator cluster / holder-owner mapping / LP custody
        |
        +--> HARD FAIL / UNKNOWN: quarantine, no paper entry
        |
        v
organic buyer diversity + wallet history + market regime + price structure
        |
        v
strategy variants -> timestamped decision ledger -> queue paper signal
                                      |                  |
                                      v                  v
                              shadow counterfactual   next-tick execution
                                      |                  |
                                      +-----> walk-forward scorecard
                                                 |
                                    alert, reproducible report, audit
```

## Three new tested modules

1. `scripts/forensics.py`: private-funding / coordinated-first-buy associations, holder classification sanity checks, conservative Token-2022 extension policy. Heuristic links do **not** prove common control. Requires real RPC normalization and provenance before use on public tokens.
2. `scripts/execution_replay.py`: ordered JSONL signals and later quotes, conservative CPMM-only approximate impact, fee/spread/latency costs, position and liquidity caps, stale marks and non-fills on missing liquidity. It **does not** support bonding curves, concentrated liquidity or any trade submission.
3. `scripts/shadow_audit.py`: after-decision price observation of WATCH/REJECTED/INSUFFICIENT_DATA/PAPER_CANDIDATE groups, explicit censorship for missing future observations. A rejected rug that later pumps remains a safety rejection. Observed chart highs are *not executable P&L*.

Legacy `hunter.py` is a simpler prototype in the earlier source ZIP; do not conflate its same-observation fill behavior with the newer replay. Do not connect either to real money.

## Priority backlog

### P0: Data integrity and safety (first)
- [ ] Versioned Solana program ID registry, decoded account schemas, launch -> bonding -> migration -> active pool state per launchpad.
- [ ] Verified mint/program owner, all Token-2022 extensions, freeze/mint authorities and LP custody. Cross-check with independent providers, not a single third-party risk label.
- [ ] Holder-account-to-owner resolution, verified pools/escrow classification and funding graph; separate same-source suspicion from proof of shared control.
- [ ] Persistent append-only observation journal with UTC received time, source event time, Solana slot, signature, commitment, parser version, provider and full raw source hashes.
- [ ] Stale-data and disconnected-feed circuit breakers; treat missed slots, reorg corrections, contradictory signals or unverified deployers as UNKNOWN.
- [ ] Unit and adversarial tests with real **archived** on-chain scam/non-scam examples, with contract IDs and verification evidence.

### P1: Realistic paper trading
- [x] CPMM-only hypothetical next-observation fills with safety/quote gates.
- [ ] Actual protocol-aware pool reserve snapshots, quoting and realistic network/slot latency distribution.
- [ ] Shadow rejected-token outcomes at equal observation frequency; separate unobserved, untradeable and documented scams.
- [ ] Slippage, spread, priority fees, compute failures, MEV adverse movement, out-of-gas, liquidity drain and inability to sell.
- [ ] Global capital allocation, exposures by creator cluster, cooldown after rug, and a durable kill switch.
- [ ] Paper trade journal and daily risk report.

### P2: Organic attention and wallet intelligence
- [ ] Wallet cohorts: newly funded vs repeat, surviving buyers, independent sources, dev/insider exits, net bought quantities and coordinated bursts.
- [ ] Read-only wallet performance with **realized** profit, complete historical sample, survivorship bias adjustments, size/latency sensitivity and linked-wallet exclusions. No automatic copy-trading.
- [ ] Social provenance and narrative momentum, with impersonation detection, delayed data and bot-activity discounts.
- [ ] Multi-factor ranking after hard gates; ablations quantify what each feature contributes versus no feature.

### P3: Strategy and validation laboratory
- [ ] Separate strategies for first minutes, migration continuation, post-migration pullbacks and mature narrative strength.
- [ ] Calibration and walk-forward by time, launchpad and creator family, with a fully untouched final test period.
- [ ] Baselines: random eligible token, liquidity-only, momentum-only, no-trade cash and simple SOL holding.
- [ ] Across all reviewed candidates report precision/recall for scams, share of missed organic runners, coverage, provider uptime, fees, P&L distribution, max drawdown, adverse selection and trade fill rate.
- [ ] Bootstrap uncertainty bands with **clustered samples by creator and day**. No edge claim based on one viral winner or screenshots.
- [ ] Monitor strategy drift and regime sensitivity; re-evaluate monthly, do not retrain continuously on latest winner.

### P4: Operational polish
- [ ] CLI service with provider health, audit table, local dashboard and Telegram notifications (alerts, not commands).
- [ ] Reproducible pinned dependencies, secret scanning, test CI, signed release tags, rollback and no transaction-sending module.
- [ ] Incident review after every missed rug, unfillable exit or data divergence, with regression fixtures.

## Metric scorecard

| Metric | Definition | Desired direction |
|---|---|---|
| Safety false-negative | Known unsafe token passed all hard gates | Toward 0, evaluated on independently labeled examples |
| Safety false-positive | Independent benign token incorrectly rejected | Low and explained |
| Shadow rejection coverage | Fraction of rejected tokens with enough future observations | Up |
| Missed runner diagnostic | Among observed rejections, share with later chart gain above threshold | Understand and minimize *for legitimate eligible coins* |
| Simulated fill rate | Executed paper orders / submitted orders | Stable and realistic |
| Net expectancy | Mean realized paper P&L after all modeled costs | Positive out of sample, with uncertainty |
| Tail loss | Worst per-position outcome including zero-value/unfilled exits | Limited by allocation, never assumed stop-fill |
| Max drawdown | Peak-to-trough paper equity including stale/illiquid marking | Lower |
| Temporal consistency | Performance by day, launchpad, pool stage and regime | Not reliant on a single short window |
| Replay reproducibility | Same data+config+code produce identical decision and fill trace | 100% |

## Explicit go/no-go gates

- **Research-ready:** provenance and data quality audited; no wallet signing code.
- **Paper-ready:** protocol-specific quote model validated against historical executable state, non-fill scenarios, independent source checks, complete event log, safety regression suite.
- **Performance claim:** at least several market regimes and sufficient decisions for meaningful uncertainty bounds, out-of-sample after-cost improvement against baselines, visible rejects, and no critical unaddressed data outages.
- **Live trading:** not in scope. Requires a separate explicit request, complete threat model, permissions review, and financial loss controls. No automatic activation.

## Next practical implementation task

Wire a read-only RPC normalization adapter that produces authenticated provenance for `forensics.py` and the risk gate, followed by protocol-specific market-event snapshots. Avoid treating a fake `risk_state='PASS'` field in a fixture as verification of live chain safety.
