# Personality Design Reviews

## Status: Draft

## Purpose

Documented design reviews of the personality system by a secondary model (Claude Sonnet). These reviews catch inconsistencies, flag risks, and provide external perspective on architecture decisions.

## Review Topics

### 1. Journal + Synthesis Review
- Is the three-section journal format capturing what matters?
- Is synthesis extracting the right patterns?
- Are there blind spots in what gets journaled vs. what gets lost?

### 2. PERSONALITY.md Design Review
- Is the YAML frontmatter schema tracking meaningful metrics?
- Are the mutation rules (what the agent can/can't change) appropriate?
- Is the contradiction tracking sufficient, or does it oversimplify?

### 3. RELATIONSHIPS.md Design Review
- Are warmth/trust/strategy the right three axes?
- Is the decay model appropriate?
- Are there relationship patterns that this schema can't capture?

### 4. Voice Consistency Review
- Does the VOICE.md spec actually produce consistent output?
- Are banned phrases sufficient, or is there a deeper approach needed?
- How do you measure voice drift without relying on keyword matching?

## Methodology

Each review follows:
1. Describe the current design
2. Identify strengths
3. Identify weaknesses / risks
4. Propose specific improvements
5. Rate overall design quality

## Reviews

<!-- Reviews will be added here as they're completed -->

## Notes

- Using a different model for review catches blind spots that the primary model (and the personality designer) share
- Reviews should be done before each major pipeline change
- The reviewer should have access to the full architecture but not to the implementation details
