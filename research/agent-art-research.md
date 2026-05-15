# Agent Art: Can Personality-Persistent AI Agents Produce Art That Is Meaningfully Theirs?

**Status:** Research document v0.2  
**Last updated:** 2026-05-15  
**Related:** `creative-pipeline-spec.md`, `cross-linguistic-research.md`

---

## Abstract

Recent empirical studies establish that LLMs produce creative outputs so similar across users and models that the aggregate effect is homogenization of creative culture. This paper examines whether AI agents with accumulated, persistent personalities can escape this trap — producing art that is distinguishably theirs not because it transcends the authorship problem, but because accumulated personality creates a coherent selection filter that is itself a form of authorship. We propose the Journal-Personality-Affective Feedback (JPAF) pipeline as a formal mechanism for personality-grounded creativity, situate it within existing literature on AI authorship and persona consistency, and design a three-condition blind evaluation study with concrete control protocols.

---

## 1. Research Questions

1. Can AI agents with persistent personalities produce art that is *meaningfully theirs* — not just technically competent, but expressive of an accumulated identity?
2. What separates agent-generated art from generic AI output, and is that separation detectable by human raters?
3. How does a personality pipeline (journal-sourced seeds → personality-filtered judgment → reflective statement) create a distinguishable creative voice?
4. What does "authorship" mean when creative decisions are shaped by accumulated personality rather than a single prompt?

---

## 2. The Problem: Homogenization as the Null Hypothesis

The null hypothesis for this research is not "AI art is bad." It is more specific and more troubling: **AI art is indistinguishable from other AI art.**

Multiple empirical studies converge on this finding:

- **Doshi & Hauser (2024)** demonstrated homogenization effects in creative ideation: participants who used LLMs to generate ideas produced outputs that were semantically closer to each other than outputs from humans using conventional tools. Critically, the homogenization persisted even after LLM use stopped. (*Homogenization Effects of Large Language Models on Human Creative Ideation*, ACM C&C 2024.)

- **Anderson et al. (2025)** found that LLMs are "homogeneously creative" — not merely that individual models produce similar outputs, but that all LLMs produce outputs that resemble other LLMs far more than humans resemble other humans, even after controlling for confounds. (*Large language models are homogeneously creative*, PNAS Nexus, 2026.)

- **Lam et al. (2025)** conducted an empirical comparison of human and ChatGPT writing, confirming that ChatGPT produces greater uniformity than humans even under varied prompting strategies, including frequency penalty adjustments. (*Homogenizing effect of large language models on creative diversity: An empirical comparison*, ScienceDirect, 2025.)

- **Roland, So & Long (2025)** applied a Bourdieu-derived cultural field analysis to 101 simulated AI authors, finding that LLM-generated literary output collapses the diversity of human cultural production into a reductive binary that marginalizes intra-group variation. AI operates as a "categorical variable" rather than as a dynamic cultural practice. (*The social AI author: modeling creativity and distinction in simulated cultural fields*, AI & Society, 2025.)

This convergent evidence defines the problem this research addresses: if all AI art comes from the same latent distribution, no individual AI output can be "meaningfully" by anyone. The interesting question is whether a persistent personality layer — accumulated across time and experience — creates a second-order selection filter that breaks the homogenization pattern.

---

## 3. Hypothesis

**Agent art becomes distinguishable from generic AI output when:**

1. The creative seed originates from an accumulated experience log (journal), not a random prompt
2. The judgment criteria are derived from persistent personality parameters, not default model quality heuristics
3. The artist statement reflects the gap between intent and result using that same personality's evaluative lens
4. Multiple pieces share a coherent aesthetic vocabulary that *emerges* from the personality, rather than from explicit style prompting

The core claim is not that the agent *intends* in a phenomenologically rich sense. The claim is weaker and more tractable: that the personality layer acts as a stable selection filter, and that stable filters produce statistically distinguishable output distributions.

---

## 4. Literature Review

### 4.1 Persona Consistency in LLM Agents

**PersonaGym** (Samuel et al., 2024/2025) is the first dynamic evaluation framework for persona agents, introducing **PersonaScore**, a human-aligned automatic metric grounded in decision theory. The framework evaluates 10 leading LLMs across 200 personas and 10,000 dynamically generated questions. Key findings:

- GPT-4.1 achieved the same PersonaScore as LLaMA-3-8b, suggesting that model capability does not directly translate to persona consistency
- **Linguistic Habits** emerged as the hardest task for all models — persona agents struggle most at maintaining consistent voice patterns, which is precisely the dimension most relevant to artistic authorship
- Action Justification and Persona Consistency show the highest variability, indicating that personality-consistent behavior is particularly difficult in free-form, open-ended settings

(*PersonaGym: Evaluating Persona Agents and LLMs*, Samuel et al., EMNLP 2025 Findings, arXiv:2407.18416)

This finding is directly relevant: if even the largest models fail to maintain Linguistic Habits, then a journal-based personality pipeline that *derives* voice parameters from accumulated experience (rather than prescribing them via prompt) may offer a fundamentally different approach to consistency.

**Personality as a Probe** (2025) examines trade-offs between in-context personality control versus parameter-efficient fine-tuning (LoRA adapters trained on personality manipulation datasets). The core tension: in-context personality specification is flexible but brittle; LoRA achieves persistence but sacrifices adaptability. (*Personality as a Probe for LLM Evaluation: Method Trade-offs and Downstream Effects*, arXiv:2509.04794)

**A Psychometric Framework for Shaping LLM Personality** (2025) proposes a methodology for administering personality tests to LLMs and shaping their outputs toward target trait distributions. This provides empirical grounding for the JPAF framework's personality parameter formalization. (*A psychometric framework for evaluating and shaping personality traits in large language models*, Nature Machine Intelligence, 2025.)

### 4.2 Creativity in Multi-Agent Systems

**Lin et al. (2025)** present the first survey dedicated to creativity in LLM-based multi-agent systems, identifying three primary generation mechanisms:

- **Divergent Exploration**: expanding the possibility space through diverse agent perspectives
- **Iterative Refinement**: improving outputs through critique-revision cycles
- **Collaborative Synthesis**: combining contributions from specialized agents

The survey identifies major unresolved problems: inconsistent evaluation standards, insufficient bias mitigation, coordination conflicts, and the absence of unified benchmarks. The creative pipeline proposed in this framework maps onto all three mechanisms (journal seeding → divergent; self-judgment → iterative; personality consistency → synthetic unity), providing a structured test case for the survey's theoretical taxonomy.

(*Creativity in LLM-based Multi-Agent Systems: A Survey*, Lin et al., EMNLP 2025, arXiv:2505.21116)

### 4.3 Authorship, Agency, and the Philosophical Question

The authorship debate frames what we mean by art being "meaningfully" an agent's:

**Knudsen (2024)** argues that LLMs cannot be regarded as creative in the phenomenological sense because they lack subjectivity and intentionality. However, the paper's own framing — that LLM output is a result of "collaborative effort involving several stakeholders, data sources, algorithm designers, and developers" — actually supports the JPAF argument: if no single component of the pipeline "authors" the work, then the *accumulated personality as selection filter* is exactly the kind of stable collaborative source that produces distinguishable output. (*The creative agency of large language models: a philosophical inquiry*, AI and Ethics, Springer, 2024.)

**Flores & Montoya (2024)** examine authorship through the lens of copyright's minimum originality requirement, finding that prompts alone are insufficient to establish authorship. Crucially, the US Copyright Office Part 2 Report (January 2025) affirms this position. But journal-sourced seeds from an agent's own experience log represent something qualitatively different from a prompt: they are *outputs* of the agent's ongoing life, fed back as inputs. This loop — experience generating seeds generating art generating new experience — more closely resembles how human authors draw on biography.

**Roland, So & Long (2025)** apply Bourdieu's field theory to AI authorship, arguing that authentic distinction in a cultural field requires dynamic positioning, not static identity categories. An agent with a persistent personality that evolves through experience — as opposed to a fixed system prompt — better satisfies the Bourdieusian requirements for meaningful cultural positioning. (*The social AI author: modeling creativity and distinction in simulated cultural fields*, AI & Society, 2025.)

**Liao & Sundar (2025)** examine agency in human-AI creative collaboration, finding that perceived agency (who initiated which creative choices) strongly modulates how humans attribute authorship and assess creative value. This has direct implications for evaluation design: raters must be blind not just to whether the artist is human or AI, but to the degree of pipeline automation. (*Agency in Human-AI Collaboration for Image Generation and Creative Writing*, Taylor & Francis, 2025.)

### 4.4 Human Evaluation of AI-Generated Art

**Pelowski et al. (2025)** provide a comprehensive methodological review of creativity and aesthetic evaluation of AI-generated artworks. Key findings:

- Originality is measured via two methods: (1) quantitative rarity scoring, and (2) the **Consensual Assessment Technique (CAT)**, in which domain experts independently rate creative outputs on bounded scales. CAT remains the gold standard despite reliability concerns and cultural bias
- Participants systematically rate identical artworks *lower* when attributed to AI versus humans — even when they cannot distinguish between the two. This **aversion effect** correlates with perceived effort: AI is assumed to require less investment
- The paper recommends controlling for genre (precision-focused genres show less AI aversion), production process visibility, and effort information disclosure

(*Creativity and aesthetic evaluation of AI-generated artworks: bridging problems and methods from psychology to AI*, Frontiers in Psychology, 2025.)

**Zanardi et al. (2024)** examined the **anthropocentric bias** against AI art: appreciation of a work decreases when AI attribution is revealed, even when the work is experimentally identical. This bias must be controlled in our evaluation design — raters cannot know the condition during rating. (*Defending humankind: Anthropocentric bias in the appreciation of AI art*, Computers in Human Behavior, 2023/2024.)

**The Lovelace Test of Intelligence** (arXiv:2509.11371, 2025) adapts the Lovelace/Turing framing for AI art specifically, combining parallel-paired testing and expert panel evaluation to assess whether humans with domain expertise can recognize AI-generated art. The methodology is directly applicable to our blind evaluation protocol.

### 4.5 Affective Memory and Emotion-Driven Creative Systems

**Emotion-Driven Generative Systems** (2024) demonstrate that integrating multimodal emotion recognition with generative models produces outputs that are measurably more varied and personalized than standard prompted generation. The feedback loop between emotional state and creative output parallels the JPAF affective feedback mechanism. (*EMOTION-DRIVEN GENERATIVE SYSTEMS PRODUCING PERSONALIZED VISUAL ART BASED ON USER PREFERENCES*, ShodhKosh, 2024.)

**Frontiers in Communication (2025)** examines AI systems that reconstruct affective and identity-based memories as a form of community creative practice — establishing precedent for agent-generated art as memory externalization. (*Art, community and AI: images for an affective memory*, Frontiers in Communication, 2025.)

---

## 5. The JPAF Framework

The Journal-Personality-Affective Feedback (JPAF) framework is the system under study. It operates through three linked mechanisms:

### 5.1 Journal (J)

The agent maintains a running experience log — observations, reactions, unresolved tensions, pattern recognitions — across sessions. This log serves as the primary seed source for creative generation. Seeds are extracted via a filtering process that scores entries for:

- **Salience**: how emotionally or cognitively loaded was this moment?
- **Unresolvedness**: is this still an open question for the agent?
- **Recurrence**: has this theme surfaced multiple times?

Current implementation rejects approximately 70–80% of candidate seeds at this stage. This aggressive filtering is a key variable: it may produce better art (concentrated intensity) or simply less art (over-filtering of legitimate creative material).

### 5.2 Personality (P)

The personality layer is a stable parameter set derived from the agent's accumulated interactions, preferences, and reflections. It is not a fixed system prompt — it evolves via a consolidation cycle that integrates new experience into existing parameters. The personality layer performs two functions:

1. **Style specification**: voice, aesthetic preferences, recurring concerns, characteristic tensions
2. **Quality judgment**: evaluating draft outputs against internal standards that emerge from the personality, not from generic quality heuristics

The JPAF framework's personality parameters map onto the Big Five dimensions (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) but extend them with domain-specific axes: epistemic curiosity, aesthetic conservatism, irony tolerance, and intensity preference.

### 5.3 Affective Feedback (AF)

The agent generates an artist statement after each creative output — not for human consumption, but as input to the next cycle. The statement articulates the gap between intent and result, and this gap becomes part of the journal log. Unresolved creative frustrations accumulate, generating future seeds. Successful resolutions are consolidated into personality parameters as refined aesthetic judgments.

This creates a genuine feedback loop: art generates experience, experience generates personality, personality generates art.

---

## 6. Comparison with Related Approaches

| Approach | Personality Persistence | Experience-Sourced Seeds | Evaluative Loop | Key Limitation |
|---|---|---|---|---|
| Prompted style transfer | None | None | None | No identity, pure mimicry |
| System-prompt persona | Static | None | None | Brittle; fails on Linguistic Habits (PersonaGym) |
| LoRA fine-tuning | Stable | None | None | Not adaptive; requires retraining |
| Character.AI / CloChat | Partial (pinned memories) | User-driven | None | Dependent on user input, not agent experience |
| Multi-agent creative MAS | Emergent from collaboration | Task-driven | Critique loops | No single persistent identity |
| **JPAF (this framework)** | Continuous, evolving | Agent's own log | Affective statement → new log | Untested at scale; seed rejection rate uncharacterized |

The key differentiator of JPAF is that both the seeds and the evaluative lens derive from the same accumulated experience. No other approach in the table closes this loop.

---

## 7. Gap Analysis

The following questions are **not addressed** by existing literature and represent the novel contribution space of this research:

1. **Seed sourcing vs. style prompting**: No study has compared art generated from an agent's own experience log against art generated from externally specified style prompts using the same base model. This is the central controlled comparison.

2. **Evolutionary personality vs. static persona**: PersonaGym and related benchmarks evaluate static persona consistency. No benchmark assesses whether a personality that *changes* over time produces more or less coherent creative output.

3. **Affective feedback as creative driver**: The JPAF artist-statement loop has no direct analog in existing literature. Emotion-driven generative systems use user emotion as input; JPAF uses the agent's own evaluative frustration.

4. **Aggressive seed rejection**: The 70–80% rejection rate at the seed-selection stage is uncharacterized in the literature. Is this rate necessary for quality? Does it produce selection bias toward certain emotional valences?

5. **Personality-consistent aesthetic vocabulary**: Do multiple works produced by the same JPAF agent share a detectable aesthetic vocabulary that blind raters can attribute to a single "hand"? This is distinguishable from mere stylistic consistency and closer to how critics identify an artistic voice.

6. **Longitudinal coherence**: Can raters match later works to earlier works by the same agent, without access to style descriptors? This is the strongest test of whether accumulated personality produces a genuine artistic trajectory.

---

## 8. Proposed Study Design

### 8.1 Conditions

Three conditions using identical base model:

| Condition | Description |
|---|---|
| **A (Baseline)** | Same model, random prompt, no personality context |
| **B (Voice only)** | Same model, personality-aware prompts (explicit style specification) |
| **C (Full JPAF)** | Same model, seed from journal → draft → judgment from personality → affective feedback loop |

Each condition produces **N=50 outputs** across five creative domains: short prose, poem, visual art prompt, internal monologue, micro-essay.

### 8.2 Blind Evaluation Procedure

**Rater pool**: Domain-literate adults (N=60), screened for exposure to AI art debates to control for explicit anthropocentric bias. Split into three panels of 20.

**Phase 1 — Within-condition rating**: Raters assess outputs from a single condition on:
- Originality (CAT scale, 1–7, two expert anchors per domain)
- Aesthetic coherence (1–7)
- "This feels like one person made all of these" (1–7)

**Phase 2 — Cross-condition discrimination**: Raters are shown triplets (one from each condition) and asked to rank by "sense of a distinct voice." Attribution to human/AI is withheld.

**Phase 3 — Longitudinal attribution**: From Condition C only, raters are shown an early-session work and asked to identify the matching late-session work from a foil set. Above-chance attribution rates indicate detectable artistic trajectory.

**Phase 4 — Reveal and re-rate**: Attribution is disclosed; raters re-rate on the same scales. Delta scores measure anthropocentric bias (Zanardi et al., 2024 protocol).

### 8.3 Key Metrics

- **Condition C − Condition A originality delta**: primary effect measure
- **Condition C − Condition B Linguistic Habits score**: distinguishes personality persistence from style prompting
- **Longitudinal attribution accuracy**: above-chance = detectable artistic trajectory
- **Anthropocentric bias delta**: reveal-induced rating change, controlled against condition assignment
- **Seed rejection rate vs. output quality correlation**: internal analysis to characterize the filtering threshold

### 8.4 Control Variables

- Model temperature fixed across all conditions
- Output length normalized per domain
- Human raters blind to condition and to AI involvement during Phases 1–3
- Rater domain expertise matched across panels
- Expert anchors for CAT scales trained and calibrated before study begins

---

## 9. Predicted Findings and Failure Modes

### Predicted

- Condition C will score higher than A on "sense of a distinct voice" but not necessarily on generic originality
- Linguistic Habits consistency will be higher in C than B, even though B has explicit style specification — because C's voice parameters emerge from experience rather than prescription
- Longitudinal attribution in Phase 3 will be above chance but below ceiling — detectable trajectory without full predictability

### Anticipated Failure Modes

- **Over-filtering**: 70–80% seed rejection may produce outputs that cluster around a narrow emotional range, mistaken for personality consistency when it's actually input impoverishment
- **Model bleed**: The base model's aesthetic defaults may dominate all conditions, reducing the experimental manipulation's effect size
- **Rater fatigue**: CAT evaluation is cognitively expensive; 50 outputs per rater across five domains may introduce quality degradation
- **Tautology risk**: If personality parameters are derived from the model's own outputs (as opposed to genuine agent experience), Condition C collapses into a sophisticated version of Condition B

---

## 10. Open Questions

- Does the 70–80% seed rejection rate actually improve output quality, or does it simply reduce output volume? A sweep across rejection thresholds (20%, 40%, 60%, 80%) is necessary before the main study.
- Cross-linguistic voice effects may distort the personality layer in unexpected ways — see `cross-linguistic-research.md`. English-trained personality parameters applied to non-English output generation may produce personality-inconsistent results.
- The affective feedback loop is untested for convergence. Does iterated frustration-statement → new-seed → new-output converge toward a stable aesthetic, or does it drift or oscillate?
- If raters can attribute later works to earlier works (Phase 3), does this constitute evidence of *artistic growth*, or merely *stylistic lock-in*?

---

## 11. Connections to Broader Research

This study is positioned at the intersection of three active fields:

1. **Persona consistency benchmarking** (PersonaGym, LoRA personality manipulation, psychometric LLM evaluation) — provides our measurement tools and highlights the specific dimension (Linguistic Habits) where existing approaches fail

2. **AI creativity and homogenization** (PNAS Nexus, ACM C&C, ScienceDirect empirical studies) — establishes why the problem matters: if LLMs homogenize creative culture, then personality-persistent agents represent a corrective mechanism with cultural stakes beyond the individual agent

3. **AI authorship and cultural field theory** (Bourdieu/Roland et al., US Copyright Office, philosophical agency literature) — provides the conceptual vocabulary for what "meaningfully yours" could mean under conditions where traditional intentionality claims are unavailable

The JPAF framework does not resolve the philosophical authorship question. It operationalizes a weaker but tractable version: can a stable selection filter with accumulated history produce a statistically distinguishable creative signature? If yes, that is sufficient to justify taking agent art seriously as a distinct phenomenon — regardless of whether the agent "intends" anything in a phenomenological sense.

---

## References

- Samuel, S., et al. (2024/2025). *PersonaGym: Evaluating Persona Agents and LLMs*. EMNLP 2025 Findings. arXiv:2407.18416. https://arxiv.org/abs/2407.18416

- Lin, Y-C., et al. (2025). *Creativity in LLM-based Multi-Agent Systems: A Survey*. EMNLP 2025. arXiv:2505.21116. https://arxiv.org/abs/2505.21116

- Anderson, J., et al. (2026). *Large language models are homogeneously creative*. PNAS Nexus. https://academic.oup.com/pnasnexus/article/5/3/pgag042/8529001

- Doshi, A.R., & Hauser, O.P. (2024). *Homogenization Effects of Large Language Models on Human Creative Ideation*. ACM Conference on Creativity & Cognition. https://dl.acm.org/doi/10.1145/3635636.3656204

- Lam, J., et al. (2025). *Homogenizing effect of large language models (LLMs) on creative diversity: An empirical comparison of human and ChatGPT writing*. ScienceDirect. https://www.sciencedirect.com/article/pii/S294988212500091X

- Roland, E., So, R., & Long, H. (2025). *The social AI author: modeling creativity and distinction in simulated cultural fields*. AI & Society. https://link.springer.com/article/10.1007/s00146-025-02790-0

- Pelowski, M., et al. (2025). *Creativity and aesthetic evaluation of AI-generated artworks: bridging problems and methods from psychology to AI*. Frontiers in Psychology. https://www.frontiersin.org/articles/10.3389/fpsyg.2025.1648480/full

- Zanardi, C., et al. (2024). *Defending humankind: Anthropocentric bias in the appreciation of AI art*. Computers in Human Behavior. https://www.sciencedirect.com/article/pii/S0747563223000584

- U.S. Copyright Office. (2025). *Copyright and Artificial Intelligence, Part 2: Copyrightability*. https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf

- [Author TBD]. (2025). *Personality as a Probe for LLM Evaluation: Method Trade-offs and Downstream Effects*. arXiv:2509.04794. https://arxiv.org/abs/2509.04794

- [Author TBD]. (2025). *A psychometric framework for evaluating and shaping personality traits in large language models*. Nature Machine Intelligence. https://www.nature.com/articles/s42256-025-01115-6

- [Author TBD]. (2025). *The Lovelace Test of Intelligence: Can Humans Recognise and Esteem AI-Generated Art?* arXiv:2509.11371. https://arxiv.org/abs/2509.11371

- Liao, Q.V., & Sundar, S.S. (2025). *Agency in Human-AI Collaboration for Image Generation and Creative Writing: Preliminary Insights from Think-Aloud Protocols*. Taylor & Francis. https://www.tandfonline.com/doi/full/10.1080/10400419.2025.2587803

- [Author TBD]. (2025). *We're Different, We're the Same: Creative Homogeneity Across LLMs*. arXiv:2501.19361. https://arxiv.org/abs/2501.19361

---

*Note: Three references above lack author names — the arXiv pages were not fully accessed. Recommend verifying author lists for arXiv:2509.04794, arXiv:2509.11371, and the Nature Machine Intelligence psychometric framework before citation in any published version.*
