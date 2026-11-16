# Skills-n-stuff

Reusable Codex agent skills collected in one place.

**Status:** 14 `SKILL.md` entrypoints are committed. The token-efficiency-optimizer skill includes its supporting script, tests, and reference documentation. The earlier music/FM-1 entrypoints were imported from `Dirtbag420/Black-Mass`. Supporting reference documents, scripts, fixtures, assets and test suites from the original skill ZIPs have **not yet been fully migrated into this GitHub repository**. Some SKILL.md files are abridged activation manifests rather than the original full-length instructions. See [MIGRATION_STATUS.md](MIGRATION_STATUS.md).

## Meme Coin Hunter 2.0 development

The Solana paper-research skill now includes three real standalone source modules, their unit tests, and a GitHub Actions check:

- [Wallet forensics and Token-2022 gates](.agents/skills/meme-coin-hunter-architect/scripts/forensics.py)
- [Realistic next-observation execution replay](.agents/skills/meme-coin-hunter-architect/scripts/execution_replay.py)
- [Counterfactual rejection shadow audit](.agents/skills/meme-coin-hunter-architect/scripts/shadow_audit.py)
- [Architecture, development backlog and go/no-go gates](.agents/skills/meme-coin-hunter-architect/references/v2-architecture-and-roadmap.md)

Run `python -m unittest discover -s .agents/skills/meme-coin-hunter-architect/tests -p 'test_*.py' -v` from the repository root.

These are **offline simulations and heuristics**. No trusted live Solana ingestion, profitable strategy, wallet signing or live execution has been implemented.

## Skills

### Crypto research
- [crypto-research-architect](.agents/skills/crypto-research-architect/SKILL.md): dated evidence, tokenomics, catalysts, relative strength, liquidity and paper-strategy research
- [meme-coin-hunter-architect](.agents/skills/meme-coin-hunter-architect/SKILL.md): Solana launches and migrations, risk gates, wallet behavior, scoring and paper-trading bot design

### Firmware
- [fm1-firmware-architect](.agents/skills/fm1-firmware-architect/SKILL.md): FM-1 DSP, engines, groovebox firmware, validation and recovery

### Music theory and production
- [music-composition-architect](.agents/skills/music-composition-architect/SKILL.md)
- [synthesizer-knowledge-patch-architect](.agents/skills/synthesizer-knowledge-patch-architect/SKILL.md)
- [synth-sound-design-architect](.agents/skills/synth-sound-design-architect/SKILL.md)
- [ableton-production-architect](.agents/skills/ableton-production-architect/SKILL.md)
- [audio-analysis-intelligence](.agents/skills/audio-analysis-intelligence/SKILL.md)
- [mixing-mastering-architect](.agents/skills/mixing-mastering-architect/SKILL.md)
- [vst-plugin-architect](.agents/skills/vst-plugin-architect/SKILL.md)
- [embedded-audio-release-architect](.agents/skills/embedded-audio-release-architect/SKILL.md)
- [live-performance-dj-architect](.agents/skills/live-performance-dj-architect/SKILL.md)
- [music-production-director](.agents/skills/music-production-director/SKILL.md)

### General workflow
- [token-efficiency-optimizer](.agents/skills/token-efficiency-optimizer/SKILL.md): adaptive context budgeting, targeted searches, bounded build-log digests, and compact handoffs without skipping necessary verification

## Install

Copy an individual complete skill folder into `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/`. This repository currently contains entrypoints rather than all full support files, so consult migration status before relying on referenced local tools or docs. Do not assume a named script exists unless the file appears in the directory.

## Safety

Do not commit API secrets, GitHub tokens, exchange credentials, wallet seed phrases, keypairs, or personal information. Crypto skills are research/paper-only. Never claim a live integration, hardware test, or profitable strategy without independently verifying it.

This is a public repository.