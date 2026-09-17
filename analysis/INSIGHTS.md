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
