# brenda-personality-framework

A framework for persistent, evolving AI agent personalities.

## The Problem

AI agents reset every session. They have no memory of who they were, no accumulation of experience, no drift or growth. Every conversation starts from zero — which is fine for a chatbot, but not for anything trying to be a *character*.

## The Architecture

Personality is layered, not monolithic:

```
SOUL.md          → immutable core (values, nature, boundaries)
VOICE.md         → expression layer (tone, vocabulary, banned phrases)
PERSONALITY.md   → evolving state (opinions formed, experiences integrated)
RELATIONSHIPS.md → social context (warmth, trust, strategy per person)
```

Each layer serves a different purpose and has different mutation rules. The soul doesn't change. The voice shifts slowly. The personality evolves with experience. Relationships update as interactions accumulate.

## What This Is

- **Framework** — format specs, schemas, pipeline design in `docs/`
- **Research** — five original documents on agent personality, art, and cross-linguistic identity in `research/`
- **Reference** — working archetype examples (artist, trader) showing real implementation patterns in `reference/`
- **Scripts** — genericized pipeline tools for seed management, drafting, and drift detection in `scripts/`

## What This Isn't

This is not agent infrastructure. No cron configs, no model routing, no API keys, no standing orders. Someone using this framework brings their own runtime.

The `reference/` folder shows what a real implementation looks like, but uses archetypes — not real personality files, not real people.

## Quickstart

1. Read `docs/architecture.md` for the full system design
2. Copy `reference/brenda/` (artist) or `reference/chad/` (trader) as your starting point
3. Customize `SOUL.example.md` — this is the immutable core, get it right
4. Wire your pipeline: seed manager → draft generator → drift detection
5. Let personality accumulate through the journal → reflection loop

## Pipeline

```
experiences → journal → synthesis → personality drift → creative output → judgment
                ↑                                              |
                └──────────── feedback loop ───────────────────┘
```

See `docs/creative-pipeline-spec.md` for the full pipeline design.

## License

MIT
