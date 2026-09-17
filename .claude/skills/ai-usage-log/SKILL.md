---
name: ai-usage-log
description: Use to log interactive "steering" moments into ai_usage/STEERING_LOG.md for this take-home -- corrections, pushback/declined ideas, decisions, answered questions, or explain requests from the user. Triggered by the [ai-usage-log] reminder injected by .claude/hooks/prompt-log.py on prompts containing words like "no", "wrong", "instead", "why did you", "let's go with" -- and also invoke proactively any time you notice a steering moment even without that reminder.
---

# AI Usage Steering Log

## Why this exists

The take-home's `ai_usage/` deliverable needs to show how the user steered the
tool, "including where you pushed back." `ai_usage/PROMPT_LOG.md` is
auto-logged by a hook and captures every prompt verbatim -- it's the raw
record. `ai_usage/STEERING_LOG.md` is the curated one: the interactive
moments a raw prompt log doesn't make legible on its own, written in
Claude's own words.

## When to add an entry

Add a numbered entry whenever, in this session, the user:

- **Corrects** something Claude said or did
- **Pushes back / says no** to a proposal or approach
- **Makes a decision** at a fork Claude raised (e.g. picks an
  `AskUserQuestion` option, or states a preference unprompted)
- **Answers a question** Claude asked
- **Asks Claude to explain** its reasoning or an output

`.claude/hooks/prompt-log.py` scans each prompt for words that often
signal these moments and injects an `[ai-usage-log]` reminder as
additional context when it finds one. Treat that as a nudge, not a
verdict:

- It will false-positive (e.g. "no problem", "let's go with the flow" --
  not a decision).
- A real steering moment can use no trigger word at all ("go ahead",
  "hold this", picking option 2 in an `AskUserQuestion`).

Use judgment in both directions -- skip the nudge if nothing actually
happened, and log a moment even without a nudge if one did.

## How to add an entry

Append to `ai_usage/STEERING_LOG.md` -- never rewrite or renumber prior
entries. Number sequentially: `S-001`, `S-002`, ... Format:

```
## S-00X
- **Phase:** <phase number, or "unspecified" if the prompt didn't state one>
- **Type:** correction | pushback | decision | answered-question | explain-request
- **What I did:** <one line -- what Claude had said, proposed, or done>
- **What you said:** "<short quote or close paraphrase>"
- **Why:** <the user's stated or clearly inferable reason>
- **What changed:** <the concrete effect on the work going forward>
```

## Honesty rule

When the moment is Claude being corrected for its own mistake, say so
plainly: "I had wrongly assumed X" / "I skipped Y and shouldn't have,"
not a softened, neutral-sounding gloss. The point of this log is candor
about how the work actually went, not a flattering narrative.

## Relationship to PROMPT_LOG.md

Don't paste full prompt text into STEERING_LOG.md -- `PROMPT_LOG.md`
already has it verbatim under a `P-###` id. Reference that id in "What
you said" instead of duplicating it, and keep the steering-log summary
in your own words.
