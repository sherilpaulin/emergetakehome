"""Phase 10 (drill-down): testing candidate explanations for I-021's
referral-source funnel differences against available fields.

Not every hypothesis is testable with what's in student_table.csv --
this script only checks the ones that are, and says plainly which
ones aren't. Read-only. Rerun any time with:

    python3 analysis/referral_source_hypotheses.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SOURCES = ["paid_social", "reentry_org", "workforce_center", "parole_probation_officer", "friend_family"]


def load():
    return pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"))


def main():
    t = load()

    print("=" * 70)
    print("has_training_plan by source -- tests 'paid_social = lower initial commitment'")
    print("=" * 70)
    for s in SOURCES:
        g = t[t["referral_source"] == s]
        print(f"  {s}: {100 * (g['has_training_plan'] == 'yes').mean():.1f}%")

    print()
    print("=" * 70)
    print("plan_has_transport_to_dmv by source (among those with a plan) -- ")
    print("tests 'reentry_org has more DMV access barriers'")
    print("=" * 70)
    for s in SOURCES:
        g = t[t["referral_source"] == s]
        g_plan = g[g["has_training_plan"] == "yes"]
        print(f"  {s}: yes={100 * (g_plan['plan_has_transport_to_dmv'] == 'yes').mean():.1f}%  "
              f"no={100 * (g_plan['plan_has_transport_to_dmv'] == 'no').mean():.1f}%  "
              f"unsure={100 * (g_plan['plan_has_transport_to_dmv'] == 'unsure').mean():.1f}%")

    print()
    print("=" * 70)
    print("joined_group_chat by source -- tests 'paid_social = less community engagement'")
    print("=" * 70)
    for s in SOURCES:
        g = t[t["referral_source"] == s]
        print(f"  {s}: {100 * (g['joined_group_chat'] == 'yes').mean():.1f}%")

    print()
    print("=" * 70)
    print("coach_calls_completed among course-completers, by source -- ")
    print("tests 'workforce_center gets more post-training coaching'")
    print("=" * 70)
    cc = t[t["course_complete_clean"]]
    for s in SOURCES:
        g = cc[cc["referral_source"] == s]
        print(f"  {s}: n={len(g):,}  mean={g['coach_calls_completed'].mean():.2f}")


if __name__ == "__main__":
    main()
