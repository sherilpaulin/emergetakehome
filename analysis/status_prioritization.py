"""Phase 10 (drill-down): does student status suggest an outreach
priority order, especially for "inactive" students close to finishing?

Segments inactive students by module proximity to Course Complete
(using stopped_module, already computed in student_table.csv) and
crosses that with the I-012 dormancy cliff (<30 days = still plausibly
returning on their own; 30+ days = confirmed unlikely, needs active
outreach). Read-only. Rerun any time with:

    python3 analysis/status_prioritization.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")

# Module order, closest-to-finish first (Final Prep/lesson 21 = already
# Course Complete, so never appears as a stopped_module for the inactive).
PRIORITY_TIERS = {
    "P1: Air Brakes / Combination Vehicles / Practice Tests (closest to done)": [
        "Air Brakes", "Combination Vehicles", "Practice Tests",
    ],
    "P2: General Knowledge (mid-course, biggest population)": ["General Knowledge"],
    "P3: Orientation (only lesson 1 done)": ["Orientation"],
}


def load():
    return pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"))


def main():
    t = load()

    print("=" * 70)
    print("STATUS DISTRIBUTION (student_table.csv, n=%d)" % len(t))
    print("=" * 70)
    print(t["status"].value_counts().to_string())
    print()
    print((t["status"].value_counts(normalize=True) * 100).round(1).to_string())

    inactive = t[t["status"] == "inactive"]
    print()
    print("=" * 70)
    print(f"INACTIVE STUDENTS: {len(inactive):,} ({100 * len(inactive) / len(t):.1f}% of all students)")
    print("=" * 70)
    print(f"Dormancy split (I-012 cliff): <30d (still plausible) = "
          f"{(inactive['days_since_last_lesson'] < 30).sum():,}, "
          f">=30d (confirmed unlikely, needs active outreach) = "
          f"{(inactive['days_since_last_lesson'] >= 30).sum():,}")
    print()

    print("Priority tiers, by module they stopped in (closest to Course Complete first):")
    for label, modules in PRIORITY_TIERS.items():
        tier = inactive[inactive["stopped_module"].isin(modules)]
        under30 = (tier["days_since_last_lesson"] < 30).sum()
        over30 = (tier["days_since_last_lesson"] >= 30).sum()
        print(f"\n-- {label} --")
        print(f"  n={len(tier):,}  |  <30d: {under30:,}  |  >=30d: {over30:,}")

    print()
    print("=" * 70)
    print("FOR CONTEXT: not_started status is a different problem (activation, not resumption)")
    print("=" * 70)
    not_started = t[t["status"] == "not_started"]
    print(f"not_started: {len(not_started):,} ({100 * len(not_started) / len(t):.1f}% of all students) "
          f"-- never completed lesson 1 at all, out of scope for this drill-down")

    print()
    print("=" * 70)
    print("'CLOSE TO CONVERTING': lesson-proximity tiers x behavioral signal, all stopped statuses")
    print("=" * 70)
    print("Signal = study_hall > 0, OR coach_calls >= 2, OR met/exceeded own week-1 pace target.")
    print("CAVEAT: study_hall/coach_calls are cumulative counts, so students further along have had")
    print("more chances to accumulate them (same tenure confound as I-017) -- this inflates P1's rate")
    print("relative to P2/P3. Use for within-tier prioritization, not to compare tiers to each other.")
    print()
    stopped = t[~t["status"].isin(["permit_passed", "permit_failed", "withdrawn"])]
    started = stopped[stopped["lessons_done_count"] >= 1].copy()
    started["high_signal"] = (
        (started["study_hall_sessions_attended"] > 0)
        | (started["coach_calls_completed"] >= 2)
        | (started["lessons_first_7_days"] >= started["plan_lessons_per_week"].fillna(999))
    )
    for label, modules in PRIORITY_TIERS.items():
        tier = started[started["stopped_module"].isin(modules)]
        hs = int(tier["high_signal"].sum())
        print(f"  {label}: n={len(tier):,}  high_signal={hs:,} ({100 * hs / len(tier):.1f}%)")


if __name__ == "__main__":
    main()
