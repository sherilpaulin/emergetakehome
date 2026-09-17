# Data Notes

Snapshot: 2026-09-15 06:00 ET. Everything below is computed from `data/`, not guessed. See `.claude/skills/data-notes/SKILL.md` for how to fill each section in.

## 1. Problems found

| ID | File | What's wrong | Rows | What we did |
|---|---|---|---|---|
| D-001 | students.csv | `user_id` doesn't match the `u_######` pattern every real row uses (`test_01`...`test_09`); all 9 also have `referral_source = internal`, not a documented value. | 9 | Excluded from CA and every funnel count (decision confirmed with user). `data/` itself untouched. |
| D-002 | students.csv vs lesson_events.csv | `lessons_completed` (summary field) is higher than the highest `lesson_number` actually logged in `lesson_events.csv`, in every case (never lower). | 19 (5 overlap with D-001 test accounts, already excluded; 14 remain among real students) | Per CLAUDE.md's existing rule, trust `lesson_events.csv`: `analysis/clean_data.py` overwrites `lessons_completed` with the event-log max (original kept as `lessons_completed_raw`), and adds `first_video_clean`/`course_complete_clean` flags from the same source. `data/` untouched. |
| D-003 | students.csv vs seats_by_city.csv | `city` has 7 raw spellings instead of the 3 canonical ones in `seats_by_city.csv` (`NYC`, `Sacramento`, `Boston`): `New York` (14), `nyc` (13), `NYC ` with a trailing space (10), `BOS` (6). | 43 | `analysis/clean_data.py` normalizes to the 3 canonical spellings (`New York`/`nyc`/`NYC ` → `NYC`, `BOS` → `Boston`); original kept as `city_raw`. `data/` untouched. |
| D-004 | students.csv | `engagement_3d_minutes > engagement_7d_minutes` -- DATA_DICTIONARY.md says 3d "should never exceed" 7d. | 11 | `analysis/clean_data.py` adds an `engagement_3d_unreliable` flag for these 11 rows; use `engagement_7d_minutes` instead wherever it's set. `data/` untouched. See Assumptions and Questions for Emerge below. |

## 2. Row counts

Produced by `analysis/clean_data.py`, writing to `analysis/clean/` (`data/` untouched).

| File | Rows before cleaning | Rows after cleaning | Note |
|---|---|---|---|
| students.csv | 3,009 | 3,000 | 9 test/internal accounts (D-001) excluded. |
| lesson_events.csv | 20,383 | 20,383 | Unchanged -- the 9 D-001 accounts had 0 event rows to begin with. |
| lessons.csv | 21 | 21 | Unchanged -- no problems found. |
| seats_by_city.csv | 3 | 3 | Unchanged -- no problems found. |

## 3. Assumptions

- **Assumption:** for the 11 D-004 rows, `engagement_7d_minutes` is used instead of `engagement_3d_minutes` wherever they disagree. **Why:** the dictionary states 3d should never exceed 7d, so 3d is the broken field in these rows, not 7d.
- **Assumption:** `student_table.csv`'s `lessons_first_7_days` uses a precise 7×24-hour window from `signup_at` (`completed_at <= signup_at + 7 days`), not calendar days. **Why:** the data dictionary doesn't define "first 7 days" precisely; a rolling window from the exact signup timestamp is the least ambiguous reading.
- **Assumption:** in `student_table.csv`, aggregate metrics (`avg_quiz_score`, `avg_minutes_watched`, `avg_minutes_expected`, `rewatch_ratio`, `longest_break_days`, `last_lesson_date`, `days_since_last_lesson`) are blank for students with 0 lessons done, not 0. **Why:** 0 would misleadingly imply "scored/watched zero on an attempted lesson," not "never attempted." `longest_break_days` is also blank for students with exactly 1 lesson (a break needs two points to measure between).

## 4. Questions for Emerge

- **Question:** of the 11 D-004 rows, 3 (`u_105733`, `u_100329`, `u_103191`) also have `last_seen_at` 3+ days stale (4.1, 6.4, 3.3 days) yet `engagement_3d_minutes > 0` -- logically impossible if 3-day tracking is correct, and this exact pattern appears nowhere else in `students.csv`. Is this a known tracking/pipeline bug? **Until we know:** all 11 D-004 rows use `engagement_7d_minutes` per the Assumption above; the 3-row pattern is treated as supporting evidence for that assumption, not as a separate or smaller problem.

## 5. Data dictionary: cleaned tables

Covers `analysis/clean/student_table.csv` (48 columns) and `analysis/clean/lesson_table.csv` (8 columns), built by `analysis/build_student_table.py` and `analysis/build_lesson_table.py`. **Any new metric added to either table from here on gets a row here in the same commit** -- this section is the contract, not an afterthought.

### student_table.csv -- unchanged from `data/students.csv`

Same field, same definition as `data/DATA_DICTIONARY.md`: `user_id`, `signup_at`, `referral_source`, `age_band`, `preferred_language`, `primary_device`, `status`, `first_video_at`, `last_lesson_completed_at`, `course_completed_at`, `last_seen_at`, `last_logged_in_at`, `engagement_7d_minutes`, `engagement_3d_minutes`, `has_training_plan`, `plan_created_at`, `plan_lessons_per_week`, `plan_study_days`, `plan_study_time`, `plan_hours_per_week`, `plan_target_permit_date`, `plan_has_transport_to_dmv`, `joined_group_chat`, `study_hall_sessions_attended`, `coach_calls_completed`, `permit_exam_date`, `permit_result`, `permit_attempts`.

### student_table.csv -- renamed or corrected during cleaning (D-002/D-003/D-004)

| Column | Definition |
|---|---|
| `city_raw` | Original `city` value from `data/students.csv`, before D-003 normalization. |
| `city` | `city_raw` normalized to `NYC`/`Sacramento`/`Boston` (D-003). Use this one for city-level analysis. |
| `lessons_completed_raw` | Original `lessons_completed` from `data/students.csv`, before the D-002 correction. |
| `lessons_completed` | Highest `lesson_number` for this student in `lesson_events.csv` (D-002: event log trusted over the summary field). Use this one everywhere. |
| `first_video_clean` | `True` if lesson 1 appears in `lesson_events.csv` for this student (event-log-derived First Video). |
| `course_complete_clean` | `True` if lesson 21 appears in `lesson_events.csv` for this student (event-log-derived Course Complete). |
| `engagement_3d_unreliable` | `True` for the 11 D-004 rows where `engagement_3d_minutes > engagement_7d_minutes`. Use `engagement_7d_minutes` instead when this is `True`. |

### student_table.csv -- new metrics (from `lesson_table.csv`, aggregated per student)

| Column | Definition |
|---|---|
| `lessons_done_count` | Count of this student's rows in `lesson_table.csv`. 0 if none. |
| `last_lesson_date` | Latest `completed_at` for this student. Blank if 0 lessons. |
| `days_since_last_lesson` | Snapshot time (2026-09-15 06:00 ET) minus `last_lesson_date`, in days. Blank if 0 lessons. |
| `lessons_first_7_days` | Count of lessons with `completed_at <= signup_at + 7 days` (a rolling 7×24h window, not calendar days). |
| `longest_break_days` | Largest gap, in days, between two consecutive `completed_at` values. Blank with fewer than 2 lessons. |
| `avg_quiz_score` | Mean `quiz_score_pct` across this student's completed lessons. Blank if 0 lessons. |
| `avg_minutes_watched` | Mean `minutes_watched` across this student's completed lessons. Blank if 0 lessons. |
| `avg_minutes_expected` | Mean `video_minutes` (nominal runtime) across the lessons this student completed. Blank if 0 lessons. |
| `rewatch_ratio` | Mean of (`minutes_watched` / `video_minutes`) computed per lesson, then averaged -- not the ratio of the two averages above (S-008). >1 suggests rewatching/slower pace, <1 suggests skimming. Blank if 0 lessons. |
| `stopped_lesson_title` | `title` of this student's highest-numbered completed lesson (where they currently are, not what's next). Blank if 0 lessons. |
| `stopped_module` | `module` of that same lesson. Blank if 0 lessons. |
| `signup_to_first_video_days` | Days from `signup_at` to lesson-1 `completed_at`. Blank if never activated. |
| `first_video_to_course_complete_days` | Days from lesson-1 `completed_at` to lesson-21 `completed_at`. Blank unless course-complete. |

### lesson_table.csv

| Column | Definition |
|---|---|
| `user_id` | Joins to `student_table.csv`/`students.csv`. |
| `lesson_number` | Which lesson, 1-21. |
| `completed_at` | When the student finished this lesson's video and quiz. |
| `minutes_watched` | Minutes of video watched for this lesson (includes rewatches). |
| `quiz_score_pct` | This lesson's quiz score, best attempt. |
| `title` | Lesson title, from `lessons.csv`. |
| `module` | CLP exam section this lesson prepares for, from `lessons.csv`. |
| `video_minutes` | Nominal/expected runtime of this lesson's video, from `lessons.csv`. |
