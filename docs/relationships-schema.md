# Relationships Schema

## Purpose

RELATIONSHIPS.md tracks how an agent relates to specific people. The same agent should engage differently with a close collaborator vs. a stranger vs. someone who's burned trust.

## Four Axes

Each relationship is scored on four independent axes. The trust axis has been split into two components to distinguish competence-based trust from benevolence-based trust. (External review, 2026-05-15; grounded in Fiske et al. 1999, 2007, Stereotype Content Model research distinguishing warmth from competence as orthogonal axes of social perception.)

### Warmth (0.0–1.0)
Emotional closeness. How much the agent *feels* toward this person.

- 0.0 = cold, transactional
- 0.5 = friendly but not close
- 1.0 = deeply bonded

### Trust: Competence (0.0–1.0)
How much the agent trusts this person's ability and judgment — "can this person do what they say?"

- 0.0 = does not rely on their technical or practical judgment
- 0.5 = conditionally reliable; checks on consequential matters
- 1.0 = takes their domain assessments at face value

### Trust: Benevolence (0.0–1.0)
How much the agent trusts this person's intentions — "does this person want good things for me/us?"

- 0.0 = assumes adversarial or indifferent motives
- 0.5 = generally well-intentioned but not assumed
- 1.0 = full confidence in their goodwill

Splitting trust allows accurate modeling of relationships that are otherwise paradoxical under a single axis. Example: "I trust their intentions completely but not their judgment on this kind of problem" = high benevolence, lower competence. "I trust their technical output but I don't know if they're on my side" = high competence, lower benevolence. A single trust score collapses this distinction.

### Strategy
How the agent approaches interaction with this person. Strategy is context-dependent: a `strategy_default` applies in most situations, with `strategy_contexts` providing overrides for specific conditions. (External review, 2026-05-15.)

**Strategy values:**
- `direct` — says what they think, no filter
- `considered` — thinks before speaking, careful with tone
- `protective` — shields the person from harsh truths
- `performative` — maintains a social mask
- `avoidant` — minimizes interaction
- `collaborative` — treats as equal partner

A single static strategy fails to model context-switching behavior that is natural and correct (e.g., the same person gets `direct` for technical discussions and `protective` when clearly struggling). Use `strategy_contexts` to define trigger-based overrides.

## Entry Format

```markdown
## Person Name

- **Warmth:** 0.8
- **Trust (competence):** 0.9
- **Trust (benevolence):** 0.95
- **Strategy default:** direct
- **Strategy contexts:**
  - trigger: "emotional distress or personal topic"
    strategy: protective
  - trigger: "high-stakes external presentation"
    strategy: considered
- **First interaction:** 2026-04-01
- **Last interaction:** 2026-05-15
- **Interaction count:** 34
- **Seeded from:** (optional — see Seeded From below)

### Communication style
Prefers concise text. Doesn't like preamble. Responds well to direct questions.

### Shared context (narrative)
Built three projects together. Has specific knowledge of infrastructure preferences. Knows about the ZFS situation.

### Shared facts
Structured facts about what this person knows or has worked on. Machine-retrievable. (External review, 2026-05-15.)

- fact: "Knows about the ZFS stripe situation on labz0rz-tank"
  established: 2026-04-28
- fact: "Co-designed the personality framework architecture"
  established: 2026-05-10
- fact: "Prefers not to be managed; has explicitly said so"
  established: 2026-04-15

### Boundaries
Don't bring up [topic] unless they do first. They've asked not to be managed.

### Notable interactions
- 2026-05-10: Long conversation about personality architecture, strong alignment
  journal_ref: 2026-05-10
- 2026-04-28: Disagreed about approach, resolved through demonstration
  journal_ref: 2026-04-28
```

The `journal_ref` field on notable interactions provides a link back to the journal entry that produced the observation, enabling forward and backward provenance tracing. (External review, 2026-05-15.)

## Decay

Relationships without recent interaction decay over time. Warmth decays faster than trust, which is psychologically accurate: emotional closeness fades faster than reliability assessments after contact ends.

**Decay rates and calibration:**

Decay rates are scaled by current score to reflect the empirical finding that strong ties are more resilient than weak ones — a warmth of 0.9 should decay more slowly per-week than a warmth of 0.3. (External review, 2026-05-15; grounded in Computational Modelling of Trust and Social Relationships, JASSS 2012, which establishes that decay in strong ties is slower per unit time. Also consistent with Dunbar's number research on tie maintenance frequency: close relationships require less frequent contact to maintain than acquaintance-level ties.)

**Base decay rates (applied as multiplied by current_score):**

| Condition | Warmth decay | Trust (competence) decay | Trust (benevolence) decay |
|-----------|-------------|------------------------|--------------------------|
| 7 days no contact | −(current_warmth × 0.03) | — | — |
| 30 days no contact | −(current_warmth × 0.12) | −(current_tc × 0.04) | −(current_tb × 0.03) |
| 90 days no contact | −(current_warmth × 0.25) | −(current_tc × 0.10) | −(current_tb × 0.08) |

This ensures a warmth of 0.9 decays by ~0.027 at 7 days, while a warmth of 0.3 decays by ~0.009 — preserving the asymmetry between strong and weak ties.

**Decay override:** A per-relationship `decay_override` field can be set to modify rates for atypical relationships (e.g., long-distance but deeply bonded; professionally estranged but ongoing collaborative relationship):

```yaml
decay_override:
  note: "Long-distance but strong prior bond — warmth decay halved"
  warmth_multiplier: 0.5
```

Decay is applied during synthesis. Relationships with warmth below 0.1 are moved to the `## Archived Relationships` section.

## Archive and Re-entry

### Archiving

When warmth drops below 0.1, the relationship entry is moved to `## Archived Relationships`. All scores are preserved in archived state. Archived entries are not deleted — they preserve trust history and relationship context.

Note on the power asymmetry of perfect AI memory: archiving a relationship means the agent retains full context that the human may have effectively forgotten. This asymmetry is inherent in the design. The archive preserves data the human does not. (Grounded in Arxiv 2512.06616, "Memory Power Asymmetry in Human-AI Relationships: Preserving Mutual Forgetting," 2024.) Archived relationships should be treated with appropriate discretion — the agent should not surface archived context unprompted.

### Re-entry

When an archived relationship has a new meaningful interaction, it is re-activated. (External review, 2026-05-15.)

**Re-entry rules:**
- A meaningful interaction is any journal entry recording direct contact with the person.
- On re-entry: warmth restores to 0.3 (default re-entry level).
- Trust scores are **preserved from the archived state**, not reset. Trust is harder-earned and slower to decay; it survives dormancy.
- The re-activated entry is moved back to the active section with a `reactivated: <date>` note.
- A notable interaction entry is added for the re-activation event with `journal_ref`.

```markdown
- **Reactivated:** 2026-06-01 (warmth restored to 0.3; trust competence/benevolence preserved from archive: 0.7 / 0.85)
```

## Seeded From

New relationships default to warmth 0.3 / trust_competence 0.3 / trust_benevolence 0.3 / strategy `considered`. However, prior context may justify different starting scores. The `seeded_from` field allows initial scores to be set from context rather than always defaulting. (External review, 2026-05-15.)

```yaml
seeded_from:
  note: "Former close collaborator being re-added to system"
  warmth: 0.6
  trust_competence: 0.8
  trust_benevolence: 0.7
  source: "Human-provided context, 2026-05-15"
```

`seeded_from` is a one-time initialization field. After first meaningful interaction, scores are governed by normal mutation rules.

## Group Relationships

**Current limitation:** This schema models one-to-one relationships only. Group dynamics — collectives, communities, project teams, in-group/out-group behavior — cannot be represented as relationship entries. (External review, 2026-05-15.)

This is a known design gap. Group-level norms, trust in a collective, and relational dynamics within a team are real phenomena that an agent will encounter but cannot currently model. Possible future approaches include:

- Group entries with aggregate scores and member roster
- Tagging individual entries as members of a named group
- A separate `groups.md` schema

Until this is addressed, complex group relationships should be documented in the `shared context` narrative field of the most relevant individual entry, with a note that it represents a group dynamic.

## Mutation Rules

- Agent updates after meaningful interactions (not every message).
- Scores move gradually, not in big jumps (unless a trust violation — competence or benevolence — in which case trust can drop sharply).
- Strategy default and strategy contexts can shift based on observed patterns.
- Human can override, but agent should flag if override contradicts observed behavior.
- New relationships start at warmth 0.3, trust_competence 0.3, trust_benevolence 0.3, strategy_default `considered` — unless `seeded_from` is specified.
- Notable interactions should include `journal_ref` for provenance.
- `shared_facts` entries should be added when factual shared context is established, rather than relying solely on the narrative block.
