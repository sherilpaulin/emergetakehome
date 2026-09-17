"""Phase 7: data cleaning.

Applies the D-001..D-004 decisions recorded in analysis/DATA_NOTES.md
and writes cleaned copies to analysis/clean/. Never touches data/ --
read-only source, per CLAUDE.md hard rule 3. Rerun any time with:

    python3 analysis/clean_data.py
"""

import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
CLEAN_DIR = os.path.join(ROOT, "analysis", "clean")

CITY_MAP = {
    "New York": "NYC",
    "nyc": "NYC",
    "NYC ": "NYC",
    "BOS": "Boston",
}


def load_raw():
    s = pd.read_csv(os.path.join(DATA_DIR, "students.csv"))
    e = pd.read_csv(os.path.join(DATA_DIR, "lesson_events.csv"))
    lessons = pd.read_csv(os.path.join(DATA_DIR, "lessons.csv"))
    seats = pd.read_csv(os.path.join(DATA_DIR, "seats_by_city.csv"))
    return s, e, lessons, seats


def clean_students(s, e):
    # D-001: exclude test/internal accounts (user_id not matching u_######)
    is_test = ~s["user_id"].str.match(r"^u_\d+$", na=False)
    excluded_ids = set(s.loc[is_test, "user_id"])
    s = s.loc[~is_test].copy()

    # D-002: trust lesson_events.csv over the lessons_completed summary field.
    # Keep the raw value for transparency, add the event-log-derived value as
    # the one to use everywhere downstream (matches CLAUDE.md's existing
    # First Video / Course Complete funnel definitions, both event-log based).
    max_lesson = e.groupby("user_id")["lesson_number"].max()
    s = s.merge(max_lesson.rename("_max_event_lesson"), on="user_id", how="left")
    s["_max_event_lesson"] = s["_max_event_lesson"].fillna(0).astype(int)
    s = s.rename(columns={"lessons_completed": "lessons_completed_raw"})
    s["lessons_completed"] = s["_max_event_lesson"]
    s["first_video_clean"] = s["_max_event_lesson"] >= 1
    s["course_complete_clean"] = s["_max_event_lesson"] >= 21
    s = s.drop(columns=["_max_event_lesson"])

    # D-003: normalize city labels to the 3 canonical spellings.
    s = s.rename(columns={"city": "city_raw"})
    s["city"] = s["city_raw"].replace(CITY_MAP)

    # D-004: engagement_3d_minutes > engagement_7d_minutes is unreliable for
    # these rows (dictionary: 3d should never exceed 7d). Flag rather than
    # overwrite -- the recorded decision was "use 7d instead", not "clip 3d".
    s["engagement_3d_unreliable"] = s["engagement_3d_minutes"] > s["engagement_7d_minutes"]

    return s, excluded_ids


def clean_events(e, excluded_ids):
    # Defensive: drop any event rows belonging to excluded (D-001) students.
    # None exist today (checked separately), but this keeps clean/ correct
    # if that ever changes on a re-export.
    return e.loc[~e["user_id"].isin(excluded_ids)].copy()


def main():
    s_raw, e_raw, lessons_raw, seats_raw = load_raw()
    os.makedirs(CLEAN_DIR, exist_ok=True)

    students, excluded_ids = clean_students(s_raw, e_raw)
    events = clean_events(e_raw, excluded_ids)
    lessons = lessons_raw.copy()  # no problems found (Phase 5/6)
    seats = seats_raw.copy()      # no problems found (Phase 5/6)

    students.to_csv(os.path.join(CLEAN_DIR, "students.csv"), index=False)
    events.to_csv(os.path.join(CLEAN_DIR, "lesson_events.csv"), index=False)
    lessons.to_csv(os.path.join(CLEAN_DIR, "lessons.csv"), index=False)
    seats.to_csv(os.path.join(CLEAN_DIR, "seats_by_city.csv"), index=False)

    print("Row counts (before -> after):")
    print(f"  students.csv:       {len(s_raw):,} -> {len(students):,}  ({len(excluded_ids)} D-001 rows excluded)")
    print(f"  lesson_events.csv:  {len(e_raw):,} -> {len(events):,}  (0 expected, D-001 accounts had no events)")
    print(f"  lessons.csv:        {len(lessons_raw):,} -> {len(lessons):,}  (unchanged)")
    print(f"  seats_by_city.csv:  {len(seats_raw):,} -> {len(seats):,}  (unchanged)")
    print()
    print(f"D-002 applied: lessons_completed corrected for "
          f"{(students['lessons_completed'] != students['lessons_completed_raw']).sum()} rows")
    print(f"D-003 applied: city normalized for "
          f"{(students['city'] != students['city_raw']).sum()} rows")
    print(f"D-004 flagged: engagement_3d_unreliable = True for "
          f"{int(students['engagement_3d_unreliable'].sum())} rows")


if __name__ == "__main__":
    main()
