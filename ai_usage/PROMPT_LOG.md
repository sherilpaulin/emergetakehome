# Prompt Log

Every prompt sent in this session, logged automatically by `.claude/hooks/prompt-log.py` (a UserPromptSubmit hook). Numbered P-001, P-002, ... in send order. Phase is parsed from a leading `Phase N:` in the prompt text; prompts sent before this hook existed (P-001, P-002) were backfilled by hand in the same format.

## P-001
- **Phase:** Phase 1
- **Time:** (backfilled -- sent before this hook existed, exact send time not logged)
- **Prompt:**
```
Phase 1: Exploration. Read CLAUDE.md, README.md, COMMUNITY_PLAN.md, .gitignore, and data/DATA_DICTIONARY.md. Look at the first few rows of each file in data/. Don't create or change any files yet.  Then tell me in simple words: 1. What this project is asking us to make. 2. The most important rules in CLAUDE.md. 3. What each data file holds and how they connect. 4. Anything in the data dictionary that is confusing or unclear. 5. Anything in .gitignore that would hide files we need to hand in. Then ask me any questions you have.
```

## P-002
- **Phase:** Phase 2
- **Time:** (backfilled -- sent before this hook existed, exact send time not logged)
- **Prompt:**
```
Phase 2: Documentation. I need to keep a record of how I worked with you. Please set up:  1. A hook that saves every prompt I send into ai_usage/PROMPT_LOG.md. Number each one (P-001, P-002...)    and note the phase if my prompt starts with "Phase N:". 2. A file ai_usage/STEERING_LOG.md for the interactive moments like when I correct you, say no to an idea, make a decision, answer your question, or ask you to explain. Each entry should have: a number (S-001...),    the phase, the type, a one-line summary of what you did, what I said, why, and what changed. 3. A skill in .claude/skills/ai-usage-log/ that tells you when and how to add those entries.  Be honest about your own mistakes in these entries. 4. Make the prompt hook also look for words that suggest a correction, pushback, or decision    (like "no", "wrong", "instead", "why did you", "lets go with"). When it finds them, add a reminder for you to check with me to log the moment in the steering log.  Explain your plan first and wait for my OK. After building, test it and show me what the files look like. Then add my Phase 1 and Phase 2 prompts to the prompt log, since they were sent before the hook was created.
```

## P-003
- **Phase:** Phase 3
- **Time:** 2026-09-17 02:27:12
- **Prompt:**
```
Phase 3: Safety. CLAUDE.md says we can't change files in data/, can't send messages, and can't use the internet. 1. Add a hook that blocks any edit to files in data/. When it blocks something, add a note to STEERING_LOG.md. 2. Write a short section to add at the END of CLAUDE.md (under 25 lines). It should say: where each kind of file goes, always use the snapshot time (2026-09-15 6:00 AM ET), never today's date, log data problems in analysis/DATA_NOTES.md and important moments in the steering log, start phase prompts with "Phase N:", log steering moments on your own, without being asked: right after any turn where I correct you, push back, reject or accept an idea, answer your question, or make a decision. If a hook reminder appears, act on it. Be honest about your own mistakes. Add this section to the end of CLAUDE.md, word for word (if it doesn't overlap with existing rules): ## How to respond to me (chat replies) -  1. Lead with the answer in the first line. No intros, no recaps, no "Great question." 2. Be blunt and direct. If something is wrong, weak, or a bad idea, say so plainly and say why. 3. Use short bullets, one idea per bullet, in plain words a 6th grader would understand. 4. Long answers are fine when the content needs it. Cut filler, not substance. 5. No filler phrases ("It's worth noting", "Overall", "In summary") and no soft hedging. 6. Numbers: always show the count behind a percent, e.g. "40% (400 of 1,000)".7.  If you're unsure, say so in one line and say what would settle it. 8. End with at most one question or one next step. Wait for my answer before doing more. 9. Don't repeat what I just said or what's already in a file. Point to the file instead. 10. When you change files, list which files changed and what changed, one line each. 11. Being blunt never means skipping required caveats: still flag self-selected fields and data problems and other requirements in the CLAUDE.md file. Show me the new CLAUDE.md section before adding these updates. Don't change any existing lines.
```

## P-004
- **Phase:** Phase 4
- **Time:** 2026-09-17 02:45:38
- **Prompt:**
```
Phase 4: Data notes. Create analysis/DATA_NOTES.md and a skill in .claude/skills/data-notes/ that explains how to fill it in. The file should have four parts: 1. Problems found: a table with an ID, which file, what's wrong, how many rows, and what we did about it. 2. Row counts: how many rows each file had before and after cleaning. 3. Assumptions: guesses we had to make, and why. 4. Questions for Emerge: things only Gabe can answer, and what we'll assume until we meet. Keep it simple and easy to read. Show me an example entry for each part before creating any new files.
```

## P-005
- **Phase:** not specified
- **Time:** 2026-09-17 02:47:41
- **Prompt:**
```
create the data_notes.md but do not add any entries yet
```

## P-006
- **Phase:** not specified
- **Time:** 2026-09-17 02:48:29
- **Prompt:**
```
yes create the data-notes skill as well
```

## P-007
- **Phase:** Phase 5
- **Time:** 2026-09-17 02:52:36
- **Prompt:**
```
Phase 5: Data exploration. Write analysis/data_explore.py. For each data file, it should show: how many rows, the columns, how many blanks each column has, the different values in text columns, and the smallest and largest dates and numbers, any other unique features. Run it and then tell me in plain words: what looks normal, what looks strange, and what you want to check more closely. Don't fix anything yet or ask me to make decisions yet, as we will do that in the next step.
```

## P-008
- **Phase:** Phase 6
- **Time:** 2026-09-17 02:58:19
- **Prompt:**
```
Phase 6: Data Issues. Using the data dictionary and CLAUDE.md, previous analysis, check the data files for problems. Examples: engagement_3d > engagement_7d, test accounts, misspelled cities, fields that disagree with each other (like lessons_completed vs the lesson events), and anything the dictionary says "should never" happen. Also check seats_by_city.csv matches the cities in students.csv.  Write analysis/check_data.py. Don't fix anything yet. For each problem, show me: what it is, how many rows, a few example user_ids, and 2 options for handling it. Then go through them with me ONE AT A TIME and ask what I want to do, and as we go along, you will be logging these decisions.
```

## P-009
- **Phase:** Phase 7
- **Time:** 2026-09-17 03:16:17
- **Prompt:**
```
Phase 7: Data Cleaning. Write analysis/clean_data.py that applies the choices we made. Save cleaned copies of the four data files in analysis/clean/ (never change or edit data/). Record every problem, choice, and row count in DATA_NOTES.md if not done so already. Run the script and then show me DATA_NOTES.md.
```

## P-010
- **Phase:** not specified
- **Time:** 2026-09-17 03:19:00
- **Prompt:**
```
Show me the exact code and the result for counting test accounts and the removals made, so I can check the number myself.
```

## P-011
- **Phase:** not specified
- **Time:** 2026-09-17 03:20:14
- **Prompt:**
```
Try again
```

## P-012
- **Phase:** not specified
- **Time:** 2026-09-17 03:33:10
- **Prompt:**
```
continuing on the data cleaning phase 7, Now build two tables from the cleaned files. Don't change the original cleaned files. 1. analysis/clean/student_table.csv: one row per student. Start from students and add columns from lesson_events: reached first video, finished course, highest lesson, # lessons done, last lesson date, days since last lesson (use the snapshot time as end time), lessons in the first 7 days, longest break, average quiz score, avg minutes watched, avg minutes expected to be watched based on lessons.csv video_minutes for the lessons they completed so far, and the lesson and module where they stopped, and any other metrics you think i should add. please suggest them before adding. If you have any questions on joins or think there are duplicate values being created, please ask me for path forward before making the student_table. 2. analysis/clean/lesson_table.csv: one row per finished lesson, with the lesson info from lessons.csv added. Then you should check: the student table has exactly one row per student, and its row count matches the cleaned students file. Show me 5 example rows and explain each new column in one line. Any data discrepancies, log it in DATA_NOTES.md.
```

## P-013
- **Phase:** not specified
- **Time:** 2026-09-17 03:46:04
- **Prompt:**
```
as part of data_noted.md, can you create a data dictionary for the newly created cleaned student_table and lesson_table. for any new metrics we define going forward, make sure to track in data_notes
```

## P-014
- **Phase:** Phase 8
- **Time:** 2026-09-17 04:02:14
- **Prompt:**
```
Phase 8: Tests. Write about 20 tests for student_table and lesson_table.
Save them in analysis/tests/test_clean_tables.py. Don't run them yet.

Check these things:
1. Rows: one row per student, no duplicate student-lesson pairs, row counts match DATA_NOTES.md.
2. Values: lessons are 1-21, quiz scores are 0-100, no negative minutes, only allowed cities and statuses.
3. Dates: nothing after the snapshot or before signup, no negative "days since" numbers.
4. Tables match: every student in lesson_table exists in student_table, and lesson counts agree.
5. Edge cases: students with zero lessons, students who finished all 21, withdrawn students, test accounts.
6. Outliers: very long breaks or very high minutes. Note as a flag instead of failing test.

Tests should only read files, never change them. Add a one-line short but descriptive comment to each test detailing the purpose of the test.
Show me the list of tests and wait for my OK.
```

## P-015
- **Phase:** not specified
- **Time:** 2026-09-17 04:06:00
- **Prompt:**
```
Run the 22 tests and tell me:
1. How many passed, failed, and gave flags.
2. For each failure: what went wrong, a few example user ids, and whether it's a data problem or a code bug.

Don't fix anything yet. Go through failures with me one at a time with suggested paths forward.
After I decide, fix code bugs and rerun, or add data problems to DATA_NOTES.md.
Don't change a test just to make it pass.
When done, save a short summary in analysis/tests/TEST_RESULTS.md.
```

## P-016
- **Phase:** Phase 9
- **Time:** 2026-09-17 04:08:07
- **Prompt:**
```
Phase 9: Funnel analysis. Using analysis/clean/student_table.csv and the funnel definitions in CLAUDE.md, show me how many students reach each step: signed up → first video → finished course → passed permit. Show it for all students and for each city and for each step, show the count and the percent.  Note that you expect recent signups haven't had time to finish. Suggest a fair way to handle that, explain it simply, and wait for my OK before using it. Also note that this piece is focused on the funnel analysis and should not go beyond that scope yet
```

## P-017
- **Phase:** not specified
- **Time:** 2026-09-17 04:14:28
- **Prompt:**
```
I agree with having per-step cutoffs. What are the pros / cons of using a generic 7 days vs a calculated cutoff period (based on video_minutes or some other metric)
```

## P-018
- **Phase:** not specified
- **Time:** 2026-09-17 04:16:22
- **Prompt:**
```
what would the funnel look like with p90 calculated cutoffs
```

## P-019
- **Phase:** not specified
- **Time:** 2026-09-17 04:18:45
- **Prompt:**
```
can you provide the mean, median, range, p90, p95 for each funnel step
```

## P-020
- **Phase:** not specified
- **Time:** 2026-09-17 04:25:08
- **Prompt:**
```
pros and cons of using mean or median as cutoff rather than p90
```

## P-021
- **Phase:** not specified
- **Time:** 2026-09-17 04:27:24
- **Prompt:**
```
lets use p90 as the funnel as part of the analysis. please create a new file in analysis where we start to track insights from our various analyses. Then i will note the next analysis to conduct
```

## P-023
- **Phase:** not specified
- **Time:** 2026-09-17 04:31:50
- **Prompt:**
```
ignore the last prompt (phase 10: cutoff points) and remove it from the prompt log. Now we will drill down into the funnel analysis, based on your initial insights, lets drill into steps that are taking longer or where we lose the most students
```

## P-024
- **Phase:** not specified
- **Time:** 2026-09-17 04:36:06
- **Prompt:**
```
lets drill into the lesson three stall point first
```

## P-025
- **Phase:** not specified
- **Time:** 2026-09-17 04:38:45
- **Prompt:**
```
how long do students usually take between lessons, and if a student takes a long break, how likely are they to come back?
```

## P-026
- **Phase:** not specified
- **Time:** 2026-09-17 04:45:46
- **Prompt:**
```
can we look into the "status" of these students. should there be a prioritization for example for the "inactive" students who are so close to finishing?
```

## P-027
- **Phase:** not specified
- **Time:** 2026-09-17 04:49:48
- **Prompt:**
```
lets add to insights for now.  Using student_table.csv, compare students who finished the course with students who stopped. List the fields we could compare (things like training plan, group chat, study hall, coach calls, device, language, age, city, how fast they started, the new metrics like rewatch ratio that was calculated in students_table). For each one, tell me in one line why it might matter and i'll choose which ones to dive deeper on.
```

## P-028
- **Phase:** not specified
- **Time:** 2026-09-17 04:55:49
- **Prompt:**
```
lets define stopped as any step prior to permit received. for this analysis, lets filter out status = permit failed or withdrawn as those are end points. I want to compare permit passed against the other status (minus the two i mentioned)
```

## P-029
- **Phase:** not specified
- **Time:** 2026-09-17 05:00:09
- **Prompt:**
```
Lets look at coach-calls/study-hall/group-chat "support" story. explain why we can't say it causes finishing. What could be another reason for the difference?
```

## P-030
- **Phase:** not specified
- **Time:** 2026-09-17 05:03:32
- **Prompt:**
```
please provide where / how you got the numerators and denominators for the controlled time table
```

## P-031
- **Phase:** not specified
- **Time:** 2026-09-17 05:06:43
- **Prompt:**
```
the exclusions should only be permit_passed, permit_failed, withdrawn; not started stays as part of the "stopped" funnel
```

## P-032
- **Phase:** not specified
- **Time:** 2026-09-17 05:12:08
- **Prompt:**
```
passed means status = permit_passed; stopped means status is either not_started, inactive, course_complete, permit_scheduled, or in_progress; end means status = withdrawn or permit failed;
```

## P-033
- **Phase:** not specified
- **Time:** 2026-09-17 05:15:30
- **Prompt:**
```
lets take a look at withdrawn, permit failed, and not started. any trends to note?
```

## P-034
- **Phase:** not specified
- **Time:** 2026-09-17 05:20:28
- **Prompt:**
```
can you provide a breakdown by referral sources, are some of them not as effective  (maybe in terms of converting from login created to permit passed)
```

## P-035
- **Phase:** not specified
- **Time:** 2026-09-17 05:23:29
- **Prompt:**
```
what are some reasons for the observations in paid_social, reentry_org, and workforce_center
```
