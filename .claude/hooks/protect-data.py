#!/usr/bin/env python3
"""PreToolUse hook: blocks Edit/Write/NotebookEdit/Bash calls that would
modify a file under data/ (CLAUDE.md hard rule 3: data/ is read-only).

Blocking mechanism: exit code 2 with a reason on stderr. Confirmed as the
working block-and-explain pattern in this environment (see
/root/.claude/stop-hook-git-check.sh, which uses the same exit(2)+stderr
convention to block the Stop event).

Bash coverage is a best-effort regex over the raw command string, not a
full shell parser: it catches clear delete/overwrite patterns (redirects,
rm, mv, sed -i, tee, truncate, dd) touching data/. It deliberately does
NOT flag `cp` referencing data/ as a source -- "cp data/x.csv
analysis/y.csv" is the CLAUDE.md-sanctioned "write cleaned copies to
analysis/" pattern, and telling source from destination for arbitrary
shell reliably needs a real parser, which is overkill here.
"""

import datetime
import json
import os
import re
import shlex
import sys

# Verbs whose arguments (or a specific argument, per COMMAND_ARG_RULES below)
# get resolved to a real path and checked against the project's data/ dir.
# This is best-effort (naive split on ; && || |, shlex per segment) --  not a
# full shell parser. It intentionally checks resolved paths rather than a raw
# substring match on "data/", because a raw substring match false-triggers on
# any command that merely mentions the word "data/" (e.g. in a comment, an
# unrelated directory of that name, or -- as caught during testing -- in this
# hook's own test harness).
REDIRECT_RE = re.compile(r">>?\s*(\S+)")


def resolve(project_dir, cwd, path):
    if not path:
        return None
    if not os.path.isabs(path):
        path = os.path.join(cwd or project_dir, path)
    return os.path.realpath(path)


def under_data(data_dir, path):
    if not path:
        return False
    return path == data_dir or path.startswith(data_dir + os.sep)


def find_phase(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return "not specified"
    last_phase = "not specified"
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "user":
                    continue
                content = (entry.get("message") or {}).get("content")
                text = content if isinstance(content, str) else ""
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            break
                m = re.match(r"\s*Phase\s+(\d+)\s*:", text or "")
                if m:
                    last_phase = f"Phase {m.group(1)}"
    except OSError:
        pass
    return last_phase


def next_id(existing_text):
    ids = [int(m) for m in re.findall(r"^## S-(\d+)", existing_text, re.MULTILINE)]
    return (max(ids) + 1) if ids else 1


def log_block(project_dir, transcript_path, tool_name, blocked_path_or_cmd, reason):
    log_path = os.path.join(project_dir, "ai_usage", "STEERING_LOG.md")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    existing = ""
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            existing = f.read()

    sid = f"S-{next_id(existing):03d}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    phase = find_phase(transcript_path)

    entry = (
        f"\n## {sid}\n"
        f"- **Phase:** {phase}\n"
        f"- **Type:** blocked-edit (automated -- written by .claude/hooks/protect-data.py, not a user exchange)\n"
        f"- **Time:** {timestamp}\n"
        f"- **What I did:** Attempted a `{tool_name}` call targeting `{blocked_path_or_cmd}`.\n"
        f"- **What you said:** N/A -- CLAUDE.md hard rule 3 (data/ is read-only), enforced automatically.\n"
        f"- **Why:** {reason}\n"
        f"- **What changed:** Nothing -- the tool call was blocked before it ran. No file in data/ was modified.\n"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        if not existing:
            f.write(
                "# Steering Log\n\n"
                "Interactive moments in this session where the user corrected, pushed back on, "
                "made a decision about, answered a question from, or asked Claude to explain "
                "something. Curated by hand per `.claude/skills/ai-usage-log/SKILL.md`, in "
                "Claude's own words -- including its own mistakes, honestly. Full prompt text "
                "lives in `ai_usage/PROMPT_LOG.md` under the referenced `P-###` id; this file "
                "doesn't repeat it.\n"
            )
        f.write(entry)


def _strip_flags(args):
    return [a for a in args if not a.startswith("-")]


def check_bash(project_dir, cwd, data_dir, command):
    """Return the offending path/command snippet if this Bash command would
    delete or overwrite something under data/, else None. Best-effort: splits
    naively on ; && || | and \\n, then shlex.split's each segment."""
    segments = re.split(r"&&|\|\||[;\n|]", command)

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue

        for m in REDIRECT_RE.finditer(seg):
            target = resolve(project_dir, cwd, m.group(1))
            if under_data(data_dir, target):
                return seg

        try:
            argv = shlex.split(seg)
        except ValueError:
            continue
        if not argv:
            continue

        cmd = os.path.basename(argv[0])
        args = argv[1:]
        non_flag_args = _strip_flags(args)

        if cmd in ("rm", "mv"):
            for a in non_flag_args:
                if under_data(data_dir, resolve(project_dir, cwd, a)):
                    return seg
        elif cmd == "cp":
            if non_flag_args and under_data(data_dir, resolve(project_dir, cwd, non_flag_args[-1])):
                return seg
        elif cmd == "sed":
            if any(a.startswith("-i") for a in args) and any(
                under_data(data_dir, resolve(project_dir, cwd, a)) for a in non_flag_args
            ):
                return seg
        elif cmd in ("tee", "truncate"):
            for a in non_flag_args:
                if under_data(data_dir, resolve(project_dir, cwd, a)):
                    return seg
        elif cmd == "dd":
            for a in args:
                if a.startswith("of="):
                    if under_data(data_dir, resolve(project_dir, cwd, a[3:])):
                        return seg

    return None


def block(project_dir, transcript_path, tool_name, target, reason):
    log_block(project_dir, transcript_path, tool_name, target, reason)
    sys.stderr.write(
        f"Blocked: {reason} (data/ is read-only per CLAUDE.md hard rule 3). "
        f"Logged to ai_usage/STEERING_LOG.md.\n"
    )
    sys.exit(2)


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    transcript_path = payload.get("transcript_path")
    data_dir = os.path.realpath(os.path.join(project_dir, "data"))

    if tool_name in ("Edit", "Write"):
        target = resolve(project_dir, cwd, tool_input.get("file_path"))
        if under_data(data_dir, target):
            block(project_dir, transcript_path, tool_name, tool_input.get("file_path"),
                  f"{tool_name} targeted a file under data/")
        sys.exit(0)

    if tool_name == "NotebookEdit":
        target = resolve(project_dir, cwd, tool_input.get("notebook_path"))
        if under_data(data_dir, target):
            block(project_dir, transcript_path, tool_name, tool_input.get("notebook_path"),
                  "NotebookEdit targeted a notebook under data/")
        sys.exit(0)

    if tool_name == "Bash":
        command = tool_input.get("command") or ""
        hit = check_bash(project_dir, cwd, data_dir, command)
        if hit:
            block(project_dir, transcript_path, tool_name, hit,
                  "Bash command appears to delete or overwrite a path under data/")
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # Never let a bug in this hook silently take down the turn in an
        # unrelated way -- but also never fail open on our own bug by
        # accident: an exception here means we couldn't evaluate the rule,
        # so err toward blocking is NOT done (could false-block unrelated
        # tool calls forever if the hook itself is broken). Fail open and
        # let a human notice via the exception in hook debug output.
        sys.exit(0)
