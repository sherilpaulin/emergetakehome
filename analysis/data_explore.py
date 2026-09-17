"""Phase 5: data exploration.

Profiles every file in data/ -- row counts, columns, blanks, distinct
values in low-cardinality text columns, min/max for dates and numbers,
and a handful of dataset-specific consistency checks ("any other unique
features"). Read-only: never writes to data/. Rerun any time with:

    python3 analysis/data_explore.py
"""

import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

LOW_CARDINALITY_LIMIT = 30
DATETIME_HINT = ("_at", "_date")


def blank_count(series):
    if series.dtype == object:
        non_null = series.dropna()
        empty_strings = (non_null.astype(str).str.strip() == "").sum()
        return series.isna().sum() + empty_strings
    return series.isna().sum()


def looks_like_datetime(col_name):
    return any(col_name.endswith(h) for h in DATETIME_HINT)


def profile_file(name):
    path = os.path.join(DATA_DIR, name)
    df = pd.read_csv(path)

    print("=" * 70)
    print(f"{name}  ({len(df):,} rows, {len(df.columns)} columns)")
    print("=" * 70)

    for col in df.columns:
        series = df[col]
        blanks = blank_count(series)
        print(f"\n-- {col} ({series.dtype}) --")
        print(f"   blanks: {blanks:,} of {len(series):,}")

        if looks_like_datetime(col):
            parsed = pd.to_datetime(series.dropna(), errors="coerce")
            parsed = parsed.dropna()
            if len(parsed):
                print(f"   min: {parsed.min()}   max: {parsed.max()}")
            continue

        if pd.api.types.is_numeric_dtype(series):
            non_null = series.dropna()
            if len(non_null):
                print(f"   min: {non_null.min()}   max: {non_null.max()}")
            continue

        # text / categorical
        nunique = series.nunique(dropna=True)
        print(f"   distinct values: {nunique}")
        if nunique <= LOW_CARDINALITY_LIMIT:
            counts = series.value_counts(dropna=False)
            for val, count in counts.items():
                label = repr(val) if (isinstance(val, str) and val != val.strip()) or pd.isna(val) else val
                print(f"     {label!r}: {count:,}")
        else:
            print(f"   (high cardinality -- not listing all {nunique} values)")
            top = series.value_counts().head(5)
            print(f"   top 5: {dict(top)}")

    return df


def check(label, condition_count, detail=""):
    flag = "FLAG" if condition_count else "ok"
    suffix = f" -- {detail}" if detail and condition_count else ""
    print(f"   [{flag}] {label}: {condition_count:,}{suffix}")


def other_features_students(s, events):
    print("\n-- other checks (students.csv) --")
    check("duplicate user_id rows", int(s.duplicated("user_id").sum()))
    test_ids = s["user_id"].str.startswith("test", na=False)
    check("user_id rows not matching u_###### pattern", int((~s["user_id"].str.match(r"^u_\d+$", na=False)).sum()),
          f"e.g. {s.loc[test_ids, 'user_id'].head(3).tolist()}")

    eng = s[["engagement_3d_minutes", "engagement_7d_minutes"]].dropna()
    check("rows where engagement_3d_minutes > engagement_7d_minutes",
          int((eng["engagement_3d_minutes"] > eng["engagement_7d_minutes"]).sum()))

    check("lessons_completed outside 0-21",
          int(((s["lessons_completed"] < 0) | (s["lessons_completed"] > 21)).sum()))

    has_plan_no_fields = s[s["has_training_plan"] == "no"][
        ["plan_lessons_per_week", "plan_study_days", "plan_study_time", "plan_hours_per_week"]
    ].notna().any(axis=1)
    check("has_training_plan == 'no' but a plan_* field is filled in", int(has_plan_no_fields.sum()))

    permit_result_blank_but_attempts = s[(s["permit_result"].isna()) & (s["permit_attempts"] > 0)]
    check("permit_result blank but permit_attempts > 0", len(permit_result_blank_but_attempts))

    max_event_lesson = events.groupby("user_id")["lesson_number"].max()
    joined = s[["user_id", "lessons_completed"]].merge(
        max_event_lesson.rename("max_event_lesson"), on="user_id", how="left"
    )
    joined["max_event_lesson"] = joined["max_event_lesson"].fillna(0).astype(int)
    mismatch = joined["lessons_completed"] != joined["max_event_lesson"]
    check("lessons_completed disagrees with max lesson in lesson_events.csv", int(mismatch.sum()))

    orphan_events_users = set(events["user_id"]) - set(s["user_id"])
    check("user_ids in lesson_events.csv not found in students.csv", len(orphan_events_users))


def other_features_events(events, lessons, students):
    print("\n-- other checks (lesson_events.csv) --")
    check("lesson_number outside 1-21", int(((events["lesson_number"] < 1) | (events["lesson_number"] > 21)).sum()))
    check("quiz_score_pct outside 0-100",
          int(((events["quiz_score_pct"] < 0) | (events["quiz_score_pct"] > 100)).sum()))
    check("minutes_watched negative or zero", int((events["minutes_watched"] <= 0).sum()))
    check("duplicate (user_id, lesson_number) pairs", int(events.duplicated(["user_id", "lesson_number"]).sum()))
    unknown_lessons = set(events["lesson_number"]) - set(lessons["lesson_number"])
    check("lesson_number values not present in lessons.csv", len(unknown_lessons), str(unknown_lessons))


def other_features_lessons(lessons):
    print("\n-- other checks (lessons.csv) --")
    check("duplicate lesson_number rows", int(lessons.duplicated("lesson_number").sum()))
    expected = set(range(1, 22))
    missing = expected - set(lessons["lesson_number"])
    check("missing lesson_number in 1-21", len(missing), str(missing))
    check("video_minutes <= 0", int((lessons["video_minutes"] <= 0).sum()))


def other_features_seats(seats, students):
    print("\n-- other checks (seats_by_city.csv) --")
    student_cities = set(students["city"].unique())
    seat_cities = set(seats["city"].unique())
    check("student city values with no exact match in seats_by_city.csv",
          len(student_cities - seat_cities), str(sorted(student_cities - seat_cities)))


def main():
    students = profile_file("students.csv")
    events = profile_file("lesson_events.csv")
    lessons = profile_file("lessons.csv")
    seats = profile_file("seats_by_city.csv")

    print("\n" + "=" * 70)
    print("ANY OTHER UNIQUE FEATURES")
    print("=" * 70)
    other_features_students(students, events)
    other_features_events(events, lessons, students)
    other_features_lessons(lessons)
    other_features_seats(seats, students)


if __name__ == "__main__":
    main()
