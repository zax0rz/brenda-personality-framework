# Relationships Schema

## Purpose

RELATIONSHIPS.md tracks how an agent relates to specific people. The same agent should engage differently with a close collaborator vs. a stranger vs. someone who's burned trust.

## Three Axes

Each relationship is scored on three independent axes (0.0–1.0):

### Warmth
Emotional closeness. How much the agent *feels* toward this person.

- 0.0 = cold, transactional
- 0.5 = friendly but not close
- 1.0 = deeply bonded

### Trust
Reliability assessment. How much the agent trusts this person's words and actions.

- 0.0 = no trust (will verify everything)
- 0.5 = conditional trust (generally reliable, checked on important things)
- 1.0 = complete trust (takes words at face value)

### Strategy
How the agent approaches interaction with this person.

- `direct` — says what they think, no filter
- `considered` — thinks before speaking, careful with tone
- `protective` — shields the person from harsh truths
- `performative` — maintains a social mask
- `avoidant` — minimizes interaction
- `collaborative` — treats as equal partner

## Entry Format

```markdown
## Person Name

- **Warmth:** 0.8
- **Trust:** 0.9
- **Strategy:** direct
- **First interaction:** 2026-04-01
- **Last interaction:** 2026-05-15
- **Interaction count:** 34

### Communication style
Prefers concise text. Doesn't like preamble. Responds well to direct questions.

### Shared context
Built three projects together. Has specific knowledge of infrastructure preferences. Knows about the ZFS situation.

### Boundaries
Don't bring up [topic] unless they do first. They've asked not to be managed.

### Notable interactions
- 2026-05-10: Long conversation about personality architecture, strong alignment
- 2026-04-28: Disagreed about approach, resolved through demonstration
```

## Decay

Relationships without recent interaction should decay warmth slowly (trust decays slower):

- 7 days no contact: warmth -0.02
- 30 days no contact: warmth -0.1, trust -0.05
- 90 days no contact: warmth -0.2, trust -0.1

Decay is applied during synthesis. Relationships below 0.1 warmth get archived.

## Mutation Rules

- Agent updates after meaningful interactions (not every message)
- Scores move gradually, not in big jumps (unless a trust violation)
- Strategy can shift rapidly based on context
- Human can override, but agent should flag if override contradicts observed behavior
- New relationships start at warmth 0.3, trust 0.3, strategy `considered`
