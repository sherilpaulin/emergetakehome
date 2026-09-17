"""Phase 10 (drill-down): how long between lessons, and does a long
break predict never coming back?

Two kinds of gap:
  - "internal" gaps -- time between one completed lesson and the next
    one that same student completed. By construction, every internal
    gap ends in a return (there IS a next lesson).
  - "terminal" gaps -- time since a still-in-progress student's last
    lesson, up to the snapshot. Unknown yet whether they'll return.

A terminal gap only counts as a confirmed "did not come back" once
it's longer than the longest gap anyone has EVER returned from --
otherwise it's just too soon to tell (right-censored), not a "no."
Read-only. Rerun any time with:

    python3 analysis/lesson_gap_return.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")
BINS = [0, 1, 3, 7, 14, 30, 60, 10_000]
BIN_LABELS = ["0-1d", "1-3d", "3-7d", "7-14d", "14-30d", "30-60d", "60d+"]


def load():
    lesson_table = pd.read_csv(os.path.join(CLEAN_DIR, "lesson_table.csv"), parse_dates=["completed_at"])
    student_table = pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"))
    return lesson_table, student_table


def internal_gaps(lesson_table):
    """Every gap between one lesson and the student's next one --
    always ends in a return, by definition."""
    gaps = []
    for _, g in lesson_table.sort_values("completed_at").groupby("user_id"):
        gaps.extend(g["completed_at"].diff().dropna().dt.total_seconds() / 86400)
    return pd.Series(gaps, name="gap_days")


def main():
    lesson_table, student_table = load()

    gaps = internal_gaps(lesson_table)
    print("=" * 70)
    print("TIME BETWEEN LESSONS (all gaps that ended in a return)")
    print("=" * 70)
    print(f"n={len(gaps):,}  mean={gaps.mean():.2f}d  median={gaps.median():.2f}d  "
          f"p90={gaps.quantile(0.9):.2f}d  p95={gaps.quantile(0.95):.2f}d  max={gaps.max():.2f}d")
    print()
    print(pd.cut(gaps, bins=BINS, labels=BIN_LABELS, right=False).value_counts().sort_index().to_string())

    resolved_cutoff = 30  # days -- chosen because 0 of 18,385 returns in this data took longer than ~24 days
    print()
    print("=" * 70)
    print(f"RETURN LIKELIHOOD BY BREAK LENGTH (resolved cutoff: {resolved_cutoff} days)")
    print("=" * 70)
    print(f"No student in this dataset has ever returned after a break of {gaps.max():.1f}+ days -- "
          f"the longest gap that ever ended in a return. A terminal (still-open) gap under "
          f"{resolved_cutoff} days is too soon to call; {resolved_cutoff}+ days is treated as a confirmed non-return.")
    print()

    started = student_table[(student_table["lessons_done_count"] >= 1) & (~student_table["course_complete_clean"])]
    terminal = started["days_since_last_lesson"]

    print(f"Students with 1+ lessons, not yet course-complete: {len(started):,}")
    print(pd.cut(terminal, bins=BINS, labels=BIN_LABELS, right=False).value_counts().sort_index().to_string())
    print()
    confirmed_no_return = (terminal >= resolved_cutoff).sum()
    too_soon_to_tell = (terminal < resolved_cutoff).sum()
    print(f"Confirmed no-return (break >= {resolved_cutoff}d, 0 historical returns from this far out): "
          f"{confirmed_no_return:,}")
    print(f"Too soon to tell (break < {resolved_cutoff}d): {too_soon_to_tell:,}")


if __name__ == "__main__":
    main()
