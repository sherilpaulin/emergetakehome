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

## S-010
- **Phase:** Phase 9
- **Type:** decision
- **What I did:** Walked through recency-cutoff options across several turns: proposed p90 signup-based cutoffs (7/55/78 days), compared generic-7-days vs. calculated cutoffs, showed the raw vs. p90-adjusted funnel side by side, gave step-duration distributions (mean/median/range/p90/p95), and compared mean/median/p90 as the cutoff basis.
- **What you said:** "lets use p90 as the funnel as part of the analysis."
- **Why:** p90 excludes only the slowest ~10% of legitimate finishers from each step's denominator; mean and especially median were rejected because a median cutoff by definition still counts roughly half of eventual finishers as "too early to judge," undermining the fairness goal.
- **What changed:** `analysis/funnel_analysis.py`'s `main()` reordered so the p90-adjusted funnel prints first as "OFFICIAL FUNNEL," with the raw funnel demoted to a labeled reference section. `analysis/DATA_NOTES.md` Assumptions section records the decision and why mean/median were rejected.

## S-011
- **Phase:** Phase 10 (retracted) / redirected to funnel drill-down
- **Type:** pushback
- **What I did:** Nothing yet -- the Phase 10 "Cutoff points" prompt (lesson-level drop-off, timing between lessons, break/return likelihood) was interrupted by the user before I acted on it.
- **What you said:** "ignore the last prompt (phase 10: cutoff points) and remove it from the prompt log... lets drill into steps that are taking longer or where we lose the most students" -- explicitly asked to redact the retracted prompt from `ai_usage/PROMPT_LOG.md`, not just move on from it.
- **Why:** Not stated -- read as: redirect the analysis to build on the I-001..I-007 insights already logged (biggest funnel drop and slowest step) rather than jumping to a new, separately-scoped lesson-level cutoff analysis.
- **What changed:** Deleted the `## P-022` entry from `PROMPT_LOG.md` (the numbering now jumps P-021 -> P-023, intentionally, documented here). No file from the retracted Phase 10 request was created. Proceeding instead with a drill-down into the funnel steps already identified as slow/lossy (I-002 FV->CC drop, I-006 CC->Permit lag).

## S-012
- **Phase:** Phase 10
- **Type:** correction (mine -- caught and fixed immediately, not user-driven)
- **What I did:** Answered the lesson-3 stall drill-down (I-011) with an ad-hoc `python3 -c` computation, then wrote `INSIGHTS.md`'s I-011 entry citing its source as "not yet saved to a script" -- the exact same mistake as S-009.
- **What you said:** N/A -- self-caught while re-reading the entry I'd just written and recognizing the same gap.
- **Why:** CLAUDE.md hard rule 4, again: a number isn't done until the script that produced it lives in `analysis/` and reruns from scratch.
- **What changed:** Added `lesson3_stall_drilldown()` to `analysis/funnel_dropoff.py`, ran it, confirmed identical numbers (216 stalled, 79.14 vs 79.75 quiz mean, 22.7% vs 34.2% group chat, etc.). Fixed I-011's source citation and moved it after I-010 in `INSIGHTS.md` (it had been inserted out of numeric order).

## S-013
- **Phase:** Phase 10
- **Type:** explain-request
- **What I did:** Asked to explain why the I-014 support-signal gaps (coach calls, study hall, group chat) can't be read as causal, and what else could explain the difference.
- **What you said:** "explain why we can't say it causes finishing. What could be another reason for the difference?"
- **Why:** Standard due diligence before treating a correlational finding as a lever for the community plan -- matches CLAUDE.md rule 7.
- **What changed:** Rather than only listing hypotheticals, tested the strongest one (tenure/opportunity confound) directly: added `tenure_adjusted_support_rates()` to `analysis/finish_vs_stop_comparison.py`. Result actually reversed I-014's raw-count finding for coach calls and study hall (both cumulative counts) once corrected for time-in-program -- stopped students used them at a *higher* rate per month, not lower. `joined_group_chat` (a one-time decision, not cumulative) survived the test. Added I-017 to `INSIGHTS.md` documenting the reversal and pointed I-014 forward to it rather than silently leaving a superseded framing standing.

## S-014
- **Phase:** Phase 10
- **Type:** correction (mine -- caught by the user, not self-caught)
- **What I did:** In `tenure_adjusted_support_rates()`, silently narrowed "stopped" to additionally exclude `not_started` students, without being asked -- a different population than every other comparison in `analysis/finish_vs_stop_comparison.py` and than the group definition the user had explicitly given earlier ("compare permit passed against the other status (minus the two i mentioned)"). This produced S-013/I-017's claim that the coach-calls/study-hall gap "reverses" once tenure-adjusted.
- **What you said:** "the exclusions should only be permit_passed, permit_failed, withdrawn; not started stays as part of the 'stopped' funnel."
- **Why:** I made an implicit judgment call (excluding zero-activity `not_started` rows to make the comparison "cleaner") instead of using the population already agreed on -- that's mine to flag and ask about, not decide unilaterally.
- **What changed:** Refactored `tenure_adjusted_support_rates()` to take `passed`/`stopped` as parameters from `main()` instead of deriving its own population, so there's exactly one definition of "stopped" used everywhere in the file. Reran: with `not_started` correctly included, the gap shrinks substantially (raw 2.5x/2.8x -> per-month ~1.1-1.2x) but does **not** reverse -- passed students still show a real, if smaller, edge, especially at the median (0.400 vs 0.000 coach calls/month). Rewrote I-017 in `INSIGHTS.md` to state this correctly, with a note explaining what was wrong in the first version rather than silently swapping the numbers.

## S-015
- **Phase:** Phase 10
- **Type:** pushback
- **What I did:** Wrote I-029 (group chat is the gate, study hall is the real signal) with a correlational flag, but framed it mainly around the mechanical group-chat/study-hall gating relationship (data dictionary: study hall only announced in chat) without spelling out the more important alternative explanation: motivated students self-select into repeated live attendance.
- **What you said:** "please edit the group chat + study hall finding to reflect that more motivated students might be pursuing those options and causing some skew in the data."
- **Why:** The mechanical gating fact (chat -> study hall visibility) explains *why* study hall requires chat, but doesn't by itself explain *why* study hall attendance predicts passing -- self-selected motivation is the more likely driver, and I'd underweighted it.
- **What changed:** Added an explicit paragraph to I-029 in `INSIGHTS.md` naming the motivation-confound directly, cross-referencing I-027 (plan adherence) as the same underlying story from a different angle, and stating plainly: don't read this as "assign more study hall and the rate goes up."

## S-016
- **Phase:** Phase 4
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit -- not logged at the time.
- **What I did:** Presented example entries for all four `DATA_NOTES.md` parts (Problems found, Row counts, Assumptions, Questions for Emerge) and asked whether to build the real file and skill now.
- **What you said (P-005):** "create the data_notes.md but do not add any entries yet"
- **Why:** Not restated -- wanted the file skeleton in place without committing to the specific example content shown.
- **What changed:** Created `analysis/DATA_NOTES.md` with the four section headers and empty tables only -- no D-### rows, no assumptions, no questions. Held off building the skill until the next prompt.

## S-017
- **Phase:** Phase 4
- **Type:** answered-question
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** After creating the empty `DATA_NOTES.md` skeleton, asked "Skill for `.claude/skills/data-notes/` still not built -- want that now too, or hold?"
- **What you said (P-006):** "yes create the data-notes skill as well"
- **Why:** Not restated.
- **What changed:** Created `.claude/skills/data-notes/SKILL.md` documenting the D-### ID scheme and how to fill in each of the four `DATA_NOTES.md` sections.

## S-018
- **Phase:** Phase 7
- **Type:** pushback
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** In response to P-010 ("show me the exact code and result for counting test accounts"), ran a Bash command showing the exact regex and its output (9 rows removed).
- **What you said (P-011):** "Try again"
- **Why:** Not stated. Being honest: I don't have clear visibility into what was insufficient about the first attempt, and I'm not inventing a reason I don't actually know.
- **What changed:** Re-ran the same verification (exact code plus a live result: 3,009 -> 3,000, the 9 `test_*` ids listed) and presented it again. No code or number differed between the two attempts.

## S-019
- **Phase:** Phase 7
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit -- only the rewatch_ratio piece of this same answer batch was logged at the time (S-008).
- **What I did:** Asked 4 clarifying questions via `AskUserQuestion` before building `student_table.csv`: what "stopped lesson/module" means, how to represent aggregate metrics for 0-lesson students, what anchor to use for "lessons in the first 7 days," and which extra metrics to add.
- **What you said (P-012 answers):** "Last lesson/module they completed" (not the next one); "Blank/empty" for 0-lesson students; `signup_at` as the 7-day anchor. (The fourth answer, the `rewatch_ratio` definition correction, is S-008.)
- **Why:** Not restated beyond picking the recommended option for the first three -- each was a definitional ambiguity that needed a call before building the table.
- **What changed:** `build_student_table.py` implements all three: `stopped_lesson_title`/`stopped_module` use the highest completed lesson; aggregate metrics stay blank (not 0) for 0-lesson students; `lessons_first_7_days` counts `completed_at <= signup_at + 7 days`.

## S-020
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** answered-question
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** After the FV->CC and CC->Permit drill-down (`funnel_dropoff.py`), asked "Want me to size those two segments precisely next, or keep drilling into the lesson-3 stall point first?"
- **What you said (P-024):** "lets drill into the lesson three stall point first"
- **Why:** Not restated.
- **What changed:** Built the lesson-3-specific drilldown (I-011) instead of sizing the two re-engagement segments (I-009/I-010) first.

## S-021
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** answered-question
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** After the status-prioritization drilldown, asked "Want this added to `INSIGHTS.md` as-is, or drill into P1's 61 students individually first?"
- **What you said (P-027):** "lets add to insights for now" (then pivoted to a new field-comparison request in the same message).
- **Why:** Not restated.
- **What changed:** Added I-013 to `INSIGHTS.md` as-is rather than first drilling into the 61 P1 students individually.

## S-022
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** Presented a menu of ~17 candidate fields to compare between "students who finished" and "students who stopped," without yet defining those two groups precisely.
- **What you said (P-028):** "lets define stopped as any step prior to permit received. for this analysis, lets filter out status = permit failed or withdrawn as those are end points. I want to compare permit passed against the other status (minus the two i mentioned)"
- **Why:** Not restated -- a definitional choice needed before running any comparison.
- **What changed:** Defined `passed` = `permit_passed`, `stopped` = every other status except `permit_failed`/`withdrawn`, and built `finish_vs_stop_comparison.py` around that split (later refined in S-014).

## S-023
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit -- handled by adding a `DATA_NOTES.md` assumption at the time, but never logged here.
- **What I did:** Had already been using the passed/stopped/end definition from S-022 in `finish_vs_stop_comparison.py`, without it being written down in `DATA_NOTES.md`.
- **What you said (P-032):** "passed means status = permit_passed; stopped means status is either not_started, inactive, course_complete, permit_scheduled, or in_progress; end means status = withdrawn or permit failed;"
- **Why:** Not restated -- reads as a request to formalize/confirm the definition already in use.
- **What changed:** Confirmed the code already matched exactly (no code change needed) and added the definition as a formal Assumption in `analysis/DATA_NOTES.md`, alongside the other methodology assumptions.

## S-024
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** answered-question
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** After testing 4 hypotheses for the referral-source funnel gaps (`paid_social`, `reentry_org`, `workforce_center`), ended with "Two of these three 'can't test' gaps are good, concrete additions to the Questions for Emerge list -- want me to add them to `DATA_NOTES.md`?"
- **What you said (P-036):** "yes please add the two questions." (then pivoted to a new Boston request in the same message).
- **Why:** Not restated.
- **What changed:** Added the `paid_social` ad-targeting question and the `workforce_center` case-management question to `DATA_NOTES.md`'s Questions for Emerge section.

## S-025
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** Presented a table of 8 suggested Boston drill-down angles (referral-source mix, `stopped_module`, lesson performance, support signals, demographics, signup timing, transport, sample-size check) and asked which to run.
- **What you said (P-037):** "Referral-source mix within Boston"
- **Why:** Not restated.
- **What changed:** Built the Boston referral-source composition decomposition (I-022) instead of any of the other 7 suggested angles.

## S-026
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** Presented a grouped menu of further analyses (segments not yet funnel-broken, behavior-over-content, time/cohort trends, prioritization extensions) and asked which to run.
- **What you said (P-041):** "start with three segment analysis"
- **Why:** Not restated -- picked the first category (age band, device, transport-by-city) over the other three.
- **What changed:** Built the age-band/device/transport-by-city funnel breakdowns (I-025/I-026) before any of the other suggested categories.

## S-027
- **Phase:** Phase 10: Deep-Dive Analysis
- **Type:** decision
- **Backfilled:** yes, added during the P-047/P-048 log audit.
- **What I did:** After the 3-segment analysis, the menu from S-026 still had 3 unrun categories (behavior-over-content, cohort trends, prioritization extensions). Asked which was next.
- **What you said:** P-042: "let's run behavior over content next"; P-044 (after the exam-lead-time detour in P-043): "lets do both" (cohort trend + prioritization extensions, the two remaining categories).
- **Why:** Not restated.
- **What changed:** Ran behavior-over-content (I-027/I-028/I-029) first, then both remaining categories together (I-031/I-032/I-033), completing the full original menu from the suggestions turn.
