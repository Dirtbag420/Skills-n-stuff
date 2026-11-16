# YouTube meme-coin creator research

**Current state:** This is a tool and source inventory. Complete channel captions have NOT been downloaded, read, or analyzed in ChatGPT. The command requires network access and yt-dlp installed.

## Sources

See channels.json for fomo, archie snipes, Fried Dev, TILLA, Sajad, plus Crypto Crew University for macro context.

## Run with internet access

Install a recent Python 3 and yt-dlp from https://github.com/yt-dlp/yt-dlp.

Trial catalog: `python3 pull_subtitles.py --catalog-only --max-per-tab 5`
Trial captions: `python3 pull_subtitles.py --max-per-tab 5 --only fomo fried_dev`
Full attempt for public uploads: `python3 pull_subtitles.py`
Offline tests: `python3 -m unittest test_pull_subtitles.py`

The script visits Videos, Shorts and Streams. It requests public metadata and accessible English subtitles only, not video/audio. Channel coverage, caption availability and extractor compatibility are not guaranteed. Rate limits or access restrictions may cause failures. No bypass of restricted access is permitted.

All output belongs in the local private-youtube-research directory, never in this public GitHub repository. Never publish full copied transcripts or API keys.

## Research audit standard

For each transcript actually read, record the source URL, creator, upload date, subtitles provenance and quality, exact timestamps of actionable rules, hypothetical signals, failure modes, whether performance claims have evidence, and whether incentives/affiliate links are present. Classify source status as TITLE_ONLY, DESCRIPTION_ONLY, PARTIAL_TRANSCRIPT, FULL_TRANSCRIPT, or NOT_AVAILABLE. Never promote lower statuses to FULL_TRANSCRIPT.

Evaluate ideas using paper simulation, including rug risk, migration timing, developer wallet patterns, wash trading, holder concentration, trading fees, liquidity, slippage, failed exit assumptions, false positive rates, survivorship and hindsight bias.

Known starting videos (descriptions and chapters verified; full captions NOT obtained):
- fomo, How to Trade Meme Coins in 2026: https://www.youtube.com/watch?v=g0cbPGqKH4o
- fomo, Your Meme Coin Workflow Is Probably Wrong: https://www.youtube.com/watch?v=jQM0w_tFIh0
- Fried Dev, Solana Sniper Bot Auto RugCheck: https://www.youtube.com/watch?v=hfVj9jCgLX0
- TILLA videos: https://glasp.co/youtube/channel/UCo_mLmdgePlMPZAUGjhbKPg
- Sajad videos: https://glasp.co/youtube/channel/UCEL7E93I1iBhjIoqRpGqUng

An alternate index is https://filmot.com/ which indexes publicly accessible subtitles but does not cover everything. A compatible vidIQ ChatGPT connection can also provide video transcript analysis once the user connects it.
