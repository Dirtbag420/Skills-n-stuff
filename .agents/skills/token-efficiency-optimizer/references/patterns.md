# Context-saving patterns

Read this reference only for longer coding sessions, repeated context loss, or oversized tool output.

## Repository reconnaissance

- Start with `git status --short` to distinguish pre-existing edits from your own changes.
- Use paths and symbols, not entire directory listings. `rg --files -g '*.py' -g '!vendor/**'` is usually cheaper than recursively printing directories.
- Prefer a narrow file range or a single symbol definition. Expand to the whole file if behavior spans it.
- Search once with meaningful alternatives; refine only when the result is inconclusive.
- If a command returns an unexpected absence, verify the working directory and exclusions before concluding that code is missing.

## Logs and tests

- Redirect noisy command output to a local file, then use the skill's `scripts/focus_log.py` for a first-pass digest. The original log is authoritative.
- Start with relevant test targets; broader checks are required for changes touching common infrastructure, release pathways, hardware recovery, or security-sensitive behavior.
- When a summary is ambiguous, inspect surrounding raw lines and full stack traces. Do not treat zero keyword matches as proof of success.
- Never conceal a nonzero exit status or delete evidence just because a digest looks clean.

## Long-session handoff (only as needed)

Use a summary with at most these fields, filled with concrete evidence rather than guesses:

```
Goal:
Constraints:
Decisions:
Files changed:
Verified (command + outcome):
Open issues:
Next action:
```

Prioritize accurate paths and observed results. Keep exact error messages only if they are needed for the next step. Do not save transient secrets or copy sensitive source data into a handoff.

## Cross-skill usage

Use this skill as a lightweight efficiency overlay alongside domain skills, such as firmware development or trading-bot engineering. A domain skill's safety, research, and test requirements take precedence over a token-saving preference. Skills are not guaranteed to activate automatically on unrelated prompts; invoke `$token-efficiency-optimizer` explicitly when predictable activation matters.
