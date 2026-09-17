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

## S-003
- **Phase:** Phase 6
- **Type:** decision
- **What I did:** Presented D-001 (9 `test_*`/`internal` rows in students.csv) with two options via `AskUserQuestion`: exclude entirely (recommended), or keep them in and just document.
- **What you said:** "Exclude entirely (Recommended)"
- **Why:** Not restated beyond picking the recommended option; matches the existing D-001 assumption that these are QA/staff test accounts, not real students.
- **What changed:** `analysis/DATA_NOTES.md` D-001 row and row-count table updated: 9 rows excluded from CA and every funnel count going forward. `data/` itself untouched.

## S-004
- **Phase:** Phase 6
- **Type:** decision
- **What I did:** Presented D-002 (19 students where `lessons_completed` overstates progress vs `lesson_events.csv`) with two options: trust the event log per CLAUDE.md's existing rule (recommended), or use `students.csv` as-is and override that rule.
- **What you said:** "Trust lesson_events.csv (Recommended)"
- **Why:** Confirms the standing CLAUDE.md rule rather than overriding it -- no new reasoning needed, this was a confirmation, not a fresh call.
- **What changed:** `analysis/DATA_NOTES.md` D-002 row added: `lesson_events.csv`'s max lesson_number is the source of truth for `lessons_completed`/Course Complete status throughout the analysis. `students.csv` untouched.

## S-005
- **Phase:** Phase 6
- **Type:** decision
- **What I did:** Presented D-003 (43 rows with non-canonical `city` spellings: `New York`, `nyc`, `NYC `, `BOS`) with two options: normalize to the 3 canonical spellings (recommended), or exclude the 43 rows from city-based analysis instead.
- **What you said:** "Normalize to 3 canonical cities (Recommended)"
- **Why:** Not restated beyond picking the recommended option; the 4 variants are unambiguous typos/case/whitespace issues, not genuinely different cities, so normalizing keeps more real students in city-level analysis than excluding them would.
- **What changed:** `analysis/DATA_NOTES.md` D-003 row added: `New York`/`nyc`/`NYC ` → `NYC`, `BOS` → `Boston`, applied only in `analysis/`, `data/` untouched.

## S-006
- **Phase:** Phase 6
- **Type:** correction (mine -- caught and fixed immediately, not user-driven)
- **What I did:** Ran `python3 analysis/check_data.py 2>&1 | sed -n '/D-004/,/CHECKED/p'` while my shell's cwd had drifted to `data/` (from an earlier `cd` in a prior command). `protect-data.py`'s redirect regex matched `>&1` in `2>&1` as "redirect into a file literally named `&1`", resolved that relative to cwd (`data/`), and blocked the call -- `&1` is shell syntax for file-descriptor duplication, never a filename. It auto-wrote a garbled `blocked-edit` entry here treating this as a real safety event.
- **What you said:** N/A -- self-caught immediately, before this reached you.
- **Why:** The redirect regex didn't exclude `&`-prefixed targets, so any `2>&1` or `>&2` in a command run with cwd inside `data/` (itself an allowed, harmless state -- read-only browsing of `data/` is fine) would false-block.
- **What changed:** Added a `(?!&)` exclusion to the redirect regex in `protect-data.py` so fd-duplication targets are never treated as paths. Verified with cwd forced to `data/` and the same `2>&1` command -- now exits 0. Also fixed my own shell cwd back to the project root. Deleted the garbled auto-generated entry this bug produced and replaced it with this one.

## S-007
- **Phase:** Phase 6
- **Type:** decision
- **What I did:** Presented D-004 (11 students with `engagement_3d_minutes > engagement_7d_minutes`) with two options: trust 7d and distrust 3d for these rows (recommended), or clip 3d to 7d as a derived correction.
- **What you said:** Picked "treat 7d as reliable" (D-004 stays at 11 rows, unchanged), and separately asked to add a Questions for Emerge entry with a specific diagnostic: check whether `last_seen_at` being 3+ days stale while `engagement_3d_minutes > 0` points to a system tracking bug. Corrected me mid-plan when my first draft plan read as narrowing D-004 down to just the 3 matching rows -- clarified the 11-row problem and the 3-row evidence are not the same thing.
- **Why:** If a student hasn't been seen in 3+ days, `engagement_3d_minutes` should be 0 by definition -- nonzero is only explainable by a tracking/pipeline bug, not normal variance.
- **What changed:** Added a permanent diagnostic to `analysis/check_data.py` (alongside the existing D-004 check, not replacing it): of the 11 D-004 rows, 3 (`u_105733`, `u_100329`, `u_103191`) also have `last_seen_at` 3+ days stale -- a pattern found nowhere else in `students.csv`. `analysis/DATA_NOTES.md` updated: D-004 row (11, unchanged) in Problems found, a new Assumption (trust 7d for these 11), and a new Question for Emerge citing the 3-row evidence.

## S-008
- **Phase:** Phase 7
- **Type:** correction (mine -- caught by the user, not self-caught)
- **What I did:** Proposed `rewatch_ratio` as an extra `student_table.csv` metric, defined as the ratio of the student's two existing averages: `avg_minutes_watched ÷ avg_minutes_expected`.
- **What you said:** "rewatch_ratio = minutes watched / video minutes, which then gets averaged across all completed lessons" -- i.e. compute the ratio per lesson first, then average the ratios, not average the two quantities first and then divide.
- **Why:** These are not the same number in general (`mean(a/b) != mean(a)/mean(b)`) -- a student with one very short lesson watched at 3x length and one very long lesson watched exactly on time would show a skewed ratio-of-averages that a lesson-by-lesson average would not.
- **What changed:** `analysis/build_student_table.py` computes `_ratio = minutes_watched / video_minutes` per row of `lesson_table.csv`, then takes `groupby("user_id")["_ratio"].mean()` -- average of ratios, per the corrected definition.

## S-009
- **Phase:** Phase 9
- **Type:** correction (mine -- caught and fixed immediately, not user-driven)
- **What I did:** Answered the Phase 9 funnel-analysis request by computing counts/percentages with ad-hoc `python3 -c` commands and reporting the numbers directly in chat, without saving a script.
- **What you said:** N/A -- self-caught before this reached you, while checking `git status` after your stop-hook nudge and noticing no new analysis file existed for numbers I'd already reported.
- **Why:** CLAUDE.md hard rule 4: "If a number came from a script, the script lives in analysis/ and reruns from scratch." An ad-hoc shell command satisfies neither half of that.
- **What changed:** Wrote `analysis/funnel_analysis.py`, ran it, and confirmed it reproduces the exact same numbers already given (CA 3,000 / FV 1,998 / CC 696 / Permit 274 overall, plus the 3-city breakdown and the 90th-percentile time-to-stage figures). No numbers changed, just given a reproducible source.
