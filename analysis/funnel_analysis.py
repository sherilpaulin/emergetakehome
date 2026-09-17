"""Phase 9: funnel analysis.

CA -> First Video -> Course Complete -> Permit passed, overall and by
city, step-to-step (FV/CA, CC/FV, Permit/CC per CLAUDE.md's funnel
definitions -- don't invent new ones). Also reports the observed
90th-percentile time-to-reach each step, used to propose a fair
recency cutoff (not yet applied -- awaiting sign-off). Read-only.
Rerun any time with:

    python3 analysis/funnel_analysis.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")


def load():
    return pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"), parse_dates=["signup_at", "course_completed_at"])


def funnel(df):
    ca = len(df)
    fv = int(df["first_video_clean"].sum())
    cc = int(df["course_complete_clean"].sum())
    permit = int((df["permit_result"] == "passed").sum())
    return {
        "CA": ca,
        "FV": fv,
        "FV_step_pct": 100 * fv / ca if ca else None,
        "CC": cc,
        "CC_step_pct": 100 * cc / fv if fv else None,
        "Permit": permit,
        "Permit_step_pct": 100 * permit / cc if cc else None,
    }


def print_funnel(label, f):
    print(f"-- {label} (CA={f['CA']:,}) --")
    print(f"  CA:     {f['CA']:,}")
    print(f"  FV:     {f['FV']:,}  ({f['FV_step_pct']:.1f}% of CA)")
    print(f"  CC:     {f['CC']:,}  ({f['CC_step_pct']:.1f}% of FV)")
    print(f"  Permit: {f['Permit']:,}  ({f['Permit_step_pct']:.1f}% of CC)")


def time_to_stage_percentiles(t):
    fv = t[t["first_video_clean"]]
    cc = t[t["course_complete_clean"]]
    passed = t[t["permit_result"] == "passed"].copy()
    passed["permit_exam_date"] = pd.to_datetime(passed["permit_exam_date"])

    signup_to_cc = (cc["course_completed_at"] - cc["signup_at"]).dt.total_seconds() / 86400
    signup_to_permit = (passed["permit_exam_date"] - passed["signup_at"]).dt.total_seconds() / 86400

    return {
        "signup_to_first_video_p90": fv["signup_to_first_video_days"].quantile(0.9),
        "signup_to_course_complete_p90": signup_to_cc.quantile(0.9),
        "signup_to_permit_passed_p90": signup_to_permit.quantile(0.9),
    }


def main():
    t = load()

    print("=" * 70)
    print("RAW FUNNEL (all signups, no recency adjustment)")
    print("=" * 70)
    print_funnel("Overall", funnel(t))
    print()
    for city, g in t.groupby("city"):
        print_funnel(city, funnel(g))
        print()

    print("=" * 70)
    print("TIME-TO-STAGE (90th percentile among students who reached it) -- ")
    print("used to propose a fair recency cutoff, not yet applied")
    print("=" * 70)
    p90 = time_to_stage_percentiles(t)
    for k, v in p90.items():
        print(f"  {k}: {v:.1f} days")

    print()
    days_since_signup = (SNAPSHOT - t["signup_at"]).dt.total_seconds() / 86400
    for window in (7, 14, 30, 60, 90):
        print(f"  signed up within last {window} days: {(days_since_signup <= window).sum():,}")


if __name__ == "__main__":
    main()
