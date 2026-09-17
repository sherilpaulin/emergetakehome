"""Phase 7 (tables): analysis/clean/student_table.csv.

One row per student. Starts from analysis/clean/students.csv as-is and
adds per-student metrics aggregated from analysis/clean/lesson_table.csv
(already the validated lesson_events + lessons.csv join -- reused here
rather than re-derived). Reads only from analysis/clean/ -- never
touches data/ or overwrites the other clean/*.csv files. Rerun any time
with:

    python3 analysis/build_student_table.py

Join safety: every metric below is computed by grouping lesson_table.csv
by user_id FIRST (one row per user_id out), then left-merging onto
students.csv (also one row per user_id). Group-then-merge, never a raw
row-level merge, so there is no fan-out/duplication risk. Every user_id
in lesson_table.csv already exists in students.csv (0 orphans, checked
in Phase 5/6), so the left join is guaranteed to keep exactly
len(students) rows.
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
NOTES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DATA_NOTES.md")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")


def load():
    students = pd.read_csv(CLEAN_DIR + "/students.csv", parse_dates=["signup_at"])
    lesson_table = pd.read_csv(CLEAN_DIR + "/lesson_table.csv", parse_dates=["completed_at"])
    return students, lesson_table


def per_student_metrics(lesson_table, students):
    lt = lesson_table.merge(students[["user_id", "signup_at"]], on="user_id", how="left")

    counts = lt.groupby("user_id").size().rename("lessons_done_count")

    last_lesson_date = lt.groupby("user_id")["completed_at"].max().rename("last_lesson_date")

    first_7 = lt[lt["completed_at"] <= lt["signup_at"] + pd.Timedelta(days=7)]
    lessons_first_7_days = first_7.groupby("user_id").size().rename("lessons_first_7_days")

    def longest_break(dates):
        dates = dates.sort_values()
        if len(dates) < 2:
            return pd.NA
        gaps = dates.diff().dropna().dt.total_seconds() / 86400
        return gaps.max()

    longest_break_days = lt.groupby("user_id")["completed_at"].apply(longest_break).rename("longest_break_days")

    avg_quiz_score = lt.groupby("user_id")["quiz_score_pct"].mean().rename("avg_quiz_score")
    avg_minutes_watched = lt.groupby("user_id")["minutes_watched"].mean().rename("avg_minutes_watched")
    avg_minutes_expected = lt.groupby("user_id")["video_minutes"].mean().rename("avg_minutes_expected")

    lt = lt.assign(_ratio=lt["minutes_watched"] / lt["video_minutes"])
    rewatch_ratio = lt.groupby("user_id")["_ratio"].mean().rename("rewatch_ratio")

    stopped = lt.sort_values("lesson_number").groupby("user_id").tail(1).set_index("user_id")
    stopped_lesson_title = stopped["title"].rename("stopped_lesson_title")
    stopped_module = stopped["module"].rename("stopped_module")

    lesson_1 = lt[lt["lesson_number"] == 1].set_index("user_id")["completed_at"]
    lesson_21 = lt[lt["lesson_number"] == 21].set_index("user_id")["completed_at"]
    signup_by_user = students.set_index("user_id")["signup_at"]

    signup_to_first_video_days = ((lesson_1 - signup_by_user).dt.total_seconds() / 86400).rename(
        "signup_to_first_video_days"
    )
    first_video_to_course_complete_days = ((lesson_21 - lesson_1).dt.total_seconds() / 86400).rename(
        "first_video_to_course_complete_days"
    )

    metrics = pd.concat(
        [
            counts,
            last_lesson_date,
            lessons_first_7_days,
            longest_break_days,
            avg_quiz_score,
            avg_minutes_watched,
            avg_minutes_expected,
            rewatch_ratio,
            stopped_lesson_title,
            stopped_module,
            signup_to_first_video_days,
            first_video_to_course_complete_days,
        ],
        axis=1,
    )
    return metrics


def append_data_note(text):
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(text)


def main():
    students, lesson_table = load()
    metrics = per_student_metrics(lesson_table, students)

    table = students.merge(metrics, on="user_id", how="left")
    table["lessons_done_count"] = table["lessons_done_count"].fillna(0).astype(int)
    table["lessons_first_7_days"] = table["lessons_first_7_days"].fillna(0).astype(int)
    table["days_since_last_lesson"] = (SNAPSHOT - table["last_lesson_date"]).dt.total_seconds() / 86400

    assert len(table) == len(students), f"row count drifted: {len(table)} vs {len(students)}"
    assert table["user_id"].is_unique, "duplicate user_id rows in student_table.csv"

    gap_mismatch = table[table["lessons_done_count"] != table["lessons_completed"]]
    negative_activation = table[table["signup_to_first_video_days"] < 0]
    negative_pace = table[table["first_video_to_course_complete_days"] < 0]

    discrepancy_notes = []
    if len(gap_mismatch):
        discrepancy_notes.append(
            f"| D-005 | analysis/clean/lesson_table.csv | `lessons_done_count` (row count) disagrees with "
            f"`lessons_completed` (max lesson_number) for a student, meaning a lesson sequence has a gap. "
            f"| {len(gap_mismatch)} | Flagged only -- see student_table.csv rows: "
            f"{gap_mismatch['user_id'].head(5).tolist()} |\n"
        )
    if len(negative_activation):
        discrepancy_notes.append(
            f"| D-006 | analysis/clean/student_table.csv | `signup_to_first_video_days` is negative "
            f"(lesson 1 completed before signup_at). | {len(negative_activation)} | Flagged only -- see rows: "
            f"{negative_activation['user_id'].head(5).tolist()} |\n"
        )
    if len(negative_pace):
        discrepancy_notes.append(
            f"| D-007 | analysis/clean/student_table.csv | `first_video_to_course_complete_days` is negative "
            f"(lesson 21 completed before lesson 1). | {len(negative_pace)} | Flagged only -- see rows: "
            f"{negative_pace['user_id'].head(5).tolist()} |\n"
        )

    if discrepancy_notes:
        append_data_note("\n" + "".join(discrepancy_notes))
        print(f"Discrepancies found and logged to DATA_NOTES.md: {len(discrepancy_notes)}")
    else:
        print("No discrepancies found (lessons_done_count matches lessons_completed for all rows; "
              "no negative day-gaps).")

    table.to_csv(os.path.join(CLEAN_DIR, "student_table.csv"), index=False)
    print(f"student_table.csv: {len(table):,} rows (students.csv: {len(students):,}), "
          f"unique user_id: {table['user_id'].is_unique}")


if __name__ == "__main__":
    main()
