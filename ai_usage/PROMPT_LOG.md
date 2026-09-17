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
