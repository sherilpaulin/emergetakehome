# Data Notes

Snapshot: 2026-09-15 06:00 ET. Everything below is computed from `data/`, not guessed. See `.claude/skills/data-notes/SKILL.md` for how to fill each section in.

## 1. Problems found

| ID | File | What's wrong | Rows | What we did |
|---|---|---|---|---|
| D-001 | students.csv | `user_id` doesn't match the `u_######` pattern every real row uses (`test_01`...`test_09`); all 9 also have `referral_source = internal`, not a documented value. | 9 | Excluded from CA and every funnel count (decision confirmed with user). `data/` itself untouched. |
| D-002 | students.csv vs lesson_events.csv | `lessons_completed` (summary field) is higher than the highest `lesson_number` actually logged in `lesson_events.csv`, in every case (never lower). | 19 | Per CLAUDE.md's existing rule, trust `lesson_events.csv`: use its max `lesson_number` for `lessons_completed`/Course Complete status everywhere. `students.csv` untouched, mismatch logged here. |
| D-003 | students.csv vs seats_by_city.csv | `city` has 7 raw spellings instead of the 3 canonical ones in `seats_by_city.csv` (`NYC`, `Sacramento`, `Boston`): `New York` (14), `nyc` (13), `NYC ` with a trailing space (10), `BOS` (6). | 43 | Normalized to the 3 canonical spellings for analysis (`New York`/`nyc`/`NYC ` → `NYC`, `BOS` → `Boston`). `data/` untouched; mapping applied only in `analysis/`. |
| D-004 | students.csv | `engagement_3d_minutes > engagement_7d_minutes` -- DATA_DICTIONARY.md says 3d "should never exceed" 7d. | 11 | Use `engagement_7d_minutes` instead of `engagement_3d_minutes` for all 11 rows where they disagree. `data/` untouched. See Assumptions and Questions for Emerge below. |

## 2. Row counts

| File | Rows before cleaning | Rows after cleaning | Note |
|---|---|---|---|
| students.csv | 3,009 | 3,000 | 9 test/internal accounts (D-001) excluded from the analysis population. |

## 3. Assumptions

- **Assumption:** for the 11 D-004 rows, `engagement_7d_minutes` is used instead of `engagement_3d_minutes` wherever they disagree. **Why:** the dictionary states 3d should never exceed 7d, so 3d is the broken field in these rows, not 7d.

## 4. Questions for Emerge

- **Question:** of the 11 D-004 rows, 3 (`u_105733`, `u_100329`, `u_103191`) also have `last_seen_at` 3+ days stale (4.1, 6.4, 3.3 days) yet `engagement_3d_minutes > 0` -- logically impossible if 3-day tracking is correct, and this exact pattern appears nowhere else in `students.csv`. Is this a known tracking/pipeline bug? **Until we know:** all 11 D-004 rows use `engagement_7d_minutes` per the Assumption above; the 3-row pattern is treated as supporting evidence for that assumption, not as a separate or smaller problem.
