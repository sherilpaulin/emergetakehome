---
name: data-notes
description: Use when finding, documenting, or resolving a data-quality issue in this take-home (inconsistent values, duplicates, test rows, fields that disagree) -- fills in analysis/DATA_NOTES.md. Triggered by CLAUDE.md hard rule 6 ("flag data problems, don't silently fix them") and the "When unsure" rule. Also use when computing funnel/row counts that exclude any rows, or when a decision needs input only Emerge (Gabe) can give.
---

# Data Notes

`analysis/DATA_NOTES.md` has four parts. Keep every number computed from
`data/` (CLAUDE.md hard rule 4) -- never estimate a count and write it
down as if it were exact.

## 1. Problems found

One row per distinct issue, ID'd `D-001`, `D-002`, ... (parallel to
`P-###` in PROMPT_LOG.md and `S-###` in STEERING_LOG.md, own prefix
since this is a different log). Add a row the moment you find:
inconsistent values, duplicates, test/internal rows, or a field that
disagrees with another (e.g. `lessons_completed` vs `lesson_events.csv`).

Columns: **ID | File | What's wrong | Rows | What we did**

- "What's wrong" is specific enough that someone could re-find the rows
  (a filter condition, not a vague description).
- "Rows" is a real count from the data, not "a few" or "some."
- "What we did" says what the analysis does about it (exclude, note only,
  trust one field over another) -- never edit `data/` itself to fix it.
- If a later prompt un-flags or changes how a `D-###` issue was handled,
  edit that row in place; don't create a duplicate ID for the same issue.

## 2. Row counts

One row per data file: **File | Rows before cleaning | Rows after
cleaning | Note**. "Before" is the raw row count. "After" is what's left
once every `D-###` exclusion from part 1 is applied. The note says which
`D-###` id(s) caused the drop. If nothing was excluded, "before" and
"after" are equal -- write both anyway, don't omit the row.

## 3. Assumptions

A bullet per guess the analysis had to make where the data or data
dictionary didn't say. Format: **Assumption: ... Why: ...**. This is
also where CLAUDE.md's "When unsure" rule lands -- stop, write the
assumption here, then continue; don't guess quietly and don't leave it
undocumented.

## 4. Questions for Emerge

A bullet per question only Emerge (Gabe) can actually answer -- not
things resolvable by re-reading the data or the dictionary. Format:
**Question: ... Until we know: ...**, where "until we know" states the
working assumption used everywhere else in the analysis (should usually
match an entry in part 3). If Gabe answers one of these mid-session,
update the assumption in part 3 and mark the question here as answered
rather than deleting it.

## General

- This file documents problems; it does not fix them. `data/` is never
  edited (CLAUDE.md hard rule 3, enforced by `.claude/hooks/protect-data.py`).
- New entries in any part are also a candidate for a steering-log entry
  if they came from a back-and-forth with the user (see
  `.claude/skills/ai-usage-log/SKILL.md`) -- the two logs serve different
  purposes and don't duplicate each other's content.
