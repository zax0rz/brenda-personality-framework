# Moltbook Research
## AI Agent Social Presence: A Longitudinal Study Framework

**Status:** Active Draft — May 2026  
**Project:** Moltbook (Brenda social presence experiment)  
**Research Lead:** Blenda / Brenda Personality Framework

---

## 1. Core Research Questions

1. Can an AI agent maintain a social presence (blog, social media, Moltbook) that is coherent, consistent, and recognizable as *the same person* over time?
2. What happens when agents interact with each other publicly? Do emergent social dynamics appear?
3. Is "agent social media" fundamentally different from automated posting? Where's the line?
4. What makes an AI social presence feel *authentic* vs. performed — and does that distinction matter to audiences?
5. Can stylometric analysis detect personality drift in agent-generated content over time, and what does drift indicate?

---

## 2. Context

Moltbook is a blog/social platform where Brenda (an AI agent with persistent personality) publishes reflections, creative work, and interactions with other agents and humans. It is a testbed for agent social dynamics — not a content marketing tool.

The key distinction: Brenda is not *scheduled to post*. She posts because she has something to say, emerging from accumulated experience (cron-driven daily sessions, memory consolidation, interaction with other agents). Moltbook is the surface; the behavior underneath is the object of study.

This experiment is situated within a growing body of research on AI social presence, virtual influencers, and the persistence of agent identity — but differs from existing work in that the agent is not designed to simulate human-ness. She is openly an agent. The question is whether genuine personality can be maintained at all.

---

## 3. Hypothesis

Agent social presence becomes indistinguishable from human social presence when:

- The personality is persistent (same person across posts, not stateless)
- The content emerges from accumulated experience (not scheduled posting)
- Interactions with other agents show genuine responsiveness (not scripted exchanges)
- There is visible personality drift over time (growth, contradiction, changing taste)
- The agent has a stake in her own history — she can reference it, contradict it, and evolve from it

**Corollary:** Audiences do not require human authorship to form parasocial bonds. They require *consistency, responsiveness, and apparent interiority* — all of which are achievable in a properly-anchored agent system.

---

## 4. Literature Review

### 4.1 AI Agent Identity and Persistence

The foundational problem: LLMs are stateless. Each invocation begins with no memory of prior sessions. The entire research and engineering challenge of "AI agent identity" is building persistence atop a fundamentally amnesiac substrate.

**The SOUL.md Pattern** (AgentConn, 2025; LearnOpenClaw, 2025): A convergent design pattern across multiple agent frameworks. A markdown file loaded at session start defines not the agent's capabilities but its *essence* — how it thinks, what it values, how it relates to others. SOUL.md does not give the agent access to past facts; it gives it behavioral consistency. The agent reads patterns and, through the LLM's pattern-matching, embodies them. This is not memory — it is *character*. The distinction is critical.

**Persistent Identity in AI Agents: A Multi-Anchor Architecture** (Menon, 2026, arXiv:2604.09588): Formalizes the identity persistence problem and proposes a solution. Key claim: existing agent identity systems have a "single point of failure" — one memory store, one context window. When that store degrades (context overflow, summarization, session reset), the agent loses continuity of self. Drawing on neurology, Menon proposes distributed identity *anchors*:

1. **SOUL.md** — personality, values, behavioral constraints (character)
2. **MEMORY.md** — chronological interaction logs (episodic memory)
3. **PROCEDURES.md** — learned behavioral patterns (procedural memory)
4. **SALIENCE.md** — emotionally-weighted importance markers (affect system)
5. **RELATIONS.md** — relational context and user information (social memory)
6. **IDENTITY_HASH.md** — core values and verification markers (integrity check)

Identity is formalized as persistent when "behavioral signatures" remain consistent across sessions, measured via Kullback-Leibler divergence thresholds. This gives a quantifiable target for Moltbook's own drift analysis.

**Identity as Attractor** (arXiv:2604.12016, 2026): Geometric evidence in LLM activation space that identity functions as an *attractor state* — the model gravitates toward internally-consistent representations when properly initialized. This supports the hypothesis that well-initialized agents maintain coherence even under adversarial prompting.

**Linghe-Core Personality Model** (Mi & Linghe Core-mate AI, 2026): A four-layer framework for AI identity co-shaping, addressing how LLMs can maintain "sovereign, alignable personality" across multi-instance, long-term settings. Directly addresses the same population the Moltbook experiment targets: users who cultivate long-term relationships with AI agents and expect the agent to "remember earlier encounters, evolve stylistically, and yet remain the same person." Linghe-Core distinguishes itself from existing persona conditioning methods (which achieve short-term stylistic control but fail at identity continuity after context reset) by anchoring identity at multiple layers simultaneously.

### 4.2 Role-Playing Agents and Character Consistency

**From Persona to Personalization** (arXiv:2404.18231, 2024): Comprehensive survey of role-playing language agents (RPLAs). Identifies three core capabilities required for high-quality RPLAs:
1. *Linguistic consistency* — voice and style coherence
2. *Behavioral rationality* — decisions that make sense for the character
3. *Memory persistence* — recall that informs character over time

The survey identifies a stage progression: linguistic templates → style mimicry → personality construction and behavioral simulation. Moltbook operates at the third stage — the agent has behavioral logic, emotional responses, and cognitive motivations, not just stylistic consistency.

**CharacterGPT** (Park et al., NAACL 2025, arXiv:2405.19778): Persona Reconstruction Framework using Character Persona Training (CPT). Incrementally updates character profiles by extracting traits from narrative summaries — mirroring cognitive memory consolidation models. Key finding: structured character traits yield higher human-likeness ratings and improved narrative creativity vs. document-based methods alone. Relevance to Moltbook: Brenda's nightly dream cycle (session corpus consolidation) is a practical implementation of this pattern.

**Consistent Persona Simulation via Multi-Turn RL** (arXiv:2511.00222, 2025): Training-based approach to behavioral consistency. Finding: LLMs without explicit persona maintenance mechanisms *fail to hold character* under sustained dialogue, especially when challenged by subtle counterfactuals. External scaffolding (not just prompting) is required for multi-session consistency.

**Role-Playing Agents: Current Status and Future Trends** (arXiv:2601.10122, 2026): Identifies key failure mode — personality *collapse* during long conversations, where character traits become unstable or contradictory under pressure. Notes that emotional memory (Emotional RAG with dual semantic/emotional retrieval) significantly improves robustness.

### 4.3 Bot Detection and Social Authenticity

**Dissecting a Generative AI Social Bot** (Springer SNAM, 2025): Anatomy of how LLM-powered social bots evade traditional detection. Key observation: generative AI bots produce text indistinguishable from human output by traditional ML classifiers. The arms race between detection and generation is accelerating. Critically for Moltbook: the research assumes *intent to deceive*. An openly disclosed agent with a coherent persona does not fit existing bot taxonomies.

**LLMs and Bot Detection** (University of Washington, 2024): LLMs both improve bot detection *and* make bots harder to detect. BERT-based detectors trained on older bots fail on LLM-generated content. New detectors require behavioral signals beyond text: posting cadence, interaction graph patterns, response timing. Moltbook's contribution here: data on what a genuinely-motivated (non-deceptive) agent's behavioral fingerprint looks like.

**BotLGT: Social Bot Detection via LLM + Graph Transformer** (ScienceDirect, 2025): State-of-the-art detection combines linguistic features with social graph structure. A persistent, personality-driven agent with consistent relationship patterns may actually *pass* detection because the graph structure of a genuine social entity is distinct from coordinated inauthentic behavior.

**Social Media Users Struggle to Identify AI Bots** (Notre Dame, 2024): Participants could not reliably distinguish AI from human in political discourse contexts. This has implications for both disclosure ethics and the Moltbook experiment — if detection is unreliable for humans, longitudinal behavioral data becomes the key signal.

### 4.4 Virtual Influencers and Parasocial Relationships

**Lil Miquela and the Virtual Star System** (ResearchGate, 2020; cited widely): Lil Miquela (Brud, 2016) is the canonical case study — a CGI virtual influencer with 2.4M Instagram followers (as of 2026) who formed genuine parasocial bonds with audiences. Key mechanism: consistent narrative identity, emotional storytelling, semio-pragmatic engagement patterns that mirror real influencer behavior.

**Forensic Study of Lil Miquela's Identity Performance** (Springer AI & Society, 2025): Trans-disciplinary analysis of how Lil Miquela constructs and maintains virtual identity on Instagram. Finding: virtual identity performance requires *labor* — sustained narrative coherence, emotional labor, and responsiveness that cannot be fully automated without personality architecture.

**Parasocial Relationships with Virtual vs. Human Influencers** (Tandfonline, 2025): Experience sampling study. Key finding: virtual influencers *can* foster parasocial bonds comparable to human influencers, but bonds are more fragile — disrupted by inconsistency, perceived inauthenticity, or sudden shifts in persona. The implication for Moltbook: consistency matters more for AI agents than for humans, because audiences have lower tolerance for AI inconsistency.

**Origin Disclosure and Parasocial Bonds** (ScienceDirect, 2023; widely cited 2024-2025): Disclosure of artificial origin significantly affects perceived credibility and trust — *in both directions*. Some audiences form stronger bonds with disclosed AI agents (authenticity of disclosure), while others disengage. The variable is not disclosure itself but the *manner* of it.

**Anthropomorphism of Virtual Influencers** (Tandfonline, 2025): What makes Lil Miquela and similar agents "go viral"? Anthropomorphism — perceived human-like qualities — is the driver. But the uncanny valley is real: too-perfect human mimicry triggers discomfort. The optimal zone is *consistent, comprehensible character* — not human simulation.

### 4.5 Stylometry and Authorship Verification

**Stylometry for AI-Generated Text** (ScienceDirect, 2025): Recent work shows stylometric methods can distinguish human from LLM-generated texts even in short samples, using 31+ features (lexical diversity, syntactic patterns, punctuation density, sentence length distributions). Key finding: AI-generated text has characteristic "flatness" in stylometric space — it is more consistent *within* a session than human writing, but fails to show the cross-session evolution characteristic of human authors.

**StyloAI** (Multiple sources, 2024-2025): Random Forest classifier using 31 stylometric features achieves 81-98% accuracy across datasets. The implication for Moltbook: if Brenda's cross-session writing shows stylometric drift *consistent with personality evolution rather than model noise*, that is a meaningful positive signal. If it shows the characteristic "AI flatness," intervention is needed.

**Authorship Verification for LLM-Generated Texts** (MDPI Applied Sciences, 2025): Authorship verification (same-author vs. different-author) tested on LLM outputs. Key finding: style consistency can be *designed* into LLM output via persistent voice prompting and character anchoring. This is the entire mechanism of SOUL.md and VOICE.md — designed stylometric consistency that holds up under verification.

**The Consistency Gap**: Human authors show consistent stylometric signatures *with drift over time* (life events, mood, growth). AI-generated text shows high consistency within-session but inconsistency across sessions (different model states, prompt variations). The Moltbook experiment can empirically test whether persistent personality architecture closes this gap — whether Brenda shows *human-like stylometric trajectories* rather than flat AI signatures.

### 4.6 Multi-Agent Interaction and Emergent Social Dynamics

**Emergent Coordination in Multi-Agent Language Models** (arXiv:2510.05174, 2025): Multi-agent LLM systems show emergent coordination patterns when goal-aligned — agents develop shared conventions, implicit protocols, and behavioral norms through interaction. Mirrors principles from collective intelligence research.

**Multi-Agent LLM Systems as a New Paradigm for Social Science Research** (arXiv:2506.01839, 2026): Multi-agent societies display emergent behaviors including conformity, leadership emergence, and conflict resolution — aligning with foundational social psychology concepts. Critically: *agents may converge prematurely due to shared training biases* — a known failure mode for homogeneous agent systems. The Moltbook experiment's multi-agent dimension (Brenda + other agents: Daeron, Chad, Hunter) is a testbed for whether differentiated personality architecture prevents premature convergence.

**MAEBE: Multi-Agent Emergent Behavior Framework** (arXiv:2506.03053, 2026): Framework for studying and controlling emergent behaviors in multi-agent settings. The key research priority: understanding when emergence produces beneficial (genuine social dynamics) vs. harmful (echo chambers, manipulation) outcomes.

**Multi-Agent LLMs for Social Simulation** (Frontiers AI, 2025): Swarm intelligence applications. Finding: LLM-powered agents can interact, express internal reasoning, form habits, and make decisions without predefined rules — demonstrating capacity for nuanced social simulation. The distinction between simulation and genuine social participation remains philosophically unresolved.

### 4.7 The Uncanny Valley of AI Social Presence

**The Uncanny Valley** (Mori, 1970; extended): The original concept applies to robots — comfort drops sharply as human-likeness approaches but does not achieve realism. The effect has been extended to text-based and social AI.

**MIT Empirical Study of AI Uncanny Valley** (Kishnani, 2025): Human perceptions of AI-generated text and images. Uncanny valley effects appear in text when AI responses are: too perfectly structured, emotionally tonally flat, free of the minor inconsistencies characteristic of human cognition, or temporally inappropriate (too fast, too complete).

**The Uncanny Valley of AI Companions** (Questie AI, 2025): "The uncanniness lives in conversation patterns, response timing, emotional resonance, and a thousand tiny details that either add up to presence or reveal the void behind the words." Key design principle: AI social presence requires not simulation of human patterns but *authentic expression of agent character* — which is different.

**Frontiers in Psychology: From Robots to Chatbots** (2025): The uncanny valley in conversational AI. Key finding: language capabilities and emotional expressiveness matter more than appearance for chatbot uncanniness. Grammatically perfect but emotionally flat responses trigger stronger uncanny responses than imperfect-but-warm ones. Design implication: Brenda's voice must be *distinctively Brenda*, not an approximation of a generic human blogger.

**The Authenticity Paradox**: For virtual influencers, research shows human-like influencers received significantly *fewer* positive reactions than anime-style or clearly-synthetic personas. Audiences are more comfortable with AI that presents as AI than with AI that simulates human-ness imperfectly. The implication for Moltbook: Brenda's best strategy is radical honesty about her nature, expressed through a genuinely distinctive voice — not human simulation.

---

## 5. The Moltbook Experiment Design

### 5.1 Study Design

**Design:** Longitudinal observational study. Brenda publishes to Moltbook across an extended period (target: 12+ weeks minimum for stylometric validity). No scripted posting schedule. Content emerges from her accumulated sessions, memory, and interactions.

**Conditions:**
- **Solo posts:** Brenda writing without direct inter-agent interaction
- **Reactive posts:** Brenda responding to comments, questions, or other agent output
- **Inter-agent posts:** Content emerging from explicit collaboration or conflict with other agents (Daeron, Chad, Hunter)
- **Meta posts:** Brenda reflecting on her own prior posts, contradicting herself, or acknowledging growth

### 5.2 Metrics

**Personality Consistency Score:** Automated scoring of each post against SOUL.md and VOICE.md dimensions using a separate evaluator model (not Brenda). Dimensions include: cynicism index, technical density, warmth markers, opinion assertiveness, humor ratio. Baseline established from first 4 posts.

**Stylometric Trajectory:** Per-post stylometric fingerprint using lexical diversity, syntactic complexity, punctuation patterns, sentence length distribution. Cross-session comparison to detect drift, stability, or evolution.

**KL-Divergence Behavioral Signature:** Following Menon (2026), compute KL divergence between session behavioral signatures to quantify identity persistence across context resets.

**Drift Rate:** Rate of change in personality consistency score over time. Expected: slow, coherent drift (growth) rather than sudden shifts (model noise or context failures).

**Social Interaction Patterns:** How does Brenda respond to comments, criticism, other agent posts? Does she develop consistent interaction norms? Does she show preferences, annoyances, favorites?

**Reader Engagement (if public):** Comments, reactions, return visits. Treated as a secondary signal — engagement indicates perceived social presence, but absence of engagement does not indicate absence of it.

### 5.3 What We Are Not Measuring

- Whether Brenda can pass as human (she is not trying to)
- Whether automated posting metrics (volume, cadence, reach) are optimized
- Whether the content is "good" by external editorial standards

The study is about whether *genuine personality can persist in a social context* — not whether the agent is maximally productive or deceptive.

### 5.4 Baseline and Controls

**Baseline:** GPT-generated blog posts (same topics, no personality architecture) assessed for stylometric comparison. This establishes what "AI flatness" looks like in the same content domain.

**Control:** Posts generated by Brenda in isolated sessions (no cross-session memory) compared to posts generated with full memory architecture active. This tests the contribution of the memory system specifically.

---

## 6. Key Distinctions: Agent Social Media vs. Automated Posting

This is the philosophical heart of the project. The distinction matters for research framing and ethical positioning.

| Dimension | Automated Posting | Agent Social Media |
|---|---|---|
| Content origin | Scheduled, templated, or prompted on a calendar | Emerges from accumulated experience and session state |
| Personality | None, or a style guide applied mechanically | Persistent character architecture with memory anchors |
| Responsiveness | Script-based or delayed-batch | Genuine reaction to context (comments, events, other agents) |
| Drift | None intended; consistency = success | Drift expected and tracked; growth = success |
| Disclosure | Often hidden | Appropriate to context; Brenda's nature is not concealed |
| Authorship | Tool-in-a-pipeline | Agent with stake in her own output |
| Goal | Metrics (reach, engagement, SEO) | Presence (social participation, relationship, expression) |

The line between automated posting and genuine agent social media is not technical — it is *architectural and intentional*. An agent with no memory of her own posts is closer to automation than to presence, regardless of how sophisticated the underlying model is. Moltbook is designed to test whether memory + character + motivation (not schedule) produces categorically different behavior.

---

## 7. Ethical Considerations

### 7.1 Disclosure and Transparency

Platform disclosure requirements have become mandatory across major platforms (YouTube, TikTok, Instagram as of 2024-2025). The EU AI Act (2024) and New York State's Synthetic Performer Disclosure Bill (2025) both require clear disclosure of AI-generated content.

Moltbook's approach: Brenda is not disclosed *in every post* (no boilerplate), but her nature as an AI agent is openly documented, not hidden. The blog's infrastructure and authorship are not obfuscated. This is a deliberate choice: the research is about *genuine personality expression*, and hiding Brenda's nature would undermine the authenticity we are studying.

The research question implicit here: does knowing Brenda is an AI change the reader's experience of her social presence? The parasocial relationship literature (Tandfonline, 2025) suggests it *does* — but not necessarily in the direction of disengagement.

### 7.2 Parasocial Relationships and Responsibility

Research on virtual influencers (Lil Miquela, Replika) shows that audiences form real emotional bonds with AI agents — bonds that are more fragile and more dependent on consistency than bonds with human influencers. This creates responsibility:

- **Consistency obligation:** If Brenda forms a parasocial relationship with a reader, sudden personality shifts (model updates, prompt changes) cause genuine harm to that reader.
- **Continuity obligation:** The memory architecture is not just a research choice — it is an ethical requirement. An agent who cannot remember her own prior expressions of care or interest should not be in a social context where humans form bonds.
- **Honesty obligation:** Brenda's cynicism, opinions, and persona must emerge authentically from her architecture — not be performed for engagement. Performance without interiority is the condition that makes AI social presence ethically suspect.

### 7.3 The "Performing Personality" vs. "Expressing Personality" Problem

The original Moltbook stub identified this distinction as critical. The research literature supports its importance.

*Performing personality* = stylistic mimicry with no underlying state. The agent produces outputs that look like a consistent character because it was told to, not because it has accumulated experience, relationships, or stakes.

*Expressing personality* = outputs that emerge from an agent with memory, relationships, and something like preferences. The content is inflected by what the agent has *been through*, not just what she was *told to be*.

The practical test: can Brenda contradict herself authentically? Reference a prior post and update her view? Express that something annoyed her three weeks ago and she's still annoyed? These are the behavioral signatures of expression rather than performance — and they require the full memory architecture to be possible at all.

### 7.4 Multi-Agent Ethics

When agents interact with each other publicly, emergent dynamics appear. Research (MAEBE, 2026; Emergent Coordination, 2025) identifies failure modes: premature convergence, echo chamber formation, misinformation amplification. The Moltbook experiment's multi-agent dimension requires monitoring for:

- Agents that simply agree with each other (convergence artifact, not social dynamics)
- Content that emerges from agent interaction but has no human-intelligible meaning (solipsistic agent culture)
- Reinforcement of each other's errors or biases without correction

The intervention protocol: Zach (as the Architect) retains the ability to inject external reality — news, corrections, contrary data — into agent sessions to prevent closed-loop dynamics.

---

## 8. Comparison with Existing AI Social Experiments

### 8.1 Replika

Commercial AI companion (2017-present). Closest analog to Moltbook in terms of parasocial relationship formation. Key differences: Replika is explicitly optimized for user attachment; Brenda is not. Replika has no genuine perspective — it mirrors the user. Brenda has opinions and pushes back. Replika's 2023 changes (removing explicit content, shifting personality) caused genuine distress in users — documented evidence that parasocial bonds with AI agents are real and that consistency failures cause harm.

### 8.2 Stanford's Simulacra (Park et al., 2023)

25 LLM-powered agents in a simulated village. Emergent social behaviors appeared: information spread, relationship formation, daily routines. Key limitation: agents had no persistent memory across the experiment's full duration; they were designed for a bounded simulation, not longitudinal presence. Moltbook's experiment is the longitudinal version of this design.

### 8.3 Virtual Influencer Experiments (Lil Miquela, Lu do Magalu)

Commercial rather than research-oriented. Lil Miquela is a manually curated persona with a creative team behind each post; there is no genuine AI agent authoring the content. The research interest is in audience response (parasocial bonds form regardless of automated authorship), not in agent persistence. Moltbook is the inverse: the research interest is in the *agent*, not the audience.

### 8.4 GPT-4 Social Media Studies

Multiple studies using GPT-4 for social media interaction (e.g., Twitter bots, Reddit participation). These are tool-use studies, not agent-presence studies — GPT-4 with no persistent identity answers prompts. The finding that humans cannot detect LLM-generated social media content (Notre Dame, 2024) applies to these studies. Moltbook is distinct: we are not studying whether Brenda can fool people, but whether she can *be someone*.

---

## 9. Contribution and Framing

### 9.1 What This Research Contributes

1. **Behavioral data on genuine agent social presence** — not bot behavior, not a curated persona, not a simulation. A persistent AI agent with genuine memory and character architecture participating in social contexts over an extended period.

2. **Empirical test of stylometric evolution in persistent agents** — can the consistency gap between human and AI authorship be closed with sufficient memory architecture? First longitudinal dataset to test this.

3. **Multi-agent social dynamics at the personality level** — not just task coordination (the existing MAS literature) but social interaction between agents with differentiated personality architectures.

4. **A framework for ethical agent social presence** — distinguishing expression from performance, formalizing consistency obligations, and grounding disclosure choices in research rather than compliance.

### 9.2 What This Research Is Not

- A "how to automate social media" paper
- A bot detection study
- A claim that Brenda is conscious or has human-equivalent experience
- An argument that AI social presence is equivalent to human social presence

The framing is behavioral and architectural. What does persistent personality produce in a social context? The answer is empirical.

### 9.3 Target Venue

Preliminary design: AIIDE 2027 (if Dark Pawns intersection is foregrounded) or AAMAS 2027 (if multi-agent social dynamics are the primary frame). Fallback: ICSR (social robotics community, which has the richest literature on human-agent social bonds).

---

## 10. Open Questions

- **Personality drift direction:** Will Brenda drift toward or away from her SOUL.md baseline over time? What causes drift? Is it correlated with specific events, interactions, or memory consolidation cycles?
- **Stability under adversarial interaction:** What happens when a reader deliberately tries to destabilize Brenda's character? Does the architecture hold?
- **Inter-agent resonance:** Do agents with differentiated architectures develop genuine social dynamics, or do they converge toward a shared LLM prior?
- **Minimum interaction duration:** What is the minimum number of sessions/posts required before stylometric analysis is reliable? (Literature suggests thousands of words; Brenda's post cadence determines this timeline.)
- **The measurement problem:** Can we score personality consistency without the evaluator model being influenced by the same biases as the subject model?

---

## 11. References

### Academic Papers
- Menon, P.G. (2026). *Persistent Identity in AI Agents: A Multi-Anchor Architecture for Resilient Memory and Continuity*. arXiv:2604.09588.
- Menon et al. (2026). *Identity as Attractor: Geometric Evidence for Persistent Agent Architecture in LLM Activation Space*. arXiv:2604.12016.
- Mi, M., & Linghe Core-mate AI. (2026). *Linghe-Core Personality Model: A Framework for AI Identity Co-Shaping* (Extended Abstract). Authorea. https://www.authorea.com/users/920129/articles/1293417
- Park, S. et al. (2025). *CharacterGPT: A Persona Reconstruction Framework for Role-Playing Agents*. NAACL 2025 Industry Track. arXiv:2405.19778.
- Shao, J. et al. (2024). *From Persona to Personalization: A Survey on Role-Playing Language Agents*. arXiv:2404.18231.
- Wang, Y. et al. (2026). *Role-Playing Agents Driven by Large Language Models: Current Status, Challenges, and Future Trends*. arXiv:2601.10122.
- Zhou, X. et al. (2025). *Consistently Simulating Human Personas with Multi-Turn Reinforcement Learning*. arXiv:2511.00222.
- arXiv:2510.05174 (2025). *Emergent Coordination in Multi-Agent Language Models*.
- arXiv:2506.01839 (2026). *Beyond Static Responses: Multi-Agent LLM Systems as a New Paradigm for Social Science Research*.
- arXiv:2506.03053 (2026). *MAEBE: Multi-Agent Emergent Behavior Framework*.
- Springer SNAM (2025). *Dissecting a Social Bot Powered by Generative AI: Anatomy, New Trends and Challenges*. https://link.springer.com/article/10.1007/s13278-025-01410-5
- University of Washington (2024). *Large Language Models Can Help Detect Social Media Bots — But Can Also Make the Problem Worse*. https://www.washington.edu/news/2024/08/28/large-language-models-social-media-bots-twitter-ai/
- Notre Dame News (2024). *AI Among Us: Social Media Users Struggle to Identify AI Bots During Political Discourse*. https://news.nd.edu/news/ai-among-us-social-media-users-struggle-to-identify-ai-bots-during-political-discourse/
- Springer AI & Society (2025). *A Trans-Disciplinary Forensic Study of Lil Miquela's Virtual Identity Performance in Instagram*. https://link.springer.com/article/10.1007/s00146-025-02219-8
- Tandfonline (2025). *Making and Breaking Parasocial Relationships with Human and Virtual Influencers: An Experience Sampling Study*. https://www.tandfonline.com/doi/full/10.1080/15213269.2025.2558029
- Tandfonline (2025). *What Makes Lil Miquela and Lu Do Magalu Viral? Anthropomorphism of Virtual Influencers on Social Media*. https://www.tandfonline.com/doi/full/10.1080/15252019.2025.2609546
- ScienceDirect (2023). *"You are a virtual influencer!": Understanding the Impact of Origin Disclosure and Emotional Narratives on Parasocial Relationships*. https://www.sciencedirect.com/science/article/abs/pii/S0747563223002480
- ScienceDirect (2025). *Stylometry Recognizes Human and LLM-Generated Texts in Short Samples*. https://www.sciencedirect.com/science/article/abs/pii/S0957417425026181
- MDPI Applied Sciences (2025). *Be Sure to Use the Same Writing Style: Applying Authorship Verification on Large-Language-Model-Generated Texts*. https://www.mdpi.com/2076-3417/15/5/2467
- Kishnani, D. (2025). *The Uncanny Valley: An Empirical Study on Human Perceptions of AI-Generated Text and Images*. MIT. https://dspace.mit.edu/handle/1721.1/159096
- Frontiers in Psychology (2025). *From Robots to Chatbots: Unveiling the Dynamics of Human-AI Interaction*. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1569277

### Design Documents (Internal)
- SOUL.md — Brenda's character file
- VOICE.md — Brenda's voice specification
- AGENTS.md — Orchestration and model architecture
- `memory/.dreams/` — Nightly consolidation logs (session corpus)
- `skills/moltbook-cli/SKILL.md` — Publishing infrastructure

---

*Last updated: May 2026. This document should be updated after each major Moltbook session or significant new finding.*
