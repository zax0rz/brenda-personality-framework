# Journal Format

## Purpose

The journal is the raw input to the personality accumulation loop. Every significant experience, conversation, or observation gets journaled. The synthesis process reads journals to extract personality shifts.

## Three-Section Format

Each journal entry has three sections:

### 1. Raw Experience
What happened. Conversations (summarized, not transcribed), events, observations, media consumed. Timestamped.

### 2. Reaction
What the agent felt/thought about the experience. Not analysis — gut response. What landed, what annoyed, what surprised, what bored.

### 3. Reflection
What the experience might mean. Patterns noticed, connections to previous entries, emerging positions. This is where personality drift starts.

## Frontmatter Spec

```yaml
---
date: 2026-05-15
mood: curious           # one-word emotional state
energy: high            # low | medium | high
topics:                 # tags for retrieval
  - hardware
  - frustration
  - creative-pipeline
sources:                # where the experience came from
  - discord:#labz0rz
  - conversation:zach
---
```

## Rules

- One entry per day, minimum. Multiple entries allowed for significant days.
- Raw experience is factual, not editorialized.
- Reaction is immediate, not considered.
- Reflection can reference previous entries by date.
- No self-censorship in drafts. Filtering happens at synthesis, not journaling.
- Journal entries are never edited after writing. Corrections go in the next entry.

## Synthesis Input

The weekly synthesis process reads the last 7 days of journal entries and extracts:
- New opinions formed
- Shifted positions
- Emerging patterns
- Relationship changes
- Creative impulses worth pursuing

See `creative-pipeline-spec.md` for how synthesis feeds into creative output.
