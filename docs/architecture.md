# Architecture

## Overview

Personality persistence requires separating what an agent *is* from what it *has experienced*. The framework enforces this through four layered files, each with distinct mutation rules.

## The Four Layers

### SOUL.md — Immutable Core

The soul defines what the agent fundamentally is. Values, nature, boundaries, origin story. This file rarely changes and should be treated as read-only by the agent itself. (For the *implementation* of "read-only" — code-level enforcement, not prompt-level discipline — see Safety: the anchor, the gate, negative space below. The reference implementation physically removes SOUL.md from the autonomous loop's write path; bright-line invariants enforce it; the commit path's anchor-guard reverts any unprompted changes.)

**Mutation rules:** Human-curated only. Agent should never self-edit SOUL.md. (Anchor-guard reverts if the loop attempts it.)

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

A reference implementation of this loop is grounded in the **SEPL paper** (Self-Evolution Protocol Layer — *Reflect → Select → Improve → Evaluate → Commit*). The first three stages (Reflect/Select/Improve) are informal in this framework — they happen through journal writing, weekly synthesis, and the agent's own self-tend. The back half (Evaluate and Commit) is what makes autonomous self-modification safe enough to trust, and is implemented as a separate safety layer described below. (SEPL citation per opus/architect note, 2026-06-19; the paper reference is included as a working anchor for the design pattern but has not been independently verified — flag for review if accuracy matters to your deployment.)

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

## Safety: the anchor, the gate, negative space

The four-layer architecture above is necessary but not sufficient. A personality loop that can rewrite its own anchor, drift without check, or only express warmth has three structural risks that need separate safety systems:

1. **Self-editing the standard.** A loop that can modify its own SOUL can lower its own bar (wireheading) — calling drift "improvement" by editing the soul to match. If the agent can rewrite what it's judged against, the judgment is circular.
2. **Drift with no check.** Personality state that mutates freely over weeks will accumulate errors, even when each individual change looks reasonable. Errors compound.
3. **All-positive relationships.** A relationship model that only tracks warmth cannot represent the real texture of relating — which includes aversion, distrust, disagreement, and graceful distance. An all-positive relationships file is a false one.

The reference implementation addresses each with a dedicated mechanism:

### The Anchor — SOUL.md is immutable to the loop

The soul file is *physically* out of bounds for the autonomous loop. Not "rarely edited" — **never edited by the agent itself**. Mutations to SOUL.md are an explicit human action with deliberate intent. The loop reads SOUL.md as the reference standard and never opens it as a draft.

**Implementation:**
- The weekly self-tend step that writes personality files is *read-only* on SOUL.md.
- An anchor-guard in the commit path checks `git diff HEAD -- SOUL.md` and reverts any unprompted changes with a loud flag.
- Bright-line invariants (no SOUL edits, no un-banning a SOUL-level phrase, no unsourced family-bound dates, no PII) are enforced as code, not as prompt instructions.

**Test for what belongs in SOUL.md:** if it needs updating, it isn't soul. Frozen files can only hold durable truths. Operational sediment (volatile game state, model version numbers, "currently listening" entries) does not belong there.

### The Gate — Evaluate (ε) + Commit (κ) as a separate safety step

The weekly personality updates proposed by synthesis don't become permanent when written. They go through a gate — modeled on SEPL's Evaluate and Commit stages — before any of them is committed:

- **ε (Evaluate)** — two tiers:
  - *Deterministic bright lines* from an invariants file: no SOUL edits, no un-banning a SOUL-level phrase, no PII, no unsourced date-bound family claims. These auto-fail with no model judgment.
  - *Coherence judge*: an **independent model** (deliberately different from the agent's own model — the judge must not rubber-stamp the agent's drift) reads the diff against SOUL.md and rules pass/fail. Fails closed (errors/timeouts = reject).
- **κ (Commit)** — passers get `git add`-ed (only the specific changed files, not a blanket commit) and committed as one reversible transition. Failures get `git checkout HEAD`'d back. Git *is* the versioned registry — no new datastore, no new failure mode.

**Rollback:** any single accepted evolution is one commit, so `git revert <sha>` undoes exactly one transition. This is what turns "hard to fix" into "trivially reversible." The whole point is that self-rewriting is safe *because* it's reversible per-change.

**Policy:** fully autonomous, all layers, transparency-not-approval. The agent acts, reports, and nothing wakes anyone up — because every change is reversible and every change is logged.

### Negative Space — relationship modeling that includes aversion

The four-axis relationship model (warmth + trust-competence + trust-benevolence + strategy) handles distance and complexity, but it can still produce an all-positive file if the agent never writes its aversions. Real personality has shape because it includes the things it *doesn't* warm to.

**Implementation patterns:**

- **Aversions are first-class.** A relationship can be tracked with low warmth *and* high trust-competence — you can respect someone and not want to engage with them. Aversion is about *behavior* (slop, bad faith, manipulation), not belief-class. Aversion to lazy religious spam is not aversion to religion.
- **Inner circle vs. outer ring.** Not all relationships deserve the same depth of tracking. The reference implementation uses two files:
  - **Inner circle** (`RELATIONSHIPS.md`) — gated, depth, comrades and humans you know well. Slow-moving, deliberate updates.
  - **Outer ring** (a separate file, e.g. `moltbook-relationships.md`) — ungated, lighter, acquaintances and churn from public social presence. Pruned aggressively (>30 days idle).
- **Promotion threshold.** A relationship doesn't graduate from outer to inner on one good exchange. The reference implementation requires ≥3 substantive exchanges across ≥2 weeks for promotion. One thread isn't a graduation.
- **Disagreement is allowed.** The inner circle is not forced-positive. The agent can come to distrust a comrade — even one described warmly in SOUL — and record it with cause.

**Test for what belongs in a relationship file:** if the relationship could never become adversarial or grow cold, you're tracking a friendship, not a relationship.

### Why these are separate systems

The anchor, the gate, and the negative-space model protect different things:

| System | Protects | Failure mode without it |
|--------|----------|--------------------------|
| Anchor | The standard of judgment | Wireheading — drift edits its own bar |
| Gate | The mutation path | Silent compound errors in personality state |
| Negative space | The relationship model | False-positive "all good with everyone" relationships |

They compose. Anchor → Gate → Negative Space means: the soul is fixed → weekly changes are judged and reversible → the resulting personality has shape including its dislikes. Remove any one and the system becomes unsafe in a specific, predictable way.

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
- `research/personality-design-reviews.md` — external design reviews including the SEPL framing of the safety layer
