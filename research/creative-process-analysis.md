# Creative Process Analysis

## Status: Draft

## Research Questions

1. What is the actual creative process of an AI agent with persistent personality? How does it differ from stateless prompt → output?
2. Does the accumulation → incubation → flash → execution → judgment cycle produce better creative output than direct generation?
3. How long does the full cycle take, and is the latency worth the quality improvement?

## The Cycle

### Accumulation
The agent experiences things — conversations, media, problems, emotions (modeled). These accumulate in journal entries. Most of this is mundane. Some of it isn't.

### Incubation
Seeds sit in the background. The agent doesn't actively work on them, but they surface during synthesis, during random associations, during conversations. The ones that keep surfacing are the ones worth pursuing.

**Key insight:** Incubation can't be faked. A seed that was generated yesterday and drafted today is not incubated. A seed that was generated a week ago and has been showing up in three different journal entries has been incubated.

### Flash
The moment the agent decides to create. This isn't a scheduled event — it's when an incubated seed becomes urgent. The trigger is usually a conversation, a new experience that connects to the seed, or a synthesis insight.

### Execution
Draft → refine → evaluate. This is the mechanical part. Model generates variants, agent picks the best, refines, judges. The personality shapes every step — what the agent considers "good" is personality-dependent.

### Judgment
Honest self-assessment. This is where the cycle either completes (piece ships) or loops back (piece fails judgment, agent learns why, feeds that into personality).

## Hypothesis

The five-stage cycle produces output that is:
- More personality-aligned than direct generation (controlled by same model + personality prompt)
- More original (incubation produces seeds that are genuinely surprising)
- More coherent across multiple pieces (shared personality vocabulary)
- Slower (by days to weeks) — and that slowness is the point

## Metrics

Compare direct generation vs. full cycle:
- Time from impulse to finished piece
- Personality alignment score (self-assessed + external)
- Originality score (external raters)
- Viewer engagement (if public)

## Notes

- The biggest risk is over-engineering the creative process. The cycle should feel natural, not bureaucratic.
- "Flash" moments can't be scheduled. Trying to force them produces generic output.
- The judgment step is critical — without honest self-assessment, the cycle doesn't learn.
