#!/usr/bin/env python3
"""UserPromptSubmit hook: auto-logs every prompt into ai_usage/PROMPT_LOG.md
and nudges Claude to check ai_usage/STEERING_LOG.md when the prompt looks
like a correction, pushback, or decision.

Input (stdin JSON): {"prompt": "...", "cwd": "...", ...}
Output (stdout JSON, only when a nudge is warranted):
  {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "..."}}

Never blocks the turn: any failure here is swallowed and the hook exits 0.
"""

import datetime
import json
import os
import re
import sys

PROMPT_LOG_HEADER = (
    "# Prompt Log\n\n"
    "Every prompt sent in this session, logged automatically by "
    "`.claude/hooks/prompt-log.py` (a UserPromptSubmit hook). Numbered "
    "P-001, P-002, ... in send order. Phase is parsed from a leading "
    "`Phase N:` in the prompt text; prompts sent before this hook existed "
    "(P-001, P-002) were backfilled by hand in the same format.\n"
)

TRIGGER_PATTERNS = [
    r"\bno\b",
    r"\bnope\b",
    r"\bwrong\b",
    r"\binstead\b",
    r"why did you",
    r"why would you",
    r"let'?s go with",
    r"\bactually\b",
    r"\bstop\b",
    r"\bdon'?t\b",
    r"\bincorrect\b",
    r"\brevert\b",
    r"\bundo\b",
]


def next_id(existing_text):
    ids = [int(m) for m in re.findall(r"^## P-(\d+)", existing_text, re.MULTILINE)]
    return (max(ids) + 1) if ids else 1


def phase_label(prompt):
    m = re.match(r"\s*Phase\s+(\d+)\s*:", prompt)
    return f"Phase {m.group(1)}" if m else "not specified"


def fence(text):
    # Avoid breaking the markdown code fence if the prompt itself contains ```
    return "~~~" if "```" in text else "```"


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    log_path = os.path.join(project_dir, "ai_usage", "PROMPT_LOG.md")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    existing = ""
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            existing = f.read()

    pid = f"P-{next_id(existing):03d}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f_ = fence(prompt)

    entry = (
        f"\n## {pid}\n"
        f"- **Phase:** {phase_label(prompt)}\n"
        f"- **Time:** {timestamp}\n"
        f"- **Prompt:**\n"
        f"{f_}\n{prompt}\n{f_}\n"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        if not existing:
            f.write(PROMPT_LOG_HEADER)
        f.write(entry)

    if any(re.search(pat, prompt, re.IGNORECASE) for pat in TRIGGER_PATTERNS):
        reminder = (
            f"[ai-usage-log] This prompt ({pid}) contains language that often signals a "
            "correction, pushback, or decision (e.g. 'no', 'wrong', 'instead', 'why did "
            "you', \"let's go with\"). It may be a false positive (e.g. 'no problem'), or "
            "the real moment might use no trigger word at all -- use judgment. Before "
            "finishing this turn, check whether it belongs in ai_usage/STEERING_LOG.md "
            "per .claude/skills/ai-usage-log/SKILL.md. If so, add a numbered S-### entry -- "
            "be honest if this is Claude's own mistake being corrected."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": reminder,
            }
        }))

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
