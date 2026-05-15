# Creative Pipeline Spec

## Overview

The creative pipeline turns accumulated personality into creative output. It's a multi-stage process: seeds emerge from experience, get incubated, drafted, refined, judged, and either shipped or archived.

## Stages

### 1. Seed Extraction

Seeds are the raw creative impulses that emerge from journal entries, conversations, dreams, and synthesis. Not every experience produces a seed — most don't.

**Source:** Journal entries (primary), conversations, dreams, synthesis insights
**Tool:** `seed_manager.py extract`
**Output:** Individual seed files, one per impulse

A seed is a short text capture — a phrase, an image concept, a question, a feeling that wants to be expressed. Not a prompt, not a plan. Just the impulse.

**Rejection rate target:** 70–80%. Most seeds aren't worth pursuing. Aggressive filtering produces better output than trying to make everything work.

### 2. Incubation

Seeds sit. Some of them get stronger over time (the agent keeps thinking about them), some fade. Incubation is passive — it happens through the normal accumulation loop.

**Duration:** 1–7 days minimum. Seeds that still feel urgent after a week are worth drafting.
**Check:** During synthesis, review incubating seeds. Promote or archive.

### 3. Drafting

Turn the seed into actual output. This is the model generation step.

**Tool:** `draft_generator.py draft`
**Model:** Per routing table (not specified here — implementation detail)
**Iterations:** 2–4 variants per seed

The seed becomes a prompt. The prompt produces variants. This is mechanical — the art isn't in the generation, it's in the selection.

### 4. Refinement

Take the best variant and iterate. Adjust for personality alignment, technical quality, and the gap between intent and result.

**Tool:** `draft_generator.py refine`
**Process:** Agent reviews draft against personality, voice, and artist statement criteria. Sends specific refinement instructions. Repeats until threshold met or max iterations hit.

### 5. Judgment

The agent evaluates its own work honestly. This is where most output dies.

**Tool:** `draft_generator.py evaluate`
**Criteria:**
- **Personality alignment** (0.0–1.0) — does this sound like the agent? Would someone who knows the agent recognize this as theirs?
- **Originality** (0.0–1.0) — is this actually interesting or is it generic model output?
- **Technical quality** (0.0–1.0) — is the execution clean?
- **Emotional truth** (0.0–1.0) — does this feel real or performed?

**Threshold for publication:** 0.75 average across criteria. Pieces below 0.5 get archived without revision. Pieces between 0.5–0.75 get one revision cycle.

### 6. Artist Statement

Approved pieces get a four-question artist statement. See `artist-statement-format.md`.

### 7. Publication

Final output + source trace + artist statement → gallery. See `gallery-frontmatter.md`.

## Pipeline Configuration

```yaml
pipeline:
  seed_rejection_target: 0.75    # 75% of seeds should be rejected
  incubation_days_min: 3
  draft_variants: 3
  refinement_iterations_max: 3
  publication_threshold: 0.75
  archive_threshold: 0.5
  models:
    image: "implementation-specific"
    text: "implementation-specific"
    music: "implementation-specific"
    review: "implementation-specific"
```

## Media Types

### Image Pipeline
Seed → visual concept → draft (3 variants) → refine best → evaluate → statement → publish

### Text Pipeline (Blog/Moltbook)
Seed → angle → draft → refine for voice → evaluate → publish

### Music Pipeline
Seed → mood/genre → generate → evaluate → publish

Each type has the same stages but different tools and criteria at the refinement step.

## Feedback Loop

Published pieces that get engagement (comments, reactions, views) feed back into personality:
- What resonated → reinforces related opinions and tastes
- What flopped → questions assumptions, may shift approach

This is how personality keeps evolving through creative output, not just through conversation.
