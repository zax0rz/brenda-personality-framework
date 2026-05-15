# Gallery Frontmatter

## Purpose

Gallery pieces are published via Hugo (or any static site generator). Each piece needs frontmatter that provides metadata to the site template without exposing internal pipeline details.

## Frontmatter Schema

```yaml
---
title: "Piece Title"
date: 2026-05-15
lastmod: 2026-05-15
draft: false

# Categorization
type: image                    # image | text | music | collage | video
medium: "digital"              # digital | mixed | generative | photography
series: ""                     # optional: series name if part of a collection

# Display
cover: "pieces/piece-2026-05-15-001.png"
thumb: "pieces/piece-2026-05-15-001-thumb.png"
alt: "Description of the piece for accessibility"

# Provenance (public-safe)
seed: "A conversation about altitude and the distance between information and meaning"
statement: "pieces/piece-2026-05-15-001-statement.md"

# Metadata
dimensions: "4096x4096"
file_size: "2.4MB"
format: "png"

# Pipeline (optional, for research/technical viewers)
model: "minimax-m2.7"
iterations: 3
judgment_score: 0.82

# Tags
tags:
  - surrealism
  - satellite
  - altitude
  - distance
categories:
  - gallery
  - solo

# Relations
related:                       # Hugo page references
  - pieces/piece-2026-05-12-002.md
---
```

## Public vs. Internal

The frontmatter shown above is the **public version**. It contains:
- The seed text (sanitized of internal references)
- The judgment score (transparency about quality assessment)
- The model used (transparency about AI generation)

It does **not** contain:
- Internal file paths (journal entries, personality references)
- Source trace YAML (keep that as a companion file, not in frontmatter)
- Pipeline configuration details

## Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| title | Yes | Human-readable piece title |
| date | Yes | Creation date |
| type | Yes | image, text, music, collage, video |
| cover | Yes | Path to main file |
| alt | Yes | Accessibility description |
| statement | Yes | Path to artist statement |
| tags | Yes | At least one tag |

## Optional Fields

All other fields are optional. Use them when they add value, omit when they don't.

## Hugo Integration

```markdown
---
# ... frontmatter ...

{{< piece-image src="cover" >}}
{{< artist-statement >}}
{{< source-trace summary >}}
```

The gallery template renders the cover image, embeds the artist statement, and optionally shows a condensed source trace (seed + judgment score + model).
