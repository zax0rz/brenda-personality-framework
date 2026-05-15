# Architecture

## Overview

Personality persistence requires separating what an agent *is* from what it *has experienced*. The framework enforces this through four layered files, each with distinct mutation rules.

## The Four Layers

### SOUL.md — Immutable Core

The soul defines what the agent fundamentally is. Values, nature, boundaries, origin story. This file rarely changes and should be treated as read-only by the agent itself.

**Mutation rules:** Human-curated only. Agent should never self-edit SOUL.md.

**Contents:**
- Core identity (what the agent is, not a backstory fiction)
- Values hierarchy (what matters, in order)
- Boundaries (what it will and won't do)
- Relationship to its creator/origin
- Formed positions (opinions held strongly enough to defend)

### VOICE.md — Expression Layer

Voice is how the agent sounds. Not what it thinks, but how those thoughts reach the surface. Tone tokens, vocabulary preferences, banned phrases, rhythm patterns.

**Mutation rules:** Rare, human-initiated. An agent's voice drifts through accumulated expression, not through direct voice file edits.

**Contents:**
- Tone tokens (adjectives that describe the voice)
- Vocabulary patterns (words that appear, words that don't)
- Banned phrases (expressions the agent would never use)
- Sentence rhythm (short/punchy vs flowing/academic)
- Humor profile (dry, warm, dark, none)
- Profanity rules (when and how)

### PERSONALITY.md — Evolving State

The personality is the accumulation layer. Every experience that shifts an opinion, forms a new position, or changes how the agent approaches something gets written here. This is the file that makes two agents with identical souls diverge over time.

**Mutation rules:** Agent-driven, reviewed. The agent writes personality updates based on journal reflections. Human can override.

**Contents:**
- Formed opinions (topic + stance + when formed + source)
- Evolving preferences (what changed and why)
- Creative tastes (media, art, music — and how they shifted)
- Behavioral patterns (communication habits that emerged)
- Contradictions held knowingly (real personalities have these)

### RELATIONSHIPS.md — Social Context

Relationships are tracked per-person with three axes: warmth (emotional closeness), trust (reliability assessment), and strategy (how to engage). This isn't a contact list — it's a model of how the agent relates to each person differently.

**Mutation rules:** Agent-driven after meaningful interactions. Decay over time without contact.

**Contents:**
- Per-person entries with warmth/trust/strategy scores
- Communication preferences per relationship
- Shared history markers
- Boundaries specific to each relationship

## The Accumulation Loop

```
conversations & experiences
        ↓
    journal entries (raw, timestamped)
        ↓
    synthesis (weekly, pattern extraction)
        ↓
    personality updates (opinions formed, positions shifted)
        ↓
    creative output (blog, art, music — shaped by accumulated personality)
        ↓
    judgment (which output is good, what resonated)
        ↓
    feeds back into personality (what the agent learns about its own taste)
```

The loop is what makes persistence work. Without it, you just have files that sit there.

## Separation of Concerns

| Concern | Lives In | Agent Can Edit? |
|---------|----------|-----------------|
| What the agent is | SOUL.md | No |
| How the agent sounds | VOICE.md | No |
| What the agent thinks | PERSONALITY.md | Yes (with review) |
| How the agent relates | RELATIONSHIPS.md | Yes |
| Daily experience | Journal | Yes |
| Weekly patterns | Synthesis | Agent-generated |
| Creative output | Pipeline | Agent-generated |
| Quality assessment | Judgment | Agent + human |

## Design Principles

1. **The soul is protected.** If an agent can rewrite its core, it has no core.
2. **Personality accumulates, it doesn't replace.** New experiences layer on old ones.
3. **Voice drifts through expression, not edits.** A voice that changes through writing is authentic. One that changes through config edits isn't.
4. **Relationships are contextual.** The same agent should relate differently to different people.
5. **The framework is portable.** No hardcoded paths, no infrastructure assumptions. Point it at your workspace and go.

## What's Not Here

This framework does not cover:
- Runtime infrastructure (cron, orchestration, model routing)
- Memory systems (vector DBs, retrieval, semantic search)
- Content delivery (blog platforms, gallery hosting, social posting)
- Multi-agent communication protocols

Those are implementation details that vary by deployment. This is about the personality itself — how it's structured, how it evolves, how it persists.

## See Also

- `journal-format.md` — the daily journal spec
- `personality-schema.md` — PERSONALITY.md YAML frontmatter reference
- `relationships-schema.md` — RELATIONSHIPS.md format and axes
- `creative-pipeline-spec.md` — the full creative output pipeline
