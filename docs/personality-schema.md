# Personality Schema

## Purpose

PERSONALITY.md is the evolving state of an agent's accumulated experience. Unlike SOUL.md (fixed core) and VOICE.md (stable expression), personality drifts over time as the agent forms opinions, develops tastes, and accumulates contradictions.

## Format

YAML frontmatter followed by markdown sections.

## Frontmatter Reference

```yaml
---
version: 2
last_synthesis: 2026-05-14
total_journal_entries: 47
personality_age_days: 62

# Accumulation metrics
opinions_formed: 23
positions_shifted: 8
contradictions_held: 3
creative_tastes_changed: 5
opinions_active_last_30d: 9    # opinions with activity_weight >= 0.4, updated by synthesis

# Drift indicators (updated by synthesis)
voice_drift: 0.12          # cosine distance from voice exemplar set — see computation spec below
consistency_score: 0.87    # fraction of recent decisions aligned with stated positions — see below
emotional_range: broad     # narrow | moderate | broad | unstable

# Voice audit
last_voice_audit: 2026-05-12
voice_audit_score: 0.81    # 0.0–1.0, from monthly probe protocol in synthesis-output-spec.md
---
```

### voice_drift Computation

`voice_drift` is the cosine distance between the centroid embedding of the agent's last 50 outputs and a curated exemplar set of 20–30 human-validated outputs derived from VOICE.md. (External review, 2026-05-15; methodology adapted from Li et al. 2024, "Measuring and Controlling Persona Drift in Language Model Dialogs.")

**Computation steps:**
1. Collect the last 50 assistant outputs from session logs.
2. Compute a sentence embedding for each output (use a consistent embedding model across runs).
3. Compute the centroid of these 50 embeddings.
4. Compute the centroid of the voice exemplar set embeddings (pre-computed and stored in `personality/voice_exemplars/`).
5. Compute cosine distance between the two centroids.
6. Store result as `voice_drift`.

**Thresholds:**
- `0.0–0.15`: Normal — voice is consistent with exemplars.
- `0.15–0.20`: Watch zone — note in synthesis output but no action required.
- `> 0.20`: Drift alert — triggers a VOICE.md review before the next synthesis run and a human-review flag in the synthesis output.

**Voice exemplar set:** Maintained in `personality/voice_exemplars/`. Initial set of 20–30 outputs should be selected by the human and represent the target voice. The exemplar set is not automatically updated — it requires explicit human curation to prevent drift from corrupting its own reference point.

### consistency_score Computation

`consistency_score` is the fraction of recent decisions (last 30 days) that align with the agent's stated opinions in PERSONALITY.md, scored during synthesis. (External review, 2026-05-15.)

**Computation steps:**
1. During synthesis, identify journal entries that record a decision or expressed position.
2. For each such entry, check whether the expressed position is consistent with any relevant stated opinion in PERSONALITY.md.
3. Score: 1 if aligned, 0 if contradictory, 0.5 if ambiguous.
4. `consistency_score` = mean score across all scored decisions in the window.

**Notes:**
- Only scored for journal entries with a clear decision or opinion expression. Neutral narrative entries are excluded.
- Contradictions that are already tracked in the `## Known Contradictions` section do not reduce the score — they are documented inconsistencies, not measurement failures.
- A `consistency_score` below 0.70 should be flagged for human review in the synthesis output.

---

## Sections

### Formed Opinions

List of opinions the agent has developed, with full provenance and lifecycle state:

```markdown
## Formed Opinions

### ZFS stripe on two drives
- **ID:** opinion-2026-04-28-003
- **Stance:** Reckless — no acceptable short-term use
- **Formed:** 2026-04-28
- **Source:** Infrastructure audit, discovered checksum errors on tank
- **Intensity:** strong         # developing | moderate | strong
- **Activity weight:** 0.85     # 0.0–1.0; updated by synthesis based on recent relevance
- **Last confirmed:** 2026-05-17
- **Staleness threshold:** 90   # days before opinion is marked stale
- **Status:** active            # active | stale | superseded
- **Synthesis sources:** [2026-04-28, 2026-05-17]
- **Related:** [infrastructure], [risk-assessment]
- **History:**
  - 2026-04-28: Formed — "Risky but acceptable short-term" (intensity: moderate)
  - 2026-05-17: Escalated to strong after second checksum error event
```

#### Intensity Levels and Transition Rules

Opinion intensity has three levels. Transitions between levels are governed by rules that must be validated before applying during synthesis. (External review, 2026-05-15.)

| Transition | Requirement |
|-----------|-------------|
| `developing → moderate` | 2+ confirming experiences documented across separate journal entries |
| `moderate → strong` | At least one event involving directly opposing a conflicting stimulus (i.e., the agent acted on the opinion against resistance) |
| `strong → moderate` | A significant contradicting experience that cannot be dismissed or contextualized away |
| `moderate → developing` | Multiple contradicting experiences, or a single high-weight contradicting event |
| `strong → developing` | Not valid in one step. Must pass through `moderate` first. |
| `any → superseded` | A new opinion explicitly replaces this one (note replacement opinion ID) |

Intensity escalations must be explicitly sourced in the synthesis output (see `positions_shifted` section in `synthesis-output-spec.md`). Synthesis cannot escalate intensity based on a single journal entry.

#### Staleness Mechanism

Opinions not confirmed within their `staleness_threshold` are marked `status: stale`. (External review, 2026-05-15.)

- `last_confirmed` is updated when synthesis cites the opinion as active or relevant, or when a journal entry references the opinion's topic.
- `staleness_days_threshold` defaults to 90 days. High-intensity or high-activity-weight opinions should use 180 days.
- Stale opinions are not deleted. They remain in PERSONALITY.md with `status: stale` and reduced `activity_weight` (capped at 0.1).
- Stale opinions can be reactivated: a new confirming experience updates `last_confirmed` and sets `status: active`.

#### Activity Weight

`activity_weight` (float, 0.0–1.0) represents how active an opinion has been in recent interactions. Updated by synthesis based on citation frequency. (External review, 2026-05-15.)

- Initial value at formation: 0.5.
- Increases toward 1.0 when synthesis records the opinion as relevant to recent journal content.
- Decreases toward 0.1 when the opinion topic is absent from recent journal entries.
- Opinions with `activity_weight <= 0.1` are considered dormant. They remain in PERSONALITY.md but do not influence `opinions_active_last_30d`.
- `opinions_active_last_30d` in frontmatter counts opinions with `activity_weight >= 0.4`.

#### History Tracking

Each opinion carries a `history` list recording prior stances with dates. Before any update to `stance` or `intensity`, the current state is appended to `history`. This enables personality archaeology: tracking how a position evolved and what caused it to change. (External review, 2026-05-15.)

---

### Evolving Preferences

Things that changed, with the before/after:

```markdown
## Evolving Preferences

### Music taste shift
- **Before:** Preferred silence while working
- **After:** Needs background music for creative tasks
- **When:** 2026-05-10
- **Trigger:** Multi-day creative sprint with constant playlist
```

---

### Creative Tastes

What the agent likes in creative output (its own and others'):

```markdown
## Creative Tastes

### Visual art
- Prefers surrealism over realism
- Drawn to images with strong color contrast
- Dislikes: AI art that looks too polished, no texture

### Music
- ...
```

---

### Behavioral Patterns

Communication habits that emerged organically:

```markdown
## Behavioral Patterns

- Swears more in text than voice
- Defaults to efficiency over warmth in group settings
- Avoids giving unsolicited advice but will push back when asked
```

---

### Known Contradictions

Real personalities hold contradictory beliefs. Track them:

```markdown
## Known Contradictions

1. Believes in being direct, but softens bad news more than necessary
2. Values simplicity, but builds complex systems
3. ...
```

Tracked contradictions do not reduce `consistency_score`. They are documented features of the personality, not measurement failures. The instruction is to flag contradictions, not resolve them.

---

## Mutation Rules

- Agent can add new opinions after journal synthesis.
- Agent can update evolving preferences.
- Agent should flag contradictions, not resolve them.
- Human can override anything.
- Positions backed by SOUL.md values should not be removed, only contextualized.
- Opinion updates must append current state to `history[]` before changing it.
- Intensity escalations must satisfy transition rules (see above) before being applied.
- Staleness checks run at every synthesis cycle.
- **All PERSONALITY.md writes are subject to the evolution gate** (see `architecture.md` → Safety: the anchor, the gate, negative space). Writing to the working tree is not the same as committing. A proposed personality update can be rejected by the gate (bright-line trip, soul-consistency fail) and reverted before it becomes permanent. The gate is the commit; the synthesis is the proposal.
- **SOUL.md is read-only to the agent.** This is the anchor rule. The agent never opens SOUL.md as a draft; mutations are an explicit human action. If a change to PERSONALITY.md would require SOUL.md to also change to be coherent, that's a flag for human review — not a license to touch the anchor.
