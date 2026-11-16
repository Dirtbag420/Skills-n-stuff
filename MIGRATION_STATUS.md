# Migration status

## Completed
- GitHub repository created and `main` initialized.
- 11 original existing activation `SKILL.md` files copied from the owner's `Black-Mass` repository without modifying that repository.
- Two new research/paper-trading `SKILL.md` files added: `crypto-research-architect` and `meme-coin-hunter-architect`.
- Skill directory layout: `.agents/skills/<skill-name>/SKILL.md`.

## Not yet migrated

The following original source packages were located in the user's ChatGPT file library or conversation working directory, but their full contents have **not** been committed to this GitHub repository:
- `music-skills-suite-9-skills.zip` (9 skills including scripts, references and auxiliary assets)
- `fm1-firmware-architect.zip`
- `synthesizer-knowledge-patch-architect.zip` (also represented within the 9-skill bundle)
- `music-composition-architect.zip` (previously generated but complete source archive is not available in the current working container)
- `codex-skills-github-ready.zip` (crypto source, scripts, fixtures, tests and workflow)
- `crypto-research-and-memecoin-hunter-skills.zip`

A 122-file combined archive covering 12 complete available skills was rebuilt in the ChatGPT conversation as `skills-n-stuff-source-bundle.zip`, excluding the missing full Music Composition package. It was not committed to this GitHub repository.

**Important:** The existing 13 activation manifests are useful for Codex skill selection, but some refer to companion files that are not yet in the repository. Treat these as partial migrations, not fully reproducible installations. Crypto paper-trading scripts and tests are present in the conversation archive, not yet in GitHub.

## Next requirements

Upload/extract original source folders into `.agents/skills/`, restore the complete Music Composition Architect source archive, retain license notices, and run validation. Check each path and reject secret or key material before publication.