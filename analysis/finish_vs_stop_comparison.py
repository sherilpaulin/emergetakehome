"""Phase 10 (drill-down): permit_passed vs. everyone else, across every
candidate field from the finish-vs-stop menu.

Groups (per the user's explicit definition):
  - PASSED: status == permit_passed (274)
  - STOPPED: any other status EXCEPT permit_failed/withdrawn, which are
    excluded as separate terminal endpoints, not "still stoppable" (2,611)
  - EXCLUDED: permit_failed, withdrawn (115) -- not compared

STOPPED is deliberately heterogeneous (includes not_started, whose
lesson-based metrics are all blank) -- every numeric comparison reports
its own non-null n rather than assuming full coverage. Self-selected
fields (group chat, study hall, coach calls, training plan) are
correlational only, per CLAUDE.md rule 7. Read-only. Rerun any time
with:

    python3 analysis/finish_vs_stop_comparison.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")

CATEGORICAL_FIELDS = [
    "joined_group_chat", "has_training_plan", "primary_device",
    "preferred_language", "city", "referral_source", "age_band",
]
NUMERIC_FIELDS = [
    "study_hall_sessions_attended", "coach_calls_completed",
    "plan_lessons_per_week", "plan_hours_per_week",
    "signup_to_first_video_days", "lessons_first_7_days",
    "avg_quiz_score", "avg_minutes_watched", "avg_minutes_expected",
    "rewatch_ratio", "longest_break_days",
    "engagement_7d_minutes", "engagement_3d_minutes",
]


def load():
    return pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"))


def compare_categorical(passed, stopped, col):
    print(f"-- {col} --")
    p = (passed[col].value_counts(normalize=True, dropna=False) * 100).round(1)
    s = (stopped[col].value_counts(normalize=True, dropna=False) * 100).round(1)
    both = sorted(set(p.index) | set(s.index), key=lambda x: (pd.isna(x), x))
    for val in both:
        print(f"  {val!r}: passed={p.get(val, 0.0)}%  stopped={s.get(val, 0.0)}%")


def compare_numeric(passed, stopped, col):
    p, s = passed[col].dropna(), stopped[col].dropna()
    print(f"-- {col} --")
    print(f"  passed:  n={len(p):,}  mean={p.mean():.2f}  median={p.median():.2f}")
    print(f"  stopped: n={len(s):,}  mean={s.mean():.2f}  median={s.median():.2f}")


def main():
    t = load()
    passed = t[t["status"] == "permit_passed"]
    stopped = t[~t["status"].isin(["permit_passed", "permit_failed", "withdrawn"])]
    excluded = t[t["status"].isin(["permit_failed", "withdrawn"])]

    print("=" * 70)
    print(f"GROUPS: passed={len(passed):,}  stopped={len(stopped):,}  "
          f"excluded (permit_failed/withdrawn)={len(excluded):,}")
    print("stopped status breakdown:", stopped["status"].value_counts().to_dict())
    print("=" * 70)

    print()
    print("CATEGORICAL / SELF-SELECTED FIELDS")
    print("=" * 70)
    for col in CATEGORICAL_FIELDS:
        compare_categorical(passed, stopped, col)
        print()

    print("=" * 70)
    print("NUMERIC FIELDS")
    print("=" * 70)
    for col in NUMERIC_FIELDS:
        compare_numeric(passed, stopped, col)
        print()


if __name__ == "__main__":
    main()
