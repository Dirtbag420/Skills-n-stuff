#!/usr/bin/env python3
"""Make a bounded failure-oriented digest of a text log, preserving raw input.

Examples:
  python3 focus_log.py build.log
  python3 focus_log.py build.log -C 3 --max-matches 12
  some_command >build.log 2>&1; status=$?; python3 focus_log.py build.log; exit "$status"

A digest cannot determine whether a build/test succeeded. Check the exit code.
"""
from __future__ import annotations

import argparse
from collections import deque
import re
import sys
from pathlib import Path

FAILURES = re.compile(
    r"(?:\berror(?:\[[A-Z]\d+\])?\b|\bfatal\b|\bexception\b|"
    r"\btraceback\b|\bpanic(?:ked)?\b|\bassertion(?:error)?\b|"
    r"\bfailed\b|\bFAIL\b|\bundefined reference\b|\bsegmentation fault\b|"
    r"\btimed out\b|\bexit(?:ed)? (?:with )?(?:code|status) [1-9]\d*\b)",
    flags=re.IGNORECASE,
)
WARNINGS = re.compile(r"\bwarning\b", flags=re.IGNORECASE)


def clip(value: str, max_chars: int) -> str:
    value = value.rstrip("\r\n")
    if len(value) > max_chars:
        return value[: max_chars - 17] + " ... [clipped]"
    return value


def digest(lines, context: int, max_matches: int, tail_count: int, max_chars: int, warnings: bool) -> str:
    selected_first: dict[int, str] = {}
    recent_windows: deque[tuple[int, dict[int, str]]] = deque(maxlen=2)
    recent_before: deque[tuple[int, str]] = deque(maxlen=context)
    final_tail: deque[tuple[int, str]] = deque(maxlen=tail_count)
    matcher = re.compile(FAILURES.pattern + ("|" + WARNINGS.pattern if warnings else ""), re.IGNORECASE)
    first_limit = max(0, max_matches - 2)
    matched = 0
    total = 0
    after = 0

    for total, original in enumerate(lines, 1):
        value = clip(original, max_chars)
        final_tail.append((total, value))
        is_match = bool(matcher.search(original))
        if is_match:
            matched += 1
            if matched <= first_limit:
                selected_first.update(recent_before)
                selected_first[total] = value
                after = context
            else:
                # Keep the final two failure windows, often the root-cause and summary.
                recent_windows.append((total, {**dict(recent_before), total: value}))
        else:
            if after:
                selected_first[total] = value
                after -= 1
        # Add following context to all retained recent windows, within C lines.
        for match_line, window in recent_windows:
            if match_line < total <= match_line + context:
                window[total] = value
        recent_before.append((total, value))

    selected = dict(selected_first)
    for _, window in recent_windows:
        selected.update(window)
    selected.update(final_tail)
    shown = min(matched, max_matches)
    report = [
        f"Log digest: {total} lines; {matched} failure/warning signals; "
        f"up to {shown} match windows shown plus last {tail_count} lines.",
        "This is not a success check. Inspect the original log and process exit code.",
    ]
    if matched > max_matches:
        report.append(f"Signals omitted due to cap: at least {matched - max_matches}; raise --max-matches if needed.")
    previous = 0
    for line_no, line in sorted(selected.items()):
        if previous and line_no > previous + 1:
            report.append(f"... [{line_no - previous - 1} lines skipped] ...")
        report.append(f"{line_no:>6}: {line}")
        previous = line_no
    return "\n".join(report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logfile", nargs="?", default="-", help="Log path, or - for stdin")
    parser.add_argument("-C", "--context", type=int, default=2, help="Lines around matches")
    parser.add_argument("--max-matches", type=int, default=20, help="Maximum interesting match windows")
    parser.add_argument("--tail", type=int, default=10, help="Final lines to preserve")
    parser.add_argument("--max-chars", type=int, default=360, help="Maximum characters shown per line")
    parser.add_argument("--include-warnings", action="store_true", help="Include warnings as signals")
    args = parser.parse_args()
    if args.context < 0 or args.max_matches < 2 or args.tail < 0 or args.max_chars < 32:
        parser.error("context >= 0, max-matches >= 2, tail >= 0, max-chars >= 32 required")
    if args.logfile == "-":
        print(digest(sys.stdin, args.context, args.max_matches, args.tail, args.max_chars, args.include_warnings))
        return 0
    try:
        with Path(args.logfile).open("r", encoding="utf-8", errors="replace") as stream:
            print(digest(stream, args.context, args.max_matches, args.tail, args.max_chars, args.include_warnings))
    except OSError as exc:
        print(f"Cannot read log: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
