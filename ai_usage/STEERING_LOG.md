# Steering Log

Interactive moments in this session where the user corrected, pushed back on, made a decision about, answered a question from, or asked Claude to explain something. Curated by hand per `.claude/skills/ai-usage-log/SKILL.md`, in Claude's own words -- including its own mistakes, honestly. Full prompt text lives in `ai_usage/PROMPT_LOG.md` under the referenced `P-###` id; this file doesn't repeat it.

## S-001
- **Phase:** Phase 1
- **Type:** pushback
- **What I did:** After the Phase 1 exploration summary, I asked four clarifying questions via `AskUserQuestion` (how to treat inconsistent `city` labels, how to treat `referral_source = internal` rows, dashboard format, and what to do next) with a recommended option pre-selected on each.
- **What you said (P-001 follow-up):** You dismissed all four with "wait for next instruction" rather than picking any option.
- **Why:** Not stated. Read as: you wanted to redirect the session (to Phase 2 documentation work) before settling those data-cleaning decisions, not as agreement with my recommended defaults.
- **What changed:** I stopped and did not act on any of the four recommended defaults (no city normalization, no exclusion of `internal` rows, no dashboard format chosen, no move to a data-quality audit). Those four questions remain open and will need to be re-asked or answered before I compute funnel numbers.

## S-002
- **Phase:** Phase 3
- **Type:** correction (mine -- caught and fixed during testing, not user-driven)
- **What I did:** My first version of `protect-data.py`'s Bash check used raw regex substring matching for "data/" anywhere in the command text. When I ran my own test script (a Bash tool call containing the literal words "rm" and "data/students.csv" inside a test-description string, plus a scratch test directory that itself contained a `/data/` path segment), the live hook wrongly blocked that meta-test command itself -- not a real attempt to touch the project's `data/`. It auto-wrote a garbled entry here describing the blocked call as if it were a real safety event.
- **What you said:** N/A -- self-caught while testing, before this reached you.
- **Why:** Substring matching doesn't know the difference between "the literal text data/" and "an actual resolved path under this project's data/ directory" -- it will false-fire on any command that merely mentions the word, including test harnesses and unrelated directories also named `data`.
- **What changed:** Rewrote the Bash check to split the command into segments, parse each with `shlex`, and resolve each candidate path against the real `data/` directory before deciding -- the same resolve-then-compare logic already used for Edit/Write. Deleted the garbled auto-generated entry this bug produced and replaced it with this one. Re-tested all 4 cases (block Edit on data/, block `rm` on data/, allow `cp` from data/ to analysis/, allow Edit on analysis/) -- all passed. Known remaining limitation: this is regex/shlex-based, not a full shell parser, so a command that builds its target path via a shell variable, command substitution, or a glob (e.g. `X=data/students.csv; rm $X`) won't be caught. Only literal path arguments are checked.
