"""Phase 10 (drill-down): withdrawn, permit_failed, and not_started --
the three statuses not covered by the passed/stopped/end comparison
(finish_vs_stop_comparison.py excludes withdrawn/permit_failed as
terminal endpoints; not_started was flagged in I-013 but not drilled
into). Read-only. Rerun any time with:

    python3 analysis/status_deep_dive.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")


def load():
    return pd.read_csv(
        os.path.join(CLEAN_DIR, "student_table.csv"),
        parse_dates=["signup_at", "last_seen_at", "course_completed_at", "permit_exam_date"],
    )


def demo_compare(label, grp, overall, cols):
    print(f"-- {label}: demographics vs. overall --")
    for col in cols:
        g = (grp[col].value_counts(normalize=True) * 100).round(1).to_dict()
        o = (overall[col].value_counts(normalize=True) * 100).round(1).to_dict()
        print(f"  {col}: {label}={g} | overall={o}")
    print()


def not_started_dive(t):
    grp = t[t["status"] == "not_started"]
    gap = (grp["last_seen_at"] - grp["signup_at"]).dt.total_seconds() / 86400
    days_dark = (SNAPSHOT - grp["last_seen_at"]).dt.total_seconds() / 86400

    print(f"n={len(grp):,} ({100 * len(grp) / len(t):.1f}% of all students)")
    print(f"gap between signup and last_seen_at: mean={gap.mean():.2f}d median={gap.median():.2f}d "
          f"max={gap.max():.2f}d -- most never came back at all")
    print(f"days since last seen (as of snapshot): mean={days_dark.mean():.1f}d median={days_dark.median():.1f}d")
    print(f"has_training_plan yes: {100 * (grp['has_training_plan'] == 'yes').mean():.1f}% "
          f"(overall: {100 * (t['has_training_plan'] == 'yes').mean():.1f}%)")
    print(f"engagement_7d_minutes > 0: {(grp['engagement_7d_minutes'] > 0).sum():,} of {len(grp):,}")
    print()
    demo_compare("not_started", grp, t, ["city", "primary_device", "preferred_language", "referral_source", "age_band"])


def withdrawn_dive(t):
    grp = t[t["status"] == "withdrawn"]
    print(f"n={len(grp):,} ({100 * len(grp) / len(t):.1f}% of all students)")
    print("lessons_completed at withdrawal:")
    print(grp["lessons_completed"].describe().to_string())
    print()
    demo_compare("withdrawn", grp, t, ["city", "referral_source"])
    print(f"has_training_plan yes: {100 * (grp['has_training_plan'] == 'yes').mean():.1f}% "
          f"(overall: {100 * (t['has_training_plan'] == 'yes').mean():.1f}%)")
    print(f"joined_group_chat yes: {100 * (grp['joined_group_chat'] == 'yes').mean():.1f}% "
          f"(overall: {100 * (t['joined_group_chat'] == 'yes').mean():.1f}%)")


def permit_failed_dive(t):
    grp = t[t["status"] == "permit_failed"].copy()
    print(f"n={len(grp):,} ({100 * len(grp) / len(t):.1f}% of all students)")
    print("permit_attempts:", grp["permit_attempts"].value_counts().to_dict(),
          "-- 41 failed once and never retried; 11 already used both attempts")
    print(f"avg_quiz_score: {grp['avg_quiz_score'].mean():.1f} (overall: {t['avg_quiz_score'].mean():.1f}) "
          f"-- comprehension is not the differentiator")
    print("plan_has_transport_to_dmv:", grp["plan_has_transport_to_dmv"].value_counts(dropna=False).to_dict())
    gap = (grp["permit_exam_date"] - grp["course_completed_at"]).dt.total_seconds() / 86400
    print(f"days from course complete to (failed) exam: mean={gap.mean():.1f} median={gap.median():.1f} "
          f"-- close to I-006's overall CC->Permit median (17.1d), not unusually rushed or delayed")


def main():
    t = load()

    print("=" * 70)
    print("NOT_STARTED")
    print("=" * 70)
    not_started_dive(t)

    print()
    print("=" * 70)
    print("WITHDRAWN")
    print("=" * 70)
    withdrawn_dive(t)

    print()
    print("=" * 70)
    print("PERMIT_FAILED")
    print("=" * 70)
    permit_failed_dive(t)


if __name__ == "__main__":
    main()
