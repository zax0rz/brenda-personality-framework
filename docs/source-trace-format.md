# Source Trace Format

## Purpose

Every creative output should be traceable back to its origin. The source trace is the provenance record — what seed produced this, what model generated it, what the judgment was, and how it connects to the agent's accumulated experience.

## Schema

```yaml
# source-trace.yaml (accompanies each gallery piece)

trace:
  id: "2026-05-15-001"           # unique piece identifier
  created: "2026-05-15T14:30:00Z"

seed:
  id: "seed-2026-05-14-003"      # references seed_manager archive
  text: "the original seed text that produced this"
  source:                        # where the seed came from
    type: journal                # journal | conversation | dream | synthesis | accumulation
    date: "2026-05-14"
    ref: "journal/2026-05-14.md#section-2"

generation:
  model: "minimax-m2.7"          # model used for generation
  prompt: "the prompt sent to the model"
  iterations: 3                  # how many times this was refined
  pipeline_stage: "draft"        # seed | draft | refine | final

judgment:
  score: 0.82                    # 0.0–1.0, agent's own assessment
  criteria:                      # what was evaluated
    personality_alignment: 0.9   # does this sound like the agent?
    originality: 0.7             # is this actually interesting?
    technical_quality: 0.85      # is it well-executed?
  human_review: pending          # pending | approved | rejected | revision_requested
  notes: "strong emotional resonance, technically clean, slightly generic composition"

output:
  type: image                    # image | text | music | video | collage
  format: "png"                  # file format
  dimensions: "4096x4096"        # or word count for text, duration for music
  files:
    - "piece-2026-05-15-001.png"
    - "piece-2026-05-15-001-statement.md"  # artist statement

connections:
  personality_entries:           # links to PERSONALITY.md opinions that influenced this
    - "formed-opinions.md#zfs-stripe"
  journal_entries:
    - "journal/2026-05-14.md"
  related_pieces:
    - "2026-05-12-002"           # earlier piece this evolved from
```

## Usage

- Place in the same directory as the output file(s)
- Read by gallery frontmatter generation
- Provides provenance for anyone viewing the work
- Enables "trace this back to its origin" for researchers and curious viewers
- Feeds into drift detection (patterns in seeds → judgment scores → personality alignment)

## Privacy

Source traces reference internal files (journal, personality). In public gallery deployments, the `seed.source.ref` and `connections` fields should be sanitized to remove internal paths. The seed text and judgment criteria are public-safe — the provenance story is part of the art.
