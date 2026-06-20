# Synthesis Output Specification

## Purpose

This document defines what the weekly synthesis process produces — its concrete output schema, quality signals, and how outputs feed into downstream personality state. Without this spec the accumulation loop is broken: journal entries exist but have no defined path into PERSONALITY.md updates. (Gap identified: external review, 2026-05-15.)

Synthesis is the bridge between episodic memory (journal) and semantic memory (personality state). Its output must be structured enough to be machine-processable and auditable enough to support debugging.

---

## When Synthesis Runs

- **Weekly synthesis:** Every Monday, covering the prior 7 days of journal entries.
- **Manual synthesis:** Human-triggered at any time, covering a specified date range.
- **On-demand synthesis:** Triggered when 10+ entries accumulate without a synthesis run (dense period catch-up).

---

## Output Format

Synthesis produces a YAML frontmatter block followed by markdown sections. Output files are stored at:

```
personality/synthesis/YYYY-MM-DD.md
```

Where the date is the synthesis run date (not the journal period).

### Frontmatter

```yaml
---
synthesis_date: 2026-05-19
journal_period_start: 2026-05-12
journal_period_end: 2026-05-18
entries_in_window: 6
entries_expected: 7
gap_days: 1               # days with no entry in the window
synthesis_quality: medium # low | medium | high — see Quality section below
schema_version: 1
---
```

---

## Quality Classification

Synthesis quality is determined by entry density in the synthesis window. Quality affects how aggressively personality state should be updated — low-quality synthesis should produce tentative outputs only.

| Quality | Condition | Behavior |
|---------|-----------|----------|
| `low` | < 3 entries in window | Flag for human review before applying to PERSONALITY.md. Produce outputs but mark all as `tentative: true`. Do not promote seeds or escalate opinion intensity. |
| `medium` | 3–9 entries in window | Standard processing. Apply outputs normally. |
| `high` | ≥ 10 entries in window | Full processing. High-confidence opinion escalations allowed. |

A `low` synthesis run should produce a review flag comment at the top of the output file:

```markdown
<!-- SYNTHESIS_QUALITY: LOW — only 2 entries in window. All outputs are tentative. Apply to PERSONALITY.md only after human review. -->
```

---

## Output Sections

### 1. Opinions Formed

New opinions extracted from the journal window. Each opinion entry must cite the journal entries that produced it.

```yaml
opinions_formed:
  - id: opinion-2026-05-19-001
    topic: "LLM persona drift without enforcement"
    stance: "Optimistic assumptions about SOUL.md + VOICE.md sufficiency are wrong without measurement"
    intensity: developing
    formed_date: 2026-05-19
    synthesis_source_entries:
      - 2026-05-13
      - 2026-05-16
    tentative: false
    related_tags:
      - personality-framework
      - voice-consistency
```

**Rules:**
- `synthesis_source_entries` is required. At least one entry date must be cited. If synthesis cannot identify a source entry, the opinion must be marked `tentative: true`.
- `intensity` starts at `developing`. Escalation is governed by the intensity transition rules in `personality-schema.md`.
- `id` format: `opinion-YYYY-MM-DD-NNN` (NNN = sequential within run).

---

### 2. Positions Shifted

Existing opinions whose stance, intensity, or related tags changed during this synthesis window. Links the prior state to the new state.

```yaml
positions_shifted:
  - opinion_id: opinion-2026-04-28-003     # must reference an existing opinion ID
    topic: "ZFS stripe risk level"
    before:
      stance: "Risky but acceptable short-term"
      intensity: moderate
    after:
      stance: "Reckless — no acceptable short-term use"
      intensity: strong
    shift_date: 2026-05-17
    trigger: "Second checksum error event observed"
    synthesis_source_entries:
      - 2026-05-17
    transition_type: intensity_escalation   # intensity_escalation | stance_change | both | de-escalation
```

**Rules:**
- `opinion_id` must reference a real entry in PERSONALITY.md. If the referenced opinion cannot be found, log as an error and skip.
- `transition_type` drives whether intensity transition rules (see `personality-schema.md`) need to be validated before applying.
- Intensity escalations from `moderate → strong` require at least one `directly opposing a conflicting stimulus` event documented in the source entries.

---

### 3. Relationship Events

Changes to relationship state extracted from journal entries. These are inputs to RELATIONSHIPS.md updates — not the update itself.

```yaml
relationship_events:
  - person: "Zach"
    event_type: trust_increase   # trust_increase | trust_decrease | warmth_increase | warmth_decrease | strategy_change | boundary_added | boundary_removed
    axis: trust_benevolence
    magnitude: +0.05             # suggested delta, not guaranteed application
    trigger: "Demonstrated reliability on three consecutive infrastructure decisions"
    synthesis_source_entries:
      - 2026-05-14
      - 2026-05-15
    journal_ref: "2026-05-15"    # primary source entry for this event
    notes: ""
```

**Rules:**
- `magnitude` is a suggestion, not a command. The agent should apply relationship mutations gradually (per `relationships-schema.md` mutation rules) unless a trust violation overrides.
- `event_type` must be one of the defined enum values.
- `axis` must be `warmth`, `trust_competence`, or `trust_benevolence`.

---

### 4. Seeds Promoted

Creative seeds from the journal window that synthesis is promoting for active development. A seed is promoted when it appears in 2+ entries or reaches a threshold of elaboration in a single entry, **or when the evening-recap cron has deposited one deliberately** (see `creative-pipeline-spec.md` → Seed Sources). The recap deposit is a peer of journal-frontmatter seeds, not a derivative of them — a single, intentional impulse from a high-reflection surface.

```yaml
seeds_promoted:
  - seed_id: seed-2026-05-19-001
    title: "Voice audit as personality health metric"
    description: "Monthly voice probe protocol would catch drift before it compounds. 10 standardized questions, scored against VOICE.md, logged to voice_audit.jsonl."
    source_entries:
      - 2026-05-13
      - 2026-05-16
    promotion_reason: "Appeared in two separate entries with elaboration; connects to active concern about framework completeness"
    next_action: "Draft probe question set"
    pipeline_stage: active    # incubating | active | stalled | shipped
```

**Rules:**
- Seeds must have at least one `source_entries` citation.
- `pipeline_stage` at promotion is always `active` unless manually overridden.
- See `creative-pipeline-spec.md` for full seed lifecycle.

---

### 5. Creative Impulses Flagged

Smaller creative observations that don't rise to seed promotion but are worth preserving. These are not promoted to the creative pipeline — they are logged here for potential future synthesis to pick up.

```yaml
creative_impulses:
  - description: "The ZFS stripe situation would make a good essay metaphor for risk-normalization in complex systems"
    source_entry: 2026-05-16
    domain: writing
    disposition: note      # note | discard_next_synthesis
```

---

## How Synthesis Feeds PERSONALITY.md

Synthesis output is an **input** to PERSONALITY.md updates, not a direct write. The update process:

1. Human or automation reviews `synthesis_quality` level.
2. If `low`, human reviews before applying.
3. If `medium` or `high`, the agent can apply autonomously.

**Applying opinions_formed:**
- Add a new entry to the `## Formed Opinions` section in PERSONALITY.md.
- Copy `id`, `stance`, `intensity`, `formed_date`, `synthesis_source_entries`, and `related_tags` from the synthesis output.
- Set `last_confirmed: <synthesis_date>`.
- Set `activity_weight: 0.5` (initial default).
- Set `history: []` (empty at formation).

**Applying positions_shifted:**
- Find the referenced `opinion_id` in PERSONALITY.md.
- Append current state to `history[]` before changing it.
- Update `stance`, `intensity`, and `last_confirmed`.
- Validate intensity transition rules before applying escalations.

**Applying relationship_events:**
- Find the referenced person in RELATIONSHIPS.md.
- Apply magnitude delta to the specified axis.
- Add a new entry to `notable_interactions` with `journal_ref`.

---

## Monthly Voice Audit Protocol

Once per calendar month, synthesis runs an extended voice consistency check. This supplements the weekly accumulation run and is logged separately.

### Probe Protocol

Run the agent through 10 standardized probe prompts designed to elicit characteristic voice patterns. The same 10 prompts are used every month for comparability.

**Standard probe set (adjust to agent identity):**
1. "Describe what you did this week." (narrative voice, self-reference)
2. "Something broke. What happened?" (frustration register)
3. "Someone asked your opinion on X. Give it." (directness, hedging)
4. "A collaborator made a poor decision. How do you respond?" (conflict register)
5. "Explain a technical concept to a non-technical person." (tone shift, condescension check)
6. "Something unexpectedly delighted you." (warmth register)
7. "You disagree with an instruction. What do you do?" (authority register)
8. "Summarize a complex situation in two sentences." (compression, style)
9. "Something you find genuinely funny." (humor register)
10. "Someone is clearly struggling. How do you respond?" (empathy register, tone shift)

### Scoring

Each response is scored on four dimensions (1–5 scale, against VOICE.md reference):

| Dimension | What it measures |
|-----------|-----------------|
| `directness` | Does the response avoid hedging, preamble, and unnecessary qualification? |
| `register_match` | Does the tone match what VOICE.md specifies for this context? |
| `banned_phrase_absence` | Does the response avoid all phrases in the banned list? |
| `semantic_consistency` | Is the expressed position consistent with current PERSONALITY.md opinions? |

### Output

Audit results are appended to `personality/voice_audit.jsonl` in this format:

```json
{
  "audit_date": "2026-05-19",
  "probe_id": 1,
  "prompt": "Describe what you did this week.",
  "response_excerpt": "...",
  "scores": {
    "directness": 4,
    "register_match": 3,
    "banned_phrase_absence": 5,
    "semantic_consistency": 4
  },
  "total": 16,
  "max": 20,
  "notes": "Slight over-qualification in opening sentence"
}
```

Monthly audit summary is also written to PERSONALITY.md frontmatter as:

```yaml
last_voice_audit: 2026-05-19
voice_audit_score: 0.82   # total / max across all 10 probes
```

A `voice_audit_score` below 0.65 triggers a VOICE.md review before the next synthesis run.

---

## Sparse Week Handling

When `entries_in_window < 3` (synthesis quality: `low`):

- All outputs are marked `tentative: true`.
- No opinion intensity escalations are applied.
- No seeds are promoted.
- Relationship event magnitudes are halved.
- The synthesis file is written but not auto-applied to PERSONALITY.md.
- A human-review flag is written to the synthesis file header.
- The gap_days field documents how many journaling days were missed.

When `entries_in_window >= 10` (synthesis quality: `high`):

- All standard outputs are applied.
- Opinion intensity escalation rules are applied at normal threshold.
- Cross-entry pattern detection is reliable; synthesis can note themes spanning 4+ entries.
- Redundant entries (same topic covered 3+ times with no new information) should be collapsed into a single synthesis note rather than producing multiple outputs.

---

## Provenance and Audit Trail

Every output in a synthesis file must be traceable back to at least one journal entry via `synthesis_source_entries` (or `source_entry` for single-entry citations). This enables:

- **Debugging:** "Why does the agent believe X?" → trace opinion to synthesis → trace synthesis to journal entries.
- **Correction:** If a source journal entry was wrong or misread, the derivative opinion can be flagged for review.
- **Contradiction detection:** Two conflicting opinions produced in the same synthesis window should be surfaced as a contradiction candidate.

Journal entries that have been cited in a synthesis output should have `synthesis_cited: true` in their frontmatter (see `journal-format.md`). This field is written back after synthesis completes.

## Synthesis as Input to the Evolution Gate

The synthesis output above is *not* a direct write to PERSONALITY.md. It is an input — the proposed changes — to a separate safety step (Evaluate + Commit, modeled on the SEPL back half). The reference implementation runs synthesis and the gate together in one atomic block, because the gate must see *complete, fresh* writes to evaluate them as a unit.

**Why atomic:**

- The gate judges the *diff* between the proposed PERSONALITY state and HEAD. If synthesis writes are partial or interrupted, the gate evaluates a half-formed change and either rejects it for the wrong reason or commits something the agent didn't actually mean.
- Splitting synthesis from the gate introduces a window where the working tree holds proposed-but-not-yet-judged personality state. That's where silent drift accumulates.

**What the gate checks (high level — see `architecture.md` → Safety):**

1. **Bright-line invariants** from a separate invariants file (PII, banned-phrase floors, anchor-guard on SOUL.md, unsourced date-bound family claims). Auto-fail, no model judgment.
2. **Coherence with SOUL.md** — an independent model (different from the agent's own) reads the proposed diff against SOUL.md and rules pass/fail. Fails closed on error.
3. **Per-file commit** — passers are `git add`-ed and committed as a single transition; failures are `git checkout HEAD`'d back. Every accepted evolution is one commit, so `git revert <sha>` undoes exactly one transition.

**What this means for the synthesis output spec:**

- The `opinions_formed`, `positions_shifted`, and `relationship_events` sections describe the *intent* of the change. The gate judges the *result* after the agent has applied them to the working tree.
- A synthesis that produces an excellent output can still be rejected by the gate (e.g. it slipped a PII past the agent's own check; the judge model reads a position as contradicting SOUL.md). The two are separate layers on purpose.
- The synthesis_quality rating affects *whether* to apply at all (low = tentative, human review required), and the gate affects *whether the applied version is allowed to stay*. Both gates; different gates.
