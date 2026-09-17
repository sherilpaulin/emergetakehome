# Insights

Running log of findings from the analyses in `analysis/`, in plain language, for use in `COMMUNITY_PLAN.md`. Every number here traces back to a script in `analysis/` -- see "Source." Correlational fields (group chat, study hall, training plan) get flagged as such per CLAUDE.md rule 7; nothing here claims cause without saying so.

## I-001: Overall permit conversion is 9.1%

274 of 3,000 signups hold a permit (raw funnel) -- matches the README's "roughly 1 in 10." **Source:** `analysis/funnel_analysis.py`.

## I-002: Most drop-off is between First Video and Course Complete

Step-to-step rate FV→CC is 34.8% raw / 41.3% p90-adjusted -- the steepest drop in the funnel either way, confirming the README's stated hypothesis with real numbers. **Source:** `analysis/funnel_analysis.py`.

## I-003: The raw funnel understated CC and Permit rates

Counting too-recent signups as failures dragged both rates down: CC moves from 34.8% to 41.3% (+6.5 pts) and Permit from 39.4% to 43.8% (+4.4 pts) once each step's denominator is restricted to students old enough (p90 signup-to-stage: 7/55/78 days) to have had a fair shot. The p90-adjusted funnel is now the official one (see `analysis/DATA_NOTES.md` Assumptions, `ai_usage/STEERING_LOG.md` S-010). **Source:** `analysis/funnel_analysis.py`.

## I-004: Boston lags at every funnel step

Boston's FV/CC/Permit rates (57.9% / 36.8% / 31.6%, p90-adjusted) trail NYC and Sacramento at every stage, raw or adjusted. Sample is small (n=250) -- worth checking whether this holds up or is noise before treating it as a real market problem. **Source:** `analysis/funnel_analysis.py`.

## I-005: Sacramento converts Course Complete to Permit far better than the other two cities

Sacramento's Permit/CC rate is 50.5% raw / 51.7% adjusted, vs. 31-42% in NYC and Boston. Worth understanding what's different there (DMV access, coaching, cohort scheduling) before assuming it's replicable elsewhere. **Source:** `analysis/funnel_analysis.py`.

## I-006: The biggest single lag is after training ends, not during it

Median time from Course Complete to Permit passed is 17.1 days (p90: 33.6 days) -- students wait over two weeks after finishing the course before sitting the exam. This point in the journey has no training content left to complete, so the lag likely reflects DMV scheduling/access friction rather than a curriculum problem. **Source:** `analysis/funnel_analysis.py` step duration stats.

## I-007: Step durations are all right-skewed

At every step, mean > median (e.g. First Video→Course Complete: mean 36.0 days vs. median 34.3 days; Course Complete→Permit: mean 19.8 vs. median 17.1). A slower minority stretches the average -- median is the more representative "typical" number, mean tells you where the tail pulls it. **Source:** `analysis/funnel_analysis.py` step duration stats.

## I-008: FV→CC drop-off is concentrated in the first 4 lessons (~2 hours of video)

Of 1,500 students who reached First Video and have had 55+ days (p90) to finish, 880 (58.7%) still haven't. Of those 880, 742 (84.3%) stalled within lessons 1-4 (Welcome & How the CLP Works, Inspecting Your Vehicle, Basic Control & Shifting, Seeing/Communicating/Speed Management) -- 8+32+44+41 = 125 minutes of video total. Lesson 3 (Basic Control & Shifting, 44 min) is the single most common stopping point (216 students), more than lesson 1 itself. The problem is front-loaded, not spread across the 21-lesson curriculum. **Source:** `analysis/funnel_dropoff.py`.

## I-009: 853 of the 880 stalled FV→CC students are simply inactive, not withdrawn

Only 18 formally withdrew and 9 are still `in_progress`. The other 853 are `inactive` -- they haven't quit on paper, they've just stopped. That's a re-engagement opportunity, not a lost cohort. **Source:** `analysis/funnel_dropoff.py`.

## I-010: The CC→Permit gap is an access/follow-through problem, not exam failure

Of 537 course-completers who've had 78+ days (p90) to sit the exam, 302 (56.2%) haven't passed. Of those, 257 (85.1%) never even scheduled an exam; only 42 (13.9%) took it and failed; 3 are pending. **Correlational flag (CLAUDE.md rule 7):** of the 257 who never scheduled, 170 (66%) either said "no"/"unsure" on `plan_has_transport_to_dmv` or never filled out a plan at all -- self-reported and self-selected, not proof of cause. 87 said "yes" to transport and still never scheduled, so transport access explains at most part of the gap. **Source:** `analysis/funnel_dropoff.py`.

## I-011: Lesson 3 isn't uniquely hard -- it's just where drop-off concentrates, and group chat is the one real gap

Of the 216 students who stalled right after lesson 3 (Basic Control & Shifting, 44 min), quiz scores (79.1 vs 79.8 avg), minutes watched (50.4 vs 49.4 avg), and rewatch ratio (1.15x vs 1.12x) all match students who continued past it -- the content isn't the barrier. Demographics (city, age band, device, referral source) also match the overall population within 1-2 points. The one real gap: only 22.7% of stalled-at-3 students joined the group chat, vs. 34.2% overall (11.5 points). **Correlational flag (CLAUDE.md rule 7):** group chat is self-selected; this doesn't show joining would have kept them going. Median time since their last lesson is 118.9 days -- long dormant, not a short pause. **Source:** `analysis/funnel_dropoff.py`.

## I-012: There's a hard 24-day cliff on returning after a break -- 971 students are past it

Across 18,385 lesson-to-lesson gaps that ended in a return, the longest one was 23.9 days -- 0 of 18,385 took 30+ days. That's a near-total wall, not a gradual decay: median time between lessons is 1.1 days, and 95% of returns happen within 6 days. Of the 1,302 students currently mid-course and not finished, 971 (74.6%) have already been silent 30+ days -- past the point anyone in this dataset has ever come back from. The other 331 are still within a plausible return window and shouldn't be written off yet. This sharpens I-009's "853 inactive, not withdrawn" figure: many of those inactive students are actually in the confirmed-unlikely-to-return group, not merely paused. **Source:** `analysis/lesson_gap_return.py`.

## I-013: `inactive` is the biggest actionable status, and almost none of it will resolve on its own

`inactive` is 1,009 of 3,000 students (33.6%) -- bigger than `not_started` (968) and bigger than every completed/permit status combined. Of those 1,009, 948 (94%) are already past the I-012 30-day return cliff -- this status is an outreach list, not a wait-and-see list. Segmented by how close they are to finishing (module they stopped in): **P1** (Air Brakes/Combination Vehicles/Practice Tests, closest to done) = 61 students, 60 of them past the cliff; **P2** (General Knowledge, mid-course) = 710 students, 665 past the cliff; **P3** (Orientation only, just lesson 1) = 238 students, 223 past the cliff. Real tradeoff, not a clear winner: P1 needs the least remaining work per conversion but is a small pool; P2 is 12x bigger but each conversion needs far more re-engagement. `not_started` (968, 32.3%) is a separate activation problem, not a resumption one -- flagged, not drilled into here. **Source:** `analysis/status_prioritization.py`.

## I-014: Coach calls, study hall, group chat, and early momentum all separate permit-passed students from everyone else

Comparing `permit_passed` (274) against every other status except the two true endpoints `permit_failed`/`withdrawn` (115 excluded, per the user's definition) vs. everyone still short of a permit (2,611): coach calls (mean 1.80 vs 0.73, **median 2.0 vs 0.0** -- over half the stopped group never had a single call), study hall sessions (mean 1.14 vs 0.41, ~2.8x), joined group chat (50.7% vs 32.5%, 18.2 pts), has a training plan (76.6% vs 61.0%, 15.6 pts), and lessons completed in the first 7 days (mean 2.81 vs 1.35, ~2x). **Correlational flag (CLAUDE.md rule 7):** all five are things students choose or opt into -- this shows association, not that assigning a coach call would cause a pass. **Update: the coach-calls and study-hall gaps here don't hold up to a tenure-adjustment test -- see I-017.** **Source:** `analysis/finish_vs_stop_comparison.py`.

## I-015: Quiz score, chosen pace, activation speed, and demographics barely differ between passed and stopped students

Avg quiz score (79.45 vs 79.47), signup-to-first-video speed (2.35 vs 2.30 days), rewatch ratio (1.13 vs 1.12), and chosen pace (5.72 vs 5.52 lessons/week) are all within noise. Device, age band, and language are within 1-4 points. Ability, chosen pace, and how fast someone starts don't predict passing -- this reinforces I-011 at the full-population level: the differentiator is support-seeking, not aptitude. **Source:** `analysis/finish_vs_stop_comparison.py`.

## I-016: Methodology note -- `engagement_7d_minutes`/`engagement_3d_minutes` look backwards for this comparison, and that's expected

Permit-passed students show almost zero recent engagement (0.07/0.01 min) vs. the stopped group (6.43/2.99 min) -- this is NOT "finishers are less engaged." These fields measure activity in the days right before the snapshot; passed students are done and have no reason to keep opening the app, while the stopped group is full of people still actively using it right now. Don't use these two fields for a finished-vs-stopped comparison -- they're measuring "still logging in," not engagement quality. **Source:** `analysis/finish_vs_stop_comparison.py`.

## I-017: Tenure explains most, but not all, of the coach-calls/study-hall gap in I-014

Coach calls and study hall sessions are cumulative counts, so anyone who stayed in the program longer has more chances to rack them up regardless of whether either one helps. Passed students have been in the program 127.3 days on average vs. 99.6 for the full stopped population (same definition as I-014: every status except `permit_passed`/`permit_failed`/`withdrawn`, `not_started` included) -- 27.7 days longer. Correcting for this with a rate-per-month-in-program: passed students average 0.488 coach calls/month (median 0.400) vs. stopped students' 0.427 (median **0.000**); study hall 0.312/month (mean) vs. 0.264. **The raw 2.5x/2.8x gaps shrink to roughly 1.1-1.2x once tenure-adjusted -- most of the raw gap was an opportunity artifact, not a support effect, but a real gap remains, especially at the median** (over half the stopped group has zero coach calls regardless of tenure). *An earlier version of this analysis wrongly excluded `not_started` students from "stopped" when computing this, which incorrectly suggested the gap fully reversed -- corrected after review; `not_started` belongs in "stopped" per the same definition used everywhere else in this comparison.*

`joined_group_chat` is unaffected by this adjustment either way: it's a one-time join decision, not a cumulative count, so tenure can't mechanically inflate it (50.7% vs 32.5%). Still correlational (self-selected motivation could drive both joining and finishing) -- but the cleanest of the three support signals, unlike coach calls/study hall which are entangled with time-in-program. **Source:** `analysis/finish_vs_stop_comparison.py`.

## I-021: `paid_social` converts end-to-end at ~60% the rate of every other referral source

True signup-to-permit conversion (p90-eligible, 78+ days since signup): `workforce_center` 15.4% (35/227), `reentry_org` 13.4% (67/500), `parole_probation_officer` 13.3% (44/330), `friend_family` 13.2% (41/311), `paid_social` **9.3% (48/515)**. `paid_social` is the largest channel by eligible volume and the weakest by rate -- real lost volume, not noise. Confirms and quantifies I-018/I-019 (paid_social overrepresented among `not_started` and `withdrawn`).

Step-by-step, sources fail at different points, not just one uniformly "bad" channel: `paid_social` is weakest at FV/CA (55.7% vs. reentry_org's 74.1%) and CC/FV (33.4% vs. reentry_org's 46.0%) -- a lead-quality problem from signup onward. `reentry_org`, despite being best at both those steps, is worst at Permit/CC (39.0%) -- these students finish training but stall right before the exam. `workforce_center` is middling early but best at Permit/CC (54.7%). **Source:** `analysis/funnel_analysis.py`.

## I-018: `not_started` students abandon within about a day of signing up, and `paid_social` leads are overrepresented

Of 968 `not_started` students (32.3% of all), the median gap between signup and their last app activity is 1.0 day, and 938 of 968 (96.9%) show zero app activity in the week before the snapshot -- this is an immediate-abandonment pattern, not a slow start. `paid_social` referrals are overrepresented (36.6% vs 27.9% overall) and `reentry_org` underrepresented (20.7% vs 25.9%) relative to the full population. **Correlational flag (CLAUDE.md rule 7):** referral source isn't chosen mid-journey, but the acquisition channel itself may bring in lower-intent leads. **Source:** `analysis/status_deep_dive.py`.

## I-019: `withdrawn` students quit early and decisively, and Boston is 2.3x overrepresented

Of 63 withdrawn students (2.1%), median `lessons_completed` at withdrawal is 0, and 75% had completed 2 or fewer lessons -- these are early, deliberate exits, not burnout after real progress. Boston makes up 19.0% of withdrawals vs. 8.3% of the overall population (2.3x) -- combined with I-004 (Boston lagging every funnel step) and I-005 (Sacramento's strong Permit conversion), this strengthens the case for a real city-level difference, not just small-sample noise. Same `paid_social`-overrepresented, low-group-chat pattern as I-018 (22.2% joined group chat vs. 34.2% overall). **Source:** `analysis/status_deep_dive.py`.

## I-020: `permit_failed` students test the same as everyone else, and most never use their second attempt

Of 52 permit-failed students (1.7%), avg quiz score (79.5) exactly matches the overall population (79.5), and their course-complete-to-exam timing (median 19.1 days) is close to I-006's overall median (17.1 days) -- not underprepared, not rushed. The concrete opportunity: 41 of 52 (78.8%) failed once and never attempted the retry the program allows (max observed `permit_attempts` is 2). This is a retry-nudge opportunity, not a curriculum fix. The other 11 already used both attempts. Transport access is mixed (22 yes / 15 no-or-unsure / 12 unknown) -- a weaker signal than I-010's "never scheduled" group. **Source:** `analysis/status_deep_dive.py`.
