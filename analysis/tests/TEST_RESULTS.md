# Test Results: test_clean_tables.py

Run: `pytest analysis/tests/test_clean_tables.py -v` against `analysis/clean/student_table.csv` (3,000 rows) and `lesson_table.csv` (20,383 rows).

## Summary

| Passed | Failed | Flagged |
|---|---|---|
| 22 | 0 | 0 |

All 22 tests passed on the first run. No failures to walk through.

## Outlier checks (flag-only, never fail)

- `test_flag_long_breaks` (threshold: 90 days) -- 0 students flagged. Actual max `longest_break_days` in the data is 23.9 days, well under threshold. 1,715 of 3,000 students have a non-null value (need 2+ lessons to have a break to measure).
- `test_flag_high_rewatch_ratio` (threshold: 5x) -- 0 students flagged. Actual max `rewatch_ratio` in the data is 1.5x. 1,998 of 3,000 students have a non-null value (need 1+ completed lesson).

Both thresholds were picked as a generous safety margin for future data exports, not tuned to this dataset -- confirmed with real non-null counts above that this is "no outliers found," not a silently-empty check.
