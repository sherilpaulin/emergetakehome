"""Phase 10 (drill-down): behavior over content -- does plan adherence,
per-lesson difficulty, or a group-chat/study-hall interaction predict
outcomes better than what's already been checked?

Uses the same p90 end-to-end eligibility (78+ days since signup) as
funnel_analysis.py's end_to_end_permit_rate() for every comparison
here, so results are apples-to-apples with the rest of the funnel
work. Read-only. Rerun any time with:

    python3 analysis/behavior_analysis.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
SNAPSHOT = pd.Timestamp("2026-09-15 06:00:00")
PERMIT_CUTOFF_DAYS = 78  # p90 signup-to-Permit, same as funnel_analysis.py


def load():
    students = pd.read_csv(os.path.join(CLEAN_DIR, "student_table.csv"), parse_dates=["signup_at"])
    lessons = pd.read_csv(os.path.join(CLEAN_DIR, "lesson_table.csv"))
    return students, lessons


def e2e(df, cutoff_days=PERMIT_CUTOFF_DAYS):
    days_since_signup = (SNAPSHOT - df["signup_at"]).dt.total_seconds() / 86400
    eligible = df[days_since_signup >= cutoff_days]
    passed = int((eligible["permit_result"] == "passed").sum())
    n = len(eligible)
    rate = 100 * passed / n if n else None
    return n, passed, rate


def print_rate(label, n_total, df):
    n, p, r = e2e(df)
    r_str = f"{r:.1f}%" if r is not None else "n/a"
    print(f"  {label}: n_total={n_total:,}  eligible={n:,}  passed={p:,}  rate={r_str}")


def plan_adherence(t):
    """Does actually hitting your OWN chosen week-1 pace target predict
    outcomes better than just having a plan at all? lessons_first_7_days
    vs. plan_lessons_per_week -- both already in student_table.csv."""
    no_plan = t[t["has_training_plan"] == "no"]
    has_plan = t[t["has_training_plan"] == "yes"]
    met = has_plan[has_plan["lessons_first_7_days"] >= has_plan["plan_lessons_per_week"]]
    missed = has_plan[has_plan["lessons_first_7_days"] < has_plan["plan_lessons_per_week"]]

    print_rate("No plan", len(no_plan), no_plan)
    print_rate("Has plan, missed own week-1 target", len(missed), missed)
    print_rate("Has plan, met/exceeded own week-1 target", len(met), met)


def quiz_and_rewatch_curve(lessons):
    """Full per-lesson quiz score / rewatch curve across all 21 lessons,
    not just lesson 3 -- is any OTHER lesson quietly hard?"""
    curve = lessons.groupby("lesson_number").agg(
        avg_quiz=("quiz_score_pct", "mean"),
        avg_minutes_watched=("minutes_watched", "mean"),
        video_minutes=("video_minutes", "first"),
        n=("user_id", "count"),
    )
    curve["rewatch_ratio"] = curve["avg_minutes_watched"] / curve["video_minutes"]
    print(curve.round(2).to_string())
    print()
    print(f"Quiz score range across all 21 lessons: {curve['avg_quiz'].min():.2f} to "
          f"{curve['avg_quiz'].max():.2f} ({curve['avg_quiz'].max() - curve['avg_quiz'].min():.2f} pts)")
    print(f"Rewatch ratio range: {curve['rewatch_ratio'].min():.2f} to {curve['rewatch_ratio'].max():.2f}")


def group_chat_study_hall_interaction(t):
    """Does doing both beat either alone? Note: the data dictionary says
    study hall is announced only in group chat, so 'study hall only'
    (attended without joining chat) should be near-zero -- confirms or
    refutes that with real data."""
    chat_yes = t["joined_group_chat"] == "yes"
    hall_yes = t["study_hall_sessions_attended"] > 0

    groups = {
        "Both (chat + study hall)": t[chat_yes & hall_yes],
        "Chat only (no study hall)": t[chat_yes & ~hall_yes],
        "Study hall only (no chat)": t[~chat_yes & hall_yes],
        "Neither": t[~chat_yes & ~hall_yes],
    }
    for label, grp in groups.items():
        print_rate(label, len(grp), grp)


def main():
    t, lessons = load()

    print("=" * 70)
    print("PLAN ADHERENCE: does hitting your own week-1 target matter more than just having a plan?")
    print("=" * 70)
    plan_adherence(t)

    print()
    print("=" * 70)
    print("QUIZ SCORE / REWATCH CURVE ACROSS ALL 21 LESSONS")
    print("=" * 70)
    quiz_and_rewatch_curve(lessons)

    print()
    print("=" * 70)
    print("GROUP CHAT x STUDY HALL INTERACTION")
    print("=" * 70)
    group_chat_study_hall_interaction(t)


if __name__ == "__main__":
    main()
