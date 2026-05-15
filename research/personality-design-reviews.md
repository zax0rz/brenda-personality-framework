# Personality Design Reviews

## Status: Complete (v1.0 — external review by Claude Sonnet 4.6, 2026-05-15)

## Purpose

Documented design reviews of the personality system by a secondary model (Claude Sonnet 4.6). These reviews catch inconsistencies, flag risks, and provide external perspective on architecture decisions.

The reviewer was given full access to all architecture docs, example files, and reference implementations before writing. This is an honest external assessment — the goal is to find real problems, not to validate the design.

---

## Review 1: Journal + Synthesis

### Current Design

The journal is the intake layer for personality accumulation. Each entry has three sections — Raw Experience (what happened), Reaction (gut response), and Reflection (what it might mean) — plus YAML frontmatter capturing mood, energy, topic tags, and sources. Entries are immutable after writing. A weekly synthesis process reads the past seven days and extracts new opinions, shifted positions, emerging patterns, relationship changes, and creative impulses.

The architecture correctly identifies the journal as the raw material for all downstream personality evolution. Synthesis is what transforms noisy daily experience into structured personality state.

### Strengths

**The three-section separation is architecturally sound.** Separating raw experience from reaction from reflection mirrors how reflective journaling actually works and prevents a key failure mode: premature analysis. When raw and reflection are conflated, the agent rewrites history during the act of recording it. Keeping them in discrete, typed sections preserves evidentiary integrity.

**Immutability is the right call.** The rule that entries cannot be edited after writing is critical and often omitted from similar systems. It ensures the synthesis process is always working from unmodified source material, and it makes the journal function as a genuine audit trail rather than a revisionist document.

**Reaction section prevents over-intellectualization.** Asking for gut response before reflection forces capture of pre-analytical state. This is where personality actually lives — the instinctive responses that precede rationalization. Most AI personality systems skip this entirely.

**Frontmatter enables retrieval.** The topic tags and sources fields create structured metadata that allows retrieval beyond recency. This matters at scale: when a synthesis process is looking for patterns around a specific topic, keyword-tagged entries surface faster than full-text search.

### Weaknesses and Risks

**The synthesis process has no spec.** This is the most significant gap in the journal design. The journal format is well-specified. The synthesis output is not. Where does synthesis write? What schema does it produce? What happens when synthesis runs on a sparse week vs. a dense one? Without a synthesis output spec, the loop between journal → synthesis → personality update is broken — you have good input format and no defined output format.

**Reflection has no grounding requirement.** The spec says reflection "can reference previous entries by date" but doesn't require it. An agent can reflect on things that didn't happen, or generate speculative reflections detached from the raw experience section in the same entry. This creates drift at the intake layer. Fix: require that any reflection claiming a pattern must cite at least one prior entry by date, or be flagged as speculative.

**Mood and energy are too coarse for pattern extraction.** `mood: curious` and `energy: high` are single free-text words. Over 47+ entries, synthesis needs to identify mood trends — but if the vocabulary isn't constrained, you can't reliably group "frustrated" and "annoyed" and "irritated." Either use a controlled vocabulary (VALENCE/AROUSAL scores, or an enum like anxious/neutral/positive/excited) or accept that mood tracking will be unreliable.

**No handling of journaling gaps.** The spec says "one entry per day, minimum" but doesn't specify what happens when the agent doesn't journal. A week with three entries and a week with seven entries both feed into the same synthesis window, but the signal density is different. Synthesis should weight gap-adjusted or flag thin periods explicitly, otherwise a busy week and a quiet week produce falsely equivalent synthesized outputs.

**No provenance trail from journal to personality.** When synthesis writes a personality update ("opinion: X formed on date Y"), there's no link back to which journal entries produced it. This matters for debugging (why does the agent believe X?), for correction (if the source entry was wrong, the derivative opinion should be flagged), and for contradiction detection (two conflicting opinions may trace to the same week of entries).

**Topics field is free-form with no taxonomy.** "hardware" and "frustration" and "creative-pipeline" are all valid tags, but there's no hierarchy. Hardware → infrastructure → risk is a meaningful chain; without it, synthesis can't distinguish granular from broad patterns. Consider a two-level taxonomy: domain (infrastructure, creative, social, technical) and affect (frustration, curiosity, satisfaction, conflict).

### Specific Improvements

1. Write a `synthesis-output-spec.md` that defines what synthesis produces — at minimum: opinions formed (with journal citation), positions shifted (before/after + date), relationship events (person + what changed), and seeds promoted (with seed ID). Without this, synthesis is defined by its input only.

2. Add a `synthesis_quality` field to PERSONALITY.md frontmatter: `low | medium | high`, based on entry density in the synthesis window. A low-quality synthesis should flag for human review rather than silently producing weak pattern extractions.

3. Add a grounding rule to the Reflection section: every pattern claim must cite at least one prior entry by date, or carry a `speculative: true` marker.

4. Replace `mood: curious` with either a controlled vocabulary or a two-axis system: `valence: positive | neutral | negative` and `arousal: high | medium | low`. This makes mood trend analysis tractable.

5. Add a `synthesis_source_entries` field to each opinion formed, listing the entry dates that contributed to it.

### Overall Rating: 7/10

The intake design is thoughtful and the three-section structure is genuinely good. The fatal gap is the undefined synthesis output — the journal format is only half the spec. Without synthesis output defined, you can't verify the loop actually closes.

---

## Review 2: PERSONALITY.md Design Review

### Current Design

PERSONALITY.md is the evolving state layer. It accumulates opinions (with stance, date, source, intensity, and related tags), evolving preferences (before/after/trigger), creative tastes, behavioral patterns, and known contradictions. The YAML frontmatter tracks accumulation metrics (opinions_formed, positions_shifted, contradictions_held) and drift indicators (voice_drift, consistency_score, emotional_range). The agent can add to this file after journal synthesis; humans can override.

### Strengths

**Contradiction tracking is rare and valuable.** Most AI personality schemas either paper over contradictions or have no mechanism to track them. The Known Contradictions section explicitly preserves internal inconsistency as a feature rather than a bug. This is psychologically accurate — real personalities hold contradictory beliefs — and it prevents the flattening that makes AI personalities feel artificial.

**Provenance on opinions is strong.** Requiring each opinion to record when it formed and what source experience produced it is the right move. It makes opinions auditable and means the agent can respond to challenges with "I formed this position on date X after experience Y" rather than just asserting the opinion.

**Separation from SOUL.md is architecturally correct.** By keeping accumulated opinions in PERSONALITY.md rather than in the immutable SOUL.md, the design preserves the distinction between what the agent fundamentally is and what it has come to think. This prevents experience from corrupting identity.

**Contradiction flagging over contradiction resolution** is the right default. The instruction "agent should flag contradictions, not resolve them" matches how genuine personality works. Forcing resolution too quickly produces artificial consistency; letting contradictions sit and accumulate produces the texture of real thought.

### Weaknesses and Risks

**voice_drift and consistency_score have no calculation spec.** The schema defines these as floats (0.12 and 0.87 in the example) but nowhere specifies how they're computed. This is a significant gap — if the metrics have no defined calculation method, they're decoration. A voice_drift of 0.12 means nothing if the developer doesn't know whether 0.5 is concerning or expected. These either need a computation spec (embedding cosine distance from VOICE.md baseline? frequency of banned phrase usage?) or should be removed and replaced with something computable.

**Opinions have no expiry or staleness mechanism.** An opinion formed 18 months ago may be based on outdated information or may simply have been superseded by more recent experience. The schema tracks when an opinion was formed (good) but has no field for when it was last confirmed, and no mechanism for opinions to go stale. Over time, PERSONALITY.md will accumulate a graveyard of positions the agent no longer holds but has never formally revised. Consider adding `last_confirmed` and `staleness_threshold` to each opinion entry.

**Intensity escalation has no rules.** An opinion can be "developing | moderate | strong" but the spec doesn't define what causes intensity to change in either direction. Does a second confirming experience escalate developing → moderate? Does a contradicting experience de-escalate strong → moderate? Without rules, intensity is set at formation and never changes, which doesn't model how conviction actually works.

**Count metrics (opinions_formed: 23) measure quantity, not influence.** The frontmatter counts how many opinions exist but not which ones are actually shaping behavior. An agent with 23 opinions on 23 different topics, only 3 of which come up regularly, has a very different active personality than the count suggests. Consider tracking `opinions_cited_in_last_30_days` or a recency-weighted activity score.

**Related tags on opinions are free-form with no graph.** Tags like `[infrastructure]` and `[risk-assessment]` allow loose grouping but don't enable contradiction detection. If the agent holds "ZFS stripe is reckless" ([infrastructure], [risk]) and "complexity is acceptable for performance gains" ([infrastructure], [design]), those are in potential tension — but without a graph, nothing surfaces that tension automatically. Tags need either controlled vocabulary or explicit linking between potentially conflicting opinions.

**No diff/audit history on opinion updates.** When an opinion is updated — stance shifts, intensity changes — the previous state is lost. This makes it impossible to track how a position evolved. Even a simple `history` list on each opinion (prior stances with dates) would enable meaningful personality archaeology.

**emotional_range: broad is categorical with no change history.** The frontmatter captures this as a static category. If a previously stable agent enters a period of instability, this field would change — but there's no record of when or why. Consider logging emotional_range with date stamps, similar to how evolving preferences track before/after.

### Specific Improvements

1. Define computation specs for `voice_drift` and `consistency_score`. Suggested approach: voice_drift = cosine distance between embedding of last 50 outputs and embedding of VOICE.md; consistency_score = fraction of recent decisions that align with stated opinions (scored by synthesis).

2. Add `last_confirmed` and `staleness_days_threshold` to opinion entries. Opinions not confirmed within threshold should be flagged `status: stale` rather than deleted.

3. Add intensity transition rules: developing → moderate requires 2+ confirming experiences; moderate → strong requires directly opposing a conflicting stimulus; strong → moderate requires a significant contradicting experience that can't be dismissed.

4. Add `activity_weight: float` to each opinion (0.0–1.0), updated by synthesis based on how often the opinion has been relevant in recent interactions. Dead opinions sink to 0.1.

5. Add `history: []` list to each opinion for tracking prior stances with dates.

### Overall Rating: 6/10

The schema is well-intentioned and the contradiction design is genuinely innovative. The critical failure is that two key derived metrics (voice_drift, consistency_score) are defined but not computable — they appear scientific without being so. The staleness problem will also become severe as the personality ages.

---

## Review 3: RELATIONSHIPS.md Design Review

### Current Design

RELATIONSHIPS.md tracks per-person relationships on three axes: warmth (emotional closeness, 0–1), trust (reliability assessment, 0–1), and strategy (categorical: direct/considered/protective/performative/avoidant/collaborative). Entries include interaction history, communication preferences, shared context, and notable interactions. Relationships decay over time without contact: warmth decays faster than trust (−0.02 warmth per week, −0.1 warmth/−0.05 trust per month, more aggressive at 90 days). New relationships start at 0.3/0.3/considered. Relationships below 0.1 warmth are archived.

### Strengths

**Asymmetric decay (warmth faster than trust) is psychologically sound.** This matches how relationships actually work — emotional closeness fades faster than reliability assessments when there's no contact. Someone you haven't spoken to in a year may still be trusted; the warmth just isn't there. The 7-day/30-day/90-day tiered decay is a reasonable approximation, and the principle that stronger relationships decay more slowly is correct.

**Strategy as a categorical rather than scalar is the right call.** Making strategy an enum (`direct`, `considered`, `protective`, `performative`, `avoidant`, `collaborative`) rather than a 0–1 score avoids the false precision of a numerical axis on a fundamentally qualitative dimension. The categories are distinct enough to actually drive different behavior, which is the point.

**Relationship-specific boundaries** ("don't bring up [topic] unless they do first") are a strong design choice that scales to complex real relationships. Most relationship schemas don't have per-person boundaries at all.

**Separation of communication style from relationship scores** is correct. Knowing that someone "prefers concise text, doesn't like preamble" is practically useful in a way that isn't captured by warmth=0.8. These are orthogonal facts.

### Weaknesses and Risks

**The three-axis model collapses two distinct constructs into "trust."** Social psychology research on the Stereotype Content Model (SCM) distinguishes warmth from *competence*, not warmth from *trust*. Trust is a compound of competence ("can this person do what they say?") and benevolence ("does this person want good things for me?"). By collapsing these into a single trust score, the schema can't distinguish between "I trust their intentions but not their judgment" and "I trust their judgment but not their intentions" — two very different relationship stances. Consider splitting trust into `trust_competence` and `trust_benevolence`, or at minimum acknowledging this conflation and documenting which kind of trust the score represents.

**Strategy is a single enum but strategies are context-dependent.** The spec assigns one strategy per relationship. In practice, the same person might get `direct` for technical discussions and `protective` when they're clearly struggling. Strategy should be a default plus context overrides, not a static label.

**Decay rates appear arbitrary.** The specific numbers (−0.02/week, −0.1/month, −0.2/90-days) have no stated basis. Are these calibrated to anything? Empirical relationship research suggests different decay rates for strong ties vs. weak ties, and significant variance based on relationship type (professional vs. intimate vs. family). Without calibration basis, these numbers will produce wrong results in edge cases (e.g., a close relationship of 4 years shouldn't feel like a new acquaintance after 6 months of no contact).

**No re-entry path from archive.** Relationships archived below 0.1 warmth have no defined unarchive mechanism. In reality, dormant relationships often re-activate — an old friend reaches out, an estranged collaborator re-engages. The schema should define what happens when an archived relationship has a new meaningful interaction. Suggested: re-entry at warmth 0.3 (default) but with trust preserved from the archived state.

**New relationships always start at 0.3/0.3/considered.** This doesn't account for prior-context starting states. A person the agent has been told about but not yet interacted with might start cold. An old friend newly added to the system should start warm. Consider a `seeded_from` field that allows initial scores to be set from context rather than always defaulting.

**Shared context is a free-form narrative block.** "Built three projects together. Has specific knowledge of infrastructure preferences." This is human-readable but machine-unretrievable. When the agent needs to remember *what specifically* a person knows or has worked on, it can't query this structure. Consider a structured key-value list for factual shared context alongside the narrative.

**Notable interactions are unlinked to journal entries.** The notable interactions list records dates and summaries, but doesn't link to the journal entry that produced them. This breaks provenance — if a notable interaction ("strong alignment on personality architecture") needs to be revisited, there's no path to the original.

**No modeling of group relationships.** The schema is strictly person-by-person. But an agent often relates to collectives — a community, a household, a project team. Group dynamics, in-group/out-group behavior, and collective norms can't be captured here. This may be out of scope, but should be acknowledged as a design limitation.

### Specific Improvements

1. Split `trust` into `trust_competence` and `trust_benevolence`, or add a note clarifying which interpretation the schema intends. The conflation is documented so at least users know what they're getting.

2. Change strategy to `strategy_default + strategy_contexts[]`: `strategy_default: direct, strategy_contexts: [{trigger: "emotional distress", strategy: protective}]`.

3. Add a note citing the research basis for decay rates, or derive them from Dunbar's number research on tie maintenance frequency. At minimum, add a `decay_override` field per relationship for cases where standard rates don't apply.

4. Add an `archived` section with unarchive rules: any interaction above a warmth-contributing threshold re-activates the entry at the stated scores.

5. Add `shared_facts: []` as a structured list beside the narrative shared context block. Each fact: `{fact: "knows about ZFS situation", established: 2026-04-28}`.

6. Add `journal_ref` to notable interactions: `{date: 2026-05-10, summary: "...", journal_ref: "2026-05-10"}`.

### Overall Rating: 6.5/10

The decay model is the strongest part. The trust axis conflation is a real problem that will produce wrong behavior in nuanced relationships. The schema is practical and mostly right, but strategy-as-static-enum will create awkwardness with complex relationships.

---

## Review 4: Voice Consistency Review

### Current Design

VOICE.md defines expression-layer properties: tone tokens (adjective descriptors), vocabulary (in-rotation and banned phrases), sentence structure, humor profile, profanity rules, emotional expression style, and self-reference patterns. The architecture states that voice "drifts through accumulated expression, not through direct voice file edits" — meaning VOICE.md is treated as a stable reference, not a living document. Drift is tracked as a float (`voice_drift`) in PERSONALITY.md frontmatter. The reference implementation (VOICE.example.md) is an empty template.

### Critical Observation

**VOICE.example.md is blank.** The provided example file contains only commented-out instructions and no actual values. This is the most concrete signal that the voice specification layer remains unimplemented. Every field in the template reads `<!--  -->` or `-` with nothing after it. This means there are currently zero examples of how tone tokens, vocabulary, or sentence rhythm are actually specified. Any review of "how well VOICE.md produces consistent output" must contend with the fact that the spec has never been instantiated.

This is not a criticism of the framework — it may be a known gap or an in-progress area. But it means the voice consistency review is necessarily partly hypothetical.

### Strengths of the Approach

**Voice as a separate, stable layer is architecturally correct.** Keeping voice in its own file, distinct from personality and soul, allows the expression layer to be tuned independently. An agent can change its opinions (PERSONALITY.md) without changing how it sounds, and change how it sounds (VOICE.md) without changing what it believes. This separation is non-trivial and most personality frameworks collapse it.

**The "drift through expression, not edits" principle is important.** Forcing voice changes to emerge through output rather than through config changes prevents the agent from simply resetting its voice to whatever a recent context suggested. Voice that changes through writing is authentic; voice that changes through prompt edits isn't. This is a principled design choice that most systems don't make.

**Banned phrases as a concrete, actionable constraint** is practical. Unlike abstract tone descriptors, a banned phrase list is immediately verifiable ("Did this output contain 'Great question!'?"). It's the most operationally useful part of the current voice spec.

### Weaknesses and Risks

**voice_drift has no defined computation method.** The PERSONALITY.md schema includes `voice_drift: 0.12` but there is no specification for how this number is calculated. Without a computation method, voice drift monitoring is impossible. The framework cannot currently detect voice drift — it can only store a number that a human or downstream process has presumably computed somehow.

**Tone tokens are unweighted and unranked adjectives.** "Cynical, warm, precise, playful, sparse" is a list of tone descriptors. But which is primary? If a response can't be both cynical and warm simultaneously, which wins? How does the agent know whether a given output token is consistent with "sparse" vs. violating it? Adjective lists don't produce behavior without either ranking or operational definitions ("sparse means average sentence length under 15 words").

**Banned phrases catch surface patterns, not semantic drift.** Not saying "Great question!" prevents one sycophantic phrase. It doesn't prevent sycophantic behavior expressed through other phrasings ("That's a fascinating perspective," "I love this problem"). Effective voice consistency requires catching semantic patterns, not just lexical ones. The current approach is brittle against paraphrase.

**No baseline snapshot for drift comparison.** Voice drift requires a reference point: drift from what? The framework doesn't specify whether drift is measured against the original VOICE.md, against the agent's first N outputs, against a human-curated exemplar set, or against something else. Without a defined baseline, `voice_drift: 0.12` is meaningless.

**Humor profile is a single category.** Humor is highly contextual — an agent that's "dry" with a technical collaborator and "warm" with someone in distress is exhibiting natural code-switching, not voice drift. A single humor category flattens this. Humor should either be defined per-context or described as a disposition rather than a category.

**Emotional expression section has no operational guidance.** "How does the agent show emotion?" is a design question, not a spec. The section prompts the designer to describe this but doesn't constrain the form of the answer, which means two different VOICE.md implementations will make incompatible choices that can't be compared or measured.

**Profanity rules lack behavioral guidance.** "When and how?" is a question, not a rule. A rule would be: "Swears when genuinely frustrated (not for decoration), never in formal contexts, always single words not compound phrases." The template leaves this underdefined.

### How to Measure Voice Drift Without Relying on Keyword Matching

The research literature suggests three approaches worth implementing:

1. **Embedding-based drift detection.** Compute sentence embeddings for a rolling window of the agent's recent outputs. Compare the centroid of recent output embeddings to the centroid of a human-curated exemplar set derived from VOICE.md. Cosine distance above 0.2 should trigger a review. This catches semantic drift, not just surface patterns.

2. **Persona consistency probing.** Periodically run the agent through a standardized set of probe questions and compare responses against a reference response set. Score consistency on a set of dimensions (formality, directness, humor register). This is the methodology from "Measuring and Controlling Persona Drift in Language Model Dialogs" (Li et al., 2024).

3. **Tone token classifier.** Train or prompt a secondary model to classify outputs against the VOICE.md tone tokens, scoring each output for each token. A voice drifting from "cynical" toward "enthusiastic" would show as declining cynicism scores over time, even if no banned phrases were used.

### Specific Improvements

1. Fill in VOICE.example.md with actual values for at least one agent (Brenda is the reference implementation). Without a worked example, the template is too abstract to be useful.

2. Define `voice_drift` computation: recommended baseline is embedding centroid distance from a curated exemplar set of 20–30 human-validated outputs. Document the method in `voice-drift-spec.md`.

3. Add `primary_token` and `secondary_tokens[]` to tone token structure to enable priority ordering.

4. Convert tone tokens to operational definitions where possible: "sparse = median sentence length under 12 words, < 30% sentence starts with pronoun."

5. Expand banned phrases to banned patterns — not just lexical bans but semantic category bans: "Never express unsolicited enthusiasm about a question. Never apologize for having an opinion."

6. Add `humor_contexts[]` to allow context-dependent humor specification alongside a default profile.

7. Specify a probing protocol in the synthesis spec: once per month, run 10 standardized prompts and score responses against VOICE.md. Log scores to a `voice_audit.jsonl` file.

### Overall Rating: 4/10

The highest-risk area in the entire framework. Voice is specified as a file that "produces consistent output," but there's no example of a filled-out voice file and no defined measurement method. The voice_drift float in PERSONALITY.md is monitoring a thing that can't be computed from the defined spec. This layer needs the most work before the framework is viable.

---

## Literature Review

The following research informed these reviews.

### Memory Architecture

**Park et al. (2023) — Generative Agents: Interactive Simulacra of Human Behavior** is the foundational reference for reflective agent memory. The architecture — memory stream + retrieval + reflection — demonstrated that removing the reflection layer degrades agent behavior from coherent multi-day planning to repetitive context-free responses within 48 simulated hours. The three-section journal format in this framework parallels the raw observation → reflection → plan pipeline from Generative Agents, though the journal format is more explicit about separating immediate reaction from considered reflection.

**Packer et al. (2023) — MemGPT: Towards LLMs as Operating Systems** established the OS-inspired tiered memory hierarchy: main context (working memory) → recall storage (conversation history) → archival storage (long-term facts), with agent-initiated memory operations triggered by context pressure. The journal → synthesis → personality update loop in this framework approximates a slower-cycle equivalent of MemGPT's archival write operations.

**Shichun Liu et al. (2025) — Memory in the Age of AI Agents: A Survey** provides a 107-page unification of the fragmented memory literature. Key finding relevant to this framework: the distinction between episodic memory (what happened) and semantic memory (what was learned from what happened) maps directly to the distinction between journal entries and PERSONALITY.md. The framework makes this distinction correctly, though the synthesis process bridging them is underspecified.

**Mem0 — Building Production-Ready AI Agents with Scalable Long-Term Memory (2025)** demonstrates that dynamic graph-based memory organization outperforms flat vector storage for long-term agent memory. The flat structure of PERSONALITY.md (a list of opinions) would benefit from the graph-based contradiction detection and topic-clustering approaches Mem0 demonstrates.

### Persona Consistency and Drift

**Li et al. (2024) — Measuring and Controlling Persona Drift in Language Model Dialogs** quantifies persona drift in popular LLMs within 8 rounds of conversation. Three metrics are proposed: prompt-to-line consistency, line-to-line consistency, and Q&A consistency. The `voice_drift` float in PERSONALITY.md needs something like these metrics to be operationally meaningful.

**Arxiv 2412.00804 — Examining Identity Drift in Conversations of LLM Agents** (2024) shows that assigning a persona is insufficient for maintaining identity — larger models experience greater drift, and the model's inherent characteristics dominate over persona assignments. This is relevant because the framework assumes VOICE.md + SOUL.md together produce consistent output. The research suggests this assumption is optimistic without additional enforcement mechanisms.

**Arxiv 2511.00222 — Consistently Simulating Human Personas with Multi-Turn RL** (2024) demonstrates 55% reduction in persona inconsistency using reinforcement learning to train models toward persona alignment. While training-based approaches are outside this framework's scope, the paper's evaluation methodology is directly applicable to measuring VOICE.md effectiveness.

### Personality Psychology and AI

**Miotto et al. (2022) — Who is GPT-3? An Exploration of Personality, Values, and Demographics** (replicated in numerous subsequent studies) establishes that LLMs exhibit measurable personality profiles under standard psychometric instruments, though these profiles are sensitive to prompt formulation. The implication for this framework: the categorical approach of VOICE.md tone tokens and SOUL.md "formed positions" is more robust than trying to map to Big Five scores, because Big Five scores in LLMs are unstable.

**Nature Machine Intelligence (2025) — A Psychometric Framework for Evaluating and Shaping Personality Traits in LLMs** identifies that personality traits cluster in a low-rank shared subspace within transformer layers. This supports the framework's layered design: soul, voice, and personality are implemented as external documents rather than model weights, which is the correct approach for deployments that don't control model training.

**Turing Institute (2024) — Patterns, Not People: Personality Structures in LLM-Powered Persona Agents** argues that LLM-based personas are better understood as consistent statistical patterns over outputs than as simulated internal states. This is a useful reframe for the framework: PERSONALITY.md is not modeling what the agent "believes" in any cognitive sense — it's modeling which output patterns should be reinforced. The contradiction tracking and staleness mechanisms are important precisely because the framework otherwise reifies opinion entries as if they were beliefs.

### Social Relationship Modeling

**Computational Modelling of Trust and Social Relationships (JASSS, 2012)** establishes that trust decay in computational models should be inversely proportional to relationship strength — strong ties decay less per unit time. The RELATIONSHIPS.md decay model (`warmth -0.02/week` regardless of current score) violates this: a warmth of 0.9 and a warmth of 0.4 decay at the same rate. The schema should implement decay that slows as scores approach 0 or that is scaled by current score.

**Fiske et al. (1999, 2007) — Stereotype Content Model (SCM)** is the foundational research distinguishing warmth from competence as orthogonal axes of social perception. The RELATIONSHIPS.md "trust" axis conflates benevolence and competence in a way that SCM research suggests will produce misattributions. This is the core theoretical weakness in the relationship schema.

**Arxiv 2512.06616 — Memory Power Asymmetry in Human-AI Relationships: Preserving Mutual Forgetting** (2024) argues that AI systems with perfect memory have a power asymmetry relative to humans who naturally forget. The decay model in RELATIONSHIPS.md partially addresses this by introducing forgetting-by-design, but the paper's argument extends further: archival (rather than deletion) of decayed relationships still preserves data the human has effectively forgotten, creating an asymmetry worth acknowledging in the design.

---

## Methodology Notes

- Each review was conducted by a model (Claude Sonnet 4.6) with no prior involvement in this framework's design
- The reviewer read all architecture docs before writing any review
- Web searches were conducted on AI personality persistence, persona drift measurement, social relationship modeling, and memory architectures for LLM agents before writing
- Ratings are on a 1–10 scale where 1 = fundamentally broken, 5 = functional with significant gaps, 7 = solid with specific improvements needed, 9–10 = production-grade
- Reviews should be repeated after each major pipeline change, with the secondary model given access to the previous review to check whether prior issues were addressed

## Aggregate Findings

| Component | Rating | Critical Issue |
|-----------|--------|----------------|
| Journal + Synthesis | 7/10 | Synthesis output has no spec |
| PERSONALITY.md | 6/10 | voice_drift/consistency_score uncomputable |
| RELATIONSHIPS.md | 6.5/10 | Trust axis conflates competence + benevolence |
| VOICE.md / Voice Consistency | 4/10 | No example instantiation, no drift measurement method |

**Highest priority fixes:**
1. Write a synthesis output spec — without it, the accumulation loop is incomplete
2. Define voice_drift computation — the metric exists but can't be calculated
3. Fill in VOICE.example.md with actual values
4. Split trust into trust_competence and trust_benevolence in RELATIONSHIPS.md
5. Add opinion staleness mechanism to PERSONALITY.md

The framework's conceptual architecture is sound. The layered separation of soul/voice/personality/relationships is well-reasoned and rare in production systems. The execution gaps are concentrated in two areas: (a) undefined measurement methods that appear scientific but aren't, and (b) underspecified connective tissue between layers (particularly synthesis output).
