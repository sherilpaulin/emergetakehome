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
