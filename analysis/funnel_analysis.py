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


def step_duration_stats(series):
    s = series.dropna()
    return {
        "n": len(s),
        "mean": s.mean(),
        "median": s.median(),
        "min": s.min(),
        "max": s.max(),
        "p90": s.quantile(0.9),
        "p95": s.quantile(0.95),
    }


def print_step_duration_stats(label, stats):
    print(f"-- {label} (n={stats['n']:,}) --")
    print(f"  mean:   {stats['mean']:.1f} days")
    print(f"  median: {stats['median']:.1f} days")
    print(f"  range:  {stats['min']:.1f} to {stats['max']:.1f} days")
    print(f"  p90:    {stats['p90']:.1f} days")
    print(f"  p95:    {stats['p95']:.1f} days")


def funnel_step_durations(t):
    """Per-step elapsed time (not cumulative from signup) for the 3
    transitions: CA->FV, FV->CC, CC->Permit. Only among students who
    actually completed that step (dropna handles the rest)."""
    fv = t[t["first_video_clean"]]
    cc = t[t["course_complete_clean"]]
    passed = t[t["permit_result"] == "passed"].copy()
    passed["permit_exam_date"] = pd.to_datetime(passed["permit_exam_date"])
    passed["course_completed_at"] = pd.to_datetime(passed["course_completed_at"])
    cc_to_permit = (passed["permit_exam_date"] - passed["course_completed_at"]).dt.total_seconds() / 86400

    return {
        "CA_to_FV": step_duration_stats(fv["signup_to_first_video_days"]),
        "FV_to_CC": step_duration_stats(cc["first_video_to_course_complete_days"]),
        "CC_to_Permit": step_duration_stats(cc_to_permit),
    }


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


def funnel_with_recency_cutoff(df, cutoff_days):
    """Step-to-step funnel where each step's denominator is restricted to
    students who signed up at least that step's cutoff (days before the
    snapshot) -- old enough to have had a fair shot at reaching it, per
    the p90 signup-to-stage times. Numerator/denominator both come from
    that restricted, eligible population -- never the full CA."""
    days_since_signup = (SNAPSHOT - df["signup_at"]).dt.total_seconds() / 86400

    fv_eligible = df[days_since_signup >= cutoff_days["fv"]]
    cc_eligible = df[(days_since_signup >= cutoff_days["cc"]) & df["first_video_clean"]]
    permit_eligible = df[(days_since_signup >= cutoff_days["permit"]) & df["course_complete_clean"]]

    return {
        "CA_total": len(df),
        "FV_eligible": len(fv_eligible),
        "FV_excluded_too_new": len(df) - len(fv_eligible),
        "FV": int(fv_eligible["first_video_clean"].sum()),
        "FV_step_pct": 100 * fv_eligible["first_video_clean"].sum() / len(fv_eligible) if len(fv_eligible) else None,
        "CC_eligible": len(cc_eligible),
        "CC_excluded_too_new": int(df["first_video_clean"].sum()) - len(cc_eligible),
        "CC": int(cc_eligible["course_complete_clean"].sum()),
        "CC_step_pct": 100 * cc_eligible["course_complete_clean"].sum() / len(cc_eligible) if len(cc_eligible) else None,
        "Permit_eligible": len(permit_eligible),
        "Permit_excluded_too_new": int(df["course_complete_clean"].sum()) - len(permit_eligible),
        "Permit": int((permit_eligible["permit_result"] == "passed").sum()),
        "Permit_step_pct": 100 * (permit_eligible["permit_result"] == "passed").sum() / len(permit_eligible)
        if len(permit_eligible) else None,
    }


def print_adjusted_funnel(label, f):
    print(f"-- {label} --")
    print(f"  FV:     {f['FV']:,} of {f['FV_eligible']:,} eligible  ({f['FV_step_pct']:.1f}%)  "
          f"-- {f['FV_excluded_too_new']:,} excluded as too new")
    print(f"  CC:     {f['CC']:,} of {f['CC_eligible']:,} eligible  ({f['CC_step_pct']:.1f}%)  "
          f"-- {f['CC_excluded_too_new']:,} excluded as too new")
    print(f"  Permit: {f['Permit']:,} of {f['Permit_eligible']:,} eligible  ({f['Permit_step_pct']:.1f}%)  "
          f"-- {f['Permit_excluded_too_new']:,} excluded as too new")


OFFICIAL_CUTOFF_DAYS = {"fv": 7, "cc": 55, "permit": 78}  # p90 signup-to-stage, locked in Phase 9


def end_to_end_permit_rate(df, cutoff_days=OFFICIAL_CUTOFF_DAYS["permit"]):
    """True signup-to-permit conversion, not step-to-step: of everyone
    who signed up long enough ago (78+ days, p90) to plausibly have
    reached Permit by now -- regardless of current progress -- how many
    actually passed. Denominator is the full eligible CA population,
    not just those who reached Course Complete."""
    days_since_signup = (SNAPSHOT - df["signup_at"]).dt.total_seconds() / 86400
    eligible = df[days_since_signup >= cutoff_days]
    passed = int((eligible["permit_result"] == "passed").sum())
    return {"eligible": len(eligible), "passed": passed,
            "rate_pct": 100 * passed / len(eligible) if len(eligible) else None}


def city_composition_decomposition(t, city, cutoff_days=OFFICIAL_CUTOFF_DAYS["permit"]):
    """How much of a city's end-to-end Permit rate gap is explained by
    its referral-source mix, vs. something city-specific on top?
    Compares the city's actual rate to a composition-adjusted expected
    rate (the city's referral-source mix, applied to each source's
    NATIONAL rate)."""
    city_df = t[t["city"] == city]
    actual = end_to_end_permit_rate(city_df, cutoff_days)

    print(f"{city} actual end-to-end: {actual['passed']} of {actual['eligible']} eligible "
          f"= {actual['rate_pct']:.1f}%")
    print()
    print(f"By referral source (national rate vs. {city}-only, small-n caveat applies):")
    expected = 0.0
    for source in sorted(t["referral_source"].unique()):
        national = end_to_end_permit_rate(t[t["referral_source"] == source], cutoff_days)
        city_source = city_df[city_df["referral_source"] == source]
        city_rate = end_to_end_permit_rate(city_source, cutoff_days)
        share = len(city_source) / len(city_df)
        expected += share * national["rate_pct"]
        city_rate_str = f"{city_rate['rate_pct']:.1f}%" if city_rate["rate_pct"] is not None else "n/a"
        print(f"  {source}: national={national['rate_pct']:.1f}% ({national['passed']}/{national['eligible']})  "
              f"{city}-only={city_rate_str} ({city_rate['passed']}/{city_rate['eligible']})  "
              f"{city} share of city population={100 * share:.1f}%")

    print()
    print(f"Composition-adjusted expected {city} rate (if {city} had each source's NATIONAL rate): "
          f"{expected:.1f}%")
    print(f"{city} actual rate: {actual['rate_pct']:.1f}%")
    print(f"Gap not explained by referral-source mix: {expected - actual['rate_pct']:.1f} points")


def main():
    t = load()

    print("=" * 70)
    print(f"OFFICIAL FUNNEL -- p90 recency-adjusted (cutoffs: {OFFICIAL_CUTOFF_DAYS})")
    print("Locked in as the funnel to use for reporting rates going forward.")
    print("=" * 70)
    print_adjusted_funnel("Overall", funnel_with_recency_cutoff(t, OFFICIAL_CUTOFF_DAYS))
    print()
    for city, g in t.groupby("city"):
        print_adjusted_funnel(city, funnel_with_recency_cutoff(g, OFFICIAL_CUTOFF_DAYS))
        print()

    print("=" * 70)
    print("BY REFERRAL SOURCE (same p90-adjusted methodology)")
    print("=" * 70)
    for source, g in t.groupby("referral_source"):
        print_adjusted_funnel(source, funnel_with_recency_cutoff(g, OFFICIAL_CUTOFF_DAYS))
        e2e = end_to_end_permit_rate(g)
        print(f"  End-to-end CA->Permit: {e2e['passed']:,} of {e2e['eligible']:,} eligible "
              f"(signed up 78+ days ago) = {e2e['rate_pct']:.1f}%")
        print()

    print("=" * 70)
    print("FOR REFERENCE: raw funnel, no recency adjustment (understates CC/Permit)")
    print("=" * 70)
    print_funnel("Overall", funnel(t))
    print()
    for city, g in t.groupby("city"):
        print_funnel(city, funnel(g))
        print()

    print("=" * 70)
    print("TIME-TO-STAGE (90th percentile among students who reached it) -- ")
    print("basis for the official cutoffs above")
    print("=" * 70)
    p90 = time_to_stage_percentiles(t)
    for k, v in p90.items():
        print(f"  {k}: {v:.1f} days")

    print()
    days_since_signup = (SNAPSHOT - t["signup_at"]).dt.total_seconds() / 86400
    for window in (7, 14, 30, 60, 90):
        print(f"  signed up within last {window} days: {(days_since_signup <= window).sum():,}")

    print()
    print("=" * 70)
    print("STEP DURATIONS (elapsed time for each transition, among those who completed it)")
    print("=" * 70)
    for step, stats in funnel_step_durations(t).items():
        print_step_duration_stats(step, stats)
        print()

    print("=" * 70)
    print("BOSTON: how much of the gap is referral-source composition vs. Boston-specific?")
    print("=" * 70)
    city_composition_decomposition(t, "Boston")


if __name__ == "__main__":
    main()
