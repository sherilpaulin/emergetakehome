"""Phase 8: standing tests for analysis/clean/student_table.csv and
lesson_table.csv.

Read-only -- loads the 2 tables plus analysis/DATA_NOTES.md, never
writes anything. Rerun any time (e.g. after a new data export) with:

    pytest analysis/tests/test_clean_tables.py -v

Not run as part of building this file -- see ai_usage/STEERING_LOG.md /
the Phase 8 request for why.
"""

import os
import re

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN_DIR = os.path.join(ROOT, "analysis", "clean")
NOTES_PATH = os.path.join(ROOT, "analysis", "DATA_NOTES.md")

SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")
VALID_CITIES = {"NYC", "Sacramento", "Boston"}
VALID_STATUSES = {
    "not_started", "in_progress", "inactive", "course_complete",
    "permit_scheduled", "permit_passed", "permit_failed", "withdrawn",
}
DAY_GAP_COLUMNS = [
    "days_since_last_lesson",
    "longest_break_days",
    "signup_to_first_video_days",
    "first_video_to_course_complete_days",
]


@pytest.fixture(scope="module")
def student_table():
    return pd.read_csv(
        os.path.join(CLEAN_DIR, "student_table.csv"),
        parse_dates=["signup_at", "last_lesson_date"],
    )


@pytest.fixture(scope="module")
def lesson_table():
    return pd.read_csv(os.path.join(CLEAN_DIR, "lesson_table.csv"), parse_dates=["completed_at"])


@pytest.fixture(scope="module")
def data_notes_counts():
    """Parses the '## 2. Row counts' table in DATA_NOTES.md so expected
    counts come from the living document, not a hardcoded number."""
    with open(NOTES_PATH, encoding="utf-8") as f:
        text = f.read()
    counts = {}
    for match in re.finditer(r"\|\s*([\w.]+\.csv)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|", text):
        fname, before, after = match.groups()
        counts[fname] = {"before": int(before.replace(",", "")), "after": int(after.replace(",", ""))}
    return counts


# --- 1. Rows ---------------------------------------------------------

# One row per student -- user_id must have no duplicates in student_table.csv.
def test_student_table_one_row_per_student(student_table):
    assert student_table["user_id"].is_unique


# Row count matches the "students.csv rows after cleaning" figure recorded in DATA_NOTES.md.
def test_student_table_row_count_matches_data_notes(student_table, data_notes_counts):
    assert len(student_table) == data_notes_counts["students.csv"]["after"]


# No duplicate (user_id, lesson_number) pairs -- a student can't finish the same lesson twice in this table.
def test_lesson_table_no_duplicate_student_lesson_pairs(lesson_table):
    assert not lesson_table.duplicated(["user_id", "lesson_number"]).any()


# Row count matches the "lesson_events.csv rows after cleaning" figure recorded in DATA_NOTES.md.
def test_lesson_table_row_count_matches_data_notes(lesson_table, data_notes_counts):
    assert len(lesson_table) == data_notes_counts["lesson_events.csv"]["after"]


# --- 2. Values --------------------------------------------------------

# Every lesson_number is a valid position in the 21-lesson course.
def test_lesson_number_in_valid_range(lesson_table):
    assert lesson_table["lesson_number"].between(1, 21).all()


# Every quiz_score_pct is a valid percentage.
def test_quiz_score_in_valid_range(lesson_table):
    assert lesson_table["quiz_score_pct"].between(0, 100).all()


# minutes_watched should never be negative.
def test_no_negative_minutes_watched(lesson_table):
    assert (lesson_table["minutes_watched"] >= 0).all()


# video_minutes (lesson runtime from lessons.csv) should never be negative.
def test_no_negative_video_minutes(lesson_table):
    assert (lesson_table["video_minutes"] >= 0).all()


# city must be one of the 3 canonical values -- D-003 normalization should have caught every variant.
def test_only_allowed_cities(student_table):
    assert set(student_table["city"].unique()) <= VALID_CITIES


# status must be one of the 8 documented values in DATA_DICTIONARY.md.
def test_only_allowed_statuses(student_table):
    assert set(student_table["status"].unique()) <= VALID_STATUSES


# --- 3. Dates -----------------------------------------------------------

# No lesson can be completed after the snapshot was taken.
def test_no_completed_at_after_snapshot(lesson_table):
    assert (lesson_table["completed_at"] <= SNAPSHOT).all()


# No lesson can be completed before that student even signed up.
def test_no_completed_at_before_signup(lesson_table, student_table):
    merged = lesson_table.merge(student_table[["user_id", "signup_at"]], on="user_id", how="left")
    assert (merged["completed_at"] >= merged["signup_at"]).all()


# None of the day-gap metrics (time between two events) should ever be negative.
def test_no_negative_day_gap_metrics(student_table):
    for col in DAY_GAP_COLUMNS:
        values = student_table[col].dropna()
        assert (values >= 0).all(), f"{col} has a negative value"


# --- 4. Tables match ------------------------------------------------------

# Every student who appears in lesson_table.csv must also exist in student_table.csv.
def test_all_lesson_table_users_exist_in_student_table(lesson_table, student_table):
    assert set(lesson_table["user_id"]) <= set(student_table["user_id"])


# lessons_done_count in student_table.csv must equal that student's actual row count in lesson_table.csv.
def test_lessons_done_count_matches_lesson_table(student_table, lesson_table):
    actual_counts = lesson_table.groupby("user_id").size()
    expected = student_table.set_index("user_id")["lessons_done_count"]
    actual = actual_counts.reindex(expected.index, fill_value=0)
    assert (expected == actual).all()


# lessons_completed must equal the highest lesson_number that student has in lesson_table.csv (0 if none).
def test_lessons_completed_matches_max_lesson_number(student_table, lesson_table):
    max_lesson = lesson_table.groupby("user_id")["lesson_number"].max()
    expected = student_table.set_index("user_id")["lessons_completed"]
    actual = max_lesson.reindex(expected.index, fill_value=0)
    assert (expected == actual).all()


# --- 5. Edge cases -----------------------------------------------------

# Students with 0 lessons done must have blank (not 0) aggregate metrics, per the Phase 7 decision.
def test_zero_lesson_students_have_blank_aggregates(student_table):
    zero_lesson = student_table[student_table["lessons_done_count"] == 0]
    for col in ["avg_quiz_score", "avg_minutes_watched", "last_lesson_date", "longest_break_days"]:
        assert zero_lesson[col].isna().all(), f"{col} should be blank for 0-lesson students"


# Every course-complete student finished exactly lesson 21, and it appears in lesson_table.csv.
def test_course_complete_students_have_21_lessons(student_table, lesson_table):
    complete = student_table[student_table["course_complete_clean"]]
    assert (complete["lessons_completed"] == 21).all()
    lesson_21_users = set(lesson_table.loc[lesson_table["lesson_number"] == 21, "user_id"])
    assert set(complete["user_id"]) <= lesson_21_users


# Withdrawn students must still be present in student_table.csv, not silently dropped.
def test_withdrawn_students_present_in_student_table(student_table):
    assert (student_table["status"] == "withdrawn").sum() > 0


# No D-001 test/internal account (user_id like test_01) should remain in either table.
def test_no_test_accounts_remain(student_table, lesson_table):
    test_pattern = r"^test_"
    assert not student_table["user_id"].str.match(test_pattern).any()
    assert not lesson_table["user_id"].str.match(test_pattern).any()


# --- 6. Outliers -- flagged, not failed --------------------------------

# Always passes; flags unusually long breaks between lessons for a human to look at, rather than failing.
def test_flag_long_breaks(student_table):
    threshold_days = 90
    long_breaks = student_table[student_table["longest_break_days"] > threshold_days]
    if len(long_breaks):
        print(f"\n[FLAG] {len(long_breaks)} students have a break longer than {threshold_days} days: "
              f"{long_breaks['user_id'].tolist()}")
    assert True


# Always passes; flags an unusually high rewatch_ratio (possible data oddity) for a human to look at.
def test_flag_high_rewatch_ratio(student_table):
    threshold_ratio = 5
    high_ratio = student_table[student_table["rewatch_ratio"] > threshold_ratio]
    if len(high_ratio):
        print(f"\n[FLAG] {len(high_ratio)} students have rewatch_ratio > {threshold_ratio}x: "
              f"{high_ratio['user_id'].tolist()}")
    assert True
