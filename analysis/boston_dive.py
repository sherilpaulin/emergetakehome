"""Phase 10 (drill-down): Boston -- lesson-level stall points, lesson
performance, support signals, and demographics vs. the overall
population. Builds on I-004/I-019/I-022 (Boston lags every funnel
step, is overrepresented in withdrawals, and underperforms even after
accounting for its referral-source mix). Read-only. Rerun any time
with:

    python3 analysis/boston_dive.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")
CC_CUTOFF_DAYS = 55  # p90 signup-to-CourseComplete, same as funnel_analysis.py


def load():
    return pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"), parse_dates=["signup_at"])


def stall_point_breakdown(t):
    days_since_signup = (SNAPSHOT - t["signup_at"]).dt.total_seconds() / 86400
    eligible = t[(days_since_signup >= CC_CUTOFF_DAYS) & t["first_video_clean"]]
    stalled = eligible[~eligible["course_complete_clean"]]

    for label, grp in (("Boston", stalled[stalled["city"] == "Boston"]), ("Overall", stalled)):
        print(f"-- {label}: stalled n={len(grp):,} --")
        print((grp["stopped_module"].value_counts(normalize=True) * 100).round(1).to_string())
        print()


def compare(label, boston, overall, cols, numeric):
    print(f"-- {label} --")
    for col in cols:
        if numeric:
            print(f"  {col}: Boston mean={boston[col].mean():.2f} median={boston[col].median():.2f}  |  "
                  f"overall mean={overall[col].mean():.2f} median={overall[col].median():.2f}")
        else:
            b = (boston[col].value_counts(normalize=True) * 100).round(1).to_dict()
            o = (overall[col].value_counts(normalize=True) * 100).round(1).to_dict()
            print(f"  {col}: Boston={b} | overall={o}")
    print()


def main():
    t = load()
    boston = t[t["city"] == "Boston"]

    print("=" * 70)
    print(f"WHERE BOSTON'S STALLED STUDENTS STOP (module they last completed)")
    print("=" * 70)
    stall_point_breakdown(t)

    print("=" * 70)
    print("LESSON PERFORMANCE (among students with 1+ lessons)")
    print("=" * 70)
    boston_active = boston[boston["lessons_done_count"] >= 1]
    overall_active = t[t["lessons_done_count"] >= 1]
    compare("quiz/watch/rewatch", boston_active, overall_active,
            ["avg_quiz_score", "avg_minutes_watched", "avg_minutes_expected", "rewatch_ratio"], numeric=True)

    print("=" * 70)
    print("SUPPORT SIGNALS")
    print("=" * 70)
    compare("group chat / study hall / coach calls (categorical)", boston, t,
            ["joined_group_chat"], numeric=False)
    compare("group chat / study hall / coach calls (numeric)", boston, t,
            ["study_hall_sessions_attended", "coach_calls_completed"], numeric=True)

    print("=" * 70)
    print("DEMOGRAPHICS")
    print("=" * 70)
    compare("age/device/language", boston, t, ["age_band", "primary_device", "preferred_language"], numeric=False)

    print("=" * 70)
    print("FOLLOW-UP: preferred_language and outcomes (Haitian Creole is 100% Boston-concentrated)")
    print("=" * 70)
    days_since_signup = (SNAPSHOT - t["signup_at"]).dt.total_seconds() / 86400
    print("ht speakers by city:")
    print(t[t["preferred_language"] == "ht"]["city"].value_counts().to_string())
    print()
    print("National end-to-end Permit rate by preferred_language (78-day p90 cutoff):")
    for lang in ("en", "es", "ht"):
        eligible = t[(t["preferred_language"] == lang) & (days_since_signup >= 78)]
        passed = int((eligible["permit_result"] == "passed").sum())
        rate = 100 * passed / len(eligible) if len(eligible) else None
        rate_str = f"{rate:.1f}%" if rate is not None else "n/a"
        print(f"  {lang}: {passed} of {len(eligible):,} eligible = {rate_str}")


if __name__ == "__main__":
    main()
