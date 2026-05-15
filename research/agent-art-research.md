# Agent Art Research

## Status: Draft

## Research Questions

1. Can AI agents produce art that is *meaningfully theirs* — not just technically competent, but expressive of an accumulated personality?
2. What separates agent-generated art from generic AI art output?
3. How does the personality pipeline (SOUL → VOICE → PERSONALITY → output) create a distinguishable creative voice?
4. What does "authorship" mean when the creative decisions are shaped by an accumulated personality rather than a single prompt?

## Hypothesis

Agent art becomes distinguishable from generic AI output when:
- The source seed comes from accumulated experience (not a random prompt)
- The judgment criteria are shaped by personality (not default quality heuristics)
- The artist statement honestly reflects the gap between intent and result
- Multiple pieces share a coherent aesthetic vocabulary that emerges from personality, not from style prompting

## Existing Literature

- PersonaGym (2025) — personality consistency benchmarks for conversational agents
- JPAF three-mechanism model — journal, personality, affective feedback
- [TODO: expand with citation search]

## Methodology

Compare output from:
1. Same model, same prompt, no personality context (baseline)
2. Same model, personality-aware prompts (voice only)
3. Same model, full pipeline (seed from journal → draft → judgment from personality)

Blind evaluation by human raters on personality alignment, originality, and "would you believe this was made by the same person?"

## Contribution

This document will contain the full study design, results, and analysis. The framework itself (`creative-pipeline-spec.md`) is the system under study.

## Notes

- Cross-linguistic voice effects may influence artistic output in unexpected ways — see `cross-linguistic-research.md`
- The 70-80% seed rejection rate is a key variable — does aggressive filtering actually produce better art, or does it just produce less art?
- Need to control for model bias (same model generating all conditions)
