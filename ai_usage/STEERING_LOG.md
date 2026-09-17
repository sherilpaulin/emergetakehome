# Steering Log

Interactive moments in this session where the user corrected, pushed back on, made a decision about, answered a question from, or asked Claude to explain something. Curated by hand per `.claude/skills/ai-usage-log/SKILL.md`, in Claude's own words -- including its own mistakes, honestly. Full prompt text lives in `ai_usage/PROMPT_LOG.md` under the referenced `P-###` id; this file doesn't repeat it.

## S-001
- **Phase:** Phase 1
- **Type:** pushback
- **What I did:** After the Phase 1 exploration summary, I asked four clarifying questions via `AskUserQuestion` (how to treat inconsistent `city` labels, how to treat `referral_source = internal` rows, dashboard format, and what to do next) with a recommended option pre-selected on each.
- **What you said (P-001 follow-up):** You dismissed all four with "wait for next instruction" rather than picking any option.
- **Why:** Not stated. Read as: you wanted to redirect the session (to Phase 2 documentation work) before settling those data-cleaning decisions, not as agreement with my recommended defaults.
- **What changed:** I stopped and did not act on any of the four recommended defaults (no city normalization, no exclusion of `internal` rows, no dashboard format chosen, no move to a data-quality audit). Those four questions remain open and will need to be re-asked or answered before I compute funnel numbers.
