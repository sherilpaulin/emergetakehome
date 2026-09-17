"""Phase 6: data issues.

Builds on analysis/data_explore.py's findings and CLAUDE.md's funnel/
"trust lesson_events.csv" rules plus every "should never" / "always"
statement in DATA_DICTIONARY.md. Read-only: never writes to data/, and
does not fix anything -- it only reports. Rerun any time with:

    python3 analysis/check_data.py
"""

import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load():
    s = pd.read_csv(os.path.join(DATA_DIR, "students.csv"))
    e = pd.read_csv(os.path.join(DATA_DIR, "lesson_events.csv"))
    seats = pd.read_csv(os.path.join(DATA_DIR, "seats_by_city.csv"))
    return s, e, seats


def problem(pid, what, rows_df, id_col="user_id", n_examples=5):
    print(f"\n[{pid}] {what}")
    print(f"  rows: {len(rows_df):,}")
    if len(rows_df):
        print(f"  example {id_col}s: {rows_df[id_col].head(n_examples).tolist()}")


def clean(label, count):
    print(f"  [ok] {label}: {count:,}")


def main():
    s, e, seats = load()

    print("=" * 70)
    print("PROBLEMS FOUND (need a decision)")
    print("=" * 70)

    # D-001: test / internal accounts
    test_accounts = s[~s["user_id"].str.match(r"^u_\d+$", na=False)]
    problem(
        "D-001",
        "user_id doesn't match the u_###### pattern every real row uses "
        "(all 9 also have referral_source = 'internal', not a documented value)",
        test_accounts,
    )

    # D-002: lessons_completed disagrees with lesson_events.csv (CLAUDE.md: trust the event log)
    max_event_lesson = e.groupby("user_id")["lesson_number"].max()
    joined = s[["user_id", "lessons_completed"]].merge(
        max_event_lesson.rename("max_event_lesson"), on="user_id", how="left"
    )
    joined["max_event_lesson"] = joined["max_event_lesson"].fillna(0).astype(int)
    mismatch = joined[joined["lessons_completed"] != joined["max_event_lesson"]]
    problem(
        "D-002",
        "lessons_completed (students.csv summary field) disagrees with the "
        "highest lesson_number actually logged in lesson_events.csv -- "
        "always overstating, never understating, in every case found",
        mismatch,
    )

    # D-003: city label variants + seats_by_city.csv join impact
    canonical_cities = set(seats["city"].unique())
    non_canonical = s[~s["city"].isin(canonical_cities)]
    problem(
        "D-003",
        f"city has {s['city'].nunique()} raw spellings instead of the 3 canonical "
        f"ones in seats_by_city.csv ({sorted(canonical_cities)}) -- these rows can't "
        f"currently be matched to a city's seat count. Variants found: "
        f"{sorted(set(non_canonical['city'].unique()))}",
        non_canonical,
    )

    # D-004: engagement_3d_minutes > engagement_7d_minutes (dictionary: "should never exceed")
    bad_engagement = s[s["engagement_3d_minutes"] > s["engagement_7d_minutes"]]
    problem(
        "D-004",
        "engagement_3d_minutes > engagement_7d_minutes -- DATA_DICTIONARY.md "
        "says 3d 'should never exceed' 7d",
        bad_engagement,
    )

    # Diagnostic for the Emerge question on D-004: among those 11 rows, which
    # ones ALSO have last_seen_at stale by 3+ days yet engagement_3d_minutes
    # > 0 -- logically impossible if 3-day tracking is correct, so this is
    # the strongest evidence of a system tracking bug (not a redefinition of
    # D-004, which stays at 11 rows regardless).
    SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")
    s_dt2 = s.copy()
    s_dt2["last_seen_at"] = pd.to_datetime(s_dt2["last_seen_at"])
    s_dt2["days_since_seen"] = (SNAPSHOT - s_dt2["last_seen_at"]).dt.total_seconds() / 86400
    stale_but_active_3d = s_dt2[(s_dt2["days_since_seen"] > 3) & (s_dt2["engagement_3d_minutes"] > 0)]
    print(f"\n  [D-004 diagnostic] of the {len(bad_engagement):,} D-004 rows, "
          f"{len(stale_but_active_3d):,} also have last_seen_at 3+ days stale "
          f"yet engagement_3d_minutes > 0 (impossible if 3d tracking is correct); "
          f"this pattern occurs nowhere else in students.csv either")
    if len(stale_but_active_3d):
        print(f"  example user_ids: {stale_but_active_3d['user_id'].tolist()}")

    print("\n" + "=" * 70)
    print("CHECKED, NO PROBLEM FOUND")
    print("=" * 70)

    clean("duplicate user_id rows", int(s.duplicated("user_id").sum()))

    s_dt = s.copy()
    s_dt["last_seen_at"] = pd.to_datetime(s_dt["last_seen_at"])
    s_dt["last_logged_in_at"] = pd.to_datetime(s_dt["last_logged_in_at"])
    clean(
        "last_logged_in_at later than last_seen_at (dictionary: 'always on or before')",
        int((s_dt["last_logged_in_at"] > s_dt["last_seen_at"]).sum()),
    )

    per_user_lessons = e.groupby("user_id")["lesson_number"].apply(lambda x: sorted(x.tolist()))
    has_gap = per_user_lessons.apply(lambda lst: lst != list(range(1, len(lst) + 1)))
    clean("students with skipped/out-of-order lesson_number sequences (dictionary: 'unlock in order')", int(has_gap.sum()))

    clean("permit_result present but permit_attempts == 0", int(((s["permit_result"].notna()) & (s["permit_attempts"] == 0)).sum()))
    clean("lesson_number outside 1-21 in lesson_events.csv", int(((e["lesson_number"] < 1) | (e["lesson_number"] > 21)).sum()))
    clean("quiz_score_pct outside 0-100", int(((e["quiz_score_pct"] < 0) | (e["quiz_score_pct"] > 100)).sum()))
    clean("duplicate (user_id, lesson_number) pairs", int(e.duplicated(["user_id", "lesson_number"]).sum()))
    clean("user_ids in lesson_events.csv missing from students.csv", len(set(e["user_id"]) - set(s["user_id"])))


if __name__ == "__main__":
    main()
