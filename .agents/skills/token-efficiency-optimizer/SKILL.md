---
name: token-efficiency-optimizer
description: Reduce Codex token usage and context bloat during repository exploration, implementation, debugging, and lengthy agent sessions. Use when asked to conserve tokens, use a smaller context budget, avoid redundant work, or handle large repositories and build logs efficiently. Preserve correctness, necessary evidence, and testing.
---

# Token Efficiency Optimizer

Deliver the requested result using the smallest **sufficient** context. Optimize *total* tokens across exploration, tool output, revisions, and handoffs, not just the length of the final answer.

## Working protocol

1. **Scope first.** Identify the deliverable, existing constraints, and likely relevant files. Reuse facts and decisions already in the current context. Do not repeat discovery unless the repository or question changed.
2. **Locate before reading.** Prefer filenames, paths, symbols, and narrow searches (`rg --files`, `rg -n`, `git status --short`, `git diff --stat`). Exclude generated artifacts and dependencies. Open only the matching portions first. Expand when dependencies or correctness demand it.
3. **Bound output, not investigation.** Use focused filters or line ranges rather than dumping full files, logs, trees, JSON responses, or test suites into conversation. Retain access to the original material. Never hide an error merely to meet a token target.
4. **One change, one verification path.** Reuse prior findings, make cohesive edits, run the most relevant focused checks, and expand to integration/regression checks when warranted. Fix the actual root cause. Avoid repeating passing tests without a reason.
5. **Answer compactly.** State what changed, whether it was verified, and meaningful blockers. Keep technical detail or citations when the user needs them. No repetitive progress narrations or speculative filler.
6. **Compact state only when needed.** For a lengthy session or explicit handoff, preserve goal, decisions, touched files, test evidence, unresolved issues, and next action in a small structured summary. Prefer writing an on-disk handoff only on request or when it prevents rework; don't silently modify project documentation.

## Adaptive depth

- **Lean (default for familiar, low-risk work):** narrow discovery, minimal necessary reads, focused validation.
- **Balanced (default for substantial implementation):** inspect interfaces and dependent code, check edge cases, run scoped tests, expand if failures appear.
- **Thorough (mandatory when consequences are high):** include security/privacy, money, data deletion, firmware flashing/recovery, migrations, concurrency, and release-sensitive changes. Never trade off required verification to save tokens.

Switch modes as the task demands, without asking permission for routine depth changes. A short answer is not evidence of complete work.

## Useful commands

```sh
rg --files src tests | head -80                # Orient, then search by symbol
rg -n 'SomeSymbol|failure text' src tests     # Relevant matches, not every file
sed -n '120,190p' path/to/file               # Narrow content window
git diff --check && git diff --stat          # Cheap pre-verification
python3 scripts/focus_log.py build.log       # Read a compact failure digest
```

Run `scripts/focus_log.py` only when a log exists. The script is optional; its path is relative to this skill, not automatically to the current project. Preserve the raw log and inspect it when the digest is insufficient. Consult [references/patterns.md](references/patterns.md) only for persistent-context or high-output workflows.

## Guardrails

- Follow the user's requested scope, citations, tests, permissions, and detail level. Never discard required information or invent evidence to reduce tokens.
- Do not auto-install dependencies, change global configuration, modify unrelated files, or suppress test failures.
- Avoid blanket word, file, or tool-call quotas. Excessive compression can cause missed defects and costly retries.
- Report optimization claims as hypotheses unless actual token counts or an A/B comparison are available.
