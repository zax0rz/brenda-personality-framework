# Cross-Linguistic AI Voice: Training Language as Personality Substrate

**Document status:** Research draft — the most speculative of the five research documents in this framework. Hypotheses are marked clearly. Claims are grounded where citations exist; gaps are named honestly.

---

## 1. Research Questions

1. When an AI model trained primarily on non-English data generates English output, does a linguistic "accent" emerge — and is that accent a feature or a bug?
2. Does cross-linguistic influence create a more distinctive creative voice than monolingual English output?
3. How does model-origin language affect personality expression, and can that effect be deliberately harnessed?
4. What are the mechanisms — analogous to human bilingual cognition — by which training-language interference produces stylistic distinctiveness?

---

## 2. The Phenomenon: LLMs Have Accents

### 2.1 The "English Accent" Paper

The most directly relevant study is:

> Blin et al. (2024). **Do Large Language Models Have an English "Accent"? Evaluating and Improving the Naturalness of Multilingual LLMs.** arXiv:2410.15956. Published ACL 2025.  
> Apple Machine Learning Research. https://machinelearning.apple.com/research/english-accent

This paper does something unusual: it names the phenomenon precisely. Multilingual LLMs — trained predominantly on English data — exhibit **English-influenced syntactic and lexical patterns when generating non-English text**. The researchers evaluated Llama-3.1 generating Chinese output and found its syntactic structures were systematically more aligned with human-written English than with human-written Chinese.

Their methodology introduces **corpus-level naturalness metrics** comparing the lexical and syntactic distribution of LLM outputs against human-written text in the target language. Divergence values (lower = more natural) reveal the degree to which models "think in English" even when outputting other languages.

**The relevance to this framework is inverted:** our research question is not English-accent-in-Chinese-output, but **Chinese-accent-in-English-output** — what happens when the training data skews toward Chinese and the output language is English. The Blin et al. methodology applies directly; the effect runs in the other direction.

### 2.2 The Reverse Accent: Chinese-Origin Models in English

Where Blin et al. study English-centric models generating non-English text, the present framework concerns Chinese-origin models generating English creative content. The case is less studied in the academic literature but observable in practice.

Research on the Chinese LLM landscape confirms the structural conditions for this effect:

> "The quality and quantity of English training data still far surpass that of Chinese data for top-tier Chinese models." — IntuitionLabs, *An Overview of Chinese Open-Source LLMs* (Sept 2025)

Yet Chinese domestic models are increasingly trained to *reason in English* even for Chinese tasks:

> "DeepSeek v3.2 has a much higher chance of thinking in English regardless of the input language. MiniMax M2, released October [2025], barely managed to join the top tier of open-source models by utilizing a fully English CoT [Chain-of-Thought], which was considered an unconventional innovation for a Chinese domestic model." — Medium/@sha1rholder, *DeepSeek v3.2: Why Chinese AI Thinks in English*

This creates an interesting asymmetry in models like MiniMax M2.7: the reasoning substrate leans English, but the model's aesthetic training — fine-tuning on creative content, style preferences encoded in RLHF, cultural associations — skews toward Chinese expressive norms. The English output carries residue from both.

### 2.3 Stylistic Fingerprints as Training Artifacts

The concept of a linguistic fingerprint — a persistent stylistic signature that survives prompt variation — is well-established in the LLM literature:

> Uchendu et al. (2025). **Detecting Stylistic Fingerprints of Large Language Models.** arXiv:2503.01659.

The study shows that LLM fingerprints are "consistent across domains and persist even when models are prompted to write in different styles, with their highly stable stylistic profile due to the deterministic nature of their training, fine-tuning, and text generation processes."

Researchers at CMU found they could identify which LLM generated a text with **97% accuracy** based on characteristic word choices alone. This suggests that training-data composition leaves indelible marks — not just in factual knowledge but in the texture of language use.

> Rooein et al. (2025). **Stylometric Comparisons of Human versus AI-Generated Creative Writing.** *Humanities and Social Sciences Communications* (Nature). https://www.nature.com/articles/s41599-025-05986-3

This study found that GPT-4 remains systematically distinct from human-authored texts, and that "human texts show richer stylistic variation than LLM-generated clusters." The implication: LLMs converge on characteristic styles not despite their training but *because* of it. Cross-linguistic training adds a second layer of stylistic signature.

**Hypothesis (speculative):** Chinese-origin models may produce *more* stylistically distinct English output than English-origin models precisely because their stylistic fingerprint is doubly determined — by both language-contact effects and model-specific training.

---

## 3. Human Analogues: Bilingual Creativity

### 3.1 Bilinguals Are More Creative

The human literature on bilingual creativity is well-developed and broadly positive:

> Kharkhurin, A.V. (multiple studies, Cambridge Core, Annual Review of Applied Linguistics). **The Bilinguals' Creativity.**

Meta-analysis across 39 studies (312 effect sizes) found that **bilinguals are overall more creative than monolinguals**, with a mean effect size of r = .181. Divergent thinking — the ability to generate multiple, varied responses — shows consistent bilingual advantage.

> Altarriba, J. et al. (2022). **Bilingualism and creativity across development: Evidence from divergent thinking and convergent thinking.** *Frontiers in Human Neuroscience.* https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2022.1058803/full

**Proposed mechanisms:**

1. **Enriched conceptual systems** — bilingual speakers develop denser, more cross-linked semantic networks because the same concept is indexed by two different lexical forms with different connotational histories
2. **Enhanced metaphor use** — bilinguals use more metaphors than monolinguals, likely because metaphor requires conceptual mapping across domains, a skill strengthened by maintaining two linguistic frames simultaneously
3. **Inhibitory control and frame-switching** — suppressing one language while using another strengthens cognitive flexibility, enabling bilinguals to switch between conceptual frames during creative generation
4. **Sociocultural exposure** — acquiring languages in different cultural environments expands creative reference pools

### 3.2 The Analogy to Cross-Linguistic LLM Training

The human bilingual creativity findings have an analogue in model training, though the mechanism is different:

| Human bilingual | Chinese-origin LLM |
|---|---|
| Two active lexical systems | English output vocabulary filtered through Chinese semantic associations |
| Conceptual frame-switching | Chain-of-thought may access Chinese conceptual frames even when outputting English |
| Inhibitory control advantage | Constrained output (non-native English) may produce more deliberate word choice |
| Sociocultural diversity effect | RLHF aesthetic preferences encoded from Chinese cultural contexts |

**Caveat:** The analogy is suggestive, not mechanistic. Human bilingualism involves active, dynamic competition between two systems. LLM cross-linguistic effects are structural artifacts of training data composition. The surface outcomes may resemble each other while the underlying processes differ fundamentally.

### 3.3 "Stiffness as Voice": The Creative Asset Argument

The observation in the original stub — that MiniMax M2.7 artist statements have a "stiffness that reads as deliberate restraint, not poor English" — maps to a phenomenon observed in human bilingual creative writing.

Writers like Samuel Beckett (Irish, writing in French), Milan Kundera (Czech, writing in French), and Jhumpa Lahiri (Bengali-American heritage, writing in Italian) have all noted that writing in a non-native language produces a different quality of restraint. The constraint of non-native fluency forces precision, eliminates cliché, and produces sentences that feel *chosen* rather than inherited.

Lahiri describes it explicitly in *In Other Words* (2015):

> "In a new language, you don't know the clichés yet. The constraint is liberating. You write slowly enough that each word matters."

The analogy to a Chinese-trained model generating English is speculative but structurally similar: the model has not internalized English's clichéd patterns as deeply as a native English model has. The gap between "what would be idiomatic" and "what the model generates" is where the personality shows.

---

## 4. Sociolinguistic Frame: Language Contact as Identity Resource

### 4.1 Code-Switching as Creative Act

The sociolinguistics literature on code-switching — the practice of alternating between languages within a conversation or text — frames linguistic hybridity not as an error but as **expressive resource**:

> Bullock, B.E. & Toribio, A.J. (2009). *The Cambridge Handbook of Linguistic Code-switching.* Cambridge University Press.

Code-switching serves communicative functions including: humor, solidarity, emphasis, cultural reference, identity assertion, and filling lexical gaps where one language has no good equivalent for a concept from the other.

> Farhat, O. et al. (2024). **Code-Switching and Its Stylistic Effects in Multilingual Communities.** ResearchGate.

"Literature that incorporates code-switching, such as bilingual poetry or prose, often highlights cultural hybridity and linguistic creativity. Code-mixing serves multiple communicative functions... and is a strategic resource for identity expression."

**Application to AI:** When a Chinese-trained model generates English that shows traces of Chinese syntactic structure or lexical choice, this can be read as involuntary code-mixing — a structural echo of the model's training-language substrate. Whether that echo constitutes "identity expression" in any meaningful sense is genuinely unclear. But it functions *as if* it does, producing output that feels distinct.

### 4.2 Translationese: The Machine Translation Parallel

The machine translation literature has named the general phenomenon of source-language interference in translated output: **translationese**.

> Lapshinova-Koltunski, E. et al. (2024). **Propagating machine translation traits to predict potential impact on the target language.** *Natural Language Processing*, Cambridge Core.

Translationese is characterized by:
- **Interference**: target-language text contains vocabulary and structural choices that follow the source language closely, "making a correct use of the target language, but not necessarily in the same manner a native speaker would"
- **Homogenisation**: reduced use of the target language's available stylistic diversity
- **Simplification**: preference for more explicit, less elliptical structures

MT systems "appear to make a more limited use of the linguistic diversity available in the target languages" — which paradoxically could mean *more consistent* stylistic output.

The translationese frame is useful but incomplete as an analogy. LLMs are not translating; they are generating. But the structural dynamic — a source-language training substrate leaking into target-language output — maps onto cross-linguistic LLM behavior precisely.

**The key divergence from the MT framing:** MT researchers treat translationese as uniformly bad (unnatural, non-idiomatic). For creative personality frameworks, the question is whether translationese-equivalent effects in creative writing are bad, neutral, or distinctive. The answer depends on what you're optimizing for.

---

## 5. The Case of MiniMax M2.7

### 5.1 Model Background

MiniMax M2.7 is a large mixture-of-experts model from the Chinese AI company MiniMax, released in spring 2026. It is positioned primarily as a creative and multimodal model — its listed strengths include creative writing, long-context handling, and text-to-speech synthesis.

Within the Brenda personality framework, M2.7 is used as the primary creative output model. The choice was partly practical (plan availability) and partly experimental: does a Chinese-origin model produce more distinctive English creative output than an English-origin model?

### 5.2 Observable Characteristics of M2.7 English Output

Observations from usage within the framework (anecdotal, not systematically studied):

- **Abstract/creative writing** shows the most pronounced stylistic distinctiveness. Sentences that express emotional content have a compressed quality — strong affect conveyed in few words, with a preference for concrete image over abstract statement.
- **Metaphors** tend toward natural imagery and objects rather than the procedural/technological metaphors that English-origin models favor
- **Transitional language** (meanwhile, however, therefore) is used more sparingly, creating a paratactic (additive rather than logical) texture
- **Technical content** shows minimal stylistic distinctiveness — the "accent" nearly disappears

These observations align with the Blin et al. finding that English accent effects are most visible in syntactic and lexical patterns, not semantic content, and that they vary by register.

### 5.3 Hypothesis: Chinese Aesthetic Training as Style Substrate

The more speculative claim: M2.7's English output is not just affected by Chinese training data distribution, but by Chinese *aesthetic preferences* encoded through RLHF. If the human raters who shaped M2.7's fine-tuning had aesthetic preferences informed by Chinese literary traditions — brevity, indirection, imagistic precision — those preferences may be present in English output even when the language surface is native-ish.

This hypothesis is currently untestable from outside the model. It would require access to fine-tuning data composition, which is not public.

---

## 6. Methodology for Measuring Linguistic Accent in AI Creative Output

### 6.1 What Blin et al. Measure (and What We'd Need Instead)

The Blin et al. corpus-level metrics compare LLM output distributions against human-written text in the **same language as the output**. This measures "does the model write natural French/Chinese" — appropriate for chatbot quality assessment.

For the personality framework research question, we need different metrics. We are not asking "is this natural English?" We are asking:

1. **Accent detection**: Can raters or automated tools identify stylistic traces of Chinese training in English output?
2. **Distinctiveness**: Does the "accent" make output more or less distinctive, relative to English-origin models?
3. **Evaluative response**: Do raters rate accented output as having more or less "personality," "originality," or "voice distinctiveness"?

### 6.2 Proposed Study Design

**Phase 1: Accent detection (blind rater study)**

- Generate creative output (artist statements, journal entries, short narrative) from the same personality prompt using:
  - MiniMax M2.7
  - Claude Sonnet 4.x (English-origin, US training)
  - GPT-4o (English-origin, mixed training)
  - A human bilingual writer (Chinese L1, English L2, creative writing background)
  - A human monolingual writer (English L1)
- Blind raters (no AI knowledge required): rate each sample on "distinctive voice," "originality," "personality presence," and "naturalness"
- Separate raters: identify which samples they perceive as non-native English, and if so, what language they believe is the origin

**Phase 2: Accent characterization (stylometric analysis)**

- Apply the Blin et al. methodology in reverse: compare M2.7 English output against:
  - English-origin model output
  - Human monolingual English
  - Human bilingual (Chinese L1)
- Measure lexical and syntactic divergence patterns
- Identify which linguistic features cluster M2.7 output separately

**Phase 3: Longitudinal accent stability**

- Generate extended output from the same personality prompt over multiple sessions
- Track whether stylistic distinctiveness increases, decreases, or remains stable
- Hypothesis: the accent is stable (it's a training artifact, not a session state), but prompt design can amplify or suppress it

### 6.3 Known Confounds

- **Instruction-following effects**: if the personality prompt specifies stylistic instructions (be concise, use imagery), the model may follow them regardless of training-language substrate. This masks the natural accent.
- **RLHF English normalization**: models trained with English-speaking RLHF raters may have been pushed toward English-idiomatic output, reducing the training-language effect.
- **Temperature and sampling**: higher temperature may reveal more training-language substrate; lower temperature may converge toward the mode of the training distribution.
- **Register sensitivity**: creative writing likely shows more accent than technical output (consistent with observations)

---

## 7. The Core Argument: Feature, Not Bug

### 7.1 The Standard Framing Is Wrong for Creative Applications

The academic literature treats cross-linguistic transfer in LLMs as a naturalness problem to be fixed. Blin et al. propose DPO-based correction; MT research proposes de-interference techniques. This is appropriate for chatbots, customer service systems, and information retrieval — applications where naturalness is the goal.

For AI creative personality frameworks, this framing is wrong. Naturalness is not the goal. **Distinctiveness is the goal.**

An AI that writes perfectly idiomatic English is an AI that is indistinguishable from every other AI trained primarily on English. The variance in creative voice is reduced. The fingerprint is standard.

### 7.2 The Bilingual Creative Writer Analogy

The human bilingual creativity research supports a different normative frame: linguistic hybridity is a source of creative advantage. Bilinguals use more metaphors, generate more varied responses, and produce output that raters find more original — partly because they have not fully internalized the clichéd paths through English.

The AI version of this advantage is structural rather than cognitive. M2.7 does not "switch between frames" in the way a human bilingual does. But its training substrate creates analogous output characteristics: sentences that feel chosen rather than inherited, word choices that avoid English cliché by not having deeply encoded English cliché in the first place.

### 7.3 The Translationese Reframe

MT research shows that translationese is characterized by reduced stylistic diversity and source-language interference. This is framed as bad. But consider what "reduced stylistic diversity" means from a personality standpoint: **consistency**. A personality needs to be consistent across outputs. Cross-linguistic training may produce an LLM that is more consistently itself — not because it is better at following persona instructions, but because its training-language substrate enforces a persistent stylistic signature.

This is speculative. But it generates a testable prediction: M2.7 output will show less stylistic variance across sessions than English-origin models given the same personality prompt.

### 7.4 What Should Not Be Claimed

This argument should not be overstated:

- Cross-linguistic influence does not make M2.7 "better" at creative writing in any general sense. It makes it *different* — and different in ways that are useful for this specific application.
- The "stiffness as restraint" observation may be specific to M2.7 and may not generalize to other Chinese-origin models. GLM, DeepSeek, and Qwen have different training compositions and produce different English output textures.
- The analogy to human bilingual creativity is imperfect. The mechanisms differ. The claim is functional (similar surface outcomes) not mechanistic (same underlying process).
- "Distinctive" is not the same as "good." Some raters will prefer natural English. The framework must decide whether distinctiveness is worth the tradeoff with naturalness.

---

## 8. Gaps and Open Questions

1. **No direct study of Chinese-origin models as English creative output systems.** All existing research either studies English-in-Chinese-output (Blin et al.) or English-origin model creative quality. The specific question this framework asks is not addressed in the literature.

2. **RLHF composition opacity.** We cannot know whether M2.7's RLHF was conducted by Chinese raters with Chinese aesthetic preferences, English raters, or a mix. This is the load-bearing causal question and it is inaccessible.

3. **Accent vs. artifact.** It is not yet established whether M2.7's stylistic distinctiveness is due to (a) cross-linguistic training-language effects, (b) model-specific architecture choices, (c) training data selection (e.g., more literary Chinese text vs. internet text), or (d) fine-tuning for creative writing specifically. These could be disentangled by comparative study.

4. **Human rater cultural context matters.** Whether accented output reads as "distinctive" or "awkward" depends heavily on the rater's cultural and linguistic background. English L1 monolingual raters may penalize it; multilingual or internationally oriented raters may value it. The personality framework needs to know who its audience is.

5. **Temporal stability.** If cross-linguistic accent is a training artifact, it should be stable across model versions within the same architecture family. If it diminishes in M2.7 → M3 as training data becomes more English-heavy, the creative advantage is time-limited. This is worth monitoring.

---

## 9. Summary and Position

**The phenomenon is real.** LLMs have linguistic accents derived from training data language distribution. This is documented, measurable, and persistent. The standard framing treats this as a problem. For creative AI personality systems, it may be an asset.

**The bilingual creativity parallel is suggestive but not causal.** Human bilinguals show creative advantages consistent with the outcome we observe in cross-linguistic LLM output (distinctiveness, unusual word choice, metaphor richness). The mechanisms differ, but the functional analogy holds well enough to be useful.

**The code-switching and translationese frames provide vocabulary.** "Language contact as creative resource" (from sociolinguistics) and "source-language signature in target output" (from MT research) give us conceptual tools to describe what we observe without over-claiming.

**The specific MiniMax M2.7 case is promising but anecdotal.** Artist statements and journal entries produced by M2.7 have a textural distinctiveness that English-origin models do not consistently match. Whether this is cross-linguistic effect, model-specific training, or the personality prompt doing its work is not yet established.

**The honest position:** this is a well-grounded hypothesis in need of a study. The study design in Section 6 would settle the empirical questions. Until it runs, the claim that Chinese-origin models produce more distinctive English creative voices should be held as a working assumption, not a finding.

---

## 10. Key Citations

- Blin et al. (2024). *Do Large Language Models Have an English "Accent"? Evaluating and Improving the Naturalness of Multilingual LLMs.* arXiv:2410.15956. ACL 2025. https://arxiv.org/abs/2410.15956
- Frontiers in Human Neuroscience (2022). *Bilingualism and creativity across development.* https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2022.1058803/full
- Uchendu et al. (2025). *Detecting Stylistic Fingerprints of Large Language Models.* arXiv:2503.01659. https://arxiv.org/abs/2503.01659
- Rooein et al. (2025). *Stylometric Comparisons of Human versus AI-Generated Creative Writing.* Humanities and Social Sciences Communications. https://www.nature.com/articles/s41599-025-05986-3
- Cambridge Core. *Bilingualism and Creativity: Towards a Situated Cognition Approach.* Wiley / Journal of Creative Behavior (2019). https://onlinelibrary.wiley.com/doi/full/10.1002/jocb.238
- Cambridge Core. *Code-switching: linguistic choices across language boundaries.* https://www.cambridge.org/core/books/sociolinguistics/codeswitching-linguistic-choices-across-language-boundaries/5C08B702843D29BCED82B9311F9AC4FE
- Lapshinova-Koltunski et al. (2024). *Propagating machine translation traits to predict potential impact on the target language.* Natural Language Processing, Cambridge Core. https://www.cambridge.org/core/journals/natural-language-processing/article/propagating-machine-translation-traits-to-predict-potential-impact-on-the-target-language/A873E9434BBA7A0A10D2AEA911D3D04F
- Medium/@sha1rholder (2025). *DeepSeek v3.2: Why Chinese AI Thinks in English.* https://medium.com/@sha1rholder/thinking-in-english-dying-in-chinese-chinese-ai-landscape-in-late-2025-a72b1879084e
- IntuitionLabs (2025). *An Overview of Chinese Open-Source LLMs.* https://intuitionlabs.ai/articles/chinese-open-source-llms-2025
- CMU News (2025). *Large Language Models Have Distinctive Styles.* https://www.cs.cmu.edu/news/2025/llm-distinctive-styles
