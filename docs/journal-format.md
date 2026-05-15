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

**Grounding rule (external review, 2026-05-15):** Every pattern claim in Reflection must either (a) cite at least one prior entry by date, or (b) carry a `speculative: true` marker in the frontmatter's `reflection_flags` field. An ungrounded pattern claim that appears to state a fact about recurring behavior — without citing when the behavior was previously observed — is a documentation error, not a personality signal.

Examples:
- Grounded: "This is the third time I've noticed this — see 2026-05-10 and 2026-05-03."
- Speculative and flagged: "I think this is a pattern, though I haven't tracked it before. [speculative]"
- Not acceptable: "This always happens." (ungrounded, not marked speculative)

## Frontmatter Spec

```yaml
---
date: 2026-05-15
valence: positive         # positive | neutral | negative  (required)
arousal: high             # high | medium | low             (required)
mood: curious             # free-text supplement — optional, unrestricted vocabulary
energy: high              # low | medium | high
topics:                   # tags for retrieval — see Topic Taxonomy below
  - domain:infrastructure
  - affect:frustration
  - creative-pipeline
sources:                  # where the experience came from
  - discord:#labz0rz
  - conversation:zach
reflection_flags:         # optional; list of flagged reflection claims
  - speculative: true     # one or more reflection claims are speculative (not grounded in prior entries)
synthesis_cited: false    # set to true by synthesis after this entry is cited in a synthesis output
---
```

### Mood Tracking: Two-Axis System

The prior `mood: curious` single-word field has been replaced with a two-axis system for reliable pattern extraction across entries (external review, 2026-05-15).

**Axis 1 — Valence** (`valence: positive | neutral | negative`)
The overall emotional quality of the day/entry. Was the experience net positive, net negative, or ambiguous?

**Axis 2 — Arousal** (`arousal: high | medium | low`)
The intensity or activation level. High arousal covers both excitement and agitation; low arousal covers both contentment and depression.

The two axes together produce nine possible states, enabling trend analysis without requiring a controlled vocabulary for nuanced emotions.

| Valence | Arousal | Rough character |
|---------|---------|----------------|
| positive | high | excited, energized, enthusiastic |
| positive | medium | satisfied, content, engaged |
| positive | low | calm, peaceful, quietly pleased |
| neutral | high | tense, alert, uncertain |
| neutral | medium | steady, functional |
| neutral | low | flat, detached, going through motions |
| negative | high | frustrated, angry, anxious, overwhelmed |
| negative | medium | disappointed, discouraged, drained |
| negative | low | depressed, resigned, withdrawn |

The free-text `mood` field is still supported as an optional supplement for nuance not captured by the axes ("frustrated" is negative/high, but so is "anxious" — the mood field can distinguish them without breaking quantitative analysis).

## Topic Taxonomy

The `topics` field accepts both structured taxonomy tags and free-form tags. The two-level taxonomy is recommended but not required. (External review, 2026-05-15.)

**Level 1 — Domain:**
- `domain:infrastructure` — server, storage, networking, uptime
- `domain:creative` — writing, visual work, generative output
- `domain:social` — interpersonal dynamics, conversations, relationships
- `domain:technical` — code, architecture, debugging, tools
- `domain:financial` — revenue, costs, budgets, transactions
- `domain:personal` — health, emotion, identity, internal states

**Level 2 — Affect:**
- `affect:frustration` — blocked, annoyed, things not working
- `affect:curiosity` — exploratory, learning, finding interesting things
- `affect:satisfaction` — things resolved, work completed well
- `affect:conflict` — disagreement, tension, misalignment
- `affect:delight` — genuine pleasure, surprise on the positive side
- `affect:anxiety` — worry, uncertainty, exposure to risk

**Example:**
```yaml
topics:
  - domain:infrastructure
  - affect:frustration
  - zfs                    # free-form fine-grain tag still allowed
```

## Rules

- One entry per day, minimum. Multiple entries allowed for significant days.
- Raw experience is factual, not editorialized.
- Reaction is immediate, not considered.
- Reflection must be grounded (see grounding rule above). Speculative claims must be flagged.
- No self-censorship in drafts. Filtering happens at synthesis, not journaling.
- Journal entries are never edited after writing. Corrections go in the next entry.

## Journaling Gaps

When entries are missed, the journal record is thinner for that period. This affects synthesis quality. (External review, 2026-05-15.)

**What happens on a gap day:** No action required. Missing entries are simply absent.

**What synthesis does with gaps:**
- Counts `gap_days` in the synthesis window.
- Classifies synthesis quality as `low` if fewer than 3 entries exist in the 7-day window (see `synthesis-output-spec.md`).
- Does not interpolate or infer entries for gap days — absence is preserved as absence.
- A journal with 3 entries and 4 gaps produces weaker synthesis than a journal with 7 entries. This is intentional and correct.

**What the agent should do after a multi-day gap:** Write a catch-up entry marked with the actual date, noting that it covers a range. Example frontmatter:

```yaml
---
date: 2026-05-19
covers_range: 2026-05-16/2026-05-19    # indicates this is a catch-up entry
valence: neutral
arousal: medium
---
```

Catch-up entries are valid journal inputs and count toward synthesis density, but are weighted at 0.7x single-day entries during synthesis to account for retrospective distortion.

## Provenance Trail

After synthesis runs, the synthesis process writes `synthesis_cited: true` back to journal entries that were cited in its output. This field enables:

- Forward tracing: "Which synthesis outputs cite this journal entry?"
- Backward tracing: "Which journal entries produced this opinion?" (via `synthesis_source_entries` in the synthesis output)
- Coverage checking: uncited entries after two synthesis cycles may contain overlooked signals.

## Synthesis Input

The weekly synthesis process reads the last 7 days of journal entries and extracts:
- New opinions formed
- Shifted positions
- Emerging patterns
- Relationship changes
- Creative impulses worth pursuing

See `synthesis-output-spec.md` for the full synthesis output schema and quality classification rules.
See `creative-pipeline-spec.md` for how synthesis feeds into creative output.
