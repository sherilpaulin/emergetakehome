"""Phase 7 (tables): analysis/clean/lesson_table.csv.

One row per finished lesson (from analysis/clean/lesson_events.csv),
with lesson info from analysis/clean/lessons.csv added. Reads only from
analysis/clean/ -- never touches data/ or the other clean/*.csv files.
Rerun any time with:

    python3 analysis/build_lesson_table.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")


def main():
    events = pd.read_csv(os.path.join(CLEAN_DIR, "lesson_events.csv"))
    lessons = pd.read_csv(os.path.join(CLEAN_DIR, "lessons.csv"))

    table = events.merge(lessons, on="lesson_number", how="left", validate="many_to_one")

    assert len(table) == len(events), "lesson_table.csv row count drifted from lesson_events.csv"
    assert table["title"].notna().all(), "some lesson_number values didn't match lessons.csv"

    out_path = os.path.join(CLEAN_DIR, "lesson_table.csv")
    table.to_csv(out_path, index=False)
    print(f"lesson_table.csv: {len(table):,} rows (matches lesson_events.csv: {len(events):,})")


if __name__ == "__main__":
    main()
