# YouTube transcript research: Solana Meme Coin Hunter

Reviewed: 2026-11-16 UTC. Method: vidIQ timestamped video transcripts. This is a **partial audit**, not all uploads. Twenty transcripts were successfully retrieved from five YouTube creators. Captions can misrecognize token names, protocol names, figures, and transaction details; verify claims against on-chain records. This document paraphrases key observations and does not rehost transcripts.

## Reviewed videos (20)

| Creator | Video ID | Focus |
|---|---|---|
| fomo | [g0cbPGqKH4o](https://youtu.be/g0cbPGqKH4o) | Solana beginner trading course, platforms, discovery and chart strategies |
| fomo | [jQM0w_tFIh0](https://youtu.be/jQM0w_tFIh0) | Trader types, extraction and narrative workflows |
| fomo | [icFkQQiuL2I](https://youtu.be/icFkQQiuL2I) | Axiom discovery, bundles, snipers and dev positions |
| fomo | [-lAoHigCME8](https://youtu.be/-lAoHigCME8) | Cielo wallet discovery and trade history |
| archie snipes | [0c1h7HIJlSc](https://youtu.be/0c1h7HIJlSc) | Sophisticated rug mechanisms and false token social signals |
| archie snipes | [7FAZsRppdSk](https://youtu.be/7FAZsRppdSk) | Mint/freeze, top-holder checks and dev history |
| archie snipes | [g0GntSsj_ws](https://youtu.be/g0GntSsj_ws) | Solana pool creation transaction signatures |
| archie snipes | [Emvg88V2JnE](https://youtu.be/Emvg88V2JnE) | Solscan holder, transfers and wallet tracing |
| archie snipes | [adBbu4QfsoM](https://youtu.be/adBbu4QfsoM) | Bot scanning workflow and strategy design |
| Fried Dev | [pTJfP8FLXKM](https://youtu.be/pTJfP8FLXKM) | Scalping and early-launch filters |
| Fried Dev | [9nYfSGDlqk4](https://youtu.be/9nYfSGDlqk4) | Wallet discovery across token cohorts |
| Fried Dev | [X_bAkyFKp2c](https://youtu.be/X_bAkyFKp2c) | Bundling and manipulated volume (defensive detection only) |
| TILLA | [ZnDXIIP1cTI](https://youtu.be/ZnDXIIP1cTI) | Smart-wallet tracking, multi-buys and copytrading traps |
| TILLA | [6_XDmsTevKA](https://youtu.be/6_XDmsTevKA) | Risk allocation, trade selectivity and account sizing |
| TILLA | [4nJedu9N9CE](https://youtu.be/4nJedu9N9CE) | New pairs, final stretch, migrated token screening |
| TILLA | [8dhfz90Be64](https://youtu.be/8dhfz90Be64) | Beginner security checks, attention and market stage |
| Sajad | [ghMaCetgw2Q](https://youtu.be/ghMaCetgw2Q) | Narrative trends and patience for pullback entries |
| Sajad | [c0jfxKdraPI](https://youtu.be/c0jfxKdraPI) | Pre-migration filters and market-cap thresholds |
| Sajad | [ac8qxt9OC_I](https://youtu.be/ac8qxt9OC_I) | Holder analysis and narrative tracking tools |
| Sajad | [DqoSJUbj61c](https://youtu.be/DqoSJUbj61c) | PumpSwap launch/migration changes and outdated Raydium assumptions |

## Testable hypotheses, not adopted truths

1. **Linked supply concentration matters more than visible top-ten concentration.** Trace common funding, coincident launches and coordinated transfers before claiming holder decentralization. Treat exchange/aggregator custody, legitimate market makers, and false-positive clustering separately.
2. **Volume is not equivalent to demand.** Distinguish distinct economic buyers from repeated transfers and wash-like round trips. Investigate creator-funded buyer clusters and abnormal buy/sell patterns.
3. **Smart wallet signals are observational.** Reconstruct realized P&L, entry timing, market impact and position size; detect paid/affiliate-promoted wallets and sellers systematically exiting into followers. Don't auto-copy addresses.
4. **Market life-cycle must be protocol aware.** Track launched, bonding curve, migrated and active-pool states per venue. PumpSwap and Raydium routes may behave differently, and YouTube launch thresholds are dated.
5. **Early entry may be dominated by unfillable prices.** Replay real-time available data and impose fees, latency, spread, slippage, price gaps, gas/priority fees and sellability.
6. **Social narratives need source verification.** Similar-looking handles and recycled posts can be impersonation; verify exact contract mint and provenance independently.
7. **Hard stop logic cannot guarantee an exit.** Some rugs gap through stops or leave no executable liquidity. Explicitly model loss-to-zero, unable-to-sell and failed transaction outcomes.

## Research protocol

- Assign each claimed rule an ID and link to video+timestamp; record 'claimed', 'independently verified', 'tested' separately.
- Extract threshold proposals (age, liquidity, insider share, holder dispersion) as sweepable parameters, **not universal constants**. Avoid fitting a strategy to screenshots of winners.
- Create timestamp-correct historical samples including failed launches, migration failures and lookalike scams.
- Use walk-forward and untouched out-of-sample splits by calendar time, group token families to avoid leakage, and report fee-adjusted P&L, max drawdown, precision of rug flags, false positives and alert lead-time.
- Flag creator financial incentives. Referrals, invitations, paid communities and extraordinary P&L claims are marketing, not performance verification.
- Stay paper-only; no wallet import, trade credentials or transaction signing.

## Source coverage limitations

The five channels have substantially more uploads than the 20 analyzed here. The vidIQ channel-video lists are capped at a subset, and this review did not exhaust Shorts, live streams or all channel uploads. This is not an endorsement of any creator or a reproducible profit claim.
