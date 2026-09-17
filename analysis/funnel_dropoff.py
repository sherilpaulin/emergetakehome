"""Phase 10 (drill-down): where the two weakest funnel steps actually
lose/delay students.

Builds on analysis/funnel_analysis.py's official p90-adjusted funnel
(I-002: biggest drop is FV->CC; I-006: biggest post-completion lag is
CC->Permit). Uses the same eligibility logic (signup-based p90 cutoffs)
so "stalled" means "had enough time and still didn't move," not "too
new to judge." Read-only. Rerun any time with:

    python3 analysis/funnel_dropoff.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")
CUTOFF_DAYS = {"fv": 7, "cc": 55, "permit": 78}  # same as funnel_analysis.py's official cutoffs
FIRST_FOUR_LESSONS = [
    "Welcome & How the CLP Works",
    "Inspecting Your Vehicle",
    "Basic Control & Shifting",
    "Seeing, Communicating & Speed Management",
]


def load():
    return pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"), parse_dates=["signup_at"])


def days_since_signup(t):
    return (SNAPSHOT - t["signup_at"]).dt.total_seconds() / 86400


def fv_to_cc_dropoff(t):
    """Among students who reached First Video and have had 55+ days
    (p90) since signup, who still hasn't finished the course, and where
    (which lesson/module) did they stop."""
    eligible = t[(days_since_signup(t) >= CUTOFF_DAYS["cc"]) & t["first_video_clean"]]
    stalled = eligible[~eligible["course_complete_clean"]]

    print(f"CC-eligible FV students: {len(eligible):,}")
    print(f"Stalled (had time, didn't finish): {len(stalled):,} ({100 * len(stalled) / len(eligible):.1f}%)")
    print()
    print("By status:")
    print(stalled["status"].value_counts().to_string())
    print()
    print("By module they stopped in:")
    print(stalled["stopped_module"].value_counts().to_string())
    print()
    print("By exact lesson they stopped at (top 8):")
    print(stalled["stopped_lesson_title"].value_counts().head(8).to_string())
    print()
    in_first_four = stalled["stopped_lesson_title"].isin(FIRST_FOUR_LESSONS).sum()
    print(f"Stalled within the first 4 lessons: {in_first_four:,} of {len(stalled):,} "
          f"({100 * in_first_four / len(stalled):.1f}%)")
    return stalled


def cc_to_permit_dropoff(t):
    """Among course-completers who have had 78+ days (p90) since
    signup and still haven't passed, what's actually holding them up:
    never scheduled, scheduled and pending, or scheduled and failed."""
    eligible = t[(days_since_signup(t) >= CUTOFF_DAYS["permit"]) & t["course_complete_clean"]]
    not_passed = eligible[eligible["permit_result"] != "passed"]

    print(f"Permit-eligible course-completers: {len(eligible):,}")
    print(f"Not passed: {len(not_passed):,} ({100 * len(not_passed) / len(eligible):.1f}%)")
    print()

    never_scheduled = not_passed[not_passed["permit_exam_date"].isna()]
    scheduled_pending = not_passed[not_passed["permit_exam_date"].notna() & not_passed["permit_result"].isna()]
    failed = not_passed[not_passed["permit_result"] == "failed"]

    print(f"  Never scheduled an exam:      {len(never_scheduled):,}")
    print(f"  Scheduled, no result yet:     {len(scheduled_pending):,}")
    print(f"  Took the exam and failed:     {len(failed):,}")
    print()
    print("Never-scheduled group, by plan_has_transport_to_dmv (self-reported, correlational only):")
    print(never_scheduled["plan_has_transport_to_dmv"].value_counts(dropna=False).to_string())
    return not_passed


def main():
    t = load()

    print("=" * 70)
    print("DRILL-DOWN 1: First Video -> Course Complete (biggest drop, I-002)")
    print("=" * 70)
    fv_to_cc_dropoff(t)

    print()
    print("=" * 70)
    print("DRILL-DOWN 2: Course Complete -> Permit (biggest lag, I-006)")
    print("=" * 70)
    cc_to_permit_dropoff(t)


if __name__ == "__main__":
    main()
