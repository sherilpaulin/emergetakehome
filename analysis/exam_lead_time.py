"""Phase 10 (drill-down): does exam-scheduling lead time (days from
Course Complete to the exam date) predict passing, across everyone who
actually took the exam -- not just the permit_failed group already
checked in I-020. Read-only. Rerun any time with:

    python3 analysis/exam_lead_time.py
"""

import os

import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "clean")
BINS = [0, 7, 14, 21, 30, 45, 60, 1000]
BIN_LABELS = ["0-7d", "7-14d", "14-21d", "21-30d", "30-45d", "45-60d", "60d+"]


def load():
    return pd.read_csv(
        os.path.join(CLEAN_DIR, "student_table.csv"),
        parse_dates=["course_completed_at", "permit_exam_date"],
    )


def main():
    t = load()
    took_exam = t[t["permit_result"].isin(["passed", "failed"])].copy()
    took_exam["lead_time_days"] = (
        took_exam["permit_exam_date"] - took_exam["course_completed_at"]
    ).dt.total_seconds() / 86400

    print(f"Took exam: n={len(took_exam):,} "
          f"(passed={int((took_exam['permit_result'] == 'passed').sum())}, "
          f"failed={int((took_exam['permit_result'] == 'failed').sum())})")
    print()

    print("Lead time by result:")
    for label in ("passed", "failed"):
        grp = took_exam[took_exam["permit_result"] == label]
        lt = grp["lead_time_days"]
        print(f"  {label}: n={len(grp):,} mean={lt.mean():.1f}d median={lt.median():.1f}d "
              f"min={lt.min():.1f}d max={lt.max():.1f}d")

    print()
    print("Pass rate by lead-time bucket:")
    took_exam["bucket"] = pd.cut(took_exam["lead_time_days"], bins=BINS, labels=BIN_LABELS, right=False)
    for b in BIN_LABELS:
        grp = took_exam[took_exam["bucket"] == b]
        if len(grp):
            rate = 100 * (grp["permit_result"] == "passed").mean()
            print(f"  {b}: n={len(grp):,}  pass_rate={rate:.1f}%")


if __name__ == "__main__":
    main()
